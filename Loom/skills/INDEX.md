---
INDEX_version: 4.0.0
last_updated: 2026-10-04
owner: sample-user
total_skills: 22
---

# Loom/skills/ 总索引

> **22 个活跃 skill（animation raw-arsenal 已移入 `_archive/`，不再计入），命名简洁（≤1 词），全部走 kebab-case。本文件由 `manage_skills.py sync` 从磁盘重建，单一事实源 = 文件系统。**

---

## 技能清单

> 全部技能按官方 Agent Skills 标准编写（name + description 必填，路由靠语义匹配，无角色分类）。

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

> 注：`animation` 为原武器库（raw-arsenal），暂不计入活跃技能数。

---

## YAML 视图（机读）

```yaml
skills:
  - name: autoresearch
    description: "自主研究循环：接收一个主题，执行迭代网页搜索与抓取，合成发现并全部归档到 wiki（concepts/entities/sources + 综合页 Research: Topic）。基于 Karpathy autoresearch，最大 3 轮，带 web 安全卫生与成本预算。 触发词：自主研究、调研、research、深度研究、查资料。"
    location: Loom/skills/autoresearch/SKILL.md
    status: active
    triggers: [auto, 自动研究]
    depends_on: [poyi, ingest]
  - name: campus
    description: "Beiyu 校园事务自动化脚本集：自动签到、作业待办、校园课堂语音转 Markdown、图书馆查询。位于 D://Tools//Scripts//Beiyu-live-better//。 触发词：北屿大学、Beiyu、校园事务、签到、校园课堂。"
    location: Loom/skills/campus/SKILL.md
    status: active
  - name: canvas
    description: "Loom 知识图谱可视化引擎：将 wiki 知识图谱转为 Obsidian Canvas（JSON Canvas 1.0 规范），按 type 颜色分组、自动网格布局生成 .canvas 文件。Canvas 是 wiki 的只读视觉投影，支持 /canvas、/canvas <topic>、/canvas full 及 add image/note/text 子命令。 触发词：canvas、知识图谱、图谱、可视化。"
    location: Loom/skills/canvas/SKILL.md
    status: active
    triggers: [canvas, 画布]
    depends_on: [poyi]
  - name: daily
    description: "消息中枢：聚合消息扫描、热点雷达、机会挖掘三个子模块。加载本 skill 后，Agent 按用户意图路由到对应子模块。触发词：'待办'、'热点'、'机会'、'今日要做'、'今天有什么活动'。"
    location: Loom/skills/daily/SKILL.md
    status: active
  - name: defuddle
    description: "网页清洗器：剥除广告/导航/页脚/社交按钮，输出纯净 Markdown，节省 40-60% token。基于 kepano/defuddle-cli。触发词：defuddle、清洗网页、剥广告、clean url"
    location: Loom/skills/defuddle/SKILL.md
    status: active
    triggers: [defuddle, 清洗, 链接清洗]
  - name: english
    description: "英语学习增强器：用户问英语表达时，先检索 Vault 知识库锚点（AI/数学/物理/计算机/工程笔记）用已知概念类比解释，再记录学习痕迹到 Loom/wiki/english-data/，并同步语料本到 Vault。会话中自然穿插复用已学表达。 触发词：英语、英语表达、英文怎么说、English。"
    location: Loom/skills/english/SKILL.md
    status: active
    triggers: [英语表达, 翻译, 英语学习, 这个用英语怎么说, 英文怎么说]
    depends_on: [filesystem]
  - name: exam
    description: "从微信公众号收集历年试卷，OCR 提取题目，AI 自行解答，生成统一排版的 LaTeX PDF 文档。触发词：'收集试卷'、'历年卷'、'OCR 试卷'。"
    location: Loom/skills/exam/SKILL.md
    status: active
    triggers: [收集试卷, 历年卷, OCR 试卷]
    depends_on: [filesystem]
  - name: filesystem
    description: "跨平台文件系统规则：约束 Agent 在所有文件操作中的路径、命名、目录结构行为。平台检测 + 决策树 + 自查机制。触发词：'放哪里'、'命名'、'装依赖'、'文件结构'、'系统盘满了'。"
    location: Loom/skills/filesystem/SKILL.md
    status: active
    triggers: [放哪里, 命名, 目录结构, 找位置, 在哪, C盘, 清理]
  - name: ingest
    description: "知识入库器：把外部源（文件/URL/图片）与正在进行的对话都写入 wiki 并交叉引用一切。源吞入支持 Delta 去重、矛盾检测、批量；会话捕获支持五型分类（synthesis/concept/source/decision/session）与保存 vs 跳过判断。所有写入用 Obsidian Flavored Markdown。触发词：ingest、吞入、处理文件/网页/PDF、归档进知识库、整理聊天记录进知识库、对话归档、保存对话、存这次讨论、save。"
    location: Loom/skills/ingest/SKILL.md
    status: active
    triggers: [ingest, 吞入, 处理这篇, 吞这个]
    depends_on: [poyi]
  - name: lint
    description: "Wiki 健康检查：每 10-15 次 ingest 或每周运行，执行 10 项检查（孤立页、死链、过期主张、缺失页、frontmatter 缺口、命名违规、写作风格等）。输出 lint-report，自动修复前先询问；附 Dataview 仪表盘与 Canvas 地图。 触发词：lint、wiki体检、死链检查、知识库健康。"
    location: Loom/skills/lint/SKILL.md
    status: active
    triggers: [lint, 健康检查, 清理 wiki, wiki 质量]
    depends_on: [poyi]
  - name: notes
    description: "批量整理课程笔记：扫描目录 → 去重 → 风格审查 → 逐章重写/扩充 → 更新索引。Designed for the dual-track note workflow (STYLE.md + WORKFLOW.md)。触发词：'整理笔记'、'统一笔记风格'、'规范化笔记'。"
    location: Loom/skills/notes/SKILL.md
    status: active
    triggers: [整理笔记, 统一笔记风格, 规范化笔记]
    depends_on: [filesystem]
  - name: papers
    description: "科研文件管理 Skill。统一 Research/ 下所有课题的文件结构、命名、引用规范。原 research-workflow + papers/projects/SRTP.md 已整合。触发词：'文献'、'论文'、'SRTP'、'科研'、'写论文'、'投稿'。"
    location: Loom/skills/papers/SKILL.md
    status: active
    triggers: [文献, 论文, SRTP, 科研, 写论文]
    depends_on: [filesystem]
  - name: poyi
    description: "Poyi 系统全局洗脑与接管协议入口。Agent 收到此技能后，必须读取 <POYI_ROOT>/AGENTS.md 并切入知识库维护角色。触发词：/poyi、Poyi系统、知识库。"
    location: Loom/skills/poyi/SKILL.md
    status: active
    triggers: [wiki, 知识库, scaffold, 搭 wiki, 初始化 wiki]
  - name: profile
    description: "统一的用户画像 skill。daily 三模块（digest/radar/scout）共享的用户画像，作为唯一权威来源。被 daily 等 skill 引用，避免重复维护。 触发词：用户画像、我的偏好、profile、我是谁。"
    location: Loom/skills/profile/SKILL.md
    status: active
    triggers: [修改用户信息, 加群, 改组织]
  - name: project
    description: "全周期项目生命周期管理：从创建脚手架到规划、进度追踪、状态流转（open/close/pause/block/archive）一站式覆盖。根据项目类型（engineering/research/coursework/content/experimental/document）选择模板并强制双根两层结构。触发词：'建项目'、'新建'、'开始做XX'、'项目状态'、'更新进度'、'开启/关闭/暂停/归档项目'、'/project'。"
    location: Loom/skills/project/SKILL.md
    status: active
    triggers: [建项目, 新建, 开始做XX, 项目状态, 更新进度, 归档项目, /project]
    depends_on: [filesystem]
  - name: query
    description: "Wiki 查询引擎：策略性读取、精准回答、主动归档让知识复利。三层查询（Quick/Standard/Deep）按复杂度匹配深度；优先 hot.md→index→页面，附 wikilink 引用，好答案归档回 wiki。 触发词：wiki查询、查wiki、query。"
    location: Loom/skills/query/SKILL.md
    status: active
    triggers: [wiki 查询, 搜索知识库, wiki 里有没有]
    depends_on: [poyi]
  - name: review
    description: "学科主动复习系统：基于骨架笔记自测驱动，加权随机选题（不会>模糊>未测>熟），记录掌握度到 mastery.json。支持刷题/费曼输出/概念图模式。产物全在 Loom 侧，不污染 Vault。 触发词：复习、刷题、自测、掌握度、review。"
    location: Loom/skills/review/SKILL.md
    status: active
    triggers: [复习, 自测, 刷题, 掌握度, 费曼, 抽题]
    depends_on: [poyi]
  - name: save
    description: "对话归档到 Wiki：取刚讨论的内容归档为永久 wiki 页面（synthesis/concept/source/decision/session 五型）。Wiki 复利——经常 save。含目标根目录决策、frontmatter 模板、保存 vs 跳过标准。"
    location: Loom/skills/save/SKILL.md
    status: active
  - name: think
    description: "10 原则思考框架（OBSERVE-外 / OBSERVE-内 / LISTEN / THINK / CONNECT-横 / CONNECT-系 / FEEL / ACCEPT / CREATE / GROW）：用于架构决策、复盘、模糊请求、多利益方权衡。元技能，告知其他技能如何思考。 触发词：思考框架、架构决策、复盘、think、权衡。"
    location: Loom/skills/think/SKILL.md
    status: active
    triggers: [/think, 深度思考, 帮我分析, 权衡]
  - name: triage
    description: "通用文件分拣引擎：将任意目录的散落文件按 filesystem 决策树与 profile 上下文自动归类到目标路径。当用户要求整理 Inbox / Downloads、分拣或归类文件，或提供目录路径时触发。 触发词：整理文件、分拣、归类、清理目录、triage。"
    location: Loom/skills/triage/SKILL.md
    status: active
  - name: wiki-mode
    description: "Loom 方法论模式切换器：管理 wiki 底层目录拓扑，支持 generic/lyt/para/zettelkasten 四种组织方法论。切换模式只影响未来写入（不迁移已有文件），路由规则存于 Loom/.vault-meta/mode.json。 触发词：wiki模式、方法论切换、zettelkasten、para。"
    location: Loom/skills/wiki-mode/SKILL.md
    status: active
    triggers: [wiki mode, wiki 模式]
    depends_on: [poyi]
  - name: wiki-retrieve
    description: "Loom 混合语义检索引擎：当 query 的确定性路径（hot→index→pages）不够时，用 BM25 稀疏检索 + 可选上下文前缀 + 可选稠密重排三层管线，从 wiki 召回最相关页面与段落。query 优先，retrieve 兜底。 触发词：语义检索、检索wiki、retrieve、搜知识库。"
    location: Loom/skills/wiki-retrieve/SKILL.md
    status: active
    triggers: [wiki 检索, 知识检索]
    depends_on: [poyi]
```

