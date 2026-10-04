<!-- source: project -->
---
name: project
description: "全周期项目生命周期管理：从创建脚手架到规划、进度追踪、状态流转（open/close/pause/block/archive）一站式覆盖。根据项目类型（engineering/research/coursework/content/experimental/document）选择模板并强制双根两层结构。触发词：'建项目'、'新建'、'开始做XX'、'项目状态'、'更新进度'、'开启/关闭/暂停/归档项目'、'/project'。"
metadata: {"version": "3.0.0", "owner": "sample-user", "last_validated": "2026-08-22", "deps": ["filesystem"]}
---
# Project — 全周期项目生命周期管理

> **加载本 skill 后，必须先与 filesystem §5.2 决策树确认项目类型，再执行对应模板。**
> **重要**：Sandbox/ 下的目录是用户主动维护的素材池（filesystem §0 陷阱 0.8）。即使实验项目 30 天无活动，Agent 也**不要主动建议**归档或删除 —— 只在用户明确要求时执行。

本 skill 管理一个项目从生到死的全部相位，**全程读写同一份事实源**（`plan.md` 的 frontmatter + `progress.md`），不另立状态文件。

---

## 单一事实源原则（为什么是单个 skill）

所有相位共享：

| 事实 | 存储位置 | 谁写 |
|---|---|---|
| 项目身份 / 类型 / 分组 / 云目录 / 状态 / 日期 | `Vault/projects/{名称}/plan.md` 的 frontmatter | create → 之后各相位只改 `status` / `updated` |
| 进度 / Sprint / Log | `Vault/projects/{名称}/progress.md` | update / open / close / archive |
| 真实工作文件 | `<CLOUD_PROJECTS>/{名称}/`（双根模型工作端） | create 建目录 |

若拆成多个 skill，每个都得重新推导「哪个项目、什么类型、cloud 在哪」，要么重复逻辑、要么约定共享状态 —— 那其实就是单 skill 的内部状态，白拆。故 **用 project 这一个 skill 覆盖全周期**。

---

## 命令语法总览

```
/project new     <type> <name>          # 脚手架 + 双根两层 + 注册（即 project skill）
/project plan    <name>                 # 深化 roadmap / milestones / decisions
/project status  <name>                 # 只读速报（quick-status）
/project update  <name> [--note "..."]  # 追加 progress.md + bump updated
/project open    <name>                 # status → active（从 paused/blocked/done 重新开启）
/project close   <name>                 # status → done（结项）
/project pause   <name>                 # status → paused
/project block   <name>                 # status → blocked
/project archive <name>                 # status → archived（不移动目录）
```

## 状态机（对齐 verifier STATUS_LABEL）

`STATUS_LABEL` 取值：`active` / `paused` / `blocked` / `done` / `archived`（由 verifier 定义，禁止自造）。

| 相位 | 作用 | 改动文件 | 附带动作 |
|---|---|---|---|
| `create` | 建双根两层 + 三件套 + 注册 | `plan.md` / `progress.md` / 真实目录 | 末尾跑一次 `verifier.py --fix-projects` |
| `plan` | 深化蓝图 | `plan.md` | — |
| `status` | 只读速报 | （无写） | — |
| `update` | 追加进度 | `progress.md` | `updated: {今天}` |
| `open` / `close` / `pause` / `block` | 状态流转 | `plan.md` frontmatter `status` | `updated: {今天}` |
| `archive` | 归档 | `plan.md` frontmatter `status: archived` | 不移动目录；INDEX 标 已归档 |

---

## Part 1 · 创建（create）

### 命名规则（与 filesystem §2 一致，名称以用户给定为准）

