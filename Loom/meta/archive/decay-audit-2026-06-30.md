---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 67e28a0cadea4c0368daeffdef023791_f8d3f190747711f1986d525400d9a7a1
    ReservedCode1: V27Sv4fsZNo6h2vK2iSBHPnzU2wDbNXgAdb0Cm8LCGwExkPWpDZRztwKBCJ3nBN0WbWHc0wQ1sY/0jKIaA6GS6IWyupjqJA4brXB3KyKd8oOXjdFF3+PkSVqEirbEHgPSTkCdLLvwvv75zMAVBWJcR3gtdrd4we8llgnQ3BmRT7fnyd1RaWTr2yO8XY=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 67e28a0cadea4c0368daeffdef023791_f8d3f190747711f1986d525400d9a7a1
    ReservedCode2: V27Sv4fsZNo6h2vK2iSBHPnzU2wDbNXgAdb0Cm8LCGwExkPWpDZRztwKBCJ3nBN0WbWHc0wQ1sY/0jKIaA6GS6IWyupjqJA4brXB3KyKd8oOXjdFF3+PkSVqEirbEHgPSTkCdLLvwvv75zMAVBWJcR3gtdrd4we8llgnQ3BmRT7fnyd1RaWTr2yO8XY=
---

# Poyi 系统腐烂度审查报告

> **审查日期**：2026-06-30  
> **审查范围**：skills（Loom + Vault）、Vault 元数据、跨文件引用一致性、Hermes 残余  
> **审查方法**：全量读取 9 个核心 skill + 4 个元数据文件 + Regex `(?i)hermes` 全盘扫描 106 处命中

---

## 一、Hermes 残余扫描

共命中 106 处（18 个文件），排除 chat-logs 归档后剩余以下需关注：

### 1.1 已知且可接受的（标注"已停用/已退役"）

| 文件 | 行号 | 内容 | 判断 |
|---|---|---|---|
| `Loom/skills/profile/SKILL.md` | L71, L73, L81, L204 | "已停用，历史数据已归档"、"Hermes 已退役"、"Hermes 曾用名" | ✅ 有明确退役标注，保留 |
| `Vault/journal/2026-06-13-Saturday.md` | L9, L11, L13, L17... | 日记中回忆 Hermes 交互历史 | ✅ 历史日记，不清理 |

### 1.2 需要清理的（仍作为操作指令存在）

| # | 文件 | 行号 | 问题 | 建议 |
|---|---|---|---|---|
| 1 | **`Vault/meta/SOUL.md`** | L1, L6 | 全文为 Hermes Agent Persona 配置文件，标题 `# Hermes Agent Persona`，注释 "customize how Hermes communicates" | 🔴 **必须清理**。Hermes 已退役，此文件已无加载者。建议删除或归档到 `chat-logs/raw/hermes-win/` |
| 2 | `Loom/skills/inbox/SKILL.md` | L99, L165, L170, L176 | changelog 中大量 Hermes 操作术语：`hermes_tools.terminal()`、`hermes send`、`Hermes cron 模式` | 🟡 建议在 changelog 条目上加 `[Hermes-era]` 标签，保留历史但不混淆当前读者 |
| 3 | `Loom/skills/inbox/references/cron-delivery-pitfalls.md` | L10, L15, L25-L28, L37, L43, L46, L49-L50, L58, L68, L160, L208, L232 | 全篇以 Hermes cron 机制为前提编写，频繁引用 `hermes send`、`~/.hermes/cron/`、`hermes_tools` | 🟡 整个文件是 Hermes cron 的实战沉淀，对 Marvis 环境下不可直接复用。建议在文件头部加醒目标注：`> ⚠️ 本文基于 Hermes cron 环境编写，Marvis 环境下需重新验证` |
| 4 | `Loom/skills/inbox/references/wechat-cli-pitfalls.md` | L288-L291 | §10.2 专门讲 `hermes send` 跳过机制 | 🟡 同上，加标注 |
| 5 | `Loom/skills/inbox/references/scout-pitfalls.md` | L157 | "hermes 跨平台" | 🟡 改为"跨平台"即可 |
| 6 | `Loom/skills/filesystem/references/sync-strategy.md` | 全文 | 标题 `Sync 策略：D:\Cloud\ vs ~/.hermes/skills/`，全篇围绕 Hermes `external_dirs` 机制、`~/.hermes/skills/` 与 Vault 的双重维护问题 | 🔴 整篇文档的上下文已过时。Marvis 不再有 `~/.hermes/skills/` 副本机制。建议归档或重写为「Vault vs Loom 双重维护问题」 |
| 7 | `Loom/skills/filesystem/references/naming-workflow.md` | L140 | "`~/.hermes/skills/` 是 Hermes 加载的副本" | 🟡 同 sync-strategy，需改写 |
| 8 | `Loom/skills/filesystem/references/misc-conventions.md` | L81, L85 | "D:\Projects\Poyi\Loom\skills\ vs ~/.hermes\skills\" | 🟡 改写为仅讨论 Loom skills |
| 9 | `Loom/skills/filesystem/references/platforms/macos.md` | L198-L202 | "已知 Bug：Hermes cwd 缓存旧用户名" | 🟡 改为"Agent cwd 缓存旧用户名" |
| 10 | `Loom/skills/INDEX.md` | L63 | `sync-strategy.md` 描述为 "D:/Cloud vs ~/.hermes 同步" | 🟡 更新描述 |
| 11 | `Loom/skills/animation/INDEX.md` | L67, L84 | "Windows + Hermes 环境"、"Hermes 库可执行 skill" | 🟡 改为"Windows + Agent 环境"、"Agent 库可执行 skill" |

