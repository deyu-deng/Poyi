# macOS 平台文件结构

> 基于 2026-06-27 实际扫描结果。本文只记录"已落地"的目录，纯设计稿中不存在的目录已删除。

---

## 系统级文件夹（不可移动，Agent 只读）

| 路径 | 用途 | Agent 使用策略 |
|---|---|---|
| `~/Desktop/` | 临时工作区（≤1 周） | 只读扫描，不清理。当前几乎为空 |
| `/Users/sample/Poyi` | Obsidian Vault/Document + 通用文档 | **核心工作区**，Agent 读写 |
| `~/Downloads/` | 下载中心（替代旧 Inbox 概念） | 只读扫描，按需整理，不主动清理 |
| `~/Movies/` | 最终视频资产 | 只读。含 Resolve Project Backups/ Videos/ bilibili/ |
| `~/Music/` | 最终音频资产 | 只读。含 Audio Music Apps/ GarageBand/ Music/ |
| `~/Pictures/` | 照片库 | 只读。含 Photos Library.photoslibrary |
| `~/Public/` | macOS 系统默认 | 几乎不使用 |
| `~/Library/` | 系统 + 应用管理，隐藏 | **绝不手动编辑**，app 自行管理 |
| `~/Applications/` | 用户级 .app 应用 | 只读 |

---

## 自定义根目录（期望存在，Agent 可读写）

### ~/Data/ — Category 3：软件运行时数据（PascalCase，大写 D）

```
~/Data/
├── AppConfig/             # 应用配置（Obsidian、VSCode、x-cmd、MuseScore 等）
├── Cache/                 # 缓存黑洞（Adobe、CloudMusic、Office 等）
├── Collaboration/         # 聊天软件本地数据库
│   ├── DingTalk/
│   ├── Feishu/
│   ├── QQ/
│   ├── TencentMeeting/
│   └── WeChat/
├── DaVinciResolve/        # DaVinci Resolve 21
│   ├── Cache/             # 缓存 + Optimized Media
│   ├── Projects/
│   └── Stills/            # Gallery stills
├── Engineering/           # 工程数据
├── Utilities/             # 杂项工具数据
├── Virtualization/        # Parallels/UTM 虚拟机
└── Zotero/                # 文献管理器
    ├── locate/
    └── storage/
```

**命名规则**：PascalCase 官方应用名，如 `DaVinciResolve/`（非 `dvr` 或 `DaVinci Resolve Media/`）。无品牌名泄露到根目录。

### ~/Development/ — 开发环境

```
~/Development/
├── AI_Engines/OllamaModels/  # Ollama 模型 blob
├── Runtimes/                 # Cargo、Miniconda/envs、Node.js、pnpm、Rustup
└── SDKs/                     # AndroidSDK、Flutter
```

### ~/Tools/ — 便携工具 + 脚本

```
~/Tools/
├── Dev/       # CC-switch 等开发工具
├── Inbox/     # ⚠️ 与 ~/Downloads/ 定位有重叠，见下方差异说明
├── Media/     # ffmpeg 等媒体工具
├── Network/   # Clash、Motrix、v2rayN
├── Scripts/   # Beiyu-live-better、campus-learning-assistant、NapCat_Shell
└── System/    # Geek、WizTree 等系统工具
```

### ~/Projects/ — 核心项目

```
~/Projects/
├── Samplelab-Animation/     # 实际项目
└── Sandbox/             # 实验场 / 素材池
```

### ~/Research/ — 科研（第二课堂）

```
~/Research/
└── （当前为空目录，预期含 NNN-SRTP/ 等编号项目）
```

---

## Obsidian Vault 结构（`/Users/sample/Poyi` 内部）

`/Users/sample/Poyi` 即 Document/Obsidian Vault，Git 版本控制：

```
/Users/sample/Poyi
├── .git/                  # Git 仓库
├── .gitignore
├── .obsidian/             # Obsidian 配置（不手动编辑）
├── README.md
├── AGENTS.md              # Agent 引导文档
├── BOOTSTRAP.md           # 启动引导
├── Loom/                  # Skills 库 + Wiki + Dist
│   ├── dist/              # 编译后的单文件 skill
│   ├── skills/            # 多文件 skill 源
│   └── wiki/              # 知识库文档
└── Vault/                 # Vault 内容主体
    ├── inbox/             # 收件箱笔记
    ├── journal/           # 日记
    ├── meta/              # 元信息和决策记录
    ├── notes/             # 主题笔记
    └── projects/          # 项目笔记
```

---

## 发现规则