- **项目目录名以用户给定为准**：专有名词（如 `Aura`、`Nymo`、`Prism`、`Kit`、`Poyi`、`SRTP`）保持原样，不强制 kebab-case，允许既有编号（如 `Research/01-SRTP`）、允许大写与连字符。仅在用户未给名称或明显冲突时建议规范化。
- 包名（代码内部）：仍建议 kebab-case 小写（如 `prism-bridge`），这是代码生态惯例，与项目目录名解耦。
- 子目录：以用户实际写法为准（如 `Code`/`Design`/`Docs`/`Pictures`），不强求小写。
- Sandbox 下的命名完全由用户掌控（见 Sandbox/ 特殊规则），不在此约束内。

---

## 双根两层模型（重要）

新建一个"项目"在 Poyi 里**同时落两个地方**（不是二选一，也不是矛盾）：

| 层 | 路径（Windows） | 作用 | 内容 |
|---|---|---|---|
| **真实工作层** | `D:/Cloud/<type>/{名称}/`（名称以用户给定为准，专有名词与既有编号保留原样） | 实际产出文件 | 代码/素材/数据/文档（见模板 A–F） |
| **Poyi 规划层** | `D:/Projects/Poyi/Vault/projects/{项目名称}/` | 规划与进度追踪 | `plan.md` + `progress.md`（AGENTS.md §4） |

- `<POYI_ROOT>`：Windows = `D:/Projects/Poyi`；macOS = `/Users/sample/Poyi`。本文凡写 `D:/Projects/Poyi` 即 `<POYI_ROOT>`。
- `D:/Cloud/...` 是**真文件**根；`D:/Projects/Poyi/Vault/projects/...` 是 **Poyi 规划脚手架**，只放规划文档，不放大文件。
- 两层通过 `plan.md` 头部的"真实工作目录"字段互链（见 Step 6）。

> 历史：`project-docs` skill 已于 2026-07-19 合并进本 skill（审计日志 2026-07-19）。三件套文档**由本 skill 内联生成**，不再调用外部 skill。

---

## 执行流程

### Step 1: 决策项目类型

加载 filesystem 后，按 §5.2 决策树确认类型：

| 类型代码 | 含义 | 目标根目录 |
|---|---|---|
| `engineering` | 长期工程（有完整 PRD） | `Projects/{名称}/` |
| `research` | 学术研究课题 | `Research/{主题}/` |
| `coursework` | 课程大作业 | `Courses/{学期-课名}/Homework/{编号-作业名}/` |
| `content` | 内容创作（视频/动画/设计） | `Media/{分类}/{名称}/` |
| `experimental` | 一次性实验 / 可能废弃 | `Projects/_Sandbox/{类型}/{名称}/`（或 `Research/Sandbox/...`，以用户实际 Sandbox 位置为准） |
| `document` | 文档 / 知识库章节 | `Vault/{学科}/...` |

### Step 2: 命名确认（无编号）

- **名称以用户给定为准**：专有名词（如 `Aura`、`Nymo`、`Prism`、`Kit`、`Poyi`、`SRTP`）保持原样，不强制 kebab-case，允许既有编号（如 `Research/01-SRTP`）。仅在用户未给名称或名称明显冲突时建议规范化。
- `engineering` / `research` / `content` / `coursework`：扫描对应根目录确认名称未被占用
- 名称由用户给定或确认；冲突时提示改名

### Step 3: 重复检查

```bash
# 检查同名项目是否已存在
search_files(pattern="{名称}", target=files, path=D:/Cloud)

# 检查同编号是否被占用
ls D:/Cloud/Projects/ | grep "^{编号}-"
```

如有冲突 → 提示用户改编号或确认覆盖。

### Step 4: 执行模板

按 §A-§F 模板 mkdir + 初始化文件。

### Step 5: 初始化元数据

每个新建项目根写一份 `README.md`（最小骨架），含：
- 项目名
- 创建日期
- 类型
- Goal（一句话目标）

---

## 模板 A：engineering

**触发条件**：用户说「做一个工程 / App / 工具 / 网站」等长期项目。

**目标路径**：`Projects/{名称}/`

**目录结构**：

```bash
mkdir -p Projects/{名称}/{Code,Design,Docs,Photos,Data}
mkdir -p Projects/{名称}/Code/{包名}
```

