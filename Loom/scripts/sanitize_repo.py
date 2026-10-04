#!/usr/bin/env python3
"""全仓身份脱敏：把真实姓名/学校/学院/城市/品牌/账号等 token 换成虚构值。

只动文本文件内容，不动路径名（路径改名由改名脚本负责）。
token 顺序重要：长串先换，避免子串抢先命中。
用法: python Loom/scripts/sanitize_repo.py [--dry]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 真实→虚构 的替换表只放本机：sanitize-tokens.local.json（不入库）。
# 缺席时本脚本什么都不做 —— 公开仓库里不内置任何真实身份信息。
_TOKENS_FILE = Path(__file__).resolve().parent / "sanitize-tokens.local.json"
TOKENS = [tuple(pair) for pair in json.loads(_TOKENS_FILE.read_text(encoding="utf-8")).get("tokens", [])] if _TOKENS_FILE.exists() else []

# 不碰：原始对话数据（将被移出跟踪）、编译产物与索引（由生成器重建）、二进制
SKIP_PARTS = ("Loom/raw/", "Loom/dist/", "__pycache__", ".retrieve-bm25", ".obsidian", ".git/")


def tracked_text_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True).stdout
    files = []
    for raw in out.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8", "ignore")
        if any(s in rel.replace("\\", "/") + "/" for s in SKIP_PARTS):
            continue
        p = ROOT / rel
        if not p.is_file():
            continue
        try:
            p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        files.append(p)
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    total = hits = 0
    for p in tracked_text_files():
        text = p.read_text(encoding="utf-8")
        new = text
        for old, rep in TOKENS:
            new = new.replace(old, rep)
        if new != text:
            total += 1
            hits += sum(text.count(old) for old, _ in TOKENS)
            if not args.dry:
                p.write_text(new, encoding="utf-8")
            print(("DRY " if args.dry else "") + str(p.relative_to(ROOT)))
    print(f"\n改写 {total} 个文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