---

## 编排依赖

各 skill 的 `depends_on` 见下方 YAML 视图。主要编排关系：

- **poyi** 路由：ingest, query, lint, wiki-retrieve, canvas, wiki-mode, think, autoresearch, defuddle
- **daily** 整合三模块（digest / radar / scout）：profile, project, campus, triage
- **review / english** 关联：notes, exam
- **filesystem** 强校验支撑：papers, notes

---

## 命名规则（2026-06-13 生效）

- ✅ 一个词最佳（如 `profile` `exam` `notes` `campus`）
- ✅ 必须多词时用 kebab-case（如 `project` 实际是 1 词）
- ❌ 禁下划线 `_`
- ❌ 禁中英混杂
- ❌ 禁超过两个词

如未来出现"笔记"领域第二个 skill，按 `note-organizer` 风格命名（参考用户 2026-06-13 反馈）。

---

## 已废弃的 Skill（保留追溯）

| 原名 | 迁移到 | 状态 |
|---|---|---|
| message-digest | daily/modules/digest.md | 合并 |
| info-radar | daily/modules/radar.md | 合并 |
| opportunity-scout | daily/modules/scout.md | 合并 |
| inbox-cleanup | triage/references/inbox-rules.md | 合并 |
| notecraft | notes/ (STYLE.md + WORKFLOW.md + README.md + skills/note-merge) | 合并 |
| research-workflow | papers/SKILL.md | 合并 |
| SRTP-research-rules | papers/projects/SRTP.md | 合并 |
| filesystem | filesystem/SKILL.md | 合并 |
| filesystem | filesystem/SKILL.md | 合并 |
| project | project/SKILL.md | 改名 |
| profile | profile/SKILL.md | 改名 |
| inbox | inbox/SKILL.md | 改名 |
| papers | papers/SKILL.md | 改名 |
| notes | notes/SKILL.md | 改名 |
| exam | exam/SKILL.md | 改名 |
| campus | campus/SKILL.md | 改名 |

