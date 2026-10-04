# Windows 平台文件结构

> 从原 filesystem SKILL.md v2.3.0 提取的 Windows 特定内容。

---

## 盘符概念

Windows 使用盘符（C: / D: / ...）区分物理/逻辑分区：

| 盘符 | 角色 | Agent 策略 |
|---|---|---|
| **C:** | 系统盘（Windows + Program Files + 用户目录） | 只读为主，清理需审计（见 `references/c-drive-audit.md`） |
| **D:** | 数据盘（用户主动管理的资产） | 读写，主要工作区 |

---

## D 盘顶层结构（期望）

| 顶层 | 角色 | 进入 | 禁止 |
|---|---|---|---|
| `Cloud/` | 核心资产（云同步） | 学习/开发/设计心血 | 软件缓存 |
| `Data/` | 软件运行时数据 | 软件配置/缓存/数据库 | 项目文件 |
| `Development/` | 开发环境（详见下方子目录分类） | Runtime/SDK/AI 引擎/库 | 项目代码 |
| `Games/` | 游戏客户端 | 游戏安装 | — |
| `Inbox/` | **临时中转站**（已扁平化） | 下载/接收/网盘临时。所有文件散落根，0 子目录 | 长期保留 |
| `Software/` | **已装软件（注册表依赖）** | 重型安装版软件 | — |
| `Tools/` | 便携工具 + 脚本 | 无注册表依赖的便携软件 | — |
| `Users/` | D 盘用户目录副本 | 用途待澄清 | — |
| `tmp/` | 临时文件 | preview 等 | 长期保留 |

---

## Development 子目录分类

**判断标准**：跨项目共享、不绑定单一仓库 → Development；绑定某个具体项目 → 跟项目走。

| 子目录 | 内容 | 示例 | 禁止 |
|---|---|---|---|
| `Home/` | 模拟 Windows 用户目录副本 | .ssh/.config/.vscode/.ohos 等 dotfiles | 项目代码 |
| `Toolchains/` | 工具链族（按工具分） | Android/ARM/C++/Flutter/Huawei/Node/Python/Rust/TeX | 项目级配置 |
| `Virtualization/` | 虚拟化 | WSL | 生产数据 |

---

## 重要路径速查

| 用途 | 路径 |
|---|---|
| 项目代码 | `D:\Cloud\Projects\{名称}\`（无编号扁平 kebab-case，如 Aura/Vaelis/Prism） |
| 项目沙盒 | `D:\Cloud\Projects\_Sandbox\` |
| 第一课堂 | `D:\Cloud\Courses\` |
| 履历/事件 | `D:\Cloud\Events\` |
| 媒体资产 | `D:\Cloud\Media\` |
| 破解版安装包收藏 | `D:\Cloud\Library\`（CAD/Media/Game/Dev 分组） |
| 知识库核心 | `D:\Projects\Poyi\Vault\`（notes/journal/meta/projects/inbox） |
| 知识库笔记 | `D:\Projects\Poyi\Vault\notes\` |
| 日记 | `D:\Projects\Poyi\Vault\journal\` |
| 知识库决策/工作流 | `D:\Projects\Poyi\Vault\meta\` |
| 知识库项目规划 | `D:\Projects\Poyi\Vault\projects\`（plan.md+progress.md+research.md 三件套） |
| Skill 权威源 | `D:\Projects\Poyi\Loom\skills\` |
| 已装软件本地 | `D:\Software\` |
| 便携工具/脚本 | `D:\Tools\`（Dev/Media/Network/Scripts/System） |
| 临时中转站 | `D:\Inbox\` 根（扁平化） |
| Zotero 文献库 | `D:\Data\AppData\Zotero\` |
| 微信本地数据库 | `D:\Data\AppData\WeChat\` |
| QQ 本地数据库 | `D:\Data\AppData\QQ\` |
| 华为模拟器/DevEco 数据 | `D:\Data\AppData\Huawei\`、`D:\Data\Cache\DevEco\` |
| npm 全局路径 | `D:\Data\AppData\npm\` |
| 开发工具链 | `D:\Development\Toolchains\`（Android/ARM/C++/Flutter/Huawei/Node/Python/Rust/TeX） |
| WSL 虚拟化 | `D:\Development\Virtualization\WSL\` |

---

## Agent 产出文件禁令

**Agent 生成的任何文件（文档、代码、截图、日志、导出 JSON 等）严禁写入 C 盘任意位置。** 所有产出强制走 Marvis 工作目录（`workspace\conv_*\output\`）或用户显式指定的 D 盘路径。

---

## C 盘 vs D 盘职责

- **D 盘**：用户主动管理的资产（Cloud/Library、Projects、Poyi/Vault + Loom）
- **C 盘**：被动产生的数据（软件缓存、聊天数据库、OneDrive 临时、卸载备份残留）+ 必须保留的系统区

详见 `references/c-drive-audit.md`。

---

## 假病毒识别（C 盘特化）

| 现象 | 真实可能 | 不要立刻判为 |
|---|---|---|
| 目录名 2-4 个随机字母（yyb 等） | 内部组件代号 / 灰软 | 病毒 |
| 有 uninstall.exe | 合法软件 | 木马 |
| `beacon_report.log` 之类 | 内部日志 | C2 通信 |
| 0 字节日志 | 卸载残留 | 通信证据 |
| uninstall 顺手把其他软件卸了 | PUA bug | 恶意软件 |

---

## 系统保护路径禁区（C 盘）

以下目录**绝不执行**删除/修改：

- `C:\Windows\`
- `C:\Program Files\`
- `C:\Program Files (x86)\`
- `C:\ProgramData\`
- `C:\Users\<user>\AppData\`（全部）
- `C:\Users\<user>\Public\`
- `C:\Users\<user>\` 内的 dotfiles（`.ssh/` `.gitconfig` 等）

---

## Desktop 隐藏空间

C 盘满时**第一嫌疑区**：`C:\Users\<user>\Desktop\` 常有卸载备份残留（`SW_Cleanup_*` 等），单目录可达 30+ GB。

---

## computer-map.json

Windows 下 `computer-map.json` 位置：`D:\Projects\Poyi\Vault\Context\computer-map.json`。由 `D:\Projects\Poyi\Loom\skills\filesystem\scripts\generate-map.py` 生成，只扫 D 盘。

---

## 与 macOS 的关键差异

| Windows | macOS |
|---|---|
| 独立盘符 C:/D: | 单根文件系统 |
| 避免使用系统文件夹（在 C 盘） | 系统文件夹是一等公民 |
| `D:\Cloud\` 为核心资产根 | 无 Cloud/，Projects/Research/ 提升到 ~/ 根 |
| `D:\Software\` 已装软件 | `/Applications/` + `~/Data/<App>/` |
| `D:\Inbox\` 临时中转 | `~/Downloads/` 替代 |
| Vault 在 `D:\Projects\Poyi\Vault\` | Vault 在 `/Users/sample/Poyi` 内 |
*（内容由AI生成，仅供参考）*
