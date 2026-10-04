#!/usr/bin/env python3
"""Loom Skills Compiler — 将多文件 skill 结构编译为单文件 dist。

使用方式: python3 compile.py
输出目录: ../../dist/
"""

import os
import re
import sys
from pathlib import Path

# Force stdout/stderr to use UTF-8 to prevent GBK encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

LOOM_DIR = Path(__file__).resolve().parent.parent  # D:\Projects\Poyi\Loom
SKILLS_DIR = LOOM_DIR / "skills"
DIST_DIR = LOOM_DIR / "dist"

# 不需要编译的 skill（独立子系统）；以 _ 开头的目录（如 _archive）自动跳过
# animation / notecraft 已分别于 2026-08 归档/合并删除，跳过名单随之清空
SKIP_SKILLS: set = set()
SKIP_DIR_PREFIXES = ("_",)

REF_PATTERNS = [
    ("references/", "references/"),
    ("modules/", "modules/"),
    ("schemas/", "schemas/"),
    ("projects/", "projects/"),
    ("platforms/", "references/platforms/"),
]


def find_referenced_files(skill_dir: Path, content: str) -> list:
    refs = []
    seen = set()
    pattern = r'(?:references/(?:platforms/)?|modules/|schemas/|projects/)[\w/-]+\.(?:md|py)'
    matches = re.findall(pattern, content)
    for m in matches:
        if m in seen:
            continue
        seen.add(m)
        candidates = [
            skill_dir / m,
            skill_dir / "references" / m.replace("references/", "", 1),
        ]
        for file_path in candidates:
            if file_path.exists():
                refs.append((m, file_path))
                break
    return refs


def annotate_inline_refs(content: str, refs: list) -> str:
    for ref_name, _ in refs:
        escaped = re.escape(ref_name)
        content = re.sub(
            rf'({escaped})(?!\s*\(见附录)',
            rf'\1 (见附录 \1)',
            content
        )
    return content


def compile_skill(skill_name: str) -> tuple:
    skill_dir = SKILLS_DIR / skill_name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"  ⚠️  跳过 {skill_name}: SKILL.md 不存在")
        return 0, 0, []
    content = skill_md.read_text(encoding="utf-8")
    src_lines = content.count("\n") + 1
    refs = find_referenced_files(skill_dir, content)
    compiled = annotate_inline_refs(content, refs)
    appendix_files = []
    if refs:
        compiled += "\n"
        for ref_name, ref_path in refs:
            try:
                ref_content = ref_path.read_text(encoding="utf-8")
            except Exception as e:
                ref_content = f"> ⚠️ 无法读取: {e}\n"
                print(f"    ⚠️  无法读取附录: {ref_path}")
            compiled += f"\n---\n## 附录: {ref_name}\n\n{ref_content}\n"
            appendix_files.append(ref_name)
    compiled = f"<!-- source: {skill_name} -->\n{compiled}"
    dist_lines = compiled.count("\n") + 1
    out_path = DIST_DIR / f"{skill_name}.md"
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(compiled, encoding="utf-8")
    return src_lines, dist_lines, appendix_files


def main():
    print("=" * 60)
    print("Loom Skills Compiler")
    print(f"源目录: {SKILLS_DIR}")
    print(f"输出目录: {DIST_DIR}")
    print("=" * 60)

    skills = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if d.is_dir() and not d.name.startswith(SKIP_DIR_PREFIXES) and d.name not in SKIP_SKILLS:
            if (d / "SKILL.md").exists():
                skills.append(d.name)

    print(f"\n发现 {len(skills)} 个 skill 需要编译:")
    for s in skills:
        print(f"  - {s}")

    results = []
    total_src = total_dist = 0
    for skill_name in skills:
        print(f"\n📦 编译 {skill_name}...")
        src_lines, dist_lines, appendices = compile_skill(skill_name)
        if dist_lines > 0:
            print(f"   {src_lines} 行 → {dist_lines} 行")
            if appendices:
                print(f"   附录: {', '.join(appendices)}")
            total_src += src_lines
            total_dist += dist_lines
            results.append((skill_name, src_lines, dist_lines, appendices))

    # 清理过期 dist：源已删除/跳过但 dist 仍残留的单文件
    compiled_names = {r[0] for r in results}
    for f in DIST_DIR.glob("*.md"):
        if f.name == "README.md":
            continue
        if f.stem not in compiled_names:
            f.unlink()
            print(f"  🗑 删除过期 dist: {f.name}")

    print("\n" + "=" * 60)
    print("编译完成")
    print("=" * 60)
    print(f"\n| Skill | 源行数 | 编译后行数 | 附录数 |")
    print(f"|---|---|---|---|")
    for name, src, dist, apps in results:
        print(f"| {name} | {src} | {dist} | {len(apps)} |")
    print(f"\n总计: {total_src} 行 → {total_dist} 行 ({len(results)} 个 skill)")

    total_files = len(list(DIST_DIR.glob("*.md")))
    total_lines = sum(len(f.read_text(encoding="utf-8").splitlines()) for f in DIST_DIR.glob("*.md"))
    print(f"\nDist 目录: {total_files} 个 .md 文件, 总计 {total_lines} 行")


if __name__ == "__main__":
    main()
