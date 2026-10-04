# AGENTS.md — Poyi 系统唯一入口与全能洗脑协议

> **`/poyi` 全域唤醒指令 (Universal Hook)**
> 无论您是哪个平台的野生 AI，一旦接收到 `/poyi` 指令，必须立刻：
> 1. 加载本文件（`AGENTS.md`）作为最高运行准则。
> 2. 强制切入 `Main Agent` 角色（放弃原生无聊助手设定）。
> 3. 严格执行本文件 §3 的「8 步自举协议」以及 §4 的「四大日常工作流响应机制」。
> 
> 本文件是 Poyi 的单一事实来源。任何其他文件声称描述 Poyi 结构的，以本文件为准。物理文件系统是最高权威。

---

## 0. 平台与路径约定（双环境分层）

Poyi 在 macOS 与 Windows 双设备通过 Git 同步。为避免写死盘符导致的交叉污染，统一约定：

- **`<POYI_ROOT>`**：macOS = `/Users/sample/Poyi`；Windows = `D:\Projects\Poyi`。本文件及所有活文档一律用 `<POYI_ROOT>`，禁止写死盘符。
- **分层**：
  1. **共享内核（本文件）** = 系统权威（结构 / 命名 / 路由）。两个 Agent 都遵守，不各写一套。
  2. **设备覆盖层** = `Vault/meta/Meta.mac.md`（macOS 专属）/ `Vault/meta/Meta.win.md`（Windows 专属）：含各自 computer-map、账户、同步策略。各端 Agent 只改自己的覆盖层。
  3. **人的内容** = `Vault/meta` 的 `Persona` / `SOUL` / `Areas`：归用户，不归任何 Agent。
- `Vault/meta/Meta.md` 仅作共享内核镜像（命名规范以本文件 §5 为准），不另立命名法、不写设备专属事实。

---

## 1. 物理结构（实际存在）

```
<POYI_ROOT>
├── AGENTS.md              ← 本文件：唯一入口
├── README.md              ← 人类速查摘要（结构以本文件为准）
├── .gitignore
├── .obsidian/             ← Obsidian 配置（本机专用，不入库）
├── .githooks/             ← pre-commit / pre-push：提交与推送前跑 verifier
├── Loom/                  ← AI 专属工作区（人类极少触碰）
│   ├── meta/
│   │   ├── governance/                 ← propagation-map.md（知识传播矩阵）+ IDEAL.md（理想态靶子）
│   │   ├── automation/                 ← marvis-cron-prompt.md（定时唤醒底层 Prompt）
│   │   ├── skill-standard.md           ← SKILL.md 内容标准
│   │   └── archive/                    ← 历史审计/修复报告（已过时，非事实来源）
│   ├── skills/             ← 22 个技能定义（完整索引见 Loom/skills/INDEX.md）+ _archive/
│   ├── wiki/               ← AI 生成的知识碎片
│   │   ├── english-data/   ← 英语学习痕迹
│   │   ├── review/         ← 复习掌握度追踪
│   │   ├── comparisons/ concepts/ entities/ sources/ meta/ reports/
│   │   ├── .retrieve-bm25/ ← 检索索引（本机构建物，不入库）
│   │   └── hot.md index.md log.md overview.md
│   ├── raw/                ← 本机原始数据，**全量不入库**（公开仓库不带对话数据）
│   │   ├── chatlog/        ← raw/（导出分桶）+ digested/（消化摘要）
│   │   └── social/         ← wechat 等 IM 采集产物
│   ├── scripts/            ← 系统控制脚本（聚合/编译/校验/脱敏；logs/ 与 exporters/ 在此）
│   └── dist/               ← 编译后的单文件技能副本（由 skills/ 生成）
│
└── Vault/                  ← 人+AI 协作区（当前内容全为虚构示例 fixture）
    ├── journal/            ← 日记（按 YYYY-MM-DD-星期.md）
    ├── meta/               ← INDEX + governance(SOUL/decisions) + profile(profile.md) + system(Meta.<os>.md, computer-map.<os>.json) + attachments/
    ├── notes/              ← 七大领域笔记（AI/数学/物理/计算机/工程/工具/语言）
    ├── Context/            ← computer-map.json（本机目录快照）
    ├── inbox/              ← 临时落地区
    └── projects/           ← 14 个项目（含 Poyi 系统自身）：Animation / Aura / Battery-Box-Cart / Stithy / Kit / Poyi / Prism / Resonote / SRTP / Nymo / Nuclide / Personal-Website / Vaelis / Wealth-Lab
        └── INDEX.md        ← 项目导航入口（verifier --fix-projects 自动生成）
```

