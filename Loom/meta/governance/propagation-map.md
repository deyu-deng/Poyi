# Poyi 知识传播矩阵

> 当从某信源学到新信息时 → 必须对表检查/更新所有落点文件。
> 每发现一次"漏改了"，就在表中补一行。此文件是活的。

---

## 信源 → 落点映射

### 1. 编程对话（Antigravity raw）

| 学到什么 | 必须检查/更新的文件 |
|---|---|
| 技术选型决策 | `projects/{project}/plan.md`、`profile SKILL.md`（技术环境） |
| 架构设计 | `projects/{project}/plan.md`、`projects/{project}/progress.md`（架构里程碑） |
| Bug 修复记录 | `projects/{project}/progress.md` |
| 新工具/库引入 | `profile SKILL.md`（技术栈）、`Persona.md`（工具熟练度） |
| 项目重命名/迁移 | `Vault/projects/INDEX.md`、`projects/{old}/progress.md`、`Persona.md`、`profile SKILL.md` |
| 阻塞问题 | `projects/{project}/progress.md` |
| 代码习惯/偏好 | `Persona.md`（技能评分）、`filesystem skill`（如有命名/路径习惯变化） |

### 2. 日常聊天（Marvis / Doubao raw）

| 学到什么 | 必须检查/更新的文件 |
|---|---|
| 项目计划/想法 | `projects/{project}/plan.md`（新增项目或更新规划） |
| 待办事项 | `projects/{project}/progress.md`、`inbox skill` |
| 生活事件/决策 | `Persona.md`（核心价值观、长期愿景） |
| 组织/身份变化 | `profile SKILL.md`（基本信息、组织） |
| 情绪模式 | `Persona.md`（情绪模式） |
| 时间节点（考试/比赛/截止） | `projects/{project}/progress.md`、`inbox skill` |
| 新设备/环境变化 | `profile SKILL.md`（设备、技术环境） |
| 兴趣变化 | `profile SKILL.md`（兴趣） |

### 3. Skill 自身演进

| 变动 | 必须检查/更新的文件 |
|---|---|
| 新增 skill | `Loom/skills/INDEX.md`、`profile SKILL.md`（skill 列表） |
| 删除/弃用 skill | `Loom/skills/INDEX.md`、`profile SKILL.md`、所有引用该 skill 的文件 |
| skill 重命名 | `Loom/skills/INDEX.md`、所有引用旧名的文件 |
| skill 路径变更 | 所有引用旧路径的文件（`profile SKILL.md`、`filesystem skill` 等） |
| 跨 skill 引用更新 | 目标 skill 的 SKILL.md + 源 skill 的引用处 |

### 4. 项目物理变更（Windows 端 `D:\Cloud\Projects\`；macOS 无对应，由 Win Agent 处理）

| 变动 | 必须检查/更新的文件 |
|---|---|
| 新建项目目录 | `Vault/projects/INDEX.md`、新建 `plan.md` + `progress.md` |
| 项目目录重命名 | `Vault/projects/INDEX.md`、`Persona.md`（项目名）、`profile SKILL.md` |
| 项目迁移/归档 | `Vault/projects/INDEX.md`、项目 `progress.md` 标注迁移 |
| 技术栈变化 | `profile SKILL.md`、项目 `plan.md` |

---

## 当前信源清单

| 信源 | 位置 | 状态 | 上次消化 |
|---|---|---|---|
| Antigravity IDE 对话 | `raw/chatlog/exports/2026-06-30/` | **未消化** | - |
| Marvis 日常聊天 | 本会话上下文 | 持续消化 | 2026-06-30 |
| Doubao Windows | 待提取 | 未开始 | - |
| Hermes 历史 | `raw/chatlog/exports/2026-06-1x/` (hermes-win_*) | ✅ 已消化 | 2026-06-30 |
| Doubao Mac | 待提取 | 未开始 | - |

---

## 项目 ↔ 落点速查

| Cloud 项目 | Vault 项目名 | plan.md | progress.md | 关联文件 |
|---|---|---|---|---|
| 01-Prism | Prism | ✅ | ✅ | profile（技术栈：Electron/TypeScript） |
| 02-Aura | Aura | ✅ | ✅ | profile（鸿蒙）、Persona（Samplelab 生态） |
| 03-Electric_Trolley | Battery-Box-Cart | ✅ | ✅ | Persona（车队） |
| 04-Vaelis | Vaelis | ✅ | ❌ | profile（全栈 Agent）、Persona（Samplelab） |
| 06-Website | Kit | ✅ | ✅ | profile（PWA 工具站） |
| — | Animation | ❌ | ❌ | 调研阶段，暂无 Cloud 目录 |
| — | SRTP | — | — | Persona（学术）；文档见 项目总览.md |

