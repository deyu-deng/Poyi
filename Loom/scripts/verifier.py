#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
Poyi 一致性校验器 (verifier)
===========================

对应 claude-obsidian 的 verifier sub-agent / pre-commit 审计能力。
Poyi 此前在「神经系统」维度为真空白（审计 2026-06-30 标记 Hooks=无、Sub Agent=0）。

本脚本做**规格声明 vs 磁盘物理**的一致性审计，专治「声明与物理不符」类 bug：
  - AGENTS.md §1 声明的 projects 列表 ≠ Vault/projects 磁盘
  - AGENTS.md 声明的技能数 ≠ Loom/skills 磁盘
  - AGENTS.md 声明的 wiki 子目录在磁盘缺失
  - 各 INDEX.md 的 wikilink 指向磁盘不存在的页面（结构级死链）
  - 空项目目录（幽灵目录，如 claude-obsidian-source）
  - 项目注册表（plan.md frontmatter）与磁盘 Cloud 目录 / INDEX 漂移

与 lint 技能的区别：lint 查 wiki *内容*健康（孤儿/死链/风格/写作），人力触发；
verifier 查 *系统规格*与磁盘是否自洽，由 git pre-commit 自动触发。两者互补。

退出码：
  0 = 通过（无 BLOCKER）
  1 = 存在 BLOCKER（应阻断提交）
  2 = 运行错误（脚本自身异常）

用法：
  python3 verifier.py            # 人类可读输出，BLOCKER 才非零退出
  python3 verifier.py --json     # 机器可读 JSON
  python3 verifier.py --strict   # 将 WARN 也视为失败（CI / 全量门禁）
  python3 verifier.py --fix-projects  # 依据 plan.md frontmatter 重新生成 Vault/projects/INDEX.md