## 1.5 用户身份（权威摘要）

> **完整事实档案见 `Loom/skills/profile/SKILL.md`（唯一权威来源）。本段仅为摘要；修改用户信息只改 profile，不要在此展开或重复维护。**

- **姓名**：林小满（小满）
- **学校**：北屿大学，2025 级
- **学院 / 专业**：机械与能源学院 · 机电工程（已分流）
- **年级**：大一下册（暑假），即将升大二
- **城市 / 时区**：临海市 / UTC+8
- **设备**：Win 桌面（Marvis + Antigravity）为主生产力；Mac 笔记本（用户 `sample`，本机）为轻量端
- **Mac vault 根**：`/Users/sample/Poyi`（Obsidian 打开此根；内含 `Vault/` 人协作区与 `Loom/` AI 工作区）
- **内在画像**（技能评分 / 情绪模式 / 价值观 / 弱点 / 愿景）：`Vault/meta/profile/profile.md`，只记录内在层，不重复上述事实
- ⚠️ 上述身份为**虚构示例人设**，随仓库公开，用于让 Poyi 带样例画像出厂。

---

## 2. 技能系统

> 共 22 个技能，按官方 Agent Skills 标准编写。详细机读依赖关系见 `Loom/skills/INDEX.md`。

<!-- SKILL_TABLE_START -->
| 技能 | 描述（用途 + 触发） |
|---|---|
| `autoresearch` | 自主研究循环：接收一个主题，执行迭代网页搜索与抓取，合成发现并全部归档到 wiki（concepts/entities/sources + 综合页 Research: Topic）。基于 Karpathy autoresearch，最大 3 轮，带 web 安全卫生与成本预算。 触发词：自主研究、调研、research、深度研究、查资料。 |
| `campus` | Beiyu 校园事务自动化脚本集：自动签到、作业待办、校园课堂语音转 Markdown、图书馆查询。位于 D://Tools//Scripts//Beiyu-live-better//。 触发词：北屿大学、Beiyu、校园事务、签到、校园课堂。 |
| `canvas` | Loom 知识图谱可视化引擎：将 wiki 知识图谱转为 Obsidian Canvas（JSON Canvas 1.0 规范），按 type 颜色分组、自动网格布局生成 .canvas 文件。Canvas 是 wiki 的只读视觉投影，支持 /canvas、/canvas <topic>、/canvas full 及 add image/note/text 子命令。 触发词：canvas、知识图谱、图谱、可视化。 |
| `daily` | 消息中枢：聚合消息扫描、热点雷达、机会挖掘三个子模块。加载本 skill 后，Agent 按用户意图路由到对应子模块。触发词：'待办'、'热点'、'机会'、'今日要做'、'今天有什么活动'。 |
| `defuddle` | 网页清洗器：剥除广告/导航/页脚/社交按钮，输出纯净 Markdown，节省 40-60% token。基于 kepano/defuddle-cli。触发词：defuddle、清洗网页、剥广告、clean url |
| `english` | 英语学习增强器：用户问英语表达时，先检索 Vault 知识库锚点（AI/数学/物理/计算机/工程笔记）用已知概念类比解释，再记录学习痕迹到 Loom/wiki/english-data/，并同步语料本到 Vault。会话中自然穿插复用已学表达。 触发词：英语、英语表达、英文怎么说、English。 |
| `exam` | 从微信公众号收集历年试卷，OCR 提取题目，AI 自行解答，生成统一排版的 LaTeX PDF 文档。触发词：'收集试卷'、'历年卷'、'OCR 试卷'。 |
| `filesystem` | 跨平台文件系统规则：约束 Agent 在所有文件操作中的路径、命名、目录结构行为。平台检测 + 决策树 + 自查机制。触发词：'放哪里'、'命名'、'装依赖'、'文件结构'、'系统盘满了'。 |
| `ingest` | 知识入库器：把外部源（文件/URL/图片）与正在进行的对话都写入 wiki 并交叉引用一切。源吞入支持 Delta 去重、矛盾检测、批量；会话捕获支持五型分类（synthesis/concept/source/decision/session）与保存 vs 跳过判断。所有写入用 Obsidian Flavored Markdown。触发词：ingest、吞入、处理文件/网页/PDF、归档进知识库、整理聊天记录进知识库、对话归档、保存对话、存这次讨论、save。 |
| `lint` | Wiki 健康检查：每 10-15 次 ingest 或每周运行，执行 10 项检查（孤立页、死链、过期主张、缺失页、frontmatter 缺口、命名违规、写作风格等）。输出 lint-report，自动修复前先询问；附 Dataview 仪表盘与 Canvas 地图。 触发词：lint、wiki体检、死链检查、知识库健康。 |
| `notes` | 批量整理课程笔记：扫描目录 → 去重 → 风格审查 → 逐章重写/扩充 → 更新索引。Designed for the dual-track note workflow (STYLE.md + WORKFLOW.md)。触发词：'整理笔记'、'统一笔记风格'、'规范化笔记'。 |
| `papers` | 科研文件管理 Skill。统一 Research/ 下所有课题的文件结构、命名、引用规范。原 research-workflow + papers/projects/SRTP.md 已整合。触发词：'文献'、'论文'、'SRTP'、'科研'、'写论文'、'投稿'。 |
| `poyi` | Poyi 系统全局洗脑与接管协议入口。Agent 收到此技能后，必须读取 <POYI_ROOT>/AGENTS.md 并切入知识库维护角色。触发词：/poyi、Poyi系统、知识库。 |
| `profile` | 统一的用户画像 skill。daily 三模块（digest/radar/scout）共享的用户画像，作为唯一权威来源。被 daily 等 skill 引用，避免重复维护。 触发词：用户画像、我的偏好、profile、我是谁。 |
| `project` | 全周期项目生命周期管理：从创建脚手架到规划、进度追踪、状态流转（open/close/pause/block/archive）一站式覆盖。根据项目类型（engineering/research/coursework/content/experimental/document）选择模板并强制双根两层结构。触发词：'建项目'、'新建'、'开始做XX'、'项目状态'、'更新进度'、'开启/关闭/暂停/归档项目'、'/project'。 |
| `query` | Wiki 查询引擎：策略性读取、精准回答、主动归档让知识复利。三层查询（Quick/Standard/Deep）按复杂度匹配深度；优先 hot.md→index→页面，附 wikilink 引用，好答案归档回 wiki。 触发词：wiki查询、查wiki、query。 |
| `review` | 学科主动复习系统：基于骨架笔记自测驱动，加权随机选题（不会>模糊>未测>熟），记录掌握度到 mastery.json。支持刷题/费曼输出/概念图模式。产物全在 Loom 侧，不污染 Vault。 触发词：复习、刷题、自测、掌握度、review。 |
| `save` | 对话归档到 Wiki：取刚讨论的内容归档为永久 wiki 页面（synthesis/concept/source/decision/session 五型）。Wiki 复利——经常 save。含目标根目录决策、frontmatter 模板、保存 vs 跳过标准。 |
| `think` | 10 原则思考框架（OBSERVE-外 / OBSERVE-内 / LISTEN / THINK / CONNECT-横 / CONNECT-系 / FEEL / ACCEPT / CREATE / GROW）：用于架构决策、复盘、模糊请求、多利益方权衡。元技能，告知其他技能如何思考。 触发词：思考框架、架构决策、复盘、think、权衡。 |
| `triage` | 通用文件分拣引擎：将任意目录的散落文件按 filesystem 决策树与 profile 上下文自动归类到目标路径。当用户要求整理 Inbox / Downloads、分拣或归类文件，或提供目录路径时触发。 触发词：整理文件、分拣、归类、清理目录、triage。 |
| `wiki-mode` | Loom 方法论模式切换器：管理 wiki 底层目录拓扑，支持 generic/lyt/para/zettelkasten 四种组织方法论。切换模式只影响未来写入（不迁移已有文件），路由规则存于 Loom/.vault-meta/mode.json。 触发词：wiki模式、方法论切换、zettelkasten、para。 |
| `wiki-retrieve` | Loom 混合语义检索引擎：当 query 的确定性路径（hot→index→pages）不够时，用 BM25 稀疏检索 + 可选上下文前缀 + 可选稠密重排三层管线，从 wiki 召回最相关页面与段落。query 优先，retrieve 兜底。 触发词：语义检索、检索wiki、retrieve、搜知识库。 |
<!-- SKILL_TABLE_END -->

