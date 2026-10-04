#!/usr/bin/env python3
"""生成虚构的 computer-map fixture，替换掉记录真实盘符与目录结构的原文件。

保持原 schema（version/generated_at/scope/total_top_level/depth_covered/note/tree），
其中 tree = {"_meta": 根标签, 根标签: {名称: {path, depth, note, info{exists,dirs_count,files_count}, children}}}。
设备与目录均为示例数据，不对应任何真实机器。

用法: python Loom/scripts/make_sample_computer_map.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATED = "2026-10-04T00:00:00"
NOTE = "示例设备映射：depth=0 根 + depth=1 一层。子目录未展开，需要更多信息时实时查询。"


def node(name: str, depth: int, dirs: int, files: int, note: str = "", children=None) -> tuple:
    return (name, {
        "path": name if depth == 0 else None,
        "depth": depth,
        "note": note,
        "info": {"exists": True, "dirs_count": dirs, "files_count": files},
        "children": children or {},
    })


def tree(scope: str, label: str, entries: list) -> dict:
    out = {"_meta": label, label: {}}
    for name, depth, dirs, files, note, kids in entries:
        key = name
        body = {
            "path": f"{scope}{name}" if scope.endswith(("\\", "/")) else name,
            "depth": depth,
            "note": note,
            "info": {"exists": True, "dirs_count": dirs, "files_count": files},
            "children": {},
        }
        for kn, kd, kf in kids:
            body["children"][kn] = {
                "path": f"{body['path']}/{kn}",
                "depth": depth + 1,
                "note": "",
                "info": {"exists": True, "dirs_count": kd, "files_count": kf},
                "children": {},
            }
        out[label][key] = body
    return out


WIN = tree(
    "D:\\", "D:\\ 盘根目录（示例）",
    [
        ("Projects", 0, 3, 0, "示例项目盘。", [("Demo-App", 2, 6), ("Sample-Notes", 1, 4)]),
        ("Cloud", 0, 4, 0, "示例同步盘。", [("Research", 2, 3), ("Courses", 6, 12)]),
        ("Tools", 0, 2, 0, "示例工具盘。", []),
        ("Data", 0, 5, 0, "运行数据与缓存。", []),
        ("Runtimes", 0, 2, 0, "语言与运行时。", []),
    ],
)

MAC = tree(
    "/Users/sample/", "/Users/sample（示例）",
    [
        ("Projects", 0, 2, 0, "示例项目目录。", [("Demo-App", 1, 3)]),
        ("Documents", 0, 3, 0, "示例文档目录。", []),
        ("Downloads", 0, 1, 4, "示例下载目录。", []),
    ],
)


def write(rel: str, version: str, scope: str, label: str, t: dict) -> None:
    payload = {
        "version": version,
        "generated_at": GENERATED,
        "scope": scope,
        "total_top_level": len(t[label]),
        "depth_covered": 1,
        "note": NOTE,
        "tree": t,
    }
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(rel)


def main() -> None:
    write("Vault/Context/computer-map.json", "1.0.0", "D:\\", "D:\\ 盘根目录（示例）", WIN)
    write("Vault/meta/system/computer-map.win.json", "1.0.0", "D:\\", "D:\\ 盘根目录（示例）", WIN)
    write("Vault/meta/system/computer-map.mac.json", "1.1.0", "/Users/sample", "/Users/sample（示例）", MAC)


if __name__ == "__main__":
    main()