> Sandbox 由 filesystem skill §4.4 定义为用户素材池，非项目，不入 Vault。
> 05-Samplelab_Animation（原 lab/实验项目集）已从 Vault/projects/ 移除。
> 07-prism 为空壳目录，不入 Vault。

---

## 新增信源 → 落点映射（2026-07-02 补全）

### 5. 笔记更新（Vault/notes/）

> 触发：写新笔记、整理/重构旧笔记、移动笔记位置后。

| 学到什么 / 做了什么 | 必须检查/更新的文件 | 更新时机 |
|---|---|---|
| 新建笔记（某领域） | `Loom/wiki/index.md`（全局索引）、对应分类 `INDEX.md`（如 `notes/计算机 Computer/INDEX.md`） | 写完即更新 |
| 笔记内容涉及项目 | 对应项目的 `plan.md` 或 `progress.md`（如笔记提到技术选型决策） | 笔记定稿后 |
| 笔记内容涉及技能 | 对应 skill 的 `SKILL.md`（如笔记总结了某工具的高级用法） | 笔记定稿后 |
| 重构/合并笔记（删除旧笔记） | `Loom/wiki/overview.md`（知识图谱）、`Loom/wiki/log.md`（操作日志） | 重构完成后 |
| 笔记中提炼出新概念 | `Loom/wiki/concepts/` 下对应条目（如概念已有则更新，无则新建） | 提炼完成时 |

### 6. Wiki 知识库更新（Loom/wiki/）

> 触发：ingest 新资料、save 对话到 wiki、手动编辑 wiki 条目后。

| 变动 | 必须检查/更新的文件 | 更新时机 |
|---|---|---|
| ingest 新资料到 wiki | `Loom/wiki/index.md`（全局目录）、`Loom/wiki/log.md`（操作日志）、对应分类 `_index.md` 或 `INDEX.md` | ingest 完成后 |
| save 对话到 wiki（新增概念页） | `Loom/wiki/index.md`、`Loom/wiki/log.md`、对应分类索引 | save 完成后 |
| 编辑已有 wiki 条目（内容变更） | `Loom/wiki/log.md`（记录变更）、`Loom/wiki/overview.md`（若影响知识图谱） | 编辑完成后 |
| wiki 条目被删除或合并 | `Loom/wiki/index.md`、`Loom/wiki/overview.md`、`Loom/wiki/log.md` | 删除/合并后 |
| hot 缓存变更（访问热点更新） | `Loom/wiki/hot.md`（自动维护，但需检查是否准确反映当前热点） | 每次 query 后 |

### 7. 英语学习痕迹（Loom/wiki/english-data/ + Vault/notes/）

> 触发：学了新的英语表达、词汇、语法点后。

| 学到什么 | 必须检查/更新的文件 | 更新时机 |
|---|---|---|
| 新表达/短语 | `Loom/wiki/english-data/expressions/<日期>.md`、`Loom/wiki/english-data/expressions/index.md` | 积累 3-5 条或每日结束时 |
| 技术英语术语 | `Loom/wiki/english-data/tech-english/<日期>.md`、`Vault/notes/语言 Language/programming language/` 下对应笔记 | 学到新术语时 |
| 语法点总结 | `Loom/wiki/english-data/grammar/index.md` | 总结完成时 |
| 每日学习笔记 | `Loom/wiki/english-data/daily-notes/index.md` | 每日学习后 |
| 英语掌握度变化 | `Loom/wiki/review/english/mastery.json`（若已建立英语复习学科） | 自测/练习后 |

### 8. 复习/掌握度追踪（Loom/wiki/review/）

> 触发：完成一次复习自测 session 后。

