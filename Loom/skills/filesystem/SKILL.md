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
   ├── Darwin  → references/platforms/macos.md
   ├── Linux   → references/platforms/linux.md（如存在）
   ├── MINGW* / MSYS* / CYGWIN* → references/platforms/windows.md
   └── 其他   → 默认加载 references/platforms/windows.md，并告知用户平台未知
3. 后续所有路径决策以平台文件中的期望结构为准
4. **静默漂移自检（A 方案）**：若 `scripts/drift-check.py` 存在，执行 `python scripts/drift-check.py --quiet`；退出码 0 则继续，非 0 则把输出的差异报告展示给用户，询问是否更新 windows.md / generate-map.py（详见 `references/self-update.md`）
```

**平台文件内容**：
- 系统级文件夹（不可移动，Agent 只读）
- 自定义根目录（期望结构 + 子目录规范）
- 发现规则（期望缺失 / 新增未识别 / 名称不一致的处理方式）
- 系统盘审计规则（如有）

---

## 0. 自更新机制

详见 `references/self-update.md`。摘要：

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
- 详细工作流见 `references/workflow.md`

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
| **系统盘审计 / 清理** | **加载 `references/c-drive-audit.md` + 平台文件的审计章节** |

---

## 7. 加载与触发

**触发关键词**：
- 「放哪里」、「命名」、「建项目」、「装依赖」
- 「找位置」、「在哪」、「文件结构」
- 「目录结构」、「文件路径」
- 用户提到具体路径
- **「系统盘满了」/「存储告急」/「扫一下系统盘」** → 加载平台文件的审计章节 + `references/c-drive-audit.md`

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

- **目录结构对齐实际磁盘**：`references/platforms/windows.md` 更新 Development 为 Home/Toolchains/Virtualization、Data 为 AppData/Cache/Config、新增 Poyi 顶层（Loom skill 权威源 + Vault）
- **项目命名规则修正**：废弃 `Projects/{NN-Name}/` 编号制，改为无编号扁平 kebab-case
- **路径速查表全面刷新**：移除失效路径（D:\Data\Literature、D:\Data\Collaboration、D:\Development\AI、D:\Development\Runtimes 等），补充实际路径
- **computer-map.json 落点修正**：`D:\Cloud\Vault\Context` → `D:\Projects\Poyi\Vault\Context`，generate-map.py 输出路径同步
- **cross-references 死链清理**：inbox skill 已归档移除，相关引用标记为历史
- **generate-map.py 注释同步**：DIRECTORY_NOTES 更新 Development/Data/Poyi 新结构

### 2026-06-30 v3.2.0

- **新增 Development 子目录分类**：`references/platforms/windows.md` 增加 Runtimes/SDKs/AI/Libraries/Tools 五类及判定标准（跨项目共享 → Development，绑定项目 → 跟项目）

### 2026-06-30 v3.1.0

- **新增 `references/platforms/windows.md` §Agent 产出文件禁令**：Agent 产出严禁写入 C 盘
- **更新 `references/platforms/windows.md` 路径速查**：新增 npm 全局路径 `D:/Development/Runtimes/npm-global/`

### 2026-06-27 v3.0.0

- **跨平台重构**：整合 mac-filesystem-hygiene，实现 Win/Mac 统一心智模型
- **新增 §0 平台检测**：Agent 加载后自动根据 uname 加载对应平台文件
- **新增 §0 自更新机制**：触发条件 + 执行流程见 `references/self-update.md`
- **新增 `references/platforms/macos.md`**：macOS 平台文件结构（已落地部分）
- **新增 `references/platforms/windows.md`**：Windows 平台文件结构（从原 SKILL.md 提取）
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

- 新增 §9 C 盘审计章节 + references/c-drive-audit.md

### 2026-06-15 v2.0.0

- 由 cloud-file-orchestrator + host-context 合并而来

---

*（本 skill 由 AI 基于合并需求 + 用户命名偏好 + 多次自我修正生成）*
*（内容由AI生成，仅供参考）*
