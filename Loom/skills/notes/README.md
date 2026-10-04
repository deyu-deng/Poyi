# 双轨制笔记整理工作流

解绑"概念理解"与"考场得分"。用两条轨道管理你的学习笔记：一条建立底层逻辑，一条训练解题直觉。

---

## 核心特色

- **第一轨（知识骨架）**：概念、定义、定理推导 —— 只读锁定，建立 What / Why
- **第二轨（解题技巧）**：If-Then 决策树、陷阱、反例 —— 持续 writable，训练 How / When
- **`/note-merge` 整合**：将 NotebookLM 的零散输出一键整理为幕布可导入的 Markdown 大纲
- **幕布原生兼容**：自动处理 `$$` 公式、表格等格式，粘贴即用

## 快速开始

### 1. 准备笔记

用 NotebookLM 生成你的知识笔记或解题策略，得到 Markdown 格式的原始文本。

### 2. 整合整理

在 Claude Code 中调用 skill：

```
/note-merge
```

粘贴你的片段，说明要整合到**哪一轨**。`/note-merge` 会自动：
- 合并多片段、去重、补全逻辑链条
- 统一标题层级
- `$$...$$` → `$...$`（幕布兼容）
- 表格 → 列表

### 3. 导入幕布

复制输出的 Markdown，直接粘贴到幕布。标题自动转为大纲节点，公式正常渲染。

## 文件结构

```
notes/
├── README.md          # 本文件：工作流介绍与快速入门
├── SKILL.md           # Agent skill 定义
├── WORKFLOW.md        # 完整工作流：双轨制策略、格式规范、风险控制
├── STYLE.md           # 笔记风格规范
├── eval.md            # 能力评估
├── meta.json          # 元数据
├── prompts/           # NotebookLM 提示词模板
│   ├── skeleton-prompt.md  # 生成第一轨（知识骨架）
│   └── tactics-prompt.md   # 生成第二轨（解题技巧）
└── skills/
    └── note-merge/
        └── SKILL.md      # /note-merge skill 的完整定义
```

工作流配置（双轨制策略、格式规范）存放于本 skill 目录；你的学科笔记（`Vault/notes/`）保持原有结构不变。

学科笔记示例：

```
数学 Math/
└── 微积分/                # 学科目录
    ├── README.md          # 学科入口
    ├── NOTESYSTEM.md      # 本学科双轨制策略
    ├── skeleton/          # 第一轨：知识骨架
    │   ├── ch07.md
    │   ├── ch08.md
    │   └── overview.md
    ├── tactics/           # 第二轨：解题技巧
    │   └── ch07.md
    ├── assets/            # 原始素材
    │   ├── textbook/      # PDF 教材
    │   └── mistakes/      # 错题截图
    └── 微积分学习笔记.md   # 存量笔记（保留）
```

## 双轨制速查

| 维度 | 第一轨（知识骨架） | 第二轨（解题技巧） |
|:---|:---|:---|
| **解决** | What / Why | How / When |
| **风格** | 严谨、递进、结构化 | 极度功利、If-Then |
| **状态** | 只读锁定 | 持续 writable |
| **使用场景** | 预习、复盘 | 刷题、考前冲刺 |
| **维护方式** | AI生成后锁定，错题反向注入 | 刷题后15分钟内补充 |

## 了解更多

- 完整工作流说明 → [WORKFLOW.md](WORKFLOW.md)
- `/note-merge` skill 定义 → [skills/note-merge/SKILL.md](skills/note-merge/SKILL.md)

## License

MIT