"""
import json
import os
import re
import subprocess
import sys
import datetime
from pathlib import Path

# ---- 解析仓库根（git 环境；非 git 时退化为脚本父级上溯） ----
try:
    REPO = Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        stderr=subprocess.DEVNULL,
    ).decode().strip())
except Exception:
    REPO = Path(__file__).resolve().parents[2]

BLOCKERS: list[str] = []
WARNS: list[str] = []


def err(msg: str) -> None:
    BLOCKERS.append(msg)


def warn(msg: str) -> None:
    WARNS.append(msg)


def read_text(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return None


def list_markdown_basenames(root: Path) -> set[str]:
    """收集仓库内所有 .md 文件名（去扩展名），用于 wikilink 死链判定。"""
    names = set()
    for f in root.rglob("*.md"):
        names.add(f.stem)
    return names


def check_projects(agents_text: str | None) -> None:
    """AGENTS §1 项目列表 ↔ Vault/projects 磁盘"""
    projects_dir = REPO / "Vault" / "projects"
    actual = sorted([d.name for d in projects_dir.iterdir() if d.is_dir()])
    if agents_text:
        m = re.search(r"(\d+)\s*个项目[^\n]*?：([^\n]+)", agents_text)
        if m:
            declared = [x.strip() for x in m.group(2).split("/") if x.strip()]
            if sorted(declared) != actual:
                err(
                    f"AGENTS §1 声明 {len(declared)} 个项目 {declared}，"
                    f"但 Vault/projects 磁盘为 {actual}"
                )
            # 空目录（幽灵目录）仅告警
            for d in actual:
                if not any((projects_dir / d).iterdir()):
                    warn(f"空项目目录（幽灵目录）: Vault/projects/{d}")
            return
        warn("AGENTS §1 未找到项目列表声明，跳过项目一致性校验")
    else:
        err("AGENTS.md 缺失，无法校验项目列表")


def check_skills(agents_text: str | None) -> None:
    """AGENTS 声明技能数 ↔ Loom/skills 磁盘"""
    skills_dir = REPO / "Loom" / "skills"
    actual = [
        d.name for d in skills_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    ]
    if agents_text:
        m = re.search(r"(\d+)\s*个技能定义", agents_text)
        if m:
            n = int(m.group(1))
            if n != len(actual):
                err(
                    f"AGENTS 声明 {n} 个技能，但 Loom/skills 磁盘有 {len(actual)} 个：{sorted(actual)}"
                )
            return
        warn("AGENTS 未声明技能数，跳过技能一致性校验")


def check_skill_count_vs_index() -> None:
    """Loom/skills/ 实际目录数 ↔ Loom/skills/INDEX.md 声明的 total_skills

    同时检查 INDEX.md 的 YAML 区是否注册了所有实际存在的 skill。
    任一不一致均为 BLOCKER，防止 Agent 绕过注册流程偷偷新建 skill 目录。
    """
    skills_dir = REPO / "Loom" / "skills"
    index_path = skills_dir / "INDEX.md"
    index_text = read_text(index_path)
    if not index_text:
        err("Loom/skills/INDEX.md 缺失，无法校验技能注册")
        return

    # 实际存在的 skill 目录（含 SKILL.md）
    actual = sorted([
        d.name for d in skills_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    ])

    # INDEX.md 声明的总数
    total_m = re.search(r"total_skills:\s*(\d+)", index_text)
    declared_total = int(total_m.group(1)) if total_m else None

    if declared_total is not None and declared_total != len(actual):
        err(
            f"Loom/skills/INDEX.md 声明 total_skills={declared_total}，"
            f"但磁盘实际有 {len(actual)} 个 skill 目录：{actual}"
        )

    # INDEX.md YAML 区注册的 skill name 列表
    registered = set()
    for m in re.finditer(r"-\s+name:\s+(\S+)", index_text):
        registered.add(m.group(1))

    unregistered = set(actual) - registered
    if unregistered:
        err(
            f"以下 skill 目录在磁盘存在但未在 INDEX.md YAML 区注册：{sorted(unregistered)}。"
            f"请在 INDEX.md 补充 YAML 条目，或确认是否应合并到已有 skill（AGENTS.md §5 修改优先于新建）。"
        )

    # 如果 skill 总数增加了，额外提醒"修改优先于新建"规则
    if declared_total is not None and len(actual) > declared_total:
        warn(
            f"skill 总数增加：{declared_total} → {len(actual)}。"
            f"请确认这些新 skill 无法合并到已有 skill 中（参见 AGENTS.md §5 修改优先于新建、审计日志 2026-07-19）。"
        )


def check_wiki_subdirs(agents_text: str | None) -> None:
    """AGENTS §1 声明的 wiki 子目录 ↔ 磁盘"""
    if not agents_text:
        return
    wiki_dir = REPO / "Loom" / "wiki"
    # 抽取 AGENTS 中 Loom/wiki 树下的子目录行：如 "│   ├── comparisons/  ← ..."
    for m in re.finditer(r"├──\s+([A-Za-z0-9_-]+)/\s*[←]", agents_text):
        sub = m.group(1)
        if sub in ("wiki", "meta", "reports", "skills", "raw", "scripts", "dist", "english-data", "review"):
            # 仅核查 wiki 直接子目录里被显式标注的
            pass
    # 直接核对 AGENTS 明确列举的那批 wiki 子目录
    expected = ["english-data", "review", "comparisons", "concepts",
                "entities", "sources", "meta", "reports"]
    for sub in expected:
        if not (wiki_dir / sub).is_dir():
            warn(f"AGENTS 声明 wiki 子目录 Loom/wiki/{sub}/ 在磁盘缺失")


def check_index_links() -> None:
    """各 INDEX.md 的 wikilink ↔ 磁盘 .md 存在性（结构级死链）"""
    basenames = list_markdown_basenames(REPO)
    index_files = [REPO / "Vault" / "projects" / "INDEX.md"]
    index_files += list((REPO / "Loom" / "wiki").rglob("INDEX.md"))
    for idx in index_files:
        txt = read_text(idx)
        if not txt:
            continue
        rel = idx.relative_to(REPO)
        seen = set()
        for link in re.findall(r"\[\[([^\]]+)\]\]", txt):
            target = link.split("|")[0].split("#")[0].strip()
            if not target or target in seen:
                continue
            seen.add(target)
            if target in basenames:
                continue
            # 可能是跨目录链接（如 [[SRTP]] → entities/SRTP.md），
            # 若全仓库无此 basename 的 .md，则视为结构死链（告警）
            if "/" not in target and not target.startswith("http"):
                warn(f"{rel} 引用 [[{target}]]，但仓库内无对应 .md（结构死链）")


def check_srtp_literature_index() -> None:
    """srtp 项目：Patent/ 或 Papers/ 新增文件时，Literature-Index.md 是否同步更新。

    限定路径范围 Vault/projects/srtp/ 下。
    通过 git diff --cached --name-status 检查 staged changes：
      - 若 Patent/ 或 Papers/ 下有新增（A 状态）的 .md 文件
      - 但 Docs/Literature-Index.md 不在 staged changes 中
      → BLOCKER：新增文献但未更新 Literature-Index.md。
    """
    srtp_root = REPO / "Vault" / "projects" / "srtp"
    if not srtp_root.is_dir():
        return  # srtp 项目不存在，跳过

    try:
        output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-status", "--", "Vault/projects/srtp/"],
            stderr=subprocess.DEVNULL,
            cwd=str(REPO),
        ).decode().strip()
    except subprocess.CalledProcessError:
        # git diff 失败（例如不在 git 仓库中），静默跳过
        return

    if not output:
        return  # srtp 目录下无任何 staged 变更

    new_patent_or_paper = False
    literature_index_staged = False

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        # 格式：<status>\t<path>
        # 合并 / 复制等操作可能产生多字符状态（如 "MM"），取首字符判断
        status, _, path = line.partition("\t")
        status = status[0] if status else ""

        if path.startswith("Vault/projects/srtp/Docs/Literature-Index.md"):
            literature_index_staged = True

        if status == "A" and (
            path.startswith("Vault/projects/srtp/Patent/") or
            path.startswith("Vault/projects/srtp/Papers/")
        ):
            new_patent_or_paper = True

    if new_patent_or_paper and not literature_index_staged:
        err(
            "srtp 项目：Patent/ 或 Papers/ 目录下有新增文献，"
            "但 Docs/Literature-Index.md 未同步更新。"
            "请在 Literature-Index.md 中添加新条目后重新 git add。"
        )


# ---------------------------------------------------------------------------
# 项目注册表（plan.md frontmatter）↔ 磁盘 Cloud 目录 / INDEX 漂移
# 与上方 check_projects()（AGENTS §1 声明 vs Vault/projects 磁盘）互补：
#   - check_projects   ：结构层一致性（声明列表 ↔ 目录）
#   - 本组函数         ：内容层一致性（frontmatter 注册 ↔ Cloud 目录 / 过期 / 未登记）
# ---------------------------------------------------------------------------
PROJECTS_DIR = REPO / "Vault" / "projects"
CLOUD_DIR = Path(os.environ.get("CLOUD_PROJECTS", r"D:\Cloud\Projects"))

GROUP_ORDER = ["system", "product", "research"]
GROUP_LABEL = {
    "system": "系统自身",
    "product": "产品 / 工程",
    "research": "科研 / 课程",
}
STALE_DAYS = 30
STATUS_LABEL = {
    "active": "进行中",
    "paused": "暂停",
    "blocked": "阻塞",
    "done": "已完成",
    "archived": "已归档",
}


def parse_frontmatter(text: str):
    """返回 (meta_dict, body)。无 frontmatter 时 meta=None。"""
    s = text.lstrip()
    if not s.startswith("---"):
        return None, text
    end = s.find("\n---", 3)
    if end == -1:
        return None, text
    block = s[3:end].strip("\n")
    body = s[end + 4:]
    meta: dict = {}
    for line in block.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            meta[k] = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
        else:
            meta[k] = v
    return meta, body


def load_registry_projects() -> list:
    """扫描 Vault/projects/*/plan.md，返回 [(name, dir, meta|None)]。"""
    projects = []
    for d in sorted(PROJECTS_DIR.iterdir()):
        if not d.is_dir():
            continue
        plan = d / "plan.md"
        if not plan.exists():
            continue
        text = read_text(plan) or ""
        meta, _ = parse_frontmatter(text)
        projects.append((d.name, d, meta))
    return projects


def registry_drift(projects: list, today: datetime.date) -> list:
    """返回漂移告警列表（cloud 不存在 / 过期 / Cloud 未登记）。"""
    warnings: list = []
    registered_cloud_bases = set()
    # cloud 基址是否在本机可访问：Windows 端 CLOUD_PROJECTS 指向真实云盘，
    # Mac 等仅持知识壳的设备无此目录。存在性校验只在可访问时进行——
    # 否则 cloud 字段（Windows 设备事实）在 Mac 上会无谓报 WARN。
    # 反向的"未登记"检查（下方 CLOUD_DIR.is_dir() 分支）已同样受此约束。
    cloud_available = CLOUD_DIR.is_dir()
    for name, d, meta in projects:
        if not meta:
            continue
        cloud = meta.get("cloud", "")
        if cloud:
            registered_cloud_bases.add(os.path.basename(cloud.rstrip("/\\")))
            if cloud_available and not (REPO / cloud).exists() and not Path(cloud).exists():
                warnings.append(f"⚠️ {name} 声明的 Cloud 目录不存在：{cloud}")
        updated = meta.get("updated", "")
        try:
            ud = datetime.date.fromisoformat(updated)
            if (today - ud).days > STALE_DAYS:
                warnings.append(
                    f"⚠️ {name} 进度超 {STALE_DAYS} 天未更新（updated={updated}）"
                )
        except ValueError:
            warnings.append(f"⚠️ {name} 的 updated 字段格式异常：{updated}")

    if CLOUD_DIR.is_dir():
        for cname in sorted(os.listdir(CLOUD_DIR)):
            cp = CLOUD_DIR / cname
            if not cp.is_dir():
                continue
            if cname.startswith("_"):  # 忽略 Sandbox 等临时目录
                continue
            if cname not in registered_cloud_bases:
                warnings.append(f"⚠️ Cloud 目录未登记：{CLOUD_DIR}\\{cname}")
    return warnings


def generate_project_index(projects: list, today: datetime.date, warnings: list) -> str:
    """依据 frontmatter 生成 Vault/projects/INDEX.md 文本。"""
    groups = {g: [] for g in GROUP_ORDER}
    for name, d, meta in projects:
        if not meta:
            continue
        g = meta.get("group", "product")
        if g not in groups:
            g = "product"
        groups[g].append((name, d, meta))
    for g in groups:
        groups[g].sort(key=lambda x: x[2].get("created", ""), reverse=True)

    out = []
    out.append("# Projects · 索引（自动生成，勿手改）")
    out.append("")
    out.append(
        f"> 本文件由 `Loom/scripts/verifier.py --fix-projects` 自动生成，"
        f"最后生成：{today.isoformat()}。"
    )
    out.append(
        "> 维护方式：修改各项目 `plan.md` 的 frontmatter 后重跑 "
        "`python Loom/scripts/verifier.py --fix-projects`，**勿直接手改本文件**。"
    )
    out.append(f"> 当前共登记 {len([p for p in projects if p[2]])} 个项目。")
    out.append("")
    out.append("---")
    out.append("")

    for g in GROUP_ORDER:
        items = groups[g]
        if not items:
            continue
        out.append(f"## {GROUP_LABEL[g]}")
        out.append("")
        for name, d, meta in items:
            title = meta.get("title", name)
            summary = meta.get("summary", "")
            cloud = meta.get("cloud", "")
            tech = meta.get("tech", [])
            status = meta.get("status", "")
            status_txt = STATUS_LABEL.get(status, status)
            created = meta.get("created", "")
            updated = meta.get("updated", "")
            out.append(f"### {title}")
            if summary:
                out.append(summary)
                out.append("")
            if cloud:
                out.append(f"- **Cloud**：`{cloud}`")
            else:
                out.append(f"- **Cloud**：无（规划层 / 系统自身）")
            out.append(f"- **技术栈**：{', '.join(tech) if tech else '待定'}")
            out.append(f"- **状态**：{status_txt} · 创建 {created} · 更新 {updated}")
            links = ["plan.md", "progress.md"]
            if (d / "research.md").exists():
                links.append("research.md")
            out.append(f"- 详见：{' · '.join(links)}")
            out.append("")

    out.append("---")
    out.append("")
    out.append("## 漂移告警")
    out.append("")
    if warnings:
        for w in warnings:
            out.append(w)
    else:
        out.append(
            "✅ 无漂移：所有项目 frontmatter 完整、Cloud 目录存在、"
            "进度新鲜、无未登记 Cloud 目录。"
        )
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 生命周期")
    out.append("")
    out.append("```")
    out.append("活跃 → 持续更新项目文档")
    out.append("  ↓")
    out.append("暂停 > 1 学期 → 标注状态，保留目录")
    out.append("  ↓")
    out.append("完成 / 废弃 → Archive/<原项目名>/")
    out.append("```")
    out.append("")
    return "\n".join(out)


def check_or_fix_project_registry(fix: bool) -> None:
    """项目注册表一致性：frontmatter ↔ Cloud 目录 / INDEX 漂移。

    fix=True  → 重新生成 Vault/projects/INDEX.md；
    fix=False → 仅将漂移作为 WARN 报告（不写文件，由主流程输出）。
    """
    projects = load_registry_projects()
    today = datetime.date.today()

    # 目录存在但无 plan.md（未登记到注册表）
    for d in sorted(PROJECTS_DIR.iterdir()):
        if not d.is_dir():
            continue
        if not (d / "plan.md").exists():
            warn(f"⚠️ Vault/projects/{d.name}/ 无 plan.md（未登记到项目注册表）")

    warnings = registry_drift(projects, today)

    if fix:
        index_text = generate_project_index(projects, today, warnings)
        (PROJECTS_DIR / "INDEX.md").write_text(index_text, encoding="utf-8")
        print(
            f"[fix-projects] 已生成 INDEX.md"
            f"（{len([p for p in projects if p[2]])} 个项目，{len(warnings)} 条告警）"
        )
        for w in warnings:
            print("  " + w)
    else:
        for w in warnings:
            warn(w)


def main() -> int:
    as_json = "--json" in sys.argv
    strict = "--strict" in sys.argv
    fix_projects = "--fix-projects" in sys.argv

    agents_text = read_text(REPO / "AGENTS.md")
    check_projects(agents_text)
    check_skills(agents_text)
    check_skill_count_vs_index()
    check_wiki_subdirs(agents_text)
    check_index_links()
    check_srtp_literature_index()
    check_or_fix_project_registry(fix_projects)

    if as_json:
        print(json.dumps({
            "blockers": BLOCKERS,
            "warns": WARNS,
            "ok": len(BLOCKERS) == 0,
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("Poyi 一致性校验 (verifier)")
        print("=" * 60)
        if BLOCKERS:
            print(f"\n🔴 BLOCKER ({len(BLOCKERS)}) — 阻断提交:")
            for b in BLOCKERS:
                print(f"  • {b}")
        if WARNS:
            print(f"\n🟡 WARN ({len(WARNS)}) — 不阻断，建议修复:")
            for w in WARNS:
                print(f"  • {w}")
        if not BLOCKERS and not WARNS:
            print("\n✅ 全部一致，无问题。")
        elif not BLOCKERS:
            print(f"\n✅ 无 BLOCKER（{len(WARNS)} 条 WARN 不阻断提交）。")
        print("=" * 60)

    if BLOCKERS:
        return 1
    if strict and WARNS:
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # 运行错误
        print(f"verifier 运行异常: {e}", file=sys.stderr)
        sys.exit(2)
