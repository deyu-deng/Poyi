<!-- source: filesystem -->
---
name: filesystem
description: "跨平台文件系统规则：约束 Agent 在所有文件操作中的路径、命名、目录结构行为。平台检测 + 决策树 + 自查机制。触发词：'放哪里'、'命名'、'装依赖'、'文件结构'、'系统盘满了'。"
metadata: {"version": "1.1.0", "owner": "sample-user", "last_validated": "2026-08-23", "deps": []}
---
# Filesystem — 跨平台文件系统 skill

> **本 skill 是整台电脑文件操作的唯一入口。Agent 加载后必须输出「✓ 已加载 filesystem」并执行 §3 决策树。**
> **本 skill 由 cloud-file-orchestrator + host-context 合并而来（2026-06-13），v3.0.0 整合 mac-filesystem-hygiene 实现跨平台（2026-06-27）。**

---

## 0. 平台检测（Agent 加载后必须执行）

Agent 加载本 skill 后，**第一步**检测当前操作系统：

```
1. 执行 uname -s（或等效命令）获取系统类型
2. 根据结果加载对应平台文件：
   ├── Darwin  → references/platforms/macos.md (见附录 references/platforms/macos.md)
   ├── Linux   → references/platforms/linux.md（如存在）
   ├── MINGW* / MSYS* / CYGWIN* → references/platforms/windows.md (见附录 references/platforms/windows.md)
   └── 其他   → 默认加载 references/platforms/windows.md (见附录 references/platforms/windows.md)，并告知用户平台未知
3. 后续所有路径决策以平台文件中的期望结构为准
4. **静默漂移自检（A 方案）**：若 `scripts/drift-check.py` 存在，执行 `python scripts/drift-check.py --quiet`；退出码 0 则继续，非 0 则把输出的差异报告展示给用户，询问是否更新 windows.md / generate-map.py（详见 `references/self-update.md (见附录 references/self-update.md)`）
```

**平台文件内容**：
- 系统级文件夹（不可移动，Agent 只读）
- 自定义根目录（期望结构 + 子目录规范）
- 发现规则（期望缺失 / 新增未识别 / 名称不一致的处理方式）
- 系统盘审计规则（如有）

---

## 0. 自更新机制

详见 `references/self-update.md (见附录 references/self-update.md)`。摘要：

| 触发条件 | 动作 |
|---|---|
| Agent 执行平台扫描时发现新目录（连续 ≥2 次出现） | 记录观察，累计后提示 |
| 用户说「把这个放到 XX/」而 XX 不在期望结构中 | 立即标记差异 |
| 用户显式说「目录结构变了」「我改了文件结构」「更新文件结构」 | 执行完整自更新流程 |

**执行流程**：扫描实际文件系统 → 与 platforms/ 期望结构对比 → 生成差异报告 → 询问用户是否更新 → 用户确认后更新平台文件。

---

## 1. 关键陷阱 — 不要重蹈本 skill 自身的诞生之错

本 skill 在 2026-06-13 经历了三次自我修正才定型，后续又多次踩坑。这些陷阱是**通用教训**，跨平台有效。

### 陷阱 1.1：扫描全盘前不要假设工作区

- ❌ 早期版本叫 `cloud-file-orchestrator`，把某个子目录当成"用户电脑"
- 真相：用户通常有多个顶层目录各有职责，不能从单个目录名推断全局
- **规则**：处理任何"电脑文件结构"类任务，**第一步必须扫描顶层全局**（`ls ~/` 或平台根目录），不要从用户提到的某个目录名推断整个心智模型

### 陷阱 1.2：命名不要凭程序员审美

- ❌ 差名字示例：`cloudfile`、`papers`、`notes`、`exam`、`profile`、`scaffold`、`host`、`sign`
- ✅ 用户最终拍板的名字反映**真实用途**：filesystem / project / papers / notes / daily / exam / profile / campus
- **规则**：建/改 skill 名前，**必须问用户**。给候选时至少给 3 个，每个带语义解释
- **强化**：用户明确"一个词最佳，最多两个词"，**严格 ≤ 2 词**

### 陷阱 1.3：批量字符串替换会在语义位置破坏原文

- 用 `replace_all` 批量替换时，会破坏 `supersedes:` 字段、章节标题、历史段落
- **规则**：批量改名时**先列受影响行**，确认替换语义安全后**逐个 patch**，不要盲目 replace_all

### 陷阱 1.4：合并前确认职责真正重叠

- 合并两个 skill 前，**先写出合并后的统一心智模型**（一句话：这个 skill 帮 Agent 做什么？），名字从心智模型推导
- **不要先起名再合并**

### 陷阱 1.5：系统盘 vs 数据盘职责不要混淆

- **数据盘/用户目录**：用户主动管理的资产（项目、笔记、研究、收藏）
- **系统盘/系统分区**：被动产生的数据（软件缓存、聊天数据库、云盘临时文件、卸载残留）+ 必须保留的系统区
- **规则**：听到用户说"X 在哪"，**先判断在哪个区域**，不要默认某个分区

### 陷阱 1.6：已装软件 vs 安装包收藏不要混淆

| 类型 | 角色 |
|---|---|
| 已装软件目录 | 注册表/配置依赖，不能动 |
| 安装包收藏目录 | 可自由移动和整理 |

- **规则**：看到 `software` 字样，**先确认是已装软件还是安装包收藏**

### 陷阱 1.7：scan → ask → propose → preview → wait 五步不可压缩

- 任何文件审计任务必须先 SCAN → 报告 → 等指令
- **不要用"病毒"等强情绪词吓用户**：先 ls 内容、查文件大小、看时间戳，冷静分析
- 详细工作流见 `references/workflow.md (见附录 references/workflow.md)`

### 陷阱 1.8：Desktop 隐藏空间挖掘

- 系统盘满了，先扫 Desktop/ —— 经常有 GB 级的卸载备份残留
- **规则**：系统盘告急，先 `du -sh` Desktop/—— 大概率找到大头

### 陷阱 1.9：子目录命名不要和顶层同名

- 如果顶层已有 `Software/`、`Tools/`、`Inbox/` 等，子目录避免重名
- **规则**：建新目录前，先检查是否有同名顶层目录

### 陷阱 1.10：用户说"以后我自己处理"立即停止

- 用户多次说"我自己来" → Agent 必须立即停止追问
- 写入 memory 和本 skill，下次遇到同类话题不要主动提

### 陷阱 1.11：看到可疑目录名不要立刻判定中毒