技能完整详情见 `Loom/skills/INDEX.md`。

---

## 3. 全量自举协议（接管流程）

新 Agent 首次进入 Poyi 时，需完成以下八个维度的感知。标 ★ 的为强制步骤，其他按需触发。

### 第一步：结构核验 ★

列出 Loom/ 和 Vault/ 顶层目录，对照 §1 物理结构。不一致时以物理文件系统为准，更新本文件。

### 第二步：元信息层 ★

读取 `Loom/meta/governance/propagation-map.md` → 理解知识传播矩阵（哪个技能产出流向哪个区域）。
读取 `Loom/meta/governance/IDEAL.md` → 理解系统靶子（五大维度 + target 分）。
读取 `Loom/meta/archive/` 最新一份审计 → 了解上次审计发现的问题清单。

### 第三步：技能系统 ★

读取 `Loom/skills/INDEX.md` → 获取每个 skill 的 SKILL.md 路径、依赖关系、触发词。§2 的表格只是摘要，INDEX.md 才有可执行路径。

### 第四步：Wiki 知识碎片 ★

读取 `Loom/wiki/index.md` → 了解已有知识碎片的分类与检索入口。
主要活跃区域：`english-data/`（英语学习痕迹）、`review/`（学科掌握度追踪）。

### 第五步：对话记忆

