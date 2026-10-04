#!/usr/bin/env python3
"""把 Vault/ 下的真实 .md 正文换成虚构示例人设的 fixture，供 Poyi 作为可分发记忆插件出厂自带样例。

不动的东西（verifier.py 与 Vault/projects/INDEX.md 依赖它们）：
  目录树、文件名、frontmatter 的键与结构字段值、标题层级与文字、wikilink 目标。
只动正文散文。幂等：重复运行输出一致（种子取自相对路径）。

用法:
  python Loom/scripts/make_sample_vault.py --only journal/2026-04 --dry   # 试点预览
  python Loom/scripts/make_sample_vault.py --all
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VAULT = ROOT / "Vault"

# 真实→虚构 的人设映射只放本机：Loom/scripts/sanitize-tokens.local.json（不入库）。
# 该文件缺席时本脚本不做身份替换，只把正文换成结构同形的示例内容 ——
# 仓库内不内置任何真实身份信息。
_TOKENS_FILE = Path(__file__).resolve().parent / "sanitize-tokens.local.json"
PERSONA = json.loads(_TOKENS_FILE.read_text(encoding="utf-8")).get("persona", {}) if _TOKENS_FILE.exists() else {}

SKIP = {"Vault/projects/INDEX.md"}  # 自动生成物，改完 plan.md 用 verifier --fix-projects 重建

POOL = {
    "notes": [
        "设 $m$ 为对象质量、$a$ 为加速度，则本节主关系写作 $F = m a$，方向沿合力方向。",
        "先做量纲检查：左端为 $[M][L][T]^{-2}$，右端展开后一致，故式子在单位上不塌。",
        "把上一节的表达式代入本节的边界条件，可约去一个中间量，剩下只含两个参数的形式。",
        "典型数值代入前先统一单位；此处取 $g = 9.8\\,\\mathrm{m/s^2}$ 仅为演示，做题时按卷面给定值替换。",
        "常见错误是把适用前提当恒成立：本式只在惯性系、且相互作用可视为瞬时传递时成立。",
        "此结论在 $v \\ll c$ 的极限下退化为上一节的低速形式，可据此自查推导是否走偏。",
        "例题为一步建模、二步约元、三步回代；中间变量统一用 $u, v, w$，避免与已知量重名。",
        "图像要点：横轴取自变量、纵轴取其共轭量，截距的物理意义见本节最后一条注记。",
    ],
    "projects": [
        "本阶段只做一件事：把输入输出接口钉死，内部实现允许后续整体替换。",
        "验收标准是在干净环境里一条命令跑通，不依赖任何手工搬运的文件。",
        "风险集中在外部依赖的版本漂移，锁定版本号即可规避，暂不引入额外抽象层。",
        "该决策的收益是省掉一次跨设备同步，代价是多一个需要长期维护的配置项。",
        "下一步先补回归用例，再考虑扩大功能面；未覆盖路径不计入完成度。",
        "阻塞项定位到接口约定不一致，对齐字段命名后解除。",
        "已完成：脚手架、索引注册与一次端到端试跑；三项均在示例环境中验证。",
        "度量口径统一按提交时间统计，避免同一变更在两台设备上重复计数。",
    ],
    "journal": [
        "上午状态一般，先做了不需要连续注意力的部分，把难的那块推到下午。",
        "推进了两件小事，节奏比预期慢，但没有出现返工。",
        "和一个外部依赖较了半小时劲，最后发现是我自己加的假设，去掉之后简单很多。",
        "把明天要走的头一步写清楚，省下次从头回忆。",
        "中途被打断两次，恢复上下文花了比预想更多的时间，下次先记录断点。",
        "读了两页与当前问题无关的东西，但顺手解决了一个一直挂着的小疑问。",
    ],
    "meta": [
        "此节只登记稳定事实，短期状态一律写到对应的进度文件里。",
        "判定原则：先问这条信息之后会不会变，会变的不进这一层。",
        "该条目只做路由，具体定义在它指向的文件里。",
        "变更需附理由与日期，否则回滚时无法判断当初为什么这么定。",
        "示例设备与账户信息，用于验证 Poyi 的多端路由，不对应任何真实机器。",
    ],
    "other": [
        "此处为示例内容，用于验证 Poyi 的记忆管线。",
        "该条目是样例数据，不含真实个人信息。",
        "保留本节结构以便测试索引与检索链路。",
    ],
}

JOURNAL_TITLES = [
    "整理与对齐", "跑通一条链路", "清掉遗留项", "读材料", "补记录",
]

CODE_DUMMY = ["# 示例片段", "result = compute(sample_input)"]
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
WIKI_RE = re.compile(r"\[\[[^\]]+\]\]")


def scrub(text: str) -> str:
    for k, v in PERSONA.items():
        text = text.replace(k, v)
    return text


def category(rel: str) -> str:
    if rel.startswith("Vault/notes/"):
        return "notes"
    if rel.startswith("Vault/projects/"):
        return "projects"
    if rel.startswith("Vault/journal/"):
        return "journal"
    if rel.startswith("Vault/meta/"):
        return "meta"
    return "other"


def rebuild_body(body: str, cat: str, seed: int) -> str:
    rng = random.Random(seed)
    pool = list(POOL[cat])
    holder = {"i": 0}

    def sent() -> str:
        if holder["i"] >= len(pool):
            rng.shuffle(pool)
            holder["i"] = 0
        s = pool[holder["i"]]
        holder["i"] += 1
        return s

    out: list[str] = []
    in_code = False
    table_row = 0

    for line in body.split("\n"):
        s = line.strip()

        if s.startswith("```"):
            in_code = not in_code
            out.append(line)
            if in_code:
                out.extend(CODE_DUMMY)
            continue
        if in_code:
            continue

        if not s:
            out.append("")
            continue

        if s.startswith("#"):
            level, _, head = s.partition(" ")
            date = re.search(r"\d{4}-\d{2}-\d{2}", head)
            if cat == "journal" and level.startswith("###"):
                out.append(f"{level} {rng.choice(JOURNAL_TITLES)}")
            elif date and cat in ("projects", "journal"):
                out.append(scrub(f"{level} {date.group(0)} · 示例进展"))
            else:
                out.append(scrub(line))
            continue

        if s.startswith("|"):
            is_sep = bool(re.fullmatch(r"\|[\s:|-]+\|", s))
            table_row += 1
            if is_sep or table_row == 1:
                out.append(scrub(line))
            else:
                cols = s.strip("|").split("|")
                out.append("| " + " | ".join(sent() if i == len(cols) - 1 else "示例" for i in range(len(cols))) + " |")
            continue

        if s.startswith(("- [ ]", "- [x]", "* [ ]", "* [x]")):
            box = s[: s.index("]") + 1]
            out.append(f"{box} {sent()}")
            continue

        links = WIKI_RE.findall(s)
        text = sent()
        if links:
            text = f"关联 [[{links[0][2:-2]}]]。{text}"
        numbered = re.match(r"^(\d+\.)\s", s)
        prefix = f"{numbered.group(1)} " if numbered else ("- " if s.startswith(("-", "*")) else "")
        indent = line[: len(line) - len(line.lstrip())]
        out.append(f"{indent}{prefix}{scrub(text)}")

    return "\n".join(out)


SUMMARY_FILLER = {
    "projects": "summary: 示例项目条目，用于验证 Poyi 的 plan/progress 三件套与索引链路。",
    "notes": "summary: 示例笔记条目，用于验证 Poyi 的知识锚点检索与复习选题。",
    "meta": "summary: 示例元文件条目，用于验证 Poyi 的画像与治理路由。",
    "journal": "summary: 示例日记条目，用于验证 Poyi 的日期索引与回顾提取。",
    "other": "summary: 示例条目，用于验证 Poyi 的记忆管线。",
}


def render(path: Path) -> str:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    fm, body = "", text
    if m:
        fm, body = m.group(0), text[m.end():]
    fm = scrub(fm)
    if re.search(r"^summary:", fm, re.M):
        fm = re.sub(r"^summary:.*$", SUMMARY_FILLER[category(rel)], fm, count=1, flags=re.M)
    return fm + rebuild_body(body, category(rel), sum(rel.encode("utf-8")))


def convert(path: Path, dry: bool) -> bool:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    if rel in SKIP:
        return False
    text = path.read_text(encoding="utf-8")
    new = render(path)
    if not new.endswith("\n"):
        new += "\n"
    if new == text:
        return False
    if not dry:
        path.write_text(new, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="处理 Vault 下全部 .md")
    ap.add_argument("--only", default=None, help="仅处理路径含该子串的 .md")
    ap.add_argument("--dry", action="store_true", help="打印结果不落盘")
    ap.add_argument("--print", dest="show", action="store_true", help="打印正文（配合 --only 单文件）")
    args = ap.parse_args()

    files = sorted(VAULT.rglob("*.md"))
    if args.only:
        files = [f for f in files if args.only in str(f.relative_to(ROOT)).replace("\\", "/")]
    elif not args.all:
        print("需指定 --all 或 --only <子串>", file=sys.stderr)
        return 2

    changed = 0
    for f in files:
        if convert(f, args.dry):
            changed += 1
            print(f"{'DRY ' if args.dry else ''}{f.relative_to(ROOT)}")
    if args.show and len(files) == 1:
        print("\n--- 渲染预览（未落盘） ---\n")
        print(render(files[0]))
    print(f"\n共 {len(files)} 个文件，改写 {changed} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