**初始化文件**：

```bash
# Projects/{名称}/README.md
cat > Projects/{名称}/README.md << 'EOF'
# {项目名称}

> 创建于 {YYYY-MM-DD} | 类型：engineering | 编号：{编号}

## Goal
{用户输入的目标}

## 子目录
- `Code/` — 源代码（npm 工程根：{包名}）
- `Design/` — 设计稿（Figma / Sketch / AI）
- `Docs/` — 项目文档（PRD / 会议纪要 / 决策记录）
- `Photos/` — 项目相关照片
- `Data/` — 实验数据、原始素材

## 启动方式
```bash
cd Code/{包名}
npm install
npm run dev
```
EOF

# Projects/{名称}/.gitignore
cat > Projects/{名称}/.gitignore << 'EOF'
node_modules/
dist/
build/
.env
.env.local
*.log
.DS_Store
.idea/
.vscode/
EOF

# Projects/{名称}/Docs/CHANGELOG.md（自动初始化为空）
cat > Projects/{名称}/Docs/CHANGELOG.md << 'EOF'
# Changelog

> 所有重要变更记录在此。

EOF
```

**后续动作**：
- 询问用户是否初始化 git
- 询问是否要 PROPOSAL.md / TASK.md 模板

---

## 模板 B：research

**触发条件**：用户说「做研究 / SRTP / 课题 / 文献综述」等学术项目。

**目标路径**：`Research/{主题}/`

**目录结构**：

```bash
mkdir -p Research/{主题}/{Lit/Papers/English,Lit/Papers/Chinese,Lit/Patents,Notes,Code,Data,Docs,Drafts}
```

**初始化文件**：

```bash
# Research/{主题}/README.md
cat > Research/{主题}/README.md << 'EOF'
# {课题名}

> 创建于 {YYYY-MM-DD} | 类型：research | 编号：{编号}

## 课题方向
{用户输入}

## 子目录
- `Lit/Papers/English/` — 英文学术论文 PDF
- `Lit/Papers/Chinese/` — 中文学术论文 PDF
- `Lit/Patents/` — 专利 PDF
- `Lit/文献汇总表.xlsx` — 主文献数据库（唯一权威表）
- `Lit/publication.bib` — BibTeX 库
- `Notes/` — 阅读笔记、组会纪要、导师沟通
- `Code/` — 仿真代码
- `Data/` — 实验数据
- `Docs/` — 申报书、指南
- `Drafts/` — 论文草稿

## 引用规范
GB/T 7714（详见 srtp-research-rules）
EOF
```

**强约束**：
- ❌ 不允许 Office 文档进入 `Lit/Papers/` 或 `Lit/Patents/`
- ❌ 不允许在 `Lit/` 下放散落的论文 PDF

---

## 模板 C：coursework

**触发条件**：用户说「做 XX 作业」且作业是独立的、值得专门建子目录的（如期末大作业）。

**目标路径**：`Courses/{学期-课名}/Homework/{编号-作业名}/`

**目录结构**：

```bash
mkdir -p Courses/{学期-课名}/Homework/{编号-作业名}/{Datasets,References,Drafts,Final}
```

**注意**：作业目录是 `Homework/` 的**子目录**，**不要直接放在课程根目录**。

**初始化文件**：

```bash
# Courses/{学期-课名}/Homework/{编号-作业名}/README.md
cat > Courses/{学期-课名}/Homework/{编号-作业名}/README.md << 'EOF'
# {作业名}

> 课程：{学期-课名} | 作业编号：{编号} | 开始日期：{YYYY-MM-DD}

## 作业要求
{用户输入或留空待填}

## 提交物
- 草稿：`Drafts/`
- 终稿：`Final/`
- 数据集：`Datasets/`（如有）
- 参考资料：`References/`
EOF
```

---

## 模板 D：content

**触发条件**：用户说「做视频 / 动画 / 设计 / 写文章」等创意项目。

