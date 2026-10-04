---
name: papers
description: "科研文件管理 Skill。统一 Research/ 下所有课题的文件结构、命名、引用规范。原 research-workflow + papers/projects/SRTP.md 已整合。触发词：'文献'、'论文'、'SRTP'、'科研'、'写论文'、'投稿'。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": ["filesystem"]}
---
# Research Orchestrator — 科研文件管理总入口

> **统一管理 Research/ 下所有课题的文件结构。**
> **加载本 skill 后，按用户提到的课题加载对应 project 配置。**

---

## 三位一体架构

研究工作流横跨三个物理位置，各司其职：

| 位置 | 路径 | 角色 | 存放内容 |
|---|---|---|---|
| Zotero | `D:/Data/Zotero/storage/` | 采集端 | 原始 PDF 附件、自动 bib 导出 |
| Research | `D:/Cloud/Research/` | 存储端 | PDF 原件、bib、汇总表、专利、数据 |
| Vault | `/Users/sample/Poyi/Vault/notes/research/` | 加工端 | Markdown 阅读笔记、项目总览 |

**数据流向**：

```
检索下载 → Zotero 入库（采集）
           ↓
     Research（存储：PDF + bib + 表格）
           ↓
     Vault/notes/research（加工：笔记 + 索引）
```

三者物理分离但通过 Citekey 统一标识，不可混放——笔记不放 Research，PDF 不放 Vault。

---

## 路由表

加载本 skill 后，按用户提到的课题加载对应配置：

| 用户提到 | 加载 |
|---|---|
| "SRTP"、"01-SRTP"、"电动装载机" | `projects/SRTP.md` |
| "毕业论文"、"02-Thesis" | `projects/thesis.md`（占位，暂未启用） |
| "新课题"、"XX-Topic" | 参考 `schemas/folder-structure.md` 自动生成 |

---

## 通用规则摘要（详见 schemas/）

### PDF 读取强制约束

**Agent 处理文献/论文时必须调用 `read_file` 读取 PDF 实际内容，严禁仅凭文件名、路径或元数据判断。** 违例场景：只扫文件名声称"已找到 X 篇论文"而不读取正文；仅凭 bib 条目做摘要；用 `search_file` 替代 `read_file` 处理 PDF。

### 课题根目录命名

单英文单词，首字母大写，禁止下划线、缩写、中文：

```
Research/
├── 01-SRTP/
├── 02-Thesis/
└── ...
```

数字前缀控制排序，课题名简洁标识。**注**：按 filesystem §2 命名规则，目录名实际推荐 `01-SRTP/` 这种短横线分隔的数字-单词格式（而非 `01_SRTP/`）。

### 课题内部 6 模块

```
{Project}/
├── Lit/         文献库（PDF、专利、bib、汇总表）
├── Notes/       笔记（阅读笔记、组会记录、导师沟通）
├── Code/        代码与仿真模型
├── Data/        实验数据、仿真结果
├── Docs/        项目管理文档（申报书、指南）
└── Drafts/      论文草稿、中期报告、结题交付物
```

详细规范见 `schemas/folder-structure.md`。

### 命名规范（通用）

> **权威规则**：filesystem skill §2，Research 目录内适用 kebab-case。
> papers 的目录名和文件名以 filesystem 为准，不再独立定义命名规则。

- **目录名**：kebab-case，≤2 词（如 `01-SRTP`、`lit-review`）
- **文件名**：中文描述性名称，清晰体现内容与用途
- **日期前缀**：需要时间标识时 `YYYY-MM-DD_` 格式
- **禁止**：空格、`-` 与 `_` 混用、无意义缩写、中英杂糅、双后缀（如 `.pdf.pdf`）
- **第三方文献**：学术 PDF 文件名含下划线视为合规（Zotero / Google Scholar 惯例）

详细规范见 `schemas/naming.md`。

### 引用格式

默认 GB/T 7714（中文期刊标准），详细著录格式见 `schemas/citation-format.md`。

---

## 加载顺序

1. **filesystem**（路径决策）
2. **papers**（本 skill）
3. **对应 projects/{name}.md**（具体课题规则）

---

## 文件清单

```
papers/
├── SKILL.md                  ← 本文件（总入口 + 路由）
├── projects/
│   ├── SRTP.md               ← SRTP 专项规则（替代原 papers/projects/SRTP.md）
│   └── thesis.md             ← 毕业论文占位（待启用）
├── schemas/
│   ├── folder-structure.md   ← 6 模块 Lit/Notes/Code/Data/Docs/Drafts 规范
│   ├── citation-format.md    ← GB/T 7714 著录格式
│   └── naming.md             ← 文件/文件夹命名规范
└── shared/
    └── README.md             ← 子文件间共享说明（暂占位）
```