| 变动 | 必须检查/更新的文件 | 更新时机 |
|---|---|---|
| 复习 session 完成 | `Loom/wiki/review/<学科>/session-log.md`（追加本次记录）、`Loom/wiki/review/<学科>/mastery.json`（更新掌握度） | 每次 session 结束后立即更新 |
| 发现薄弱点 | `Loom/wiki/review/<学科>/mastery.json`（`weak_points` 字段）、对应笔记的 skeleton（若需补充） | 标记"不会"时 |
| 掌握度显著提升（模糊→熟） | 对应笔记可补充「已掌握」标记；若涉及考试节点，更新 `projects/SRTP/项目总览.md` 或 `meta/semester-spring-2026.md` | 掌握度变更时 |
| 复习计划调整（下次建议时间） | 可写入 `Loom/skills/inbox/data/activity_state.md`（若需推送提醒） | session 结束时 |

### 9. 日记/个人记录（Vault/journal/）

> 触发：写完一篇新日记后。

| 日记中出现了什么 | 必须检查/更新的文件 | 更新时机 |
|---|---|---|
| 情绪模式/情绪波动 | `Vault/meta/Persona.md`（情绪模式段）、`Vault/meta/SOUL.md`（若有价值观洞察） | 日记写完后，定期（每周）批量更新 Persona |
| 生活事件/决策 | `Vault/meta/Persona.md`（核心价值观、长期愿景段）、`Vault/meta/decisions.md` | 事件发生后 |
| 项目进展提及 | 对应项目的 `progress.md` | 日记中提到具体进展时 |
| 时间节点/DDL 提及 | `Loom/skills/inbox/data/activity_state.md`（若需追踪）、对应项目 `progress.md` | 日记中提及 DDL 时 |
| 兴趣变化/新发现 | `Vault/meta/profile SKILL.md`（兴趣段） | 兴趣明显变化时 |

> **注意**：日记 → Persona 的更新不需要每次写日记都做，建议每周或每两周批量消化一次日记，统一更新 Persona.md。

### 10. 对话归档消化（Loom/raw/chatlog/）

> 触发：将 raw/ 对话消化归档到 digested/ 后（即 `summary.md` + `knowledge.json` + `preferences.json` 已生成）。

| 消化结果中包含什么 | 必须检查/更新的文件 | 更新时机 |
|---|---|---|
| 技术决策/代码习惯 | `projects/{project}/plan.md`、`Vault/meta/profile SKILL.md`（技术栈） | 消化完成后立即更新 |
| 项目想法/计划 | `projects/{project}/plan.md`、`projects/{project}/progress.md` | 消化完成后立即更新 |
| 用户偏好变化 | `Vault/meta/profile SKILL.md`、`Vault/meta/Persona.md` | 消化完成后立即更新 |
| 新知识点（非项目相关） | `Loom/wiki/concepts/` 对应条目、`Vault/notes/` 对应笔记 | 消化完成后 |
| wiki 相关知识页面需更新 | `Loom/wiki/` 下对应概念页（若对话中有相关知识） | 消化完成后 |
| 英语表达/学习痕迹 | `Loom/wiki/english-data/` 下对应文件 | 消化完成后 |

> **原则**：对话消化产出 `knowledge.json` 后，必须对照本表逐条检查，确保无遗漏。

### 11. inbox 三模块具体落点

> 触发：各模块推送后，若有需要持久化的信息。

| 模块 | 数据文件路径 | 更新时机 |
|---|---|---|
| **digest**（待办） | `Loom/skills/inbox/data/activity_state.md`（已报名活动状态）、对应项目 `progress.md`（若待办关联项目） | 推送后，用户确认行动项时 |
| **radar**（热点） | `Loom/wiki/hot.md`（若热点需加入缓存）、`Loom/wiki/concepts/` 下对应条目（若热点包含可沉淀知识） | 推送后，用户标记"有价值"时 |
| **scout**（机会） | `Loom/skills/inbox/data/activity_state.md`（报名状态）、`projects/{project}/progress.md`（若机会关联项目） | 用户决定报名/参与后 |

> **注意**：inbox 三模块的 cron 推送本身是只读扫描，不主动修改文件。文件更新发生在用户基于推送内容采取行动后。

### 12. 连锁更新机制

> 当 A 文件更新后，依赖 A 的 B 文件可能也需要更新。本条列出已知的连锁依赖关系。