**目标路径**：
- 视频/动画：`Media/Videos/Projects/{名称}/`
- 设计：`Media/Pictures/Designs/{名称}/`
- 音乐：`Media/Music/Song/{名称}/`

**目录结构（以视频为例）**：

```bash
mkdir -p Media/Videos/Projects/{名称}/{Assets,Audio,Footage,Drafts,Final}
```

**初始化文件**：

```bash
# Media/Videos/Projects/{名称}/README.md
cat > Media/Videos/Projects/{名称}/README.md << 'EOF'
# {作品名}

> 类型：content | 创建：{YYYY-MM-DD}

## 一句话简介
{用户输入}

## 制作清单
- `Assets/` — 素材（图片、字体、图标）
- `Audio/` — 音频（BGM、音效、配音）
- `Footage/` — 原始录制
- `Drafts/` — 剪辑草稿
- `Final/` — 成品导出
EOF
```

---

## 模板 E：experimental

**触发条件**：用户说「试试看 / 实验 / sandbox / 不知道能不能成」。

**目标路径**：以用户实际 Sandbox 位置为准（当前为 `Projects/_Sandbox/{类型}/{名称}/` 或 `Research/Sandbox/...`），不强制固定路径

**`{类型}` 分类**：
- `Code` — 代码实验
- `Design` — 设计实验
- `AI` — AI 模型实验
- `Music` — 音乐实验
- `Hardware` — 硬件实验

**目录结构**：

```bash
mkdir -p Projects/_Sandbox/{类型}/{名称}/{Code,Data,Notes}
```

**初始化文件**：

```bash
# Projects/_Sandbox/{类型}/{名称}/README.md
cat > Projects/_Sandbox/{类型}/{名称}/README.md << 'EOF'
# {实验名}

> 类型：experimental | Sandbox/{类型} | 创建：{YYYY-MM-DD}
> 注：本项目为实验性。Agent 不主动监控活动状况，不主动提示归档。
>      维护决定权完全在用户。详见 filesystem skill §0 陷阱 0.8。

## 实验目标
{一句话}

## 状态
- [ ] 进行中
- [ ] 已完成（移至 Projects/）
- [ ] 已废弃
EOF

# Projects/_Sandbox/{类型}/{名称}/Notes.md（单文件记录）
cat > Projects/_Sandbox/{类型}/{名称}/Notes.md << 'EOF'
# 实验笔记

> 一切实验过程、踩坑、结论记录在此。

EOF
```

---

## 模板 F：document

**触发条件**：用户说「写一份文档 / 整理 XX 知识 / 做知识库章节」。

**目标路径**：`Vault/{学科}/...`

**目录结构**：

```bash
# 学科下新建章节
mkdir -p Vault/{学科}/{主题}/{assets}
```

**初始化文件**：

```bash
# Vault/{学科}/{主题}/README.md
cat > Vault/{学科}/{主题}/README.md << 'EOF'
# {主题}

> 学科：{学科} | 创建：{YYYY-MM-DD}

## 章节
- 章节列表（自动生成）

## 引用
（双链自动）
EOF
```

---

## 通用规则

1. **永远不裸建目录**：所有 mkdir 必须配套至少一个 README.md
2. **永远先检查冲突**：见 Step 3
3. **永远问用户**：当类型模糊时，列出 6 种让用户选
4. **永远记录动作**：mkdir 后在 Obsidian Daily Note 写一行
5. **永远不嵌套项目**：Projects/_Sandbox/A/B/C 这种结构禁止
6. **尊重用户给定名称**：专有名词与既有编号保留原样，不强制 kebab-case；仅在用户明确要求时规范化

---

## 反例（禁止出现的结构）

❌ `Projects/foo/bar/` — 项目嵌套项目（禁止，见通用规则 5）
❌ `Projects/my-test/code/index.js` — 工程没有 Code 子目录包裹
❌ `Research/MyResearch/papers/paper1.pdf` — 没用 Papers/English/ 路径
❌ `Sandbox/Hackathon/health-agent/` — Sandbox 下应先有类型子目录
❌ `Courses/2025秋冬-线性代数/homework1.py` — 作业应在 Homework 子目录下
❌ `Projects/plobi_animation` — 一般项目避免下划线（Sandbox 例外，见 Sandbox/ 特殊规则）