---

## 更新日志

### 2026-07-19 (v3.5.0) — newproject v2.0.0 文档三件套

- **newproject** 从 v1.2.0 升级到 v2.0.0，内置项目文档三件套格式规范（§7）
- 新增 plan.md（六区块：目标/路线/里程碑/约束与风险）
- 新增 progress.md（Obsidian 复选框 + changelog 标题风格，四状态分类）

### 2026-08-22 (v3.6.0) — newproject 更名为 project（全周期扩展）

- 技能由 `newproject` 更名为 `project`（目录 `Loom/skills/newproject/` → `Loom/skills/project/`，dist 同步 `newproject.md` → `project.md`）
- 职责由「脚手架」扩展为「全周期」：`new`(建双根两层+注册) / `plan`(深化蓝图) / `status`(只读速报) / `update`(追加进度) / `open`·`close`·`pause`·`block`·`archive`(状态流转，archive 不移动目录)
- 全局引用一致性更新：AGENTS §2、本 INDEX、filesystem 路由、各 skill eval.md、`skill-standard.md`；历史变更日志与审计日志保留旧名 `newproject` 以存真
- 新增 research.md（日期倒序 + [AI调研]/[灵感] 来源标注）
- 新增项目类型差异化规则（科研/工程/产品/创作/系统/实验）
- 新增 §8 handoff 模板，用于文档填充任务转交
- 格式源于 2026-07-19 会话中用户与 Agent 的共同设计

