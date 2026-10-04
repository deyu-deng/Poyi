import os
import re
import sys
import json
import argparse
import shutil
from pathlib import Path
from datetime import date, datetime

# Force stdout/stderr to use UTF-8 to prevent GBK encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 脚本相对定位（AGENTS §0：<POYI_ROOT> 双端占位，禁止写死盘符；
# 本文件位于 <POYI_ROOT>/Loom/scripts/ 下，向上两级即仓库根）
_SCRIPT = Path(__file__).resolve()
POYI_ROOT = _SCRIPT.parents[2]
SKILLS_DIR = POYI_ROOT / "Loom" / "skills"
AGENTS_MD = POYI_ROOT / "AGENTS.md"
INDEX_MD = SKILLS_DIR / "INDEX.md"
INDEX_VERSION = "4.0.0"
TODAY = date.today().isoformat()

# 官方 Agent Skills 开放标准 + Claude Code 扩展字段（Match skill-standard.md §2.1）
ALLOWED_KEYS = [
    "name", "description",          # 必填（开放标准）
    "allowed-tools", "license", "metadata",  # 可选（开放标准：metadata=官方扩展机制）
    "model", "context", "agent",    # 可选（Claude Code 子代理/模型覆盖）
    "user-invocable", "disable-model-invocation",  # 可选（调用权限）
    "hooks", "argument-hint",       # 可选（生命周期钩子 / 参数补全）
]

# 活跃发现需跳过的目录前缀（_archive 等）与显式跳过名
SKIP_DIR_PREFIXES = ("_",)


def parse_frontmatter(content):
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}, content
    yaml_text = match.group(1)
    body = content[match.end():]
    data = {}
    for line in yaml_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip().strip('"').strip("'")
            data[key] = val
    return data, body


def parse_metadata(val):
    """把 frontmatter 里的 metadata 单线 inline-JSON 解析成 dict（容错）。"""
    if not val:
        return {}
    try:
        return json.loads(val)
    except Exception:
        return {}


def build_frontmatter(data):
    lines = ["---"]
    for key in ALLOWED_KEYS:
        if key in data:
            if key == "description":
                lines.append(f'{key}: "{data[key]}"')
            else:
                lines.append(f"{key}: {data[key]}")
    lines.append("---")
    return "\n".join(lines)


def is_active_skill_dir(item: Path) -> bool:
    return item.is_dir() and not item.name.startswith(SKIP_DIR_PREFIXES) and (item / "SKILL.md").exists()


