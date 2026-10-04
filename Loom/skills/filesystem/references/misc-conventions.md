# 杂项约定 — 时间戳/日期/Journal 等

## Journal/ 日记文件命名

**位置**：`D:\Projects\Poyi\Vault\journal\`

**命名格式**：`{Weekday}, {Month} {Day}, {Year}.md`

**例子**：
- `Saturday, June 13, 2026.md`
- `Friday, April 10, 2026.md`
- `Tuesday, March 31, 2026.md`

**注意**：
- 逗号后必须**有空格**（你的常见写法）
- 月份全英文：`January February March April May June July August September October November December`
- 星期全英文：`Monday Tuesday Wednesday Thursday Friday Saturday Sunday`
- 文件扩展名是 `.md`（不是 `.markdown`）
- **不要**用 `2026-06-13.md` 这种 ISO 格式（Obsidian Daily Notes 插件能识别但你的习惯不是这个）

**文件存在即视为已写日记**。`Journal/` 目录是 Obsidian 加载的，没有特殊配置文件。

**关于日记空窗**（2026-04-25 → 2026-06-13 共 48 天）：
- **不要主动提醒**用户写日记
- 用户想写时自己会写
- 如果用户**主动问**"我好久没写日记了怎么办"，可以：
  - 提议从今天开始
  - 不要复盘历史空窗
  - 不要建议补写过去日期

**为什么是英文文件名 + 中文内容**：你 2026-06-13 的日记文件名是英文，但内容可以中文或英文（看你心情）。

## 文件结构守则.md 的迁移

**状态**：原 `D:\Projects\Poyi\Vault\Plan\文件结构守则.md` 已经被 `filesystem` skill 替代。

**位置保留**：Plan/ 下的旧文件**不删**，作为"为什么这样组织"的设计哲学层保留。

**加载指引**：执行 mkdir/mv/npm install 时加载 `filesystem`，**不要加载**文件结构守则.md。

## `naming-debt.md` 的处理

**位置**：`D:\Projects\Poyi\Vault\Plan\naming-debt.md`

**内容**：历史下划线命名的清单（`Projects/05-Samplelab_Animation`、`Sandbox/Code/extract_outline_v3.py` 等）。

**不要主动改**：用户说"等下我自己来"（2026-06-15）。

**何时可以提**：用户**主动问**"这些债务怎么处理"时，给完整方案。

## `INDEX.md` 的更新规则

**位置**：`D:\Projects\Poyi\Loom\skills\INDEX.md`

**何时更新**：
- 新建 skill
- 改 skill 名字
- 合并 / 删除 skill
- skill 大重构（v2.0.0 这种）

**不要为小事更新**（比如改个 description 字段）。

## Obsidian Vault 的位置

**注意**：用户的 Obsidian vault **就是** `D:\Projects\Poyi\Vault\`。

- 双链在 `.md` 文件里写 `[[另一个文件名]]` 即可
- Obsidian 插件配置在 `D:\Projects\Poyi\Vault\.obsidian\`（**别删**）
- Dataview/Templater 等插件如果启用，相关文件在 `D:\Projects\Poyi\Vault\.obsidian\plugins\`

**Agent 不要修改 Obsidian 配置**（除非用户明确要求）。

## Projects/Sandbox/ 的 5 个空目录

**位置**：`D:\Cloud\Projects\Sandbox\Drawing/ Illustration/ Music/ Video/ Design/`

**状态**：用户刻意保留的占位（"我就是喜欢这样"）。

**不要主动清理、合并、重命名**。详见 filesystem §0 陷阱 0.8 和 project skill 的"Sandbox/ 特殊规则"。

## D:\Projects\Poyi\Loom\skills\（唯一 skill 目录）

**核心**：永远只编辑 `D:\Projects\Poyi\Loom\skills\`。这是 Poyi 系统加载 skill 的唯一权威目录。

## 关于"个人知识管理"约定

- **所有笔记、计划、知识整理**都放在 `D:\Projects\Poyi\Vault\` 下
- **双链**优先于文件夹嵌套
- **不用** Git 管理 `D:\Cloud\`（云盘同步即可，用户选择）
- **定期备份** Vault（云盘自动 + 手动）
- Agent 操作 vault 时**避免创建**新的 `Tags/` `Archive/` `Templates/` 等"框架性"目录 —— 用户有自己的结构