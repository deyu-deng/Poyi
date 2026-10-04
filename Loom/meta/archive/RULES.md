<!-- 来自 Poyi Vault，2026-07-01 归档 -->

# Poyi Vault · Agent 写入规则

> 本文件为 Agent（Claude Code / Claudian / Copilot）的**强制写入规范**。
> 每次会话开始必读。每次写入前**先走决策树**。

---

## 一、写入决策树（拿到任何新信息，先问这 4 个问题）

```
Q1: 这是要按时间记录的事件吗？
  ✅ 是 → Journal/<YYYY-MM-DD-Weekday>.md（不存在则新建，append 流水）
        例：2026-04-10-Friday.md
  ❌ 否 → Q2

Q2: 这是某个具体项目的进展/产出吗？
  ✅ 是 → Projects/<项目名>/notes.md（append）
        项目对照表：
          - SRTP → Projects/SRTP/
          - SamplelabOS → Projects/SamplelabOS/
          - 学期课程 → Projects/College2026Spring/
          - 示例车队底盘 → Projects/FormulaStudentChassis/
  ❌ 否 → Q3

Q3: 这是新的主题知识（概念/原理/读书笔记）吗？
  ✅ 是 → 检查 Knowledge/<学科>/ 下是否已有相关笔记
          有 → 打开原文件，**合并到相关章节**，不要 append！
          无 → 在 Knowledge/<学科>/ 新建
  ❌ 否 → Q4

Q4: 这是借来的/暂存的资料（AI 对话、网页剪藏等）吗？
  ✅ 是 → Resources/<类别>/（append）
        类别：AIConversations / ReadingNotes / Clippings
  ❌ 否 → _Inbox/（gitignored，本地暂存等用户手动归档）
```

---

## 二、追加 vs 合并 vs 新建的判定

| 文件类型 | 默认操作 | 例外 |
|---------|---------|------|
| `Journal/*.md` | **append**（流水） | — |
| `Projects/<name>/notes.md` | **append** | — |
| `Resources/AIConversations/*.md` | **append** | — |
| `Knowledge/**/*.md` | **合并到最相关章节** | 新主题才新建 |
| `Areas/**/*.md` | **合并到最相关章节** | 新主题才新建 |
| `Context/RULES.md` / `Meta.md` | **合并到最相关章节** | — |

---

## 三、二级目录命名规则（PascalCase）

- **单字**：`Math` `AI` `Physics`
- **多字**：`VehicleEngineering` `FormulaStudentChassis` `SamplelabOS` `AIConversations`
- **禁止**：空格、下划线 `_`、连字符 `-`、中英混杂
- **顶层**：10 个固定，**不轻易新增**
  ```
  _Inbox  Journal  Knowledge  Projects  Areas  Resources  Archive  Context  Skills  Media  Templates
  ```

---

## 四、frontmatter 规范（仅新建文件）

**新建文件时**必须包含以下字段。已有文件不强制回填。

```yaml
---
id: note-YYYYMMDD-xxxx
title: 笔记标题
type: [Journal | Knowledge | Project | Area | Resource | Meta]
tags: [学科, 主题, 状态]
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
summary: 一句话说明笔记核心
---
```

---

## 五、内容风格

- **核心原则**：`简洁直接，信息密度高`，不拖泥带水
- **公式**：只用单行 `$...$`，禁止 `$$...$$`
- **表格**：用于对比（≤4 列），避免过度使用
- **示例**：典型且有难度，不写完整计算
- **语言**：中文优先

---

## 六、Vault 顶层结构（10 个固定）

| 顶层 | 内容 | 写入方式 |
|------|------|---------|
| `_Inbox/` | Agent 临时区（gitignored） | append |
| `Journal/` | 日记（`<YYYY-MM-DD-Weekday>.md`） | append |
| `Knowledge/` | 主题知识（学科分类） | **合并** |
| `Projects/` | 当前项目 | append（每项目一个 notes.md） |
| `Areas/` | 长期持续责任 | **合并** |
| `Resources/` | 借来的资料 | append |
| `Archive/` | 已结束的 Projects | append |
| `Context/` | Agent 系统上下文 | **合并** |
| `Skills/` | AI 工作流库 | append |
| `Media/` | 附件 | — |
| `Templates/` | 笔记模板 | — |

---

## 七、信息归属不明时的处理

**Agent 不确定新信息该放哪时**：
1. 优先询问用户（不要擅自新建顶层目录）
2. 暂时写入 `_Inbox/`，并在文件头注明 `# TODO: 待归档`
3. 等用户手动归档

**禁止行为**：
- ❌ 在旧文件末尾直接 append 不相关的内容
- ❌ 新建顶层目录（除非用户明确同意）
- ❌ 修改已 commit 的文件名（除非走 git mv）
- ❌ 删除其他 Agent 创建的文件（除非用户明确同意）

---

## 严禁向文件写元注释

**元注释 = 只对单次对话有用的元说明**，典型例子：

| 写法 | 问题 |
|---|---|
| `"双源合并：原 A.md + 原 B.md"` | 历史已发生，用户不需要看来源 |
| `"v2 重构时合并"` | 时间戳+动作描述，未来永远用不到 |
| `"由 Agent 在 YYYY-MM-DD 自动整理"` | 谁/何时改的不属于笔记内容 |
| `"本文件定义..."` | 文件名已经说明这是什么 |
| `"# TODO: 待归档"` 仅在 `_Inbox/` 内部允许 | — |
| 任何形式的"自我介绍/前言/来源说明" | — |

**判定原则**：一句话如果删掉后**未来所有读者都不会受影响**，那就是元注释。

**正确做法**：
- 迁移说明 → 写在 commit message（git 历史里能看到）
- 时间戳 → git 自动记录，不需要写在文件里
- 文件用途 → 文件名 + 第一个 `# 标题` 已经说明
- 临时任务 → `_Inbox/` 里的文件头可以有 `# TODO`，但归档后必须删除

**示例对比**：

```markdown
# ❌ 错：充满元注释
# 个人画像 · 小满（v2 重构时从 persona.md 迁移而来）
> 本文件由 Agent 在 2026-06-19 自动整理。
> 涵盖用户基本信息、风险意识、长期愿景等。

## 基本信息
...

# ✅ 对：干净的主题内容
# 用户画像 · 小满

## 基本信息
...
```

---

## 八、知识关联要求

- 跨主题引用必须用 `[[双链]]`
- 主题笔记必须打 `tags`
- 每个顶层目录保持一个 `INDEX.md` 作为入口

---

## 九、与用户的协作约定

- 每次执行破坏性操作（rm、移动大批文件）前**先列出清单确认**
- 多方案对比时用表格 + 简短说明
- 用户说"暂停"立即停止，给出当前进度
- 用户说"撤回"立即 `git reset`/`git restore`

---