### 2026-06-30 (v3.4.0) — 全物理盘点补全

- 补全 3 个缺失 skill 到索引：**inbox-cleanup** / **notecraft** / **animation**
- 表格视图：用户技能 12 → 13（animation 标为 raw-arsenal 不计数）
- YAML 视图：新增 inbox-cleanup / notecraft / animation 三个条目
- 修正：english YAML `knowledge_domains` 路径改为平台中立（`<POYI_ROOT>/Vault/notes/`）
- 修正：filesystem YAML 移除已删除的 `sync-strategy.md` 引用
- 修正：正文 "16 个 skill" → "23 个 skill（含 1 个 raw-arsenal）"
- Wiki 核心技能编号更新 11-20 → 14-23
- 依赖关系图补充 3 个新技能

### 2026-06-27 (v3.2.0) — 新增 review 技能

- 新增 **review** 技能：学科主动复习系统
- 自测驱动 + 间隔重复 + 加权选题（不会 5× > 模糊 3× > 熟 1×）
- 三种模式：标准复习 / 刷题模式 / 费曼输出 / 概念图
- 所有产物落盘 Loom/wiki/review/，不污染 Vault
- 大学物理 mastery.json 已初始化（8 章，全部未测）

### 2026-06-27 (v3.1.0) — Obsidian 特性补全

- 7 个 wiki 核心技能逐行对比 claude-obsidian 源码后补全 Obsidian 相关特性：
  - **poyi**: +Obsidian 语法标准、`.raw/` 隐藏机制、modes 决策表、`_templates/` 生成、`.obsidian/snippets/vault-colors.css`、vault CLAUDE.md 模板、git 初始化
  - **ingest**: +Obsidian 语法标准、`defuddle` URL 清洗、图片附件路径修正（`_attachments/images/`）、manifest 路径修正（`.raw/`）、contradiction callout 依赖说明、source frontmatter schema
  - **lint**: +过期 index 条目检查（第 8 项）、命名规范检查（第 9 项）、写作风格检查（第 10 项）、Dataview 仪表盘、Canvas 地图、自动修复前置确认
  - **save**: +目标根目录决策（Step 0）
  - **query**: 格式完善
  - **research**: 结构完善
  - **think**: 已完整
- 故意跳过：DragonScale（opt-in/bash 依赖）、Transport（Claude Code 层）、Mode awareness（固定 D+E）、Community footer（商业推广）

### 2026-06-26 (v2.2.0) — 新增 english 技能

- 新增 **english** 技能：英语学习增强体系
- 核心机制：知识锚点类比法 —— 用 Vault 中已有学科笔记（AI/数学/物理/计算机/工程）类比解释新英语表达
- 四阶段工作流：理解问题 → 检索知识库锚点 → 生成关联解释 → 记录学习痕迹
- 学习痕迹写入 Vault/notes/语言 Language/natural language/English/（expressions/ tech-english/ grammar/ daily-notes/）
- 触发词：英语表达、翻译、英语学习、这个用英语怎么说
- 依赖 filesystem + Vault 6 个知识域

### 2026-06-13 (v2.1.0) — filesystem references 完善

- filesystem YAML 条目新增 `references:` 字段，列出全部 8 个 references
- 修正 `old_names:` 从占位符 → `[cloud-file-orchestrator, host-context]` 真实历史
- 触发关键词扩充：补 C盘/清理
- INDEX_version: 2.0.0 → 2.1.0

### 2026-06-13 (v2.0.0) — 大重构

- 合并 filesystem + filesystem → **filesystem**
- 改名 6 个 skill 到单词名：profile / inbox / papers / notes / exam / campus
- newproject 保持单次但改名（去 -scaffolder 后缀）
- skill 总数：13 → **8**（净减 38%）
- 所有 skill 全部 ≤ 10 字符

### 2026-06-13 (v1.0.0) — 初版

- 创建本 INDEX.md
- 合并 message-digest + info-radar + opportunity-scout → inbox + profile
- 合并 research-workflow + SRTP-research-rules → papers
- 新建 filesystem + newproject
- 统一所有 skill 为目录形态
- 重命名 exam（中文文件名 → 英文目录）

---

## 维护规则

- 修改任何 skill 后，**必须更新本 INDEX**（last_updated + YAML）
- 新建 skill：先在本文件加 YAML 块，再创建 skill 目录
- 删除 skill：把 YAML 块移到「已废弃」表
- 重命名 skill：同步修改本文件 + 所有引用该 skill 的地方
- 命名必须 ≤ 1 词，必要时 ≤ 2 词（参考用户 2026-06-13 反馈）