- 用户报"某个目录的 uninstall 卸了 XX"，可能只是 PUA bug 或正常组件
- **规则**：先 ls 看内容，不要恐慌。0 字节日志文件不是证据

### 陷阱 1.12：杀进程/重启服务/强制结束任务前必须问

**惨痛教训**：Agent 为删除目录执行了 `Stop-Process -Force`，未确认就杀掉用户正在使用的进程。

**规则**：
- ❌ **永远不要** `Stop-Process -Force` / `taskkill /F` / `pkill -9` 等不可逆操作
- ✅ **必须先列出**要杀的进程（PID + 名字 + 路径）
- ✅ **问用户**确认后才执行
- **唯一例外**：用户明确说"重启 X 服务""杀 X 进程"——可以直接做

### 陷阱 1.13：评估一个本地工具"能不能用"——先 ls + cat 主文档/源码

**规则（强制 3 步）**：
1. **`ls` 工具根目录**——看 README / 入口 / 配置文件
2. **`cat` 主文档**（README.md / 使用手册）
3. **`cat` 关键源码入口**——只看签名和注释行
- ❌ 不要凭文件大小判断实现完整度
- ❌ 不要凭"没看到 README"宣布跑不通

### 陷阱 1.14：用户说"我们的 skill 库 / 工具库"时不要跨系统模式匹配

- 听到"skill 库" → 先确认指哪个库（私有策划库 vs 运行时库），**不要默认**
- 两个系统的目标、规模、规范完全不同
- **规则（强制 4 步）**：`ls` 顶层 → 读既定的索引/规范文件 → 看条目数量和格式 → 拿不准就问

---

## 2. 命名规则（强制 — 跨平台通用）

**用户偏好（强）**：**一个词最佳**。必须多词时用 kebab-case，**严格 ≤ 2 词**。

| 规则 | 说明 | 反例 |
|---|---|---|
| **禁下划线 `_`** | 命名中绝不出现下划线作为分隔符 | `my_file`, `extract_outline.py` ❌ |
| **一个词优先（强偏好）** | 单个英文单词能表达就用单词 | `homework`, `notes`, `slides` ✅ |
| **多词用 kebab-case** | 必须多词时用连字符 `-` 连接 | `course-work`, `prism-bridge` ✅ |
| **严格 ≤ 2 词** | 超过 2 词视为违规 | `cloud-file-orchestrator` ❌（3 词）|
| **禁中英混杂** | 一个名字要么全英文要么全中文 | `my-笔记`, `笔记-file` ❌ |
| **能用英文就用英文** | 默认英文命名（便于命令行） | `homework` 优于 `作业` |
| **必须中文时用中文** | 课程专有名词、人名除外 | `习概`, `马原资料` ✅ |
| **项目编号** | `Projects/{NN-Name}/` 两位数 + 连字符 | `01-Prism`, `06-Website` ✅ |
| **课程命名** | `Courses/{YYYY学期-课程名}/` | `2025秋冬-线性代数` ✅ |
| **事件命名** | `Events/{YYYYMMDD-事件名}/` | `20260510-北屿大学AI全栈极速黑客松` ✅ |
| **文件命名** | 单个英文描述性单词 或 kebab-case | `proposal.md`, `index.html` ✅ |
| **日期前缀** | 需要时间标识时 `YYYY-MM-DD_` | `2026-06-10-期中笔记.md` ✅ |
| **第三方不动** | npm / 框架 / 学术惯例文件名不强制 | `package.json`, `index.html` 不动 |
| **不管理用户主动维护目录** | 用户明确说"不要管"的目录，Agent 不主动清理 | "你不要管了" → 立即停止追问 |

---

## 3. 决策树（Agent 加载后必须执行）

### 3.1 "我要新建/保存 X 到哪里？"

> **以下路径为通用模板，具体路径以当前平台文件为准。**

```
X 是什么类型？
├── Office 文档 (.docx/.pptx/.xlsx)
│   ├── 课程相关？→ Courses/{学期-课名}/Homework 或 Notes
│   ├── 项目相关？→ Projects/{项目}/Docs/
│   ├── 科研相关？→ Research/{课题}/Docs/
│   ├── 媒体相关？→ Media/{分类}/...
│   └── 其他？→ ❓ 问用户
├── 学术文献 PDF
│   ├── 英文学术论文 → Research/{课题}/Lit/Papers/English/
│   ├── 中文学术论文 → Research/{课题}/Lit/Papers/Chinese/
│   └── 专利         → Research/{课题}/Lit/Patents/
├── 代码文件 (.ts/.py/.js/.tsx)
│   ├── 属于哪个项目？→ Projects/{项目}/Code/{包名}/
│   ├── Sandbox 实验？→ Projects/Sandbox/{类型}/{实验名}/Code/
│   └── 新建项目？→ §3.2（调用 project skill）
├── 媒体文件 (.mp4/.mp3/.jpg/.png)
│   ├── 创作内容？→ Movies/ / Music/ / Pictures/（系统文件夹，见平台文件）
│   ├── 课程录像？→ Courses/{学期-课名}/Slides/
│   └── 项目截图？→ Projects/{项目}/Photos/
├── Markdown 笔记 (.md)
│   ├── 课程笔记？→ Vault/{学科}/...
│   ├── 通用知识？→ Vault/...
│   ├── 项目进展？→ Projects/{项目}/Docs/CHANGELOG.md
│   └── 日记？      → Vault/journal/{星期, 月 日, 年}.md
├── 安装包 (.dmg/.exe/.msi)
│   ├── 临时？→ Downloads/ 根（装完后清空）
│   └── 长期收藏？→ Library/{category}/（见平台文件）
├── 凭证 (身份证/合同)
│   └── Archive/Credentials/{ID|Party}/...
├── 配置/缓存（软件运行时）
│   └── Data/{AppData|Cache|Config}/...
├── 工具脚本
│   └── Tools/Scripts/{你的脚本}/
├── 其他 / 不确定
│   └── ❓ 问用户
```

### 3.2 "我要新建一个项目？"

**调用 `project` skill**。

### 3.3 "我要 npm install 吗？"

```
当前任务在哪个目录？
├── Projects/{项目}/Code/{包名}/     → ✅ 可以装，先 ls ../ 看是否有现成工程可复用
├── Projects/Sandbox/{实验}/Code/    → ✅ 可以装，提示"实验性，30 天后将清理"
├── 其他位置                          → ❌ 禁止：先创建正确目录
└── 检测到上层已存在 package.json？
    ├── 同名工程 → 复用，禁止新建
    ├── 不同名工程但有 pnpm-workspace.yaml → 允许（monorepo）
    └── 不同名工程无 monorepo 配置 → 禁止嵌套
```

