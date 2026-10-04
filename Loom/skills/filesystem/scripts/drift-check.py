#!/usr/bin/env python3
"""
drift-check.py — filesystem skill 结构漂移检测（被动自更新 A 方案）

用法：
    python drift-check.py                 # 扫描 D 盘并与期望结构对比，输出差异
    python drift-check.py --quiet         # 无差异时零输出（供 skill 加载钩子用）
    python drift-check.py --base D:\\     # 自定义根目录（测试用）

退出码：
    0 = 无差异（结构一致）
    1 = 有差异（新增/缺失，需人工确认是否更新 windows.md）
    2 = 运行错误

原理：
    以 generate-map.py 的 DIRECTORY_NOTES 为"期望结构"（与 windows.md 同源），
    扫描实际磁盘顶层+二层，报告两类漂移：
      缺失 = 期望存在但实际不存在（文档写了不存在的路径，会误导 Agent）
      新增 = 实际存在但期望未记录（磁盘变了，文档没跟上）
    受控顶层（Data/Development/Poyi/Inbox/Tools/tmp）下的新增子目录才会报告，
    Software/Cloud/Games 等动态目录只查顶层，避免软件、媒体目录噪音。
"""

import argparse
import importlib.util
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
GEN_MAP = SCRIPT_DIR / "generate-map.py"

# 受控顶层：新增二层子目录时报告（这些目录结构是精心设计的）
STRUCTURED_TOPS = {"Data", "Development", "Poyi", "Inbox", "Tools"}

# 已知噪音顶层：不作为"新增"报告
NOISE_TOPS = {".appdata", "WPS Software", "WpSystem", "腾讯应用宝文件管理", "Program Files"}


def load_generate_map():
    """加载 generate-map.py 模块（复用 DIRECTORY_NOTES / SKIP_TOP / SKIP_DEEP）"""
    spec = importlib.util.spec_from_file_location("generate_map", GEN_MAP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scan(base: Path, mod) -> tuple[set, set]:
    """扫描实际结构，返回 (顶层集合, 二层 key 集合)"""
    tops = set()
    sub_keys = set()
    for top in base.iterdir():
        if not top.is_dir() or top.name.startswith(".") or top.name in mod.SKIP_TOP:
            continue
        tops.add(top.name)
        for sub in top.iterdir():
            if not sub.is_dir() or sub.name.startswith(".") or sub.name in mod.SKIP_DEEP:
                continue
            sub_keys.add(f"{top.name}/{sub.name}")
    return tops, sub_keys


def expected_from_notes(notes: dict) -> tuple[set, set]:
    """从 DIRECTORY_NOTES 提取期望顶层与期望 key（排除 ⚠️ 历史路径标记）"""
    exp_tops = set()
    exp_keys = set()
    for key, note in notes.items():
        if note.startswith("⚠️"):
            continue
        parts = key.split("/")
        exp_tops.add(parts[0])
        exp_keys.add(key)
    return exp_tops, exp_keys


def main():
    parser = argparse.ArgumentParser(description="filesystem skill 结构漂移检测")
    parser.add_argument("--base", default=r"D:\\", help="扫描根目录（默认 D:\\）")
    parser.add_argument("--quiet", action="store_true", help="无差异时零输出")
    args = parser.parse_args()

    base = Path(args.base)
    if not base.exists():
        print(f"❌ 根目录不存在：{base}")
        sys.exit(2)

    try:
        mod = load_generate_map()
    except Exception as e:
        print(f"❌ 无法加载 generate-map.py：{e}")
        sys.exit(2)

    notes = mod.DIRECTORY_NOTES
    actual_tops, actual_sub_keys = scan(base, mod)
    exp_tops, exp_keys = expected_from_notes(notes)

    missing = []   # 期望有、实际无
    added = []     # 实际有、期望无

    # 缺失：期望 key 中 depth<=2 的路径实际不存在
    for key in sorted(exp_keys):
        depth = key.count("/")
        if depth > 2:
            continue
        if not (base / Path(*key.split("/"))).is_dir():
            missing.append(key)

    # 新增顶层
    for top in sorted(actual_tops - exp_tops):
        if top not in NOISE_TOPS:
            added.append(f"[顶层] {top}")

    # 新增受控顶层下的二层子目录
    for key in sorted(actual_sub_keys - exp_keys):
        top = key.split("/")[0]
        if top in STRUCTURED_TOPS:
            added.append(f"[{top}] {key}")

    if not missing and not added:
        if not args.quiet:
            print("✅ 文件系统结构与期望一致，无漂移")
        sys.exit(0)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"⚠️  filesystem 结构漂移检测（{ts}）")
    if missing:
        print("\n### 缺失（期望有，实际无）— windows.md 可能写了不存在的路径")
        for key in missing:
            print(f"- {key}")
    if added:
        print("\n### 新增（实际有，期望未记录）— 磁盘结构已变化，windows.md 未同步")
        for key in added:
            print(f"- {key}")
    print("\n处理建议：核对后更新 windows.md / generate-map.py DIRECTORY_NOTES，再重跑生成 map。")
    sys.exit(1)


if __name__ == "__main__":
    main()
