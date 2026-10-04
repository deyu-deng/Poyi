#!/usr/bin/env python3
"""
generate-map.py — 重新生成 D:\Cloud\Vault\Context\computer-map.json

用法：
    python generate-map.py                    # 重新生成
    python generate-map.py --base D:\\custom  # 自定义根目录（测试用）
    python generate-map.py --depth 3          # 自定义深度（默认 2）

输出：D:\Cloud\Vault\Context\computer-map.json
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from argparse import ArgumentParser


# 顶层注释（与 filesystem SKILL.md 对齐）
# 如要修改注释，直接编辑这个 dict
DIRECTORY_NOTES = {
    # ===== D:/Cloud/ =====
    "Cloud": "核心资产与云端真理源。所有学习、开发、设计心血存放于此，开云同步。内部严禁出现软件运行缓存。",
    "Cloud/Archive": "大档案库（>1年未访问 / 凭证 / 法律文件）。定期归档，时不时打开一次。",
    "Cloud/Archive/Credentials": "具法律效力的官方核心文件（身份证扫描件、学位证、合同、获奖证书）。",
    "Cloud/Archive/Driver": "厂家驱动包备份。装机后基本不再访问。",
    "Cloud/Archive/Finance": "发票、账单、重要电子收据。",
    "Cloud/Archive/Manual": "重型软硬件的产品手册、保修卡、授权码。",
    "Cloud/Archive/Organizations": "组织/社团归档（示例车队等）。",
    "Cloud/Archive/Password": "⚠️ 密码明文 .txt 文件。安全风险，待迁移到 Bitwarden。",
    "Cloud/Courses": "第一课堂资源。按学期-课程名组织。",
    "Cloud/Events": "社会履历时间线。YYYYMMDD-事件名 格式，有明确结束点的活动。",
    "Cloud/Media": "媒体资产。Music/Pictures/Videos 三类。",
    "Cloud/Media/Music": "音乐资产。Song/ 下 400 个艺术家目录。",
    "Cloud/Media/Music/Musical Instrument": "乐器相关资料（吉他/口琴/钢琴/萨克斯）。",
    "Cloud/Media/Pictures": "图片。Album Cover 是音乐封面，Photos 是照片。",
    "Cloud/Media/Videos": "视频。MV/Projects/Videos/。",
    "Cloud/Projects": "核心工程与实验沙盒。无编号扁平 kebab 命名。",
    "Cloud/Projects/_Sandbox": "实验场/Samplelab 素材池。空目录多（Drawing/Illustration/Music/Video）。",
    "Cloud/Research": "第二课堂。SRTP/课题文献。",
    "Cloud/Vault": "⚠️ 历史路径，Vault 已迁至 D:/Projects/Poyi/Vault。此处仅为旧结构残留记录。",
    "Cloud/Vault/Skills": "⚠️ 历史路径，skill 权威源已迁至 D:/Projects/Poyi/Loom/skills。",
    "Cloud/Vault/Context": "⚠️ 历史路径，computer-map 已迁至 D:/Projects/Poyi/Vault/Context。",
    "Cloud/Vault/Plan": "⚠️ 历史路径，规划文档已迁至 D:/Projects/Poyi/Vault/meta。",
    "Cloud/Vault/Knowledge": "⚠️ 历史路径，学科知识笔记已迁至 D:/Projects/Poyi/Vault/notes。",
    "Cloud/Vault/Journal": "⚠️ 历史路径，日记已迁至 D:/Projects/Poyi/Vault/journal。",
    "Cloud/Vault/Research": "⚠️ 历史路径，研究笔记已迁至 D:/Projects/Poyi/Vault/projects。",

    # ===== D:/Data/ =====
    "Data": "本地软件运行时数据。AppData/Cache/Config 三类。⚠️ 不应污染核心工作区。",
    "Data/AppData": "软件运行时数据（WeChat/QQ/Zotero/npm/Huawei 等）。",
    "Data/AppData/WeChat": "微信本地数据库。",
    "Data/AppData/QQ": "QQ 本地数据。",
    "Data/AppData/Zotero": "Zotero 文献管理。含 sqlite + storage（PDF 附件）。papers 引用此处。",
    "Data/AppData/Zotero/storage": "Zotero 抓取的 PDF 附件存放地。",
    "Data/AppData/npm": "npm 全局包。",
    "Data/AppData/Huawei": "华为模拟器/DevEco 运行时数据（Emulator deployed 等）。",
    "Data/Cache": "缓存黑洞。Cargo/CloudMusic/Conda/DevEco/GoogleDrive/npm/pnpm/WPS 等。",
    "Data/Cache/DevEco": "DevEco 缓存。",
    "Data/Config": "软件配置（Obsidian/VMware/VSCode/x-cmd）。",

    # ===== D:/Development/ =====
    "Development": "底层算力发动机舱。Home + Toolchains + Virtualization 三类。",
    "Development/Home": "模拟 Windows 用户目录的副本（.ssh/.config/.vscode/.ohos 等 dotfiles）。",
    "Development/Toolchains": "工具链族（按工具分）：Android/ARM/C++/Flutter/Huawei/Node/Python/Rust/TeX。",
    "Development/Toolchains/Huawei": "华为工具链（HarmonyOS SDK / system-image 镜像）。",
    "Development/Toolchains/Python": "Python 工具链。",
    "Development/Toolchains/Node": "Node.js 工具链。",
    "Development/Virtualization": "虚拟化。",
    "Development/Virtualization/WSL": "WSL 发行版数据。",

    # ===== D:/Projects/Poyi/ =====
    "Poyi": "知识库核心。Loom（skill 权威源）+ Vault（Obsidian 金库）。",
    "Poyi/Loom": "Loom 知识库工程（skills 权威源 + 方法论）。",
    "Poyi/Loom/skills": "Skill 权威源。Marvis 侧 market 为软链接指向此处。",
    "Poyi/Vault": "Obsidian 知识金库（notes/journal/meta/projects/inbox）。",
    "Poyi/Vault/Context": "Agent 启动上下文（computer-map.json 在此）。",

    # ===== D:/Games/ =====
    "Games": "游戏客户端安装。Epic Games + Galgame + Minecraft 多版本 + WeGame。",
    "Games/Epic Games": "Epic Games 平台。Launcher 和已装的 FallGuys。",
    "Games/Galgame": "Galgame 游戏。",
    "Games/Minecraft": "Minecraft 整合包，含 Mods 和 PCL 启动器。",
    "Games/Minecraft Launcher": "Minecraft 启动器。",
    "Games/Minecraft- Java Edition": "Minecraft Java 版。",
    "Games/WeGameApps": "WeGame 游戏。",

    # ===== D:/Inbox/ =====
    "Inbox": "临时中转站。所有文件直接散落在 Inbox/ 根（已扁平化，2026-06-15）。定期清理或转移——大部分内容很快过期。",

    # ===== D:/Software/ =====
    "Software": "已安装的生产力软件（重型安装版）。注册表依赖。",
    "Software/Adobe": "Adobe 全家桶。",
    "Software/Android Studio": "Android 开发 IDE。",
    "Software/Antigravity": "AI IDE（与 Marvis/Windsurf 同类）。",
    "Software/Blender": "3D 建模与动画。",
    "Software/CAD2026": "AutoCAD 2026。",
    "Software/CloudMusic": "网易云音乐客户端。",
    "Software/Creo": "PTC Creo（机械 CAD）。",
    "Software/DevEco Studio": "华为鸿蒙开发 IDE（与 02-Aura 项目配合）。",
    "Software/DingDing": "钉钉客户端。",
    "Software/EarMaster 7": "视唱练耳。",
    "Software/Feishu": "飞书客户端。",
    "Software/foobar2000": "音频播放器。",
    "Software/Git": "Git 客户端。",
    "Software/Guitar Pro 8": "吉他谱软件。",
    "Software/Inkscape": "矢量图编辑器。",
    "Software/Kimi": "Kimi AI 客户端。",
    "Software/Marvis": "你日常使用的办公 / 编程一体化 AI 平台。MarvisAgent 是核心。",
    "Software/Marvis/MarvisAgent": "Marvis 的 Agent 运行时（你日常用的 AI 助手）。",
    "Software/MarvisData": "Marvis 的运行时数据（knowledgebase/attachments/rdelivery 等）。",
    "Software/MATLAB": "MATLAB（科学计算）。",
    "Software/Microsoft VS Code": "VS Code（与 D:/Development/Runtimes/Node.js 配合）。",
    "Software/Mubu": "幕布（思维导图/大纲）。",
    "Software/Obsidian": "Obsidian 客户端（与 D:/Data/AppConfig/Obsidian 配合）。",
    "Software/PotPlayer": "视频播放器。",
    "Software/Qoder": "AI IDE。",
    "Software/Quark": "夸克网盘。",
    "Software/Solidworks": "Solidworks（机械 CAD）。",
    "Software/Steam": "Steam 平台。",
    "Software/Trae CN": "字节 AI IDE（国内版）。",
    "Software/TRAE SOLO CN": "Trae Solo（独立模式）。",
    "Software/Ultimate Vocal Remover": "AI 人声分离。",
    "Software/VMware": "虚拟机。",
    "Software/WPS Office": "WPS 办公套件。",
    "Software/Zotero": "Zotero 文献管理客户端。",

    # ===== D:/Tools/ =====
    "Tools": "便携软件与脚本集合。无注册表依赖。",
    "Tools/Dev": "开发便携工具。",
    "Tools/Dev/CC-switch": "Claude Code 配置切换工具。",
    "Tools/Dev/Dev-Cpp": "Dev-Cpp 编译器。",
    "Tools/Download": "下载暂存。",
    "Tools/Media": "媒体/AI 工具（ComfyUI 等）。",
    "Tools/Media/ComfyUI": "ComfyUI（AI 绘图工作流）。",
    "Tools/Network": "网络工具。Clash/Motrix/Putty/v2rayN/下载加速。",
    "Tools/Scripts": "用户脚本集合。",
    "Tools/Scripts/Beiyu-live-better": "北屿大学校园自动化脚本（自动签到/课程作业/校园课堂/图书馆）。inbox 和 campus skill 引用。",
    "Tools/Scripts/NapCat_Shell": "NapCat QQ 机器人。",
    "Tools/Scripts/campus-learning-assistant": "北屿大学课程辅助脚本。",
    "Tools/Scripts/xzzd-pro-chrome-v1.1.0": "Chrome 辅助工具。",
    "Tools/System": "系统工具。App_Migrator/Geek/LastActivityView/WizTree。",
    "Tools/wechat": "微信相关工具。",

    # ===== 其他顶层 =====
    "tmp": "临时文件目录。",
    "Downloads": "下载文件。",
    "Users": "D 盘上的 Users 副本（意义不明，可能用于测试或特定软件）。",
    "Users/xgbc": "用户目录副本。",
    ".appdata": "隐藏应用数据目录。",
    "WpSystem": "WPS 系统目录。",
    "腾讯应用宝文件管理": "应用宝文件管理（手机投屏/文件传输）。",
}

# 跳过目录
SKIP_TOP = {"$RECYCLE.BIN", "System Volume Information", "Config.Msi", "WindowsApps"}
SKIP_DEEP = {"node_modules", ".git", "__pycache__"}


def get_info(path):
    """获取目录的关键信息"""
    try:
        items = list(path.iterdir())
    except (PermissionError, FileNotFoundError, OSError):
        return {"exists": False}

    dirs = [i for i in items if i.is_dir()]
    files = [i for i in items if i.is_file()]

    info = {
        "exists": True,
        "dirs_count": len(dirs),
        "files_count": len(files),
    }

    key_files = []
    for f in files:
        n = f.name.lower()
        if n in ("package.json", "pyproject.toml", "cargo.toml", "go.mod",
                 "readme.md", "license", "config.yaml", "config.json",
                 ".gitignore", "task.md", "handoff.md", "proposal.md",
                 "claude.md", "development.md"):
            key_files.append(f.name)
    if key_files:
        info["key_files"] = key_files

    return info


def build_tree(base_path, max_depth=2):
    """构建目录树"""
    tree = {"_meta": f"{base_path} 盘根目录", "children": {}}

    for top_item in sorted(base_path.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
        if not top_item.is_dir():
            continue
        if top_item.name in SKIP_TOP:
            continue

        top_name = top_item.name
        top_path_key = top_name
        info = get_info(top_item)
        note = DIRECTORY_NOTES.get(top_path_key, "")

        node = {
            "path": top_name,
            "depth": 0,
            "note": note,
            "info": info,
            "children": {}
        }

        if max_depth >= 1:
            for sub_item in sorted(top_item.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
                if not sub_item.is_dir():
                    continue
                if sub_item.name in SKIP_DEEP:
                    continue

                sub_key = f"{top_name}/{sub_item.name}"
                sub_info = get_info(sub_item)
                sub_note = DIRECTORY_NOTES.get(sub_key, "")

                node["children"][sub_item.name] = {
                    "path": sub_key,
                    "depth": 1,
                    "note": sub_note,
                    "info": sub_info,
                    "children": {}  # 不深入第三层
                }

        tree["children"][top_name] = node

    return tree


def main():
    parser = ArgumentParser(description="生成 D:\\Cloud\\Vault\\Context\\computer-map.json")
    parser.add_argument("--base", default=r"D:\\", help="扫描根目录（默认 D:\\）")
    parser.add_argument("--depth", type=int, default=2, help="扫描深度（默认 2 层）")
    parser.add_argument("--output", default=r"D:\Projects\Poyi\Vault\Context\computer-map.json",
                        help="输出文件路径")
    args = parser.parse_args()

    base = Path(args.base)
    if not base.exists():
        print(f"❌ 根目录不存在：{base}")
        sys.exit(1)

    print(f"🔍 扫描 {base}，深度 {args.depth} 层...")
    tree = build_tree(base, max_depth=args.depth - 1)  # 0 层 = 顶层，所以 depth-1

    output = {
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "scope": str(base),
        "total_top_level": len(tree["children"]),
        "depth_covered": args.depth,
        "note": "depth=0 顶层 + depth=1 二层。深层目录未展开，避免 JSON 爆炸。Agent 需要深层信息时用 terminal 或 search_files 实时查询。",
        "tree": tree,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    size = out.stat().st_size
    total_second = sum(len(t["children"]) for t in tree["children"].values())
    print(f"✅ 生成完成：{out}")
    print(f"   大小：{size/1024:.1f} KB")
    print(f"   顶层：{len(tree['children'])} 个")
    print(f"   二层：{total_second} 个")


if __name__ == "__main__":
    main()