### 3.4 "我要找一个东西在哪？"

```
1. 先查平台的 computer-map.json 或结构描述文件
2. 找不到 → 用终端实时 ls 查
3. 仍找不到 → ❓ 问用户
```

---

## 4. 项目根目录结构（按项目类型）

> **以下路径为通用模板，具体根路径以当前平台文件为准。**

### 4.1 工程项目（Projects/{NN-Name}/）

```
Projects/{NN-Name}/
├── Code/                    ← 强制：所有源代码
│   └── {包名}/              ← 唯一 npm 工程根（kebab-case）
├── Design/                  ← 强制：所有设计稿
├── Docs/                    ← 强制：README.md, PROPOSAL.md 等
├── Photos/                  ← 可选：项目相关照片
├── Data/                    ← 可选：实验数据、原始素材
└── Drafts/                  ← 可选：中间产物
```

### 4.2 科研课题（Research/{NN-主题}/）

```
Research/{NN-主题}/
├── Lit/
│   ├── Papers/{English,Chinese}/
│   ├── Patents/
│   ├── 文献汇总表.xlsx
│   └── publication.bib
├── Notes/
├── Code/
├── Data/
├── Docs/
└── Drafts/
```

详细见 `papers` skill。

### 4.3 课程作业（Courses/{学期-课程名}/）

```
Courses/{学期-课程名}/
├── Syllabus/                ← 教学大纲
├── Slides/                  ← 课件
├── Textbook/                ← 教材
├── Homework/{编号-作业名}/  ← 每份大作业独立子目录
├── References/              ← 拓展资料
├── Notes/                   ← 个人笔记
└── Exams/                   ← 历年卷（可选）
```

### 4.4 实验项目（Projects/Sandbox/{类型}/{名称}/）

```
Projects/Sandbox/{类型}/{名称}/
├── Code/
├── Data/
├── Notes.md
└── README.md
```

**Sandbox 类型**：Code / Design / AI / Music / Hardware

**重要**：`Projects/Sandbox/` 是用户主动维护的素材池，**Agent 不主动清理空目录**。

### 4.5 Archive/Organizations/ — 组织文档

```
Archive/Organizations/
├── {组织名}/                ← 按组织名建子目录
│   └── {文档}.pdf
```

**规则**：按"组织名"建子目录，归档**该组织相关的所有重要文档**（PDF、协议、活动资料等）。

---

## 5. 自动化检查

### 5.1 项目脚手架检查

Agent 收到"创建项目 X"指令时，**必须调用 `project` skill**（不要在本 skill 内 mkdir）。

### 5.2 命名合规检查

Agent 写新文件前必须检查文件名是否违反 §2。违反时**禁止写入**，要求用户重命名或自动 rename。

**自动 rename 规则**：
- 下划线 → 连字符：`my_file.md` → `my-file.md`
- 含空格 → 连字符：`my file.md` → `my-file.md`
- 中英混杂 → 询问用户

### 5.3 反复装依赖检测

每次 `npm install` / `pip install` 前：检查上级目录是否已有同名配置文件，避免重复安装。

---

## 6. 与其他 Skill 的协同

| 场景 | 调用 |
|---|---|
| 新建项目脚手架 | `project` skill |
| 科研文件操作 | `papers` skill |
| 笔记整理 | `notes` skill |
| 消息扫描 | `daily` skill |
| 试卷收集 | `exam` skill |
| 修改用户信息 | `profile` skill |
| Beiyu 校园自动化 | `campus` skill |
| **系统盘审计 / 清理** | **加载 `references/c-drive-audit.md (见附录 references/c-drive-audit.md)` + 平台文件的审计章节** |

---

## 7. 加载与触发

**触发关键词**：
- 「放哪里」、「命名」、「建项目」、「装依赖」
- 「找位置」、「在哪」、「文件结构」
- 「目录结构」、「文件路径」
- 用户提到具体路径
- **「系统盘满了」/「存储告急」/「扫一下系统盘」** → 加载平台文件的审计章节 + `references/c-drive-audit.md (见附录 references/c-drive-audit.md)`

**加载行为**：
1. 输出「✓ 已加载 filesystem」
2. 执行 §0 平台检测，加载对应平台文件
3. 列出本次任务相关的 §3 决策树分支
4. 等用户给出文件/项目信息
5. 按决策树执行，**不允许跳过**

---

## 8. 文件清单

```
filesystem/
├── SKILL.md                               ← 本文件
├── scripts/
│   └── generate-map.py                    ← 平台特定，重新生成目录结构地图
└── references/
    ├── platforms/
    │   ├── macos.md                       ← macOS 平台文件结构和发现规则
    │   └── windows.md                     ← Windows 平台文件结构和发现规则
    ├── self-update.md                     ← 自更新机制
    ├── workflow.md                        ← 5 步工作流（scan → ask → propose → preview → wait）
    ├── naming-workflow.md                 ← skill 命名流程 + 用户否决过的名字库
    ├── cleanup-recipes.md                 ← 14 个可复用 recipe
    ├── scan-rules.md                      ← Python iterdir 缓存 + bash 子 shell 陷阱
    ├── c-drive-audit.md                   ← 系统盘特化审计（"假病毒"识别 + 隐藏空间挖掘）
    ├── misc-conventions.md                ← 命名/位置/Sandbox 杂项
    └── cross-references.md                ← 跨 skill 引用清单
```

---

## 9. changelog

### 2026-08-23 v1.2.0

- **新增被动自更新双通道（A+B 方案）**：`scripts/drift-check.py` 结构漂移检测脚本（复用 generate-map.py DIRECTORY_NOTES 为期望源，扫描顶层+二层，报告缺失/新增）
- **A 方案**：SKILL.md §0 平台检测新增第 4 步「静默漂移自检」，Agent 加载 skill 时自动跑 `drift-check.py --quiet`，有差异才提示
- **B 方案**：每周日 09:00 定时任务自动巡检 drift-check，有差异才提醒用户
- **generate-map.py 清理**：移除 Software/iTunes、Software/KGMusic 等失效键，Tools/Media 对齐实际（ComfyUI）
- **self-update.md 重写**：新增 drift-check 说明，旧手动触发条件降级为兜底

### 2026-08-23 v1.1.0