def update_skill_metadata():
    """扫描所有活跃 skill，强制对齐官方标准（仅保留 allowed 字段，name=目录名）。"""
    print("[*] 正在扫描并校准所有 Skill 的 frontmatter ...")
    for item in sorted(SKILLS_DIR.iterdir()):
        if not is_active_skill_dir(item):
            continue
        skill_name = item.name
        skill_file = item / "SKILL.md"
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
        data, body = parse_frontmatter(content)
        clean = {k: data[k] for k in ALLOWED_KEYS if k in data}
        clean["name"] = skill_name
        if "description" not in clean or not clean["description"]:
            clean["description"] = "No description provided."
        new_fm = build_frontmatter(clean)
        new_content = new_fm + "\n" + body.lstrip("\n")
        if new_content != content:
            with open(skill_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  ~ 校准了 {skill_name}/SKILL.md")


def gather_skills():
    """返回扁平的 (name, description) 列表，无角色分组，从磁盘推导。"""
    rows = []
    for item in sorted(SKILLS_DIR.iterdir()):
        if not is_active_skill_dir(item):
            continue
        with open(item / "SKILL.md", "r", encoding="utf-8") as f:
            data, _ = parse_frontmatter(f.read())
        name = data.get("name", item.name)
        desc = data.get("description", "")
        rows.append((name, desc))
    return rows


def render_table(rows):
    lines = [
        "| 技能 | 描述（用途 + 触发） |",
        "|---|---|"
    ]
    for name, desc in rows:
        d = desc.replace("|", "\\|")
        lines.append(f"| `{name}` | {d} |")
    return "\n".join(lines)


def replace_anchor(content, anchor_start, anchor_end, new_text):
    pat = re.compile(re.escape(anchor_start) + r".*?" + re.escape(anchor_end), re.DOTALL)
    if pat.search(content):
        return pat.sub(anchor_start + "\n" + new_text + "\n" + anchor_end, content)
    return content


def extract_old_meta(index_text):
    """从旧 INDEX 的 YAML 视图中抢救 curated 的 triggers / depends_on（避免信息丢失）。"""
    meta = {}
    for m in re.finditer(r"name:\s*(\S+)", index_text):
        nm = m.group(1)
        seg_start = m.end()
        nxt = re.search(r"name:\s*\S+", index_text[seg_start:])
        seg_end = seg_start + (nxt.start() if nxt else (len(index_text) - seg_start))
        seg = index_text[seg_start:seg_end]
        trig = re.search(r"triggers:\s*\[([^\]]*)\]", seg)
        dep = re.search(r"depends_on:\s*\[([^\]]*)\]", seg)
        meta[nm] = {
            "triggers": trig.group(1).strip() if trig else "",
            "depends_on": dep.group(1).strip() if dep else "",
        }
    return meta


def render_yaml(rows, old_meta):
    lines = ["skills:"]
    for name, desc in rows:
        safe = desc.replace('"', '\\"')
        loc = f"Loom/skills/{name}/SKILL.md"
        lines.append(f"  - name: {name}")
        lines.append(f'    description: "{safe}"')
        lines.append(f"    location: {loc}")
        lines.append(f"    status: active")
        om = old_meta.get(name, {})
        if om.get("triggers"):
            lines.append(f"    triggers: [{om['triggers']}]")
        if om.get("depends_on"):
            lines.append(f"    depends_on: [{om['depends_on']}]")
    return "\n".join(lines)


def fix_index_header(content, total):
    content = re.sub(r"(?m)^INDEX_version:.*$", f"INDEX_version: {INDEX_VERSION}", content)
    content = re.sub(r"(?m)^last_updated:.*$", f"last_updated: {TODAY}", content)
    content = re.sub(r"(?m)^total_skills:.*$", f"total_skills: {total}", content)
    return content


def sync_docs():
    print("=== 开始同步文档（单一事实源 = 磁盘）===")
    update_skill_metadata()
    rows = gather_skills()
    table = render_table(rows)

    # AGENTS.md：注入扁平表格
    if AGENTS_MD.exists():
        c = AGENTS_MD.read_text(encoding="utf-8")
        c = replace_anchor(c, "<!-- SKILL_TABLE_START -->", "<!-- SKILL_TABLE_END -->", table)
        AGENTS_MD.write_text(c, encoding="utf-8")
        print(f"[*] 已更新 AGENTS.md 技能表格（{len(rows)} 个）")

    # INDEX.md：重建表格 + YAML 视图 + 头部
    idx = INDEX_MD.read_text(encoding="utf-8")
    idx = replace_anchor(idx, "<!-- SKILL_TABLE_START -->", "<!-- SKILL_TABLE_END -->", table)
    old_meta = extract_old_meta(idx)
    new_yaml = render_yaml(rows, old_meta)
    idx = re.sub(r"```yaml\n.*?\n```", f"```yaml\n{new_yaml}\n```", idx, flags=re.DOTALL)
    idx = fix_index_header(idx, len(rows))
    INDEX_MD.write_text(idx, encoding="utf-8")
    print(f"=== 同步完成（共 {len(rows)} 个活跃技能）===")


def delete_skill(name):
    skill_dir = SKILLS_DIR / name
    if not skill_dir.exists():
        print(f"[!] 技能 {name} 不存在，无法删除。")
        return
    shutil.rmtree(skill_dir)
    print(f"[*] 已删除目录 {name}/")
    sync_docs()


def create_skill(name, desc):
    skill_dir = SKILLS_DIR / name
    if skill_dir.exists():
        print(f"[!] 技能 {name} 已存在。")
        return
    skill_dir.mkdir(parents=True)
    meta = {"version": "1.0.0", "owner": "sample-user",
            "last_validated": TODAY, "deps": []}
    data = {"name": name, "description": desc,
            "metadata": json.dumps(meta, ensure_ascii=False)}
    with open(skill_dir / "SKILL.md", "w", encoding="utf-8") as f:
        f.write(build_frontmatter(data) + f"\n\n# {name}\n\n此处编写该技能的具体逻辑...\n")
    print(f"[*] 成功创建技能 {name}")
    sync_docs()


def scan_trigger_collisions():
    """跨技能触发词精确碰撞检测：两个 skill 显式声明同一触发 token 即报警（WARN）。"""
    per_skill = {}
    for item in sorted(SKILLS_DIR.iterdir()):
        if not is_active_skill_dir(item):
            continue
        data, _ = parse_frontmatter((item / "SKILL.md").read_text(encoding="utf-8"))
        # 长度 >10 的 token 视为散文泄漏（如描述里误吞的句子片段），跳过以免误报
        per_skill[item.name] = {t for t in extract_triggers(data.get("description", ""))
                                if len(t) <= 10}
    collisions = {}
    names = list(per_skill)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            ov = per_skill[names[i]] & per_skill[names[j]]
            if ov:
                collisions.setdefault(names[i], []).append((names[j], ov))
                collisions.setdefault(names[j], []).append((names[i], ov))
    return collisions


def doctor():
    """健康度扫描：eval 缺失 / metadata 缺失 / last_validated 过期 / description 缺触发词 / deps 悬空 / 跨技能触发词碰撞。"""
    print("=== Skill doctor（健康度扫描）===")
    all_names = {d.name for d in SKILLS_DIR.iterdir()
                 if is_active_skill_dir(d)}
    total = errs = warns = infos = 0
    for item in sorted(SKILLS_DIR.iterdir()):
        if not is_active_skill_dir(item):
            continue
        name = item.name
        total += 1
        with open(item / "SKILL.md", "r", encoding="utf-8") as f:
            data, _ = parse_frontmatter(f.read())
        desc = data.get("description", "")
        issues = []

        # 1. eval.md
        if not (item / "eval.md").exists():
            issues.append("ERROR 缺 eval.md")

        # 2. metadata 完整性
        meta = parse_metadata(data.get("metadata", ""))
        if not meta:
            issues.append("ERROR 缺 metadata")
        else:
            for fld in ("version", "owner", "last_validated"):
                if not meta.get(fld):
                    issues.append(f"ERROR metadata.{fld} 缺失")
            lv = meta.get("last_validated", "")
            try:
                d = datetime.strptime(lv, "%Y-%m-%d").date()
                if (date.today() - d).days > 90:
                    issues.append(f"WARN last_validated 已过期({lv})")
            except Exception:
                if lv:
                    issues.append("WARN last_validated 格式异常")

        # 3. description 触发词（软提示，非阻断）
        if not extract_triggers(desc):
            issues.append("INFO description 无显式触发词")

        # 4. deps 悬空
        deps = meta.get("deps", []) if isinstance(meta.get("deps"), list) else []
        for dep in deps:
            if dep not in all_names:
                issues.append(f"WARN deps 悬空: {dep}")

        if issues:
            lvl = ("ERROR" if any(i.startswith("ERROR") for i in issues) else
                   "WARN" if any(i.startswith("WARN") for i in issues) else "INFO")
            if lvl == "ERROR":
                errs += 1
            elif lvl == "WARN":
                warns += 1
            else:
                infos += 1
            print(f"  [{lvl}] {name}: " + " | ".join(issues))
        else:
            print(f"  [OK] {name}")

    # 5. 跨技能触发词碰撞（精确 token 相撞 = 路由歧义）
    collisions = scan_trigger_collisions()
    if collisions:
        print("\n--- 跨技能触发词碰撞 (WARN) ---")
        seen = set()
        for name in sorted(collisions):
            for other, toks in collisions[name]:
                key = tuple(sorted((name, other)))
                if key in seen:
                    continue
                seen.add(key)
                print(f"  [WARN] {name} ∩ {other}: {sorted(toks)}")
                warns += 1
    else:
        print("\n--- 跨技能触发词碰撞：无 ---")

    print(f"=== 完成：{total} 技能, {errs} ERROR, {warns} WARN, {infos} INFO ===")
    print("提示：ERROR 必须修；WARN 建议修（含跨技能触发词相撞）；INFO 为触发词风格提示（靠 token 重叠兜底）。")


# ---------------------------------------------------------------------------
# eval 回路：离线启发式校验「应触发 / 不应触发」用例
# ---------------------------------------------------------------------------

def parse_eval(text):
    cases = {"should": [], "shouldnot": []}
    cur = None
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"#+\s*should\s+not\s+trigger", s, re.I):
            cur = "shouldnot"
            continue
        if re.match(r"#+\s*should\s+trigger", s, re.I):
            cur = "should"
            continue
        if cur and (s.startswith("-") or s.startswith("*")):
            cases[cur].append(s.lstrip("-*").strip())
    return cases