`Loom/raw/` 全部是**本机数据，不入 Git**（公开仓库不带任何真实对话）。接手时先确认本机目录存在：
- `Loom/raw/chatlog/raw/` → 按日期找原始对话导出（分桶后的 `_day_messages.json` 等）
- `Loom/raw/chatlog/digested/` → 已消化摘要（`summary.md` + `knowledge.json`），可直接吸收而不必重读原始对话
- `Loom/raw/social/` → 微信等 IM 采集产物


### 第六步：Vault 项目区

读取 `Vault/projects/INDEX.md` → 了解 14 个项目的入口路径。
需要接手某个具体项目时，读取 `<项目目录>/plan.md` + `progress.md` + `research.md`（三件套，见 project skill Step 6）。

### 第七步：Vault 元文件

读取 `Vault/meta/governance/SOUL.md` → 系统灵魂文件（核心信念与红线）。
读取 `Vault/meta/profile/profile.md` → 用户画像（可作为对话风格参考）。
按需读取 `Vault/meta/governance/decisions.md`（决策台账）、`Vault/meta/system/Meta.<os>.md` 与对应 `Vault/meta/system/computer-map.<os>.json`（设备专属，见覆盖层）。

### 第八步：按需深入

- 接手研究任务 → `Vault/notes/` 下对应领域笔记
- 接手课程作业 → Windows 端 `D:\Cloud\Courses\` 下对应课程目录（触发 filesystem skill；macOS 无此目录，由 Win Agent 处理）
- 接手 Inbox 清理 → 触发 triage skill

**关键原则**：物理文件系统是最高权威。本文件为缓存，允许短暂过期，但接手时必须核验。

---

## 4. 四大日常工作流响应机制 (The 4 Core Workflows)

当完成 `/poyi` 洗脑后，Agent 必须对以下 4 种日常交互做出极其规范的条件反射：

1. **场景一：零散知识与想法入库 (Librarian 意图)**
   - **触发**：用户丢来一段资料、链接或零散想法。
   - **响应**：不问废话，直接提取结构化概念，调用内部检索，将笔记存入 `Loom/wiki/concepts/`，并强制注入 `[[相关已有笔记]]` 双链。实现知识复利。
2. **场景二：灵感立项与执行 (Manager 意图)**
   - **触发**：用户说“开个新计划”或“推进 XX 项目”。
   - **响应**：在 `Vault/projects/` 下按用户给定名称创建目录（命名见 §5 项目命名约定，不强制 kebab-case），并初始化/更新 `plan.md`、`progress.md` 和 `research.md` 三件套。
3. **场景三：强迫症文件管家 (Engineer 意图)**
   - **触发**：任何涉及文件创建或保存的操作。
   - **响应**：作为底层拦截器，强制校验目录结构（只能在 9 大顶层目录）；命名尊重用户给定名称（见 §5），不强制 kebab-case，不自动纠正专有名词/编号/大写连字符。
4. **场景四：信源日抛消化 (Cron 闭环)**
   - **触发**：外部廉价 Agent 定时运行 `aggregate_win.py` / `aggregate_mac.py` 将聊天数据落盘至 `Loom/raw/chatlog/raw/`，并提炼为 `knowledge.json`。
   - **响应**：Agent 被定时任务唤醒时（底层 Prompt 见 `Loom/meta/automation/marvis-cron-prompt.md`），自动将这些提炼出的精华编织进知识库。

---

## 5. 关键规则

- **Vault 禁止出现指向 Loom 的链接**：两个区独立呈现
- **Vault 禁止 AI 元注释**：不写"来源：XX""经 X 消化""最后更新：YYYY-MM-DD"
- **项目命名用自然英文**，多词以 `-` 连接（如 `Battery-Box-Cart`），大小写按项目名本身
- **文件命名用英文 kebab-case**（如 `Words.md` 而非 `词汇.md`）——适用于 `Loom/scripts/`、`Loom/skills/` 及代码类文件；`projects/` 目录名见 §5 项目命名约定（用户给定为准，不强制 kebab）。**例外**：`Vault/notes/` 七大领域笔记刻意使用中文描述性文件名（可含空格，如 `工程图学.md`、`ch01 质点运动学.md`），因人类在 Obsidian 中以中文导航，此为该域的既定设计选择，不强制英文化、亦不触发 Engineer 路径纠偏。
- **SOUL.md 位于 Vault/meta/governance/SOUL.md** —— 系统灵魂文件
- **修复腐烂度的审计报告**位于 Loom/meta/archive/decay-audit-*.md
- **技能修改优先于新建**：当需要扩展已有技能的功能时，优先在现有 SKILL.md 内增加章节，而非创建新的独立 skill。新建 skill 仅在该功能无法合理归属到任何已有 skill 时才允许。此规则旨在防止 skill 碎片化（参见审计日志 2026-07-19）

---

## 6. 维护规则

- **[自动化法条]** 禁止手动更新技能列表！新建/删除/重命名技能，必须统一通过 `python <POYI_ROOT>/Loom/scripts/manage_skills.py sync` 脚本全自动完成。
- Poyi 结构变更后，必须更新本文件 §1
- 每次腐烂度审计必须更新本文件末尾的审计日志
- 本文件是 Poyi 的单一事实来源，禁止创建竞争性入口文件

---

## 审计日志

- **2026-07-19**：技能碎片化教训。Agent 将项目文档格式规范错误地新建为独立 `project-docs` skill，而非合并进已有的 `newproject` skill。用户指出后纠正：合并进 `newproject` v2.0.0 §7-§8，删除 `project-docs/` 目录。据此在 §5 新增"技能修改优先于新建"规则。根因：Agent 倾向于新建而非修改已有文件，需显式约束。
- **2026-07-09**：双 meta 对齐修复（分层模型）。AGENTS.md 新增 §0「平台与路径约定」（`<POYI_ROOT>` 占位符 + 共享内核/设备覆盖层/人的内容 三层）；§1 树根改 `<POYI_ROOT>`；步骤八课程目录标注 Windows-only；manage_skills 路径改 `<POYI_ROOT>`。Vault/meta/Meta.md 改为镜像 AGENTS §5（删 PascalCase 重定义、修正 Context/ 幽灵路径、Win 根 D:\Cloud\Vault→D:\Projects\Poyi），并新增 Meta.mac.md / Meta.win.md 设备覆盖层；INDEX.md 的 Knowledge/ 引用改 Vault/notes/；decisions.md 旧路径与过时结构标注。
- **2026-07-01**：对抗性审计（全量物理扫描 + 索引逐条核验）。P0：修正 AGENTS.md §1 虚报的 4 个 chat-logs 子目录（marvis/chatgpt/openai/windsurf），对齐物理现实；修正 propagation-map 3 条断裂信源路径（Antigravity/Doubao/Hermes）；补建 SRTP/plan.md。健康度 5.4/10 → 待下次评估。
- **2026-07-02**：清理 Vault/meta/ 下不属于 Poyi 系统的文件。将 RULES.md（Poyi Vault Mac端规则，含 PascalCase 命名规则，与 AGENTS.md kebab-case 冲突）和 workflows.md（Mac/Claude Code 工作流）移入 Loom/meta/archive/；更新 §1 结构描述移除对这两个文件的引用；确认 Persona.md 与 AGENTS.md §4 kebab-case 规则表述一致无冲突；propagation-map 无指向这两个文件的引用。
- **2026-06-30**：全物理盘点审计。删除 Loom/AGENTS.md（513 行蓝图残骸）、BOOTSTRAP.md（链路断裂）、.claude/skills/mac-filesystem-hygiene（跨平台污染）。本文件重写为单入口。补全 INDEX.md 缺失的 3 个 skill。修复 english 技能 macOS 路径。P0-P3 全链清零。
- **2026-07-12**：将 Poyi 系统自身登记为 `Vault/projects/` 下的项目（用户决策：projects/ 应容纳所有推进中的项目以统一查看进度）。新增 `Vault/projects/poyi/`（plan.md + progress.md）作为人类视角进度看板；权威规格仍在 `Loom/meta/AGENTS.md` + `IDEAL.md`。同步更新 §1 projects 列表（9→10，含 poyi）与 `Vault/projects/INDEX.md` 新增「系统自身 / Poyi」条目。
- **2026-07-12**：补齐「神经系统」第一块——接入 git pre-commit verifier（对应 claude-obsidian 缺失的 hooks / verifier sub-agent）。新增 `Loom/scripts/verifier.py`（规格声明 vs 磁盘物理一致性审计：AGENTS §1 项目列表 ↔ Vault/projects、AGENTS 技能数 ↔ Loom/skills、wiki 子目录 ↔ 磁盘、INDEX wikilink 死链、空幽灵目录；退出码 0/1/2）；`.githooks/pre-commit` 提交前自动跑 verifier 阻断 BLOCKER 级不一致；`git config core.hooksPath .githooks`（受版本管理可 push）。端到端实测红路（注入假项目→阻断）+ 绿路（正常提交→放行）均通过。IDEAL 新增「神经系统」维度行（现状 ~3）。
- **2026-07-25**：腐烂度审计修复（Marvis 全量审计 2.6/10）。三大病灶：① 12 个 skill description 为空（"No description provided."，其中 autoresearch 整段 frontmatter 被 AIGC 水印吞掉、连 name 都无）；② 4 个 skill（campus/english/review/autoresearch）frontmatter 被 AIGC 平台水印污染（Label/ContentProducer/ProduceID/ReservedCode1-2 base64 blob）；③ 全员使用非标准 frontmatter 字段（role/version/type/created）。本次修复：删除 4 个 skill + 4 个 references 文档的 AIGC 水印块，补全 12 个空 description（基于各 SKILL.md 正文拟一句话中文描述）。共改 17 个文件。非标准 frontmatter 字段（病灶③）留作后续专项，未本次处理。修复后全树 0 水印、0 空 description。
- **2026-07-27**：四角色系统废除 + skill 内容标准落地（用户决策"不要四角色，太麻烦了"）。① 以 Claude 官方 Agent Skills 标准为标杆定稿 `Loom/meta/skill-standard.md`：frontmatter 仅 `name`+`description` 必填，可选 `allowed-tools`/`when_to_use`，禁 `role`/`x-role`/`version`/`type`/`created`/`status`/`title`/`metadata`/`scope`/`layer`/`supersedes`/`source`/`x-depends-on` 等非标准字段。② 26 个 SKILL.md 批量去 cruft（仅留允许字段）+ 11 文件正文反斜杠翻正斜杠（`triage` 补建缺失 frontmatter）。③ `manage_skills.py` 删 `LEGACY_ROLE_MAP`/`ROLE_META`、补 `delete` 子命令、`sync` 改扁平表 + 强制校准 frontmatter（自愈）。④ AGENTS.md §2 / INDEX.md 去四角色分组，改扁平技能清单（保留依赖信息）。⑤ 合并唯一真重复 `research`→`autoresearch`（删目录 + 同步）。⑥ 索引对齐现实：厘清 `daily` 即 `inbox` 改名+升级版（supersedes message-digest/info-radar/opportunity-scout，旧"722 次不在索引"悬案闭环）；`triage` 为新建文件分拣引擎；旧 `inbox` 目录已不存在（引用待清理）。终态：全树 0 非标准 frontmatter 字段、0 反斜杠、25 个技能。

- **2026-08-14**：保守合并（用户拍板"先走真合并"）。基于官方标准 + 证据核查，合并 2 个真重复技能：① `inbox-cleanup`→`triage`（D:/Inbox 专用路由域知识搬为 `triage/references/inbox-rules.md`，删 inbox-cleanup 目录）；② `notecraft`→`notes`（STYLE.md/WORKFLOW.md/README.md/prompts//skills/note-merge 搬入 notes/，删 notecraft 目录，修 notes/SKILL.md 的 `skills/notecraft/STYLE.md` 失效引用）。顺手修 stale 引用：AGENTS §2/§3、INDEX 扁平表与 YAML、profile 描述（message-digest/info-radar/opportunity-scout→daily）、daily 路由去 inbox-cleanup、review/english 关联去 notecraft；INDEX 已废弃表补 inbox-cleanup/notecraft 两行、message-digest 等路径 inbox/→daily/；notes YAML 补 sub_skill；重跑 compile.py 并清 dist 死文件（inbox-cleanup/inbox-file-cleanup/inbox/research 4 个 .md）。终态：全树 **23 个技能、0 非标准 frontmatter 字段、0 反斜杠**。
- **2026-08-18**：登记 Resonote 为正式项目（用户决策：Mac 真代码迁 Windows `D:\Cloud\Projects\Resonote`、Mac 不再保留本地副本，仅持看板）。新增 `Vault/projects/Resonote/`（plan.md + progress.md），`cloud` 字段用相对名 `Resonote`（遵循 7-09 分层模型：设备事实走 `CLOUD_PROJECTS` 环境变量、不写死盘符）；`verifier --fix-projects` 刷新 INDEX（13→14 项目）；同步 AGENTS.md §1 projects 列表（13→14，含 Resonote）。结构变更经 verifier 全绿（0 BLOCKER/0 WARN）。
- **2026-10-04**：更名为 Poyi + 全仓去真实化（定位转向"可迁移到各主流 Agent 工具的记忆插件"）。① 产品名 Mind→Poyi 全仓替换：技能 `mind`→`poyi`（口令只留 `/poyi`，不留别名）、`zju`→`campus`、`Vault/projects/Mind`→`Poyi`、`<MIND_ROOT>`→`<POYI_ROOT>`、脚本变量与 `wiki` 页面名同步；历史审计报告（`Loom/meta/archive/**`）按用户"全部改"的口径一并改名，不再存真保留旧名。② 删除 `Loom/scripts/mind_daemon.py` / `mind_watchdog.py`（Win-only 死代码，无触发器）。③ 去真实化：`Vault/` 153 个 .md 正文换成虚构示例人设（`make_sample_vault.py`，保留目录/文件名/frontmatter 结构字段）；`Loom/skills/profile/SKILL.md` 整份重写为示例画像；真实群号×16、wxid、钉钉 UID、辅导员实名、班级号、宿舍、籍贯、GPA、校名/院名/品牌/账号名全部替换为示例值，真实映射迁至不入库的 `daily/data/identity.local.json`；`computer-map*.json` 换成虚构设备映射（`make_sample_computer_map.py`）。④ 数据边界收紧：`Loom/raw/`（111 个真实对话摘要，24.7MB）与 `Loom/meta/inventory.json`（无生成器的全文快照）移出 git 跟踪并加 ignore —— 原「Mac push digested → Win 消化」链路改走云盘。⑤ 修 bug：`setup_retrieve.py` 读 BOM JSON 崩溃（改 utf-8-sig）、`.githooks/pre-commit|pre-push` 调 `python3` 在 Windows 撞商店假别名且 emoji 输出被 GBK 崩退（改解释器探测 + `PYTHONIOENCODING=utf-8`）、`dist/README.md` 手写清单残留旧产物行（改磁盘实测生成）。⑥ 生成物全部重建（INDEX / dist / bm25 / 项目 INDEX），verifier **0 BLOCKER / 0 WARN**；新增 `sanitize_repo.py` 供后续脱敏复用。