- **目录结构对齐实际磁盘**：`references/platforms/windows.md (见附录 references/platforms/windows.md)` 更新 Development 为 Home/Toolchains/Virtualization、Data 为 AppData/Cache/Config、新增 Poyi 顶层（Loom skill 权威源 + Vault）
- **项目命名规则修正**：废弃 `Projects/{NN-Name}/` 编号制，改为无编号扁平 kebab-case
- **路径速查表全面刷新**：移除失效路径（D:\Data\Literature、D:\Data\Collaboration、D:\Development\AI、D:\Development\Runtimes 等），补充实际路径
- **computer-map.json 落点修正**：`D:\Cloud\Vault\Context` → `D:\Projects\Poyi\Vault\Context`，generate-map.py 输出路径同步
- **cross-references 死链清理**：inbox skill 已归档移除，相关引用标记为历史
- **generate-map.py 注释同步**：DIRECTORY_NOTES 更新 Development/Data/Poyi 新结构

### 2026-06-30 v3.2.0

- **新增 Development 子目录分类**：`references/platforms/windows.md (见附录 references/platforms/windows.md)` 增加 Runtimes/SDKs/AI/Libraries/Tools 五类及判定标准（跨项目共享 → Development，绑定项目 → 跟项目）

### 2026-06-30 v3.1.0

- **新增 `references/platforms/windows.md (见附录 references/platforms/windows.md)` §Agent 产出文件禁令**：Agent 产出严禁写入 C 盘
- **更新 `references/platforms/windows.md (见附录 references/platforms/windows.md)` 路径速查**：新增 npm 全局路径 `D:/Development/Runtimes/npm-global/`

### 2026-06-27 v3.0.0

- **跨平台重构**：整合 mac-filesystem-hygiene，实现 Win/Mac 统一心智模型
- **新增 §0 平台检测**：Agent 加载后自动根据 uname 加载对应平台文件
- **新增 §0 自更新机制**：触发条件 + 执行流程见 `references/self-update.md (见附录 references/self-update.md)`
- **新增 `references/platforms/macos.md (见附录 references/platforms/macos.md)`**：macOS 平台文件结构（已落地部分）
- **新增 `references/platforms/windows.md (见附录 references/platforms/windows.md)`**：Windows 平台文件结构（从原 SKILL.md 提取）
- **抽象化硬编码路径**：删除所有 `D:/` / `C:/` 硬编码，改为"当前系统对应路径"表述
- **`supersedes` 字段**：新增 `mac-filesystem-hygiene`
- **保留全部 14 个核心陷阱**：重编号为 1.1-1.14，语言抽象化以跨平台适用

### 2026-06-19 v2.3.0

- 新增陷阱 0.14：跨系统概念消歧

### 2026-06-15 v2.2.0

- 新增陷阱 0.12：杀进程前必须问
- 强化 §1 命名规则：严格 ≤ 2 词
- 新增 §4.4 Sandbox 不主动清理

### 2026-06-15 v2.1.0

- 新增 §9 C 盘审计章节 + references/c-drive-audit.md (见附录 references/c-drive-audit.md)

### 2026-06-15 v2.0.0

- 由 cloud-file-orchestrator + host-context 合并而来

---

*（本 skill 由 AI 基于合并需求 + 用户命名偏好 + 多次自我修正生成）*
*（内容由AI生成，仅供参考）*


---
## 附录: references/platforms/macos.md

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



---
## 附录: references/platforms/windows.md

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


---
## 附录: references/self-update.md

# 自更新机制

> 文件系统是动态的，用户随时可能新增/删除/重命名目录。本机制确保 platforms/ 下的期望结构保持与实际一致。
> **2026-08-23 升级（A+B 双被动方案）**：新增 `scripts/drift-check.py` 结构漂移检测，由「Agent 加载 skill 时静默自检」+「每周定时巡检」双通道触发，不再依赖用户主动开口。旧的手动触发条件保留为兜底。

---

## 触发条件

| # | 触发场景 | 说明 |
|---|---|---|
| 1 | **A 方案·skill 加载钩子** | Agent 每次加载 filesystem skill 时自动执行 `drift-check.py --quiet`，退出码非 0 才展示差异报告（见 SKILL.md §0 第 4 步） |
| 2 | **B 方案·每周定时巡检** | 每周定时任务自动跑 `drift-check.py`，有差异才提醒用户确认更新 |
| 3 | Agent 执行 `ls` 扫描时发现新目录，**连续 ≥2 次**出现 | 兜底：避免临时目录误触发 |
| 4 | 用户说「把这个放到 XX/」而 XX 不在期望结构中 | 用户的实际使用习惯已超出规范 |
| 5 | 用户显式说「目录结构变了」「我改了文件结构」「更新文件结构」 | 用户主动告知变更 |

---

## drift-check.py 快速说明

- **位置**：`scripts/drift-check.py`（与 generate-map.py 同目录）
- **原理**：以 generate-map.py 的 `DIRECTORY_NOTES` 为期望结构（与 windows.md 同源），扫描实际磁盘顶层+二层，报告「缺失」（期望有实际无）与「新增」（实际有期望无）两类漂移
- **参数**：`--quiet` 无差异时零输出（skill 加载钩子用）；`--base` 自定义根目录（测试用）
- **退出码**：0 = 一致；1 = 有差异；2 = 运行错误
- **噪音控制**：`.` 开头隐藏目录、`node_modules`/`.git` 等深目录、已知噪音顶层（Program Files、WPS 残留等）不报告

---

## 执行流程

### 步骤 1：扫描实际文件系统

```
Agent 执行：
1. ls ~/（或平台对应根目录）获取顶层目录列表
2. 对每个自定义根目录（Data/ Development/ Tools/ Projects/ Research/），ls 获取二层结构
3. 记录完整目录树到临时文件
```

### 步骤 2：对比期望结构

```
将扫描结果与 platforms/<当前平台>.md 中的期望结构逐项对比：

扫描结果 ──对比──→ 期望结构
    │
    ├── 新增目录（扫描有，期望无）
    ├── 缺失目录（期望有，扫描无）
    └── 名称变化（两边有但名字不同，可能是重命名）
```

### 步骤 3：生成差异报告

```
## 文件结构差异报告（YYYY-MM-DD）

### 新增（扫描发现但期望结构中没有）
- ~/NewDir/          ← 首次发现于 YYYY-MM-DD，已连续出现 N 次

### 缺失（期望结构中有但扫描不到）
- ~/ExpectedDir/     ← 期望结构标记为存在，实际不存在

### 名称变化（可能被重命名）
- ~/OldName/ → ~/NewName/

### 建议
- 以上差异是否需要更新到文件结构规范？
```

### 步骤 4：询问用户

用 `ask_user` 工具展示差异报告，选项：
- 「是，全部更新」
- 「只更新新增项」
- 「暂不更新」