---

## Sandbox/ 的特殊规则（重要）

`D:/Cloud/Projects/_Sandbox/` 是用户的**主动维护素材池**，不是普通实验项目区。

**用户原话**（2026-06-13）：
> "我就是喜欢这样，以后我的不同类型但又不属于某个特定的项目的东西我会往里面放。"

**规则**：

1. **不要建议清理 Sandbox/ 下的空目录** — 它们是用户刻意保留的占位
2. **不要建议清理 Sandbox/Code/Hackathon/ 等下的 v1/v2/v3/final 多版本** — 那是用户的工作方式
3. **不要主动重命名 Sandbox/ 下的任何内容** — 即便其命名不符合项目命名建议
4. **不要主动监控 Sandbox/ 下项目的活动状况** — "30 天无活动" 之类的话术**禁止**

**何时 Agent 可以动 Sandbox/**：

- 用户**明确说**"帮我整理 Sandbox/ 下的 XX"
- 用户**明确问**"Sandbox/Code/Hackathon/ 还能用吗？" — 这种情况给现状报告
- 其他情况 — **只问不动**

详见 `filesystem` skill §0 陷阱 0.8 和 `references/workflow.md`。

---

## 与 filesystem 的衔接（加载顺序）

本 skill 是 filesystem §5.2 决策树的**执行层**：

```
filesystem §5.2（决策：选类型）
        ↓
project（本文件）（执行：建双根两层）
        ↓ mkdir 真实工作层 + README.md（模板 A–F）
        ↓ mkdir Poyi 规划层 + plan.md + progress.md + research.md（Step 6）
```

加载顺序：filesystem **必须先加载**，project 才能用。
**不再调用已废弃的 `project-docs` skill** —— 三件套由本 skill 在 Step 6 内联生成。

---

## Step 6: Poyi 规划脚手架（双根第二层）

对**长期项目**（`engineering` / `research` / `content` / `coursework`）在创建真实工作层后，**额外**于 `<POYI_ROOT>/Vault/projects/` 下建规划脚手架：

```bash
mkdir -p D:/Projects/Poyi/Vault/projects/{项目名称}
```

- 目录名以用户给定为准（专有名词/编号/大写连字符均保留）；与 AGENTS.md §4 一致。
- `experimental`（Sandbox）与 `document`（已落 Vault）**不建**此层。

### plan.md 模板

```bash
cat > D:/Projects/Poyi/Vault/projects/{项目名称}/plan.md << 'EOF'
---
project: {项目名称}
title: {项目名}
type: {type}
group: {group}            # system | product | research（按类型映射）
cloud: D:/Cloud/<type>/{名称}   # 无独立工作目录时删除此行
status: active
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
tech: [{技术栈逗号分隔}]
summary: {一句话目标}
---

# {项目名} — Plan

## Goal
{一句话目标}

## Roadmap
| # | 阶段 | 交付标准 |
|---|------|----------|
| 1 |  |  |
| 2 |  |  |

## Milestones
- [ ] M1：
- [ ] M2：

## Status
- 当前阶段：
- 下一步：

## Decisions
- （只留结论，一行一条；理由进 research.md）

## Risks
- 

## References
- AGENTS.md §4（项目治理）
EOF

cat > D:/Projects/Poyi/Vault/projects/{项目名称}/progress.md << 'EOF'
# {项目名} — Progress

> 最后更新：{YYYY-MM-DD}

## Status
- 阶段：
- 进行中：
- 阻塞：
- 下一步：

## Sprint
| 日期 | 任务 | 状态 |
|------|------|------|

## Log
### {YYYY-MM-DD}
- 完成：
- 决策：
- 阻塞：
EOF

cat > D:/Projects/Poyi/Vault/projects/{项目名称}/research.md << 'EOF'
# {项目名} — Research

> 最后更新：{YYYY-MM-DD}

## Notes
### {YYYY-MM-DD} · {主题}
- 来源：[AI调研] / [灵感] / [链接]
- 结论：

## TODO
- [ ] 
EOF
```

> 所有长期项目统一三件套：`plan.md`（蓝图）+ `progress.md`（看板）+ `research.md`（调研）。**严格对齐模板骨架**：`plan.md` 须含规范区块 **Goal / Roadmap / Milestones / Status / Decisions / Risks / References**（顺序与命名以本 skill 模板为准，中英文标题皆可，但区块集合须完整）；`progress.md` 须含 **Status / Sprint / Log**；`research.md` 须含 **Notes / TODO**。`experimental`（Sandbox）与 `document`（已落 Vault）不建规划层。
> **内容保留原则**：归位到对应区块即可，**不得删除或改写用户既有内容**——规范区块之外的额外章节（如技术架构、产品定位、第一性原理推导、成本路线等）一律原样保留，缺的规范区块补占位（如 `- （待补充）`）而非凭空编造。
> `research` 类项目可在规划层额外加 `research.md`（文献与方向追踪）；其余类型保持 `plan.md` + `progress.md` 两件套即可。
> **建完后务必运行 `python Loom/scripts/verifier.py --fix-projects` 刷新 INDEX.md** —— 索引由 plan.md frontmatter 自动生成，勿手改（该命令同时做项目注册表漂移校验）。
*（内容由AI生成，仅供参考）*

## Part 2 · 生命周期操作（create 之后的后半生）

> 除 `create` 末尾与 `update` 外，状态流转**不跑 verifier**（仅改 frontmatter / progress 文本，verifier 在 `create` 时已注册过；`--fix-projects` 仅在 create 末尾跑一次）。

### 2.1 plan — 深化蓝图

读 `plan.md`，按 `Roadmap` / `Milestones` / `Decisions` 提示用户补充或修订；可 LLM 辅助生成草案，但**落盘前让用户确认**。不新建文件，只改 `plan.md`。

### 2.2 status — 只读速报（quick-status）

读 `plan.md` + `progress.md`，输出：当前阶段 / 阻塞 / 下一步 / 最近 Log 条目。**不写任何文件**。

### 2.3 update — 追加进度

在 `progress.md` 的 `## Log` 追加 `### {今天}` 小节，写完成情况 / 决策 / 阻塞；同步把 `plan.md` frontmatter 的 `updated` bump 为今天。

### 2.4 open / close / pause / block / archive — 状态流转

统一步骤：
1. 编辑 `plan.md` frontmatter：`status: <目标值>`；`updated: {今天}`。
2. 若该相位需记 Log（上表"附带动作"列），在 `progress.md` 的 `## Log` 追加对应小节。
3. 全部为 frontmatter / progress 文本改动，**不跑 verifier**。
4. 回用户一句确认（如「`Aura` 已 `close` → 状态 已完成」）。

> 状态值严格取自 verifier `STATUS_LABEL`（active/paused/blocked/done/archived），禁止自造（如 `someday` / `backlog`），否则 INDEX 渲染 fallback 成裸英文。

---

## 全周期闭环示例

```
/project new engineering prism        → 建双根 + 三件套 + verifier 注册（status: active）
/project plan prism                   → 填 Roadmap / Milestones / Decisions
…（日常开发）…
/project update prism --note "完成编译器前端"   → Sprint+Log 追加，updated bump
/project status prism                 → 速报当前阶段/阻塞/下一步
/project pause prism                  → status: paused（考试周搁置）
/project open prism                   → status: active（回归）
/project close prism                  → status: done（结项）
/project archive prism                → status: archived（留原位，INDEX 标 已归档）
```

每一步都只碰 `plan.md` / `progress.md` 同一份事实源，verifier 全程无需为状态流转重跑（仅 create 末尾跑一次 --fix-projects 生成 INDEX）。