| A 文件更新 | 可能引发 B 文件更新 | 触发条件 |
|---|---|---|
| `Vault/meta/profile SKILL.md`（技术栈段） | 所有引用该技术栈的 `projects/{project}/plan.md` | 技术栈发生实质性变化（如新增/移除核心框架） |
| `Vault/meta/Persona.md`（技能评分） | `Vault/meta/profile SKILL.md`（技能列表段） | 技能评分变化反映用户能力变化，profile 中的熟练度描述需同步 |
| `Loom/skills/INDEX.md`（skill 列表） | `Vault/meta/profile SKILL.md`（skill 列表段）、所有引用该 skill 的 SKILL.md | skill 新增/删除/重命名时 |
| `Vault/projects/INDEX.md`（项目列表） | `Vault/meta/Persona.md`（项目列表段）、`Vault/meta/profile SKILL.md` | 项目新增/归档/重命名时 |
| `Loom/wiki/concepts/` 下某条目 | `Loom/wiki/overview.md`（知识图谱）、`Loom/wiki/index.md` | 概念条目新增/删除/合并时 |
| `Vault/notes/` 下笔记重构 | `Loom/wiki/concepts/` 中引用该笔记的条目、对应项目文档 | 笔记路径/标题变更时 |
| skill 重命名/路径变更 | 所有引用该 skill 的 SKILL.md、`Loom/skills/INDEX.md`、`Vault/meta/profile SKILL.md` | 重命名/路径变更时 |

> **操作建议**：每次更新 A 文件后，花 30 秒对照本表检查是否需连锁更新 B 文件。不必每次都更新，只在"触发条件"满足时才更新。

---

## 13. 自动化 Watchdog 协议 (Automation Hooks)

> **目标**：将状态同步从“Agent自觉检查”升级为“系统强制路由”。
> **执行核心**：具体负责全域扫雷更新的底层 Prompt 存放在 `Loom/meta/marvis-cron-prompt.md`。
> 未来负责维护 Poyi 的后台任务（Cron/Daemon）必须解析并实现以下触发器：

| 触发源 (Trigger Source) | 监控路径 (Watch Path) | 自动化动作 (Action Hook) | 验收状态 (Validation) |
|---|---|---|---|
| **对话归档消化** | `Loom/raw/chatlog/digested/*/knowledge.json` | 发现文件变更时，自动比对 JSON 内容与 `projects/*/plan.md` 及 `Vault/meta/profile SKILL.md`，主动提议或执行修改。 | 确保新挖掘的技术栈和决策 100% 落盘。 |
| **项目状态翻转** | `Vault/projects/*/progress.md` | 侦测到项目里程碑完成或产生新阻塞时，同步更新 `inbox/data/activity_state.md`。 | inbox 的代办与实际项目进度零延迟。 |
| **复习薄弱点** | `Loom/wiki/review/*/mastery.json` | 当 `weak_points` 新增条目时，在 `Vault/notes/` 对应学科的 skeleton 文件中自动注入 `[!] 待补强` 标签。 | 实现“复习自测 → 笔记补充”的闭环自动化。 |
| **知识网络重组** | `Loom/wiki/log.md` | 侦测到 `ingest` 或 `save` 动作后，自动触发 `lint` 技能重构 `wiki/index.md`，并刷新热缓存。 | `index.md` 条目数与物理文件绝对一致。 |

## 14. 新 Agent 自举自检清单 (Bootstrapping Checklist)

新 Agent 在读取本文件完成自举时，必须完成以下内部断言（Assertion）：
- [ ] **作用域断言**：我明确知道自己不能在 `Vault/` 区留下任何 AI 元注释或指向 `Loom/` 的链接。
- [ ] **传播断言**：如果用户做出一项架构变更，我清楚必须同步修改 `plan.md` 和 `profile SKILL.md`。
- [ ] **规范断言**：我知道新建所有项目/技能的目录名必须遵守 `kebab-case`（基于 filesystem 规范）。
- [ ] **自动化意识**：对于目前尚未实现自动化的同步环节，我必须在每次沟通后**主动**代替系统完成文件更新。

---

## 更新日志

| 日期 | 版本 | 变更内容 |
|---|---|---|
| 2026-07-02 | v2.1 | 基于第一性原则引入架构重构：新增 §13 自动化 Watchdog 协议（定义硬性机器 Hook 规则）与 §14 自举自检清单 |
| 2026-07-02 | v2.0 | 补全 8 大盲区：新增 §5 笔记更新、§6 Wiki 更新、§7 英语学习痕迹、§8 复习追踪、§9 日记、§10 对话归档消化、§11 inbox 三模块落点、§12 连锁更新机制 |