### 步骤 5：执行更新

用户确认后：
1. 更新 `references/platforms/<当前平台>.md` 对应章节
2. 在文件顶部的 changelog 记录本次变更日期和摘要
3. **绝不修改 SKILL.md 核心陷阱和工作流**——只有 platforms/ 文件需要更新

---

## 更新约束

| 约束 | 说明 |
|---|---|
| **只更新 platforms/** | SKILL.md 核心陷阱（§1）和工作流（§3-§7）不因目录变化而修改 |
| **每次记录 changelog** | 更新 platforms/xxx.md 时在文件顶部记录日期 + 变更摘要 |
| **不自动执行** | 必须用户确认后才写入，不能静默更新 |
| **最小改动** | 只更新变化的部分，不重写整个平台文件 |

---

## 目录分类规则

扫描到新目录时，按以下规则分类：

| 目录特征 | 分类 | 处理 |
|---|---|---|
| 大写开头、含明确软件名 | 自定义根目录候选 | 列入差异报告的新增项 |
| `.` 开头（dotfile 目录） | 系统和工具配置 | **忽略**，不列入差异报告 |
| macOS 系统目录（`Library/` `Applications/` 等） | 系统目录 | **忽略** |
| 已知临时目录（`tmp/` `temp/` 等） | 临时目录 | **忽略** |
| 其他无法判断的 | 待确认 | 列入差异报告，标注「待确认」 |

---

## changelog 格式

每次更新 platforms/xxx.md 时，在文件顶部添加：

```markdown
<!--
changelog:
- 2026-XX-XX: 新增 ~/NewDir/（用户确认），移除 ~/DeletedDir/（已不存在）
- 2026-06-27: 初始版本，基于实际扫描
-->
```

---

*创建于 2026-06-27，随 filesystem v3.0.0 发布*
*（内容由AI生成，仅供参考）*


---
## 附录: references/workflow.md

# Filesystem Skill — 文件操作工作流

> **本文是 filesystem §0 陷阱 0.7 的详细操作手册。**
> **任何文件操作任务（删除/重命名/移动/新建）都必须按这个流程走。**

---

## 为什么需要这个工作流

用户 2026-06-13 反复强调：

- "你可以现在问问我每个文件夹里面都是什么"
- "我觉得应该再问，再看，最后才动"
- "我觉得你应该扫描一下整个目录结构"

背景：用户电脑经过多年混乱整理，很多目录：
- **含义变了**（如 `D:/Software` 已装软件 vs `Cloud/Software` 破解版）
- **状态模糊**（如 `D:/Development/Home` dotfiles 是"烂尾了"还是"在用"？）
- **历史残留**（如 `D:/Cloud/Projects/Sandbox/Code/Hackathon/health-agent/.next` 是真的项目还是过期构建产物？）

**盲目行动 = 误删/误改**。

---

## 5 步标准流程

### 步骤 1: SCAN（强制）

**第一步必须是扫描，不是问问题**。扫描深度 ≥ 3 层。

```bash
# 错误：直接问用户
Agent: "你想怎么整理 D:/Cloud/Projects/Sandbox/Code/Hackathon？"
User: "...不知道。"

# 正确：先扫，看到什么再问
$ find D:/Cloud/Projects/Sandbox/Code/Hackathon -maxdepth 3 -type d
$ du -sh D:/Cloud/Projects/Sandbox/Code/Hackathon/
$ ls -la D:/Cloud/Projects/Sandbox/Code/Hackathon/
Agent: "Hackathon/ 下有 health-agent/ 子项目，44,400 文件，其中 .next/ 占大头。
        你想删 .next/ 还是整个 health-agent/？"
```

**扫描清单**：
- `find -maxdepth 3 -type d` 看 3 层结构
- `du -sh` 看大小（**绝不只看文件数**）
- `ls -la` 看 dotfiles（隐藏文件）
- `find -name "*.tmp" -o -name "*.bak" -o -name "*.crdownload"` 找垃圾

---

### 步骤 2: ASK（必要才问）

扫描完了之后，**只问不知道的**。已经知道的不要重复问。

**问之前先想**：

```
Agent 内部 checklist：
□ 用户给的信息够用吗？
□ 扫描结果能推断吗？
□ 这个信息会影响下一步吗？

如果三个都"是" → 不要问，直接做。
否则 → 用"对 X 你想怎么？"或"X 是 A 还是 B？"的形式问。
```

**问的格式**：

| ❌ 差的问法 | ✅ 好的问法 |
|---|---|
| "你想怎么处理？" | "A 方案（删除）或 B 方案（迁移到 X）你选哪个？" |
| "我可以帮你整理吗？" | "扫到了 7 类垃圾，按危险程度排序，你想从哪个开始？" |
| "你确定吗？"（没有上下文）| "BaiduNetdisk 42 GB，里面有 SolidWorks 安装包。这是你说的『长期收藏』还是『还没整理』？" |
| "Sandbox/ 下有空目录，要删吗？" | "Sandbox/ 是你主动维护的素材池（filesystem §0 陷阱 0.8），**不主动清理**。你有空目录的需求我可以做。" |

---

### 步骤 3: PROPOSE（先给方案）

不要直接动手。**给至少 3 个候选方案**让用户选：

```
Agent: "命名我有 3 个候选：
        A: filesystem (处理整台电脑的文件结构) — 推荐
        B: host (本机语义)
        C: structure (结构，但太抽象)
        你选哪个？"
```

**为什么至少 3 个**：1 个不够选择空间，2 个像在做选择题，3 个能体现你真的想过。

**带语义解释**：每个候选要说**为什么这个名字**。

---

### 步骤 4: PREVIEW（dry-run 必做）

**任何 mv/rm/rmdir 之前，必须 dry-run 给用户看清单**：

```bash
echo "===== Dry-run（不会真动）====="
echo "[mkdir]   D:\\Cloud\\Library\\CAD"
echo "[move]    D:\\Cloud\\Software\\AutoCAD → D:\\Cloud\\Library\\CAD\\AutoCAD"
echo "[rename]  D:\\Cloud\\Software\\SW2026 → D:\\Cloud\\Library\\CAD\\Solidworks2026"
echo "[rmdir]   D:\\Cloud\\Software (空后)"
echo
echo "回复 OK/go/执行 我才真动。"
```

**禁止**：直接执行 `rm -rf` 或批量 `mv`，然后才告诉用户。

**反例**（要避免）：
```
❌ Agent: [悄悄 mv 50 个文件]
   Agent: "整理好了。"
   User: "...你动了什么？"
   User: "我没说要动 XXX！"

✅ Agent: [打印 dry-run 清单]
   User: "OK"
   Agent: [执行]
   Agent: "✅ 全部完成。"
```

#### 冲突检测（重命名场景必做）

重命名前**必须检测目标是否存在**：

```python
# ❌ 危险：直接 mv 会覆盖目标文件
mv "old.pdf.pdf" "old.pdf"  # 如果 old.pdf 已存在，会覆盖！

# ✅ 安全：先检测
import os
if os.path.exists("old.pdf"):
    print(f"⚠️  目标已存在：old.pdf")
    print(f"    选项 A：删除 .pdf.pdf 副本（保留 .pdf 正本）")
    print(f"    选项 B：手动对比两个文件哪个更新更完整")
else:
    print(f"✅ 安全重命名：.pdf.pdf → .pdf")
```

**用户原话**："第 1 个 `.pdf.pdf` 有冲突 FROM: ... TO: ... ← 这个文件已经存在！"

→ 必须**先报告冲突**，让用户选 A1/A2/A3 之一。

#### 扫描结果分类

把扫描结果按"处理方式"分组：

| 类别 | 处理方式 | 示例 |
|---|---|---|
| **A. 重复副本** | 删除（保留正本） | `.pdf.pdf` 与 `.pdf` 同时存在 |
| **B. 下载失败残留** | 直接删除 | `.crdownload` |
| **C. Office 临时锁** | 直接删除 | `~WRL2087.tmp` |
| **D. 旧版本备份** | 询问用户（保留或删） | `.bak` `.tmp` 文件 |
| **E. 待分类** | **不动**，让用户决定 | 空目录、过时文件等 |

**关键原则**：
- **E 类（待分类）绝不在本次清理中动** — 用户没明确说要动
- D 类必须列出每个文件 + 创建时间，让用户判断

---

### 步骤 5: WAIT + EXECUTE + VERIFY

#### 5a: WAIT（等确认）

**明确等待用户回复 "执行" / "OK" / "go" 才动**。

如果用户给了多个选项（如 A1 / A2 / A3）— 必须按选项分支处理，**不能擅自选一个**。

如果用户沉默 >1 分钟没回，**重新询问**而不是自动执行。

**用户回应处理**：

| 用户回应 | 含义 | Agent 动作 |
|---|---|---|
| "OK" / "执行" / "go" | 同意 | 立刻执行 |
| "等一下" | 想再看看 | 暂停，等明确指令 |
| "你看呢" / "你觉得呢" | 让我决定 | 主动给推荐方案（不是 dry-run） |
| "算了" / "不做" | 取消 | 不动，记录到 memory（如果用户重复取消类似操作） |
| "以后再说" / "以后我自己处理" | 不再追问 | 标记完成，下次不问 |

**特别注意**：**"以后我自己处理" 必须立即停止**，写入 memory 和 skill（filesystem §0 陷阱 0.10），**下次遇到同样话题不要主动提**。

#### 5b: EXECUTE（执行）

按 preview 清单逐项执行：

```bash
# 1a: 删除 .pdf.pdf 副本
rm "Research/01-SRTP/Lit/Patents/xxx.pdf.pdf"

# 1b: 重命名 .pdf.pdf → .pdf
mv "Research/01-SRTP/Lit/Patents/yyy.pdf.pdf" \
   "Research/01-SRTP/Lit/Patents/yyy.pdf"

# 2: 删除 .crdownload
rm "Courses/.../01-12.mp4.crdownload"
rm "Courses/.../01-14.mp4.crdownload"
rm "Courses/.../01-18.mp4.crdownload"

# 3: 删除 .tmp
rm "Courses/.../Homework/~WRL2087.tmp"
```

**每步 echo 进度**，让用户能跟踪：

```
✅ 步骤 1a 完成：删除 xxx.pdf.pdf (4.9 MB)
✅ 步骤 1b 完成：重命名 yyy.pdf.pdf → yyy.pdf
✅ 步骤 2 完成：删除 3 个 .crdownload (4.1 GB)
✅ 步骤 3 完成：删除 ~WRL2087.tmp (21 KB)
```

#### 5c: VERIFY（验证扫描）

执行完**必须再扫一次**，确认没漏：

```python
# 重新跑 Step 1 的扫描
# 应该返回 0 个结果（除非有未处理的类别）
```

输出：

```
✅ 验证扫描结果
  .pdf.pdf        ✅ 无残留
  .crdownload     ✅ 无残留
  ~*.tmp          ✅ 无残留
  .bak            ⚠️ 还有 1 个（用户保留）
```

---

## 实战模板（每次任务按这个格式）

```markdown
## [阶段 1: SCAN]
- 扫描: `find D:/Target -maxdepth 3 -type d`
- 大小: `du -sh D:/Target/*`
- 关键发现:
  - /A/ 子目录 50 个文件，200 MB
  - /B/ 有 .crdownload 42 GB（重要！）

## [阶段 2: ASK]
- 问: B 的 42 GB 是...？
- 答: "我自己处理"

## [阶段 3: PROPOSE]
- 方案 A: ...
- 方案 B: ...
- 推荐: A

## [阶段 4: PREVIEW]
- [mkdir] /A/
- [move] /B/x → /A/x
- [rm] /B/y

## [阶段 5: WAIT]
- 用户: OK
- 执行: [全部完成]
```

---

## 用户已知的"主动维护"目录

以下目录**绝不**进入清理清单（参考 SKILL.md §0 陷阱 0.8）：

| 目录 | 跳过原因 |
|---|---|
| `D:\Cloud\Projects\Sandbox\*` | 用户素材池，含空占位 |
| `D:\Cloud\Archive\Password\*` | 用户自管的密码文件（待迁移 Bitwarden 但时机由用户决定） |
| `D:\Cloud\Media\Music\Song\*` | 400 个艺术家目录，个人音乐库 |
| `D:\Cloud\Games\*` | 个人游戏目录 |
| `D:\Cloud\Archive\*` 的大部分 | 用户没明确说要动 |

**反例**：

```
❌ 扫描 D:\Cloud 全树后建议删除 Sandbox/Code/Hackathon/ 下 v1/v2/v3 文件
   → 用户立刻说："你不要管了。我就是喜欢这样"
```

---

## 大小判断（什么时候值得清理）

| 单文件大小 | 建议 |
|---|---|
| < 1 MB | 低优先级（除非是大量累积） |
| 1-100 MB | 中优先级（preview + 等确认） |
| > 100 MB | 高优先级（必须 preview + 详细说明） |
| > 1 GB | **必须先确认文件性质**（视频？数据集？真实下载？） |

**陷阱**：`.crdownload` 文件常常看起来大但实际是"下载到一半的失败"。要明确说明：

```
"3 个 .crdownload 总计 4.1 GB，但这些都是 2025 年（去年）的微积分录像课未完成下载，建议直接删除"
```

不要让用户以为 4.1 GB 是有价值的数据。

---

## 反模式速查

| ❌ 反模式 | ✅ 正确 |
|---|---|
| 直接 `rm -rf` | 先 dry-run |
| "我帮你删了 X" | "我建议删 X，请确认" |
| 自动判断"应该删" | 用户没说就不动 |
| 把空目录列进"建议清理" | 空目录可能是用户的占位 |
| 跳过 preview 因为"看起来很安全" | **永远 preview** |
| "我重命名了 11 个文件，你看下效果" | preview 时**先检测目标冲突**，再让用户选 |

---

## 完成报告模板

清理完成后，输出：

```
✅ 清理完成（{YYYY-MM-DD}）

执行：
- 🗑️ 删除 N 个 .pdf.pdf 副本（M MB）
- 📝 重命名 N 个文件（M MB）
- 🗑️ 删除 N 个 .crdownload（M GB）
- 🗑️ 删除 N 个 .tmp（M KB）

跳过（按用户决定保留）：
- ⏭️ Drawing2.bak（用户决定保留）

释放空间：X.X GB
验证扫描：0 个残留（除保留项）

后续建议：
- 还有 6 个 .bak 文件未处理，需要时再清理
- Sandbox/ 下仍有空目录，建议保留
```

---

## 不要做的事

- ❌ 跳过 SCAN 直接问"你想怎么整理"
- ❌ PROPOSE 时只给 1 个方案（这不是提议，是通知）
- ❌ PREVIEW 时只给"我会创建 X 目录"（不说清楚删什么、改什么、移到哪）
- ❌ 用户没回复就执行
- ❌ 用户说"等一下"还继续动
- ❌ 用户说"以后再说"还重复问

---

## 写 Skill 时的元教训

任何 cleanup 类 skill 必须在 SKILL.md 里**明确写出**这 5 步流程，并在 reference 文件里给出**具体命令模板**。

不要假设 Agent 会自动遵循 —— 必须有：

```markdown
## 工作流（强制）

### 步骤 1: 扫描
```bash
# 至少 3 层
find D:/Target -maxdepth 3 -type d
du -sh D:/Target/*
ls -la D:/Target/
```

### 步骤 2: 询问
- 只问扫描后**还不知道**的信息
- 给 3 个候选方案 + 推荐

### 步骤 3: Dry-run
- 打印每个 mv/rm 的具体目标
- 告诉用户"回复 OK 才动"

### 步骤 4: 执行
- 用户说 OK 后**一次性执行**
- 不分批

### 步骤 5: 验证
- 再跑一次 find/du -sh
- 对比前后差异
```

---

## 元信息

- **合并时间**：2026-06-15
- **来源**：
  - `cleaning-checklist.md`（清理细节、冲突检测、用户已知目录、大小判断）
  - `scan-then-ask-workflow.md`（5 步通用流程）
- **保留独立**：技术踩坑见 `scan-rules.md`；具体命令配方见 `cleanup-recipes.md`

---

*（本文档沉淀自 2026-06-13 长会话的 3 次清理操作（.pdf.pdf/.crdownload/.tmp）+ 2026-06-15 多次 C 盘清理的实战经验。）*

---
## 附录: references/c-drive-audit.md

# C 盘审计手册

> 当用户说"扫一下 C 盘"或"C 盘又满了"时加载本文。
> 重点：**C 盘内容高度个性化，必须 scan → 报告 → 等指令，不要自作主张**。

## 与 D 盘审计的区别

| 维度 | D 盘（Cloud） | C 盘（系统） |
|---|---|---|
| Agent 熟悉度 | 高（已知结构） | 低（千人千面） |
| 误删代价 | 低（自己文件） | 高（系统/软件崩） |
| 大量已知规则 | 有（filesystem §4） | 几乎无 |
| 系统目录 | 无 | 有 Windows/Program Files 等禁区 |
| 风险 | 误删用户文件 | **破坏系统 / 触发软件不可用** |

## 必须执行的扫描动作（顺序敏感）

### 1. 先看 C 盘健康度

```bash
# 磁盘剩余
wmic logicaldisk get caption,freespace,size

# 顶层目录概览（只看顶层，不递归）
ls -la C:/
```

**必须排除**：`Windows/`、`Program Files/`、`Program Files (x86)/`、`ProgramData/`、`$Recycle.Bin/`、`Recovery/`、`System Volume Information/`、`PerfLogs/`、`Boot/`、`Config.Msi/`。

### 2. 用户主目录深扫

```bash
ls -la /c/Users/xgbc/        # 顶层隐藏目录（60+ 个是常态）
ls -la /c/Users/xgbc/AppData/Local/   # 经常 GB 级，但需要时间
ls -la /c/Users/xgbc/Desktop/ /c/Users/xgbc/Documents/ /c/Users/xgbc/Downloads/
```

⚠️ `AppData/Local/Packages/` 和 `AppData/Local/Microsoft/` 通常巨大且结构复杂，先 ls 不 rglob。

### 3. 立刻报告 4 件事

1. **磁盘剩余**
2. **顶层非系统目录清单**（用户通常会指着其中一个说"那是什么"）
3. **Desktop/Documents/Downloads 大小**
4. **AppData 总大小**（用 `du -sh` 不展开）

不要立刻提建议，等用户问。

## 高频"看起来像病毒但其实不是"的陷阱

> 2026-06-15 用户在 `C:\yyb/` 看到 `beacon_report.log` 后怀疑中毒。我差点过度反应。
> 实际上 `yyb/` 是**百度网盘的 P2P 加速组件**，不是木马。

**判断启发**：

| 现象 | 真实可能 | 不要立刻判为 |
|---|---|---|
| 目录名是 2-4 个随机字母（yyb、abc、xyz） | 内部组件代号 / 灰软 | 病毒（先看文件） |
| 目录里有 `uninstall.exe` | 合法软件 | 木马 |
| `beacon_report.log` 之类日志 | 内部日志（很多软件叫这名字） | C2 通信（看大小） |
| 0 字节日志 | 卸载残留 | 通信证据 |
| uninstall 顺手把其他软件卸了 | PUA bug | 恶意软件 |
| 时间戳是最近安装其他软件前后 | 捆绑安装 | 注入 |

**冷静原则**：先 ls 内容、查文件大小、看时间戳，**不要用"beacon"这种词吓用户**。

## Desktop 隐藏空间挖掘

很多用户不知道 Desktop 有**卸载备份残留**。

```bash
# 常见模式
ls -la /c/Users/xgbc/Desktop/ | grep -E "SW_Cleanup|Uninstall|Backup|Install"

# 这种往往 GB 级
du -sh /c/Users/xgbc/Desktop/SW_Cleanup_*
```

**2026-06-15 实测**：SolidWorks 卸载备份 `SW_Cleanup_Backup2_20260614_191605/` 占 34.14 GB，但用户以为"早就删了"。

## C 盘 vs D 盘的判断规则（重要 pitfall）

用户说"C 盘又满了"，不要直接去动 C 盘。**先问 3 个问题**：

1. **D 盘也满了吗？** — 如果 D 盘空，C 盘满了通常是 D 盘该装的不在 D 盘
2. **什么类型文件占得多？** — 系统更新？软件缓存？用户文件？
3. **哪些软件是必须留在 C 盘的？** — 浏览器、聊天工具通常只能在 C 盘

## 危险操作红线（绝不执行）

| 操作 | 风险 |
|---|---|
| 删除 `C:\Windows\`, `C:\Program Files\`, `C:\Program Files (x86)\`, `C:\ProgramData\` | 系统崩溃 |
| 删除 `C:\Users\xgbc\AppData\` 全部 | 所有软件配置丢失，需重装 |
| 删除 `C:\Users\Public\` | 共享文件丢失 |
| 删除注册表相关文件 | 软件失能 |
| 在 `C:\Users\xgbc\` 内 `rm -rf .*` | **所有 dotfiles（含 .ssh/、.gitconfig）丢失** |

## 操作 C 盘前的强制 dry-run

即使是删 1 个文件：

```bash
echo "===== Dry-run ====="
echo "[rm] /c/Users/xgbc/Desktop/SW_Cleanup_Backup2/"
echo "  预估大小: $(du -sh /c/Users/xgbc/Desktop/SW_Cleanup_Backup2/ 2>/dev/null | cut -f1)"
echo "  预计释放: 34 GB"
echo
echo "回复 OK/go/执行 我才真动"
```

不要被"C 盘满了"的紧迫感推动跳过 dry-run。

## 真实案例（2026-06-15）

**场景**：用户说"C 盘存储告急，可能有些软件本应装在 D 盘"。

**发现**：
1. `Desktop/` 占 35 GB — 全是 SolidWorks 卸载残留（`SW_Cleanup_Backup2_20260614_191605/`，含百度网盘未完成下载 16.7 GB）
2. `C:\yyb/` 不是病毒，是百度网盘 P2P 加速组件的目录
3. uninstall yyb 把 QQ 一起卸了 — 百度网盘 PUA bug

**处理**：
1. 先扫描 Desktop，发现 `SW_Cleanup_Backup2_20260614_191605/` 占 34 GB
2. 确认是 SolidWorks 卸载备份（用户已装好 SolidWorks）
3. 用户拍板"直接删" → 删除整个目录
4. 释放 34 GB

**结论**：先发现桌面隐藏的"卸载备份"目录（30+ GB 级别），是 C 盘空间释放的**第一手选项**——比动 AppData 安全。

## C 盘 → D 盘迁移候选清单（标准建议）

| 类型 | 迁移目标 | 可行性 |
|---|---|---|
| 软件安装包（已下载） | `D:\Cloud\Library\{category}/` | ✅ 完全可行 |
| 软件缓存（Adobe、钉钉、微信等） | `D:\Data\Cache\{软件}/` | ⚠️ 软件要支持改缓存路径 |
| 软件数据库（聊天记录、Zotero） | `D:\Data\Collaboration/{软件}/` 或 `D:\Data\Literature/` | ⚠️ 需要 Symlink，复杂 |
| dotfiles（`.bashrc`、`.gitconfig`、`.ssh/`） | `D:\Development\Home/`（已存在） | ⚠️ 需要修改 $HOME 或 PATH |
| 用户文件（Desktop/Documents/Downloads） | `D:\Cloud\` 对应分类 | ⚠️ 需要用户主动迁移，软链有兼容性问题 |
| XboxGames 数据 | `D:\Games\` | ⚠️ Xbox 不支持自由移动 |
| OneDrive 缓存 | `D:\Data\CloudDrive/` | ✅ 可在 OneDrive 设置里改 |

**铁律**：**不能简单 cp/move** AppData 内容——会破坏注册表关联。要用 mklink（Junction）。

## C 盘审计后建议的输出格式

```markdown
## C 盘审计报告

### 磁盘
- C 盘剩余: XX GB / 总 XX GB
- D 盘剩余: XX GB / 总 XX GB

### 顶层（15 个非系统目录）
| 目录 | 大小 | 角色判断 |
|------|------|----------|
| Autodesk/ | X GB | AutoCAD 残留，**应移 D 盘** |
| KingsoftData/ | X MB | WPS 缓存 |
| ... | | |

### 用户主目录（/c/Users/xgbc/）
- Desktop/: 35 GB（**主嫌疑**：卸载备份残留）
- Documents/: 32 MB
- Downloads/: 0
- AppData/Local/: X GB（**主嫌疑 2**）

### 建议下一步
按风险从低到高：
1. 删除 Desktop 卸载备份（释放 35 GB）
2. 清理 OneDrive 缓存
3. 迁移 OneDrive 到 D 盘
4. 清理 AppData/Local/Microsoft/Windows/Explorer/

每步都需要单独确认。
```

## 与 filesystem SKILL.md 的关系

- **filesystem §1 命名规则** —— 不变
- **filesystem §3 决策树** —— 仍以 Cloud/ 为主，C 盘条目最少
- **filesystem §5.3 修复命令** —— 适用于 D:/Cloud，D 盘用法不同
- **本文** —— C 盘特化，**加载 filesystem skill 后必须额外加载本文**

## 元教训

写 C 盘相关 skill 时要时刻记着：

1. **用户对 C 盘有强烈感情（可能含珍贵文件）**——比 D 盘谨慎 10 倍
2. **C 盘"看起来像病毒但其实不是"的陷阱很多**——冷静分析
3. **Desktop 是 C 盘隐藏空间的"重灾区"**——先扫 Desktop
4. **任何 mv/rm 之前必须 dry-run**——绝对不要凭感觉
5. **不要因为"C 盘满了"就急着清理**——先问清楚用户痛点