Agent 首次执行时 `ls ~/`，与实际对比：

| 情况 | 行为 |
|---|---|
| **期望目录缺失** | 提醒用户「X 目录在期望结构中但不存在，是否需要创建？」 |
| **新增未识别目录** | 记录观察，累计 ≥2 次后触发自更新（见 `references/self-update.md`） |
| **名称不一致** | 记录映射（如 `BlackmagicDesign/` 与 `DaVinciResolve/` 并存） |

---

## 已知偏差（2026-06-27）

| # | 位置 | 偏差 | 说明 |
|---|---|---|---|
| 1 | `~/Desktop/` | 几乎为空 | 规范定位为临时工作区，实际完全空闲 |
| 2 | `~/Research/` | 空目录 | 目录骨架存在但无内容 |
| 3 | `~/Data/BlackmagicDesign/` | 与 `DaVinciResolve/` 并存 | 可能是品牌名残留，待确认 |
| 4 | `~/Tools/Inbox/` | 概念重叠 | `~/Downloads/` 已替代 Inbox 概念 |

---

## 四类数据模型

用户对软件数据的认知分四类：

| 类别 | 内容 | macOS 位置 | 是否可触碰 |
|---|---|---|---|
| 1. 系统配置 | App 必需的配置文件 | `~/Library/Application Support/<Brand>/` | ❌ 绝不 |
| 2. App 二进制 | App 本身 | `/Applications/` 或 `~/Applications/` | ❌ 绝不 |
| 3. 深度绑定输出 | 缓存、草稿、自动保存 — 有用但可重新生成 | **`~/Data/<SoftwareName>/`** | ✅ 可自由迁移 |
| 4. 自由输出 | 最终用户产物 | `~/Documents/` `~/Movies/` `~/Music/` `~/Pictures/` | ✅ 完全自由 |

`~/Data/` 仅用于 Category 3。

---

## Library vs Data

| | `~/Library/` | `~/Data/` |
|---|---|---|
| 管理者 | 系统 + App | 用户 |
| 路径固定 | 是 | 否，用户自定义 |
| App 可改路径 | ❌ 不可 | ✅ 可（通过 App Preferences） |
| 卸载后存活 | 配置可能存活 | 总能存活（用户控制） |
| Windows 等效 | `C:\Users\<name>\AppData\` | `D:\Data\` |

---

## 命名约定

- **根自定义目录**：PascalCase（`Data/` `Development/` `Tools/`）
- **`~/Data/` 下 App 目录**：PascalCase 官方 App 名（`DaVinciResolve/`）
- **子目录**：PascalCase 单数形式（`Cache/` 非 `Caches/`）
- **禁止品牌名泄露到根目录**
- **禁止创建与系统文件夹功能重复的根目录**

---

## App 类别 — macOS 放哪里

| 类型 | 格式 | 放置位置 |
|---|---|---|
| 大型官方 GUI App | `.app` | `/Applications/` 或 `~/Applications/` |
| 命令行二进制 | 单可执行文件 | `~/Tools/<Category>/` + 加 PATH |
| 绿色便携 App | 含可执行文件的目录 | `~/Tools/<Category>/` |
| 用户脚本 | `.py` / `.sh` | `~/Tools/Scripts/` |
| Homebrew 安装 | 自动管理 | `/opt/homebrew/`（Apple Silicon）或 `/usr/local/`（Intel） |

---

## 已知 Bug：Agent cwd 缓存旧用户名

重命名 macOS 账户后 Hermes 可能卡在旧 cwd。两个文件含旧路径：
1. `~/.hermes/state.db` — SQLite，`sessions.cwd` + `messages.content/tool_calls`
2. `~/Library/LaunchAgents/com.google.GoogleUpdater.wake.plist`

**修复**：见本文件 §Known Bug（出现在 SKILL.md 供运行时直接执行）。

---

## 被否决的设计（不要重新提议）

- `~/Cloud/` — 完全抛弃，子目录（Projects/Research/Vault）提升到根
- `~/Games/` — macOS 游戏生态不相关
- `~/Inbox/` — 由 `~/Downloads/` 替代
- `~/tmp/` — 使用系统 `/tmp/`
- `~/Software/` — 使用 `/Applications/`
- `~/Document/`（单数，根级）— **绝不创建**，`/Users/sample/Poyi` 就是 Vault/Document
- 任何 Windows 专属子目录

---

*基于 2026-06-27 实际扫描 + 2026-06-16 mac-filesystem-hygiene 设计去芜存菁*
*（内容由AI生成，仅供参考）*