### 1.3 已消化日志中的（无需处理）

- `Loom/raw/chat-logs/digested/2026-06-27/summary.md`、`2026-06-28/summary.md`：agent 名称出现在 summary 中是正常归档行为
- `Loom/chat-logs/raw/hermes-win/`：整个目录是 Hermes 历史归档，保留

---

## 二、跨文件矛盾

### 2.1 🔴 严重：Skill 物理位置矛盾

| 来源 | 声称位置 | 实际位置 |
|---|---|---|
| `profile/SKILL.md` L74 | "自维护 8 个 skill，位于 `D:\Cloud\Vault\Skills\`" | **`D:\Projects\Poyi\Vault\Skills\` 不存在**，实际在 `D:\Projects\Poyi\Loom\skills\`（23 个目录） |
| `filesystem/references/sync-strategy.md` L7 | "`D:\Cloud\Vault\Skills\` 是唯一权威源" | 同上，不存在 |

**影响**：任何按 profile 指引去 `Vault/Skills/` 找 skill 的 Agent 会找不到。  
**修复**：profile L74 改为 `D:\Projects\Poyi\Loom\skills\`；sync-strategy.md 整体需重写。

### 2.2 🔴 严重：Skill 数量矛盾

| 来源 | 声称数量 | 实际 |
|---|---|---|
| `profile/SKILL.md` L74 | "自维护 8 个 skill（filesystem / newproject / profile / inbox / papers / notes / exam / campus）" | INDEX.md 列出 20 个活跃 skill（10 用户 + 10 Wiki） |
| `INDEX.md` frontmatter | `total_skills: 19` | 实际表格编号 1-20（20 个），且 Loom/skills/ 下有 23 个目录（含 animation、canvas、inbox-file-cleanup、NoteCraft 未入索引） |

**修复**：profile L74 更新为实际数量或改为"参见 Loom/skills/INDEX.md"；INDEX.md frontmatter 修正为 20。

### 2.3 🔴 严重：命名规范矛盾 — PascalCase vs kebab-case

| 来源 | 规则 |
|---|---|
| `Vault/meta/Persona.md` L109 | "文件命名：二级目录 **PascalCase**（去掉空格/下划线/中英混合）" |
| `filesystem/SKILL.md` §2 | "一个词优先、多词用 **kebab-case**、禁下划线" |
| `papers/schemas/naming.md`（从 SKILL.md 引用） | "文件夹：单英文单词，首字母大写，**禁止下划线、连字符**" |

**三套规则互相矛盾**：
- Persona 说 PascalCase → `MyProject/`
- filesystem 说 kebab-case → `my-project/`
- papers 说禁止连字符 → 不允许 kebab-case

**实际落地情况**：项目目录使用 `{NN-Name}` 格式（如 `01-SRTP`、`02-Thesis`），这是 kebab-case 的变体，包含连字符，违反了 papers 的"禁止连字符"规则。

**修复**：以 filesystem §2 为权威（用户已在 2026-06-13 日记中确认 kebab-case），其他两处需对齐：
- Persona.md "PascalCase" → "kebab-case（详见 filesystem skill §2）"
- papers/schemas/naming.md 删除"禁止连字符"，改为"项目编号用 `{NN-Name}` 格式（与 filesystem 一致）"

### 2.4 🟡 中等：AI 工具集描述不一致

| 来源 | 列出的 AI 工具 |
|---|---|
| `profile/SKILL.md` L69-L73 | Marvis（办公）+ Antigravity（编程）+ Hermes（已停用） |
| `Persona.md` L23 | "Claude/Gemini/Claudian/Copilot/Vibe Coding" |

两处描述的 AI 工具生态完全不同。Profile 面向 Marvis 生态（Win 端桌面工具），Persona 面向通用 AI 协作者。未说明这是双设备（Win 桌面 vs Mac 笔记本）的差异。

**修复**：Persona.md 补充说明"笔记本端使用"或注明设备差异；profile 补充 "Mac 端使用 Claude/Gemini 等（详见 Persona.md）"。

### 2.5 🟡 中等：操作系统信息缺失

| 来源 | 设备信息 |
|---|---|
| `Persona.md` L14 | "笔记本：macOS（首次 MacBook），用户名 `sample`" |
| `profile/SKILL.md` | 无设备信息，所有路径为 Windows 格式 |

Profile 完全未提及用户还有 Mac 设备，导致只看 profile 的 Agent 不知道用户有跨平台需求。filesystem skill v3.0.0 已做跨平台重构但 profile 未同步。

**修复**：profile 基本信息表增加"设备"行。

### 2.6 🟢 轻微：项目名称不一致（已大部分对齐）

profile 中「项目」表已对齐 Vault/projects/INDEX.md（使用 FormulaStudentChassis / SamplelabOS），但 Persona.md 的「在研项目」表仍有轻微差异：

| Persona.md 名称 | INDEX.md 名称 | 差异 |
|---|---|---|
| Samplelab Aura | SamplelabOS | Persona 用子项目名，INDEX 用品牌名 |
| 示例车队（Horizon Fleet）| FormulaStudentChassis | Persona 用中文，INDEX 用代码名 |

**建议**：Persona.md 项目表增加"Vault 索引名"列以显式映射。

---

## 三、过期引用

### 3.1 🔴 引用不存在的文件

| 引用来源 | 引用的路径 | 实际情况 |
|---|---|---|
| `newproject/SKILL.md` L396 | `references/scan-then-ask-workflow.md` | **不存在**，实际文件是 `references/workflow.md` |
| `inbox/SKILL.md` L153（文件清单） | `shared/README.md` | `inbox/shared/` **目录不存在** |
| `profile/SKILL.md` L74 | `D:\Cloud\Vault\Skills\` | **目录不存在** |

### 3.2 🟡 引用已废弃工具/概念

| 文件 | 问题 | 建议 |
|---|---|---|
| `exam/SKILL.md` | 多次引用 `browser agent`、`inherit_agent_id`，这些是 Hermes 专属概念 | 改为当前 Marvis 可用的替代方案，或标注为"Hermes-era 流程，待验证" |
| `notes/SKILL.md` | 频繁引用 `file-agent`，在当前 Marvis 环境中需确认对应实体 | 改为通用术语或确认 Marvis 等效能力 |
| `inbox/modules/digest.md` L17 | Marvis venv 路径 `1.0.1100.193`，但 inbox SKILL.md 关键路径声明中已更正为 `1.0.1100.219` | digest.md 内部路径未同步更新 |
| `papers/SKILL.md` readme 模板 | 引用 `srtp-research-rules`，该 skill 已被 papers 合并 | 改为自引用 `papers/projects/srtp.md` |
| `filesystem/references/cross-references.md` L11 | 声称 §0 应引用 `cron-delivery-pitfalls.md §F`，标记为"当前状态：⚠️ 未引用" | 2026-06-15 遗留的 TODO，需确认是否仍需处理 |

### 3.3 🟡 时间敏感内容

| 文件 | 内容 | 判断 |
|---|---|---|
| `profile/SKILL.md` L11 | "2025 级本科生" | ✅ 仍有效（大一在读） |
| `Persona.md` L7 | "大一下 → 大二过渡" | 🟡 2026-06-30 处于期末，即将升大二，建议更新 |
| `Persona.md` L31 | SRTP "2025.04 - 2026.03" | 🟡 即将到期（2026-03），需确认是否已结题或延期 |
| `Persona.md` L59 | After Effects "~5%，刚起步" | 🟡 3 个月未更新，可能已有变化 |
| `INDEX.md` L307 | "考前两周 Samplelab 开发冻结" | 该条来自 Persona.md 而非 INDEX.md（INDEX.md 无此内容，实际在 Persona.md），确认后可保留 |

---

## 四、僵尸目录/文件

### 4.1 空壳/占位

| 路径 | 状态 | 建议 |
|---|---|---|
| `Loom/skills/papers/projects/thesis.md` | "占位，暂未启用" | 保留，大二/大三启用 |
| `Loom/skills/papers/shared/README.md` | "暂占位" | 可删除或补内容 |
| `Loom/skills/inbox/shared/` | 在 SKILL.md 文件清单中列出但**物理不存在** | 要么创建，要么从清单中删除 |

### 4.2 未在索引中的活跃目录

以下目录存在于 `Loom/skills/` 但不在 INDEX.md 中：

| 目录 | 内容 | 判断 |
|---|---|---|
| `animation/` | 30MB vibe-motion 源码快照 | 🟡 有 INDEX.md 子索引但主索引未收录。状态为 `raw-arsenal`，非活跃 skill，可保留不收录 |
| `inbox-file-cleanup/` | 只有 `meta.json` + `SKILL.md` | 🟡 需确认是否为活跃 skill，如是则补入主索引 |
| `NoteCraft/` | 有 `STYLE.md` + `WORKFLOW.md` + prompts + 子 skill | 🟡 被 `notes` skill 引用，是笔记风格的规范源。属于基础设施但未在主索引中声明。建议补入或归档 |

### 4.3 冗余脚本

| 路径 | 问题 |
|---|---|
| `inbox/scripts/archive/digest_run_2026-06-18.py` | inbox SKILL.md changelog 已标记为"临时跑批副本，下次优先复用 digest_scan.py" |
| `inbox/scripts/archive/digest_run_2026-06-18_7d.py` | 同上 |

这些临时脚本已归档，状态正常，无需额外处理。

---

## 五、综合评分与修复建议

### 5.1 健康度评分

| 维度 | 评分 | 说明 |
|---|---|---|
| **引用一致性** | 🟡 6/10 | Skill 位置矛盾（Vault/Skills vs Loom/skills）是严重问题；数量声明不一致（8 vs 20） |
| **命名规范统一** | 🔴 4/10 | Persona / filesystem / papers 三套规则互相矛盾，是系统级设计债 |
| **Hermes 残余** | 🟡 5/10 | 核心 skill 仍有 11 处需清理（含 SOUL.md 和 sync-strategy.md 两个重灾区） |
| **过期引用** | 🟡 6/10 | 3 处引用不存在文件、若干 Hermes 概念残留、digest.md 路径未同步 |
| **僵尸资产** | 🟢 8/10 | 仅少量占位文件，无严重膨胀。临时脚本已归档 |
| **整体健康度** | 🟡 **5.8/10** | 系统功能正常但积累了一定迁移债（Hermes→Marvis 过渡不彻底）和规范冲突 |

### 5.2 优先修复建议（按紧急度排序）

#### 🔴 P0 — 立即修复（本周内）

1. **统一 Skill 物理位置声明**  
   修改 `profile/SKILL.md` L74：`D:\Cloud\Vault\Skills\` → `D:\Projects\Poyi\Loom\skills\`  
   修改 `filesystem/references/sync-strategy.md`：全篇重写，去掉 `~/.hermes/skills/` 逻辑

2. **清理 SOUL.md**  
   删除或归档 `Vault/meta/SOUL.md`（Hermes Agent Persona 配置文件，已无加载者）

3. **解决命名规范三体问题**  
   - Persona.md "PascalCase" → "kebab-case（详见 filesystem skill §2）"  
   - papers/schemas/naming.md 删除"禁止连字符"，改为引用 filesystem §2  
   - 确认以 filesystem §2 为唯一权威

#### 🟡 P1 — 两周内

4. **更新 profile skill 数量**：从"8 个"更新为引用 INDEX.md
5. **修正 INDEX.md frontmatter**：`total_skills: 19` → `20`
6. **补全未收录 skill**：`inbox-file-cleanup`、`NoteCraft` 确认状态后补入或归档
7. **修复过期文件引用**：`newproject/SKILL.md` 的 `scan-then-ask-workflow.md` → `workflow.md`
8. **inbox 文件清单**：补建或删除 `shared/` 条目
9. **Hermes 操作术语批量标注**：inbox 及其 references 中为 Hermes 专属操作加 `[Hermes-era]` 标签

#### 🟢 P2 — 一月内

10. **exam skill 现代化**：将 `browser agent`、`inherit_agent_id` 改为 Marvis 等效能力
11. **digest.md 路径同步**：更新内部 Marvis venv 版本号与 inbox SKILL.md 关键路径声明一致
12. **Persona.md 时间敏感字段更新**：SRTP 截止日期、大二过渡状态、AE 熟练度
13. **跨设备信息补充**：profile 增加 Mac 设备信息；Persona 说明 AI 工具列表的设备差异

---

*本报告由自动化审查生成，覆盖 9 个核心 skill + 4 个元数据文件 + 全盘 Hermes 扫描（106 处命中）。*  
*审查范围外（未检查）：canvas、english、ingest、lint、poyi、query、research、review、save、think、wiki-mode、wiki-retrieve 等 Wiki 核心 skill 的内部一致性。*
*（内容由AI生成，仅供参考）*