def extract_triggers(desc):
    m = re.search(r"触发词\s*[:：]\s*([^\n]+)", desc)
    if not m:
        return []
    seg = m.group(1).lstrip("：:")
    parts = re.split(r"[、，,\s|/]", seg)
    out = []
    for p in parts:
        p = p.strip().strip('"').strip("'").strip("「").strip("」").strip("（").strip("）").strip("。").strip(".")
        if p:
            out.append(p)
    return out


def _tokens(s):
    return set(re.findall(r"[一-鿿]|[a-z0-9]+", s.lower()))


def _overlap(a, b):
    return len(_tokens(a) & _tokens(b)) >= 2


def check_cases(cases, desc, trigs):
    warns = []
    dl = desc.lower()
    for p in cases["should"]:
        pl = p.lower()
        hit = any(t.lower() in pl for t in trigs) if trigs else False
        if not hit and not _overlap(pl, dl):
            warns.append(f"should-trigger 可能不唤醒: {p[:38]}")
    for p in cases["shouldnot"]:
        pl = p.lower()
        if trigs and any(t.lower() in pl for t in trigs):
            warns.append(f"should-not-trigger 却含触发词，可能误触发: {p[:38]}")
    return warns


def eval_skills():
    print("=== Skill eval 回路（离线启发式）===")
    total = gaps = warns = 0
    for item in sorted(SKILLS_DIR.iterdir()):
        if not is_active_skill_dir(item):
            continue
        name = item.name
        total += 1
        ev = item / "eval.md"
        if not ev.exists():
            print(f"  [GAP] {name}: 缺少 eval.md")
            gaps += 1
            continue
        with open(item / "SKILL.md", "r", encoding="utf-8") as f:
            data, _ = parse_frontmatter(f.read())
        desc = data.get("description", "")
        trigs = extract_triggers(desc)
        cases = parse_eval(ev.read_text(encoding="utf-8"))
        w = check_cases(cases, desc, trigs)
        warns += len(w)
        print(f"  [OK] {name}: +{len(cases['should'])} -{len(cases['shouldnot'])} 警告:{len(w)}")
        for ww in w:
            print(f"        ! {ww}")
    print(f"=== 完成：{total} 活跃技能, {gaps} 缺 eval.md, {warns} 离线警告 ===")
    print("提示：eval.md 写法 -> '## Should trigger' / '## Should not trigger' 下每条一个 - 用例。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poyi Skills Manager")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("sync", help="从磁盘重建 INDEX.md / AGENTS.md（表格+YAML+头部）并校准 frontmatter")
    subparsers.add_parser("eval", help="扫描各 skill 的 eval.md，离线校验触发/不触发用例")
    subparsers.add_parser("doctor", help="扫描 skill 健康度（eval/metadata/last_validated/deps）")

    del_parser = subparsers.add_parser("delete", help="删除一个技能（删目录 + 同步）")
    del_parser.add_argument("name", help="技能名")

    create_parser = subparsers.add_parser("create", help="新建技能")
    create_parser.add_argument("name", help="技能名")
    create_parser.add_argument("--desc", default="Auto-generated skill", help="描述")

    args = parser.parse_args()
    if args.command == "sync":
        sync_docs()
    elif args.command == "eval":
        eval_skills()
    elif args.command == "doctor":
        doctor()
    elif args.command == "delete":
        delete_skill(args.name)
    elif args.command == "create":
        create_skill(args.name, args.desc)
    else:
        parser.print_help()
