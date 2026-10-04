<!-- source: papers -->
---
name: papers
description: "科研文件管理 Skill。统一 Research/ 下所有课题的文件结构、命名、引用规范。原 research-workflow + papers/projects/SRTP.md (见附录 projects/SRTP.md) 已整合。触发词：'文献'、'论文'、'SRTP'、'科研'、'写论文'、'投稿'。"
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
| "SRTP"、"01-SRTP"、"电动装载机" | `projects/SRTP.md (见附录 projects/SRTP.md)` |
| "毕业论文"、"02-Thesis" | `projects/thesis.md (见附录 projects/thesis.md)`（占位，暂未启用） |
| "新课题"、"XX-Topic" | 参考 `schemas/folder-structure.md (见附录 schemas/folder-structure.md)` 自动生成 |

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

详细规范见 `schemas/folder-structure.md (见附录 schemas/folder-structure.md)`。

### 命名规范（通用）

> **权威规则**：filesystem skill §2，Research 目录内适用 kebab-case。
> papers 的目录名和文件名以 filesystem 为准，不再独立定义命名规则。

- **目录名**：kebab-case，≤2 词（如 `01-SRTP`、`lit-review`）
- **文件名**：中文描述性名称，清晰体现内容与用途
- **日期前缀**：需要时间标识时 `YYYY-MM-DD_` 格式
- **禁止**：空格、`-` 与 `_` 混用、无意义缩写、中英杂糅、双后缀（如 `.pdf.pdf`）
- **第三方文献**：学术 PDF 文件名含下划线视为合规（Zotero / Google Scholar 惯例）

详细规范见 `schemas/naming.md (见附录 schemas/naming.md)`。

### 引用格式

默认 GB/T 7714（中文期刊标准），详细著录格式见 `schemas/citation-format.md (见附录 schemas/citation-format.md)`。

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
│   ├── SRTP.md               ← SRTP 专项规则（替代原 papers/projects/SRTP.md (见附录 projects/SRTP.md)）
│   └── thesis.md             ← 毕业论文占位（待启用）
├── schemas/
│   ├── folder-structure.md   ← 6 模块 Lit/Notes/Code/Data/Docs/Drafts 规范
│   ├── citation-format.md    ← GB/T 7714 著录格式
│   └── naming.md             ← 文件/文件夹命名规范
└── shared/
    └── README.md             ← 子文件间共享说明（暂占位）
```

---
## 附录: projects/SRTP.md

# SRTP Project Config — 01-SRTP 专项规则

> 课题「电动装载机多源能量-热系统协同管理与控制策略研究」
> 适用：`D:\Cloud\Research\01-SRTP\` 及关联目录

---

## 加载指引

加载 `papers` 后，本文件提供 SRTP 专项补充规则。

---

## 目录结构

按 `schemas/folder-structure.md` 的 6 模块布局：

```
01-SRTP/
├── Lit/
│   ├── Papers/{English,Chinese}/
│   ├── Patents/
│   ├── 文献汇总表.xlsx
│   └── publication.bib
├── Notes/           （阅读笔记、组会记录、导师沟通纪要）
├── Code/            （仿真模型代码）
├── Data/            （实验数据、仿真结果）
├── Docs/            （申报书、指南）
└── Drafts/          （论文草稿、中期报告）
```

---

## 表格管理

### 主表（文献汇总表.xlsx）

**唯一的文献数据库**，三张工作表：

| 工作表 | 当前内容 | 排序规则 |
|---|---|---|
| 中文论文 | 8 篇 | 第一作者姓氏拼音升序 |
| 英文论文 | 38 篇 | 第一作者姓氏字母升序 |
| 中文专利 | 4 件 | 专利权人拼音升序 |

**列结构**（18 列，完整版）：

```
序号 → 阅读状态 → 标题 → 作者 → 年份 → 期刊/来源 → DOI →
卷/期/页码 → 是否有原件 → Vault笔记 → 标准引用 → 与课题关联度 →
关联度说明 → 摘要 → 关键词 → 方法&场景 → 核心结论/贡献 → 实验数据规模
```

### 表格维护原则

- **主表唯一**：不接受导出副本、草稿版本与主表并存
- **冗余即删**：incoPat 原始导出、WoS 导出残骸、早期草稿一旦汇总到主表即删除
- **结构变更先确认**：增删列、合并列等操作先出方案，用户确认后执行
- **覆盖保存**：修改主表时直接覆盖，不产生 .bak / .fixed / _tmp 版本

### 文献清单导出

向师姐/导师提交时，从主表提取子集生成 `文献清单_GB7714.xlsx`：

- 三个独立工作表：中文论文 / 中文专利 / 英文论文
- 各表独立编号，从 1 开始
- 9 列：`序号 → 阅读状态 → 标准引用 → 标题 → 作者 → 期刊/来源 → DOI → 摘要 → 与课题关联度`
- 阅读状态按实际填写（如「未读」），不虚构

---

## 清理原则

- **冗余 xlsx 立即删**：incoPat 时间戳导出、WoS 导出、早期草稿
- **空目录可保留**：如 `Papers/Chinese/`，为后续填充留占位
- **PDF 不重复存储**：同一文献只存一份
- **命名异常修复**：双后缀（`.pdf.pdf`）、临时文件名需手工修正
- **操作前先出方案**：涉及大规模文件迁移或删除时，先输出目标结构再执行

---

## 与通用规则的差异

本 SRTP 配置**不修改** papers 通用规则，只补充：

1. **主表唯一性原则**（更严格）
2. **导出清单命名约定**（`文献清单_GB7714.xlsx`）
3. **18 列完整版** vs 通用导出的 9 列精简版

如未来有新课题（如 02-Thesis），应新建 `projects/thesis.md` 并写自己的专项规则。

---
## 附录: projects/thesis.md

# Thesis Project Config — 占位

> 毕业论文专用配置。**当前未启用**——等启动 02-Thesis 时填充。

---

## 何时启用

- 用户提到"毕业论文"、"thesis"、"02-Thesis"
- 或 Research/02-Thesis/ 目录创建时

---

## 待填充内容

启动时需要确定：
- 课题方向
- 是否有外部合作（如 SRTP 延伸 / 实验室分配课题）
- 引用格式偏好（默认 GB/T 7714，与 SRTP 一致）
- 草稿版本管理策略（git / 手动）
- 模板（如学校提供的 Word 模板路径）

---

## 当前状态

- ⏸ 占位，未启用
- 📂 预期目录：`D:\Cloud\Research\02-Thesis/`
- 🔗 与 SRTP 的关系：可继承 SRTP 的 schemas/folder-structure.md 和 schemas/citation-format.md

---

## 占位规则

未启用期间，本文件不应被加载。如 Agent 误触发，应输出「02-Thesis 尚未启用，请先创建目录或确认课题方向」。

---
## 附录: schemas/folder-structure.md

# Folder Structure Schema — 课题内部 6 模块规范

> 所有 Research/{课题}/ 内部统一使用 6 模块布局。

---

## 6 模块总览

```
{课题根}/
├── Lit/         文献库（PDF、专利、bib、汇总表）
├── Notes/       笔记（阅读笔记、组会记录、导师沟通）
├── Code/        代码与仿真模型
├── Data/        实验数据、仿真结果
├── Docs/        项目管理文档（申报书、指南）
└── Drafts/      论文草稿、中期报告、结题交付物
```

---

## Lit/ 内部结构

```
Lit/
├── Papers/
│   ├── English/     英文学术论文 PDF
│   └── Chinese/     中文学术论文 PDF
├── Patents/         专利 PDF（纯文献，不含表格）
├── 文献汇总表.xlsx   主文献数据库
├── publication.bib   BibTeX 文献库
└── 文献整理参考模板.docx
```

**规则**：
- PDF 只放在 Papers/{English,Chinese}/ 和 Patents/，不得散落他处
- 表格类文件不得进入 Papers/ 或 Patents/
- 每个子目录职责单一，不混放不同类型文件
- 空目录可保留占位（如 Chinese/），不主动删除

---

## 各模块内容定义

| 模块 | 内容 | 不应放 |
|---|---|---|
| Lit/Papers/English/ | 英文学术论文 PDF | 中文论文、表格 |
| Lit/Papers/Chinese/ | 中文学术论文 PDF | 英文论文、表格 |
| Lit/Patents/ | 专利 PDF | 论文、表格 |
| Lit/文献汇总表.xlsx | 主文献数据库（唯一权威表） | — |
| Lit/publication.bib | BibTeX 文献库 | 非学术引用 |
| Notes/ | 阅读笔记、组会纪要、导师沟通 | 大型 PDF |
| Code/ | 仿真代码、数据处理脚本 | Office 文档 |
| Data/ | 原始实验数据、仿真结果 | 代码 |
| Docs/ | 申报书、项目指南 | 实验数据 |
| Drafts/ | 论文草稿、中期报告 | 终稿（终稿移到 Drafts/final/） |

---

## Vault/Research/{课题}/ 笔记结构

```
Vault/Research/{课题}/
├── Papers/          每篇文献一个 .md，以 Citekey 命名
├── 项目总览.md       课题整体说明
└── {Topic}/         按主题分组的笔记
```

**笔记命名**：`{第一作者姓氏小写}{年份}{标题首词小写}.md`，如 `zhou2026a.md`

---
## 附录: schemas/naming.md

# Naming Schema — Research/ 命名规范

> 与 filesystem §2 一致，Research/ 专项补充。

---

## 课题根目录命名

- **格式**：`{两位数}-{单英文单词}`（如 `01-SRTP`、`02-Thesis`）
- **首字母大写**，禁止下划线
- **禁止**：缩写（如 `ML` 而非 `MachineLearning`，除非已约定）、中文

**示例**：
- ✅ `01-SRTP`
- ✅ `02-Thesis`
- ❌ `01-srtp`（应首字母大写，除非约定）
- ❌ `01-s-r-t-p`（单词内不应拆字符）
- ❌ `01_Project`（下划线）

---

## 内部 6 模块命名

固定使用以下单词（来自原 srtp-research-rules + filesystem）：

| 模块 | 单词 | 内容 |
|---|---|---|
| 文献库 | Lit | PDF、专利、bib、汇总表 |
| 笔记 | Notes | 阅读笔记、组会记录、导师沟通 |
| 代码 | Code | 仿真模型 |
| 数据 | Data | 实验数据、仿真结果 |
| 文档 | Docs | 申报书、指南 |
| 草稿 | Drafts | 论文草稿、报告 |

---

## Lit/ 内部命名

| 子目录 | 命名 | 内容 |
|---|---|---|
| 英文学术论文 | `Papers/English/` | 英文学术论文 PDF |
| 中文学术论文 | `Papers/Chinese/` | 中文学术论文 PDF |
| 专利 | `Patents/` | 专利 PDF |
| 主表 | `文献汇总表.xlsx` | 主文献数据库（唯一权威表） |
| BibTeX | `publication.bib` | BibTeX 文献库 |
| 模板 | `文献整理参考模板.docx` | 参考模板 |

---

## 文献 PDF 文件命名

按惯例，文献 PDF 文件名**允许下划线**（与全局禁下划线规则冲突，但学术检索工具 Zotero / Google Scholar 识别下划线分隔的关键词）：

**推荐格式**：
```
{年份}_{作者/机构}_{标题关键词}_{类型}.pdf
```

**示例**：
- ✅ `2025_NUAA_CN121341270A_Multi_Mode_Steering_Cooperative_Control.pdf`
- ✅ `2024_Breton_Tech_CN119489657A_Vehicle_Thermal_Management_Integration.pdf`
- ✅ `2026_zhou_energy_management.pdf`
- ❌ `2026NUAA_Multi Mode Steering.pdf`（无下划线分隔，年份难识别）

**类型后缀**：英文学术论文可省略，专利 / 中文 / 其他必须带。

---

## 表格命名

| 表格 | 命名 |
|---|---|
| 主文献数据库 | `文献汇总表.xlsx`（唯一） |
| 导出给师姐/导师 | `文献清单_GB7714.xlsx` |
| 备份/快照 | `文献汇总表_YYYYMMDD.xlsx`（仅备份用） |

---

## 笔记命名（Vault/Research/）

格式：`{第一作者姓氏小写}{年份}{标题首词小写}.md`

**示例**：
- ✅ `zhou2026energy.md`
- ✅ `smith2025review.md`
- ❌ `zhou_2026_energy.md`（下划线——但这是 citekey 命名约定的子集，可保留）
- ❌ `ZHOU2026energy.md`（首字母不应大写）

**YAML frontmatter**（必填）：
```yaml
---
title: 论文标题
authors: 作者列表
year: 年份
journal: 期刊名
doi: DOI
tags: [主题关键词]
citekey: zhou2026energy
status: unread | reading | read | cited
---
```

---

## 禁止规则

| 禁止 | 反例 | 改法 |
|---|---|---|
| 空格 | `paper 1.pdf` | `paper-1.pdf` |
| 双后缀 | `paper.pdf.pdf` | `paper.pdf` |
| 中英混杂 | `paper笔记.md` | `paper-notes.md` 或 `论文笔记.md` |
| 下划线（除文献 PDF） | `extract_outline.py` | `extract-outline.py` |
| 无意义缩写 | `mgt.pdf` | `management.pdf` |

---
## 附录: schemas/citation-format.md

# Citation Format Schema — GB/T 7714 著录格式

> 中国学术期刊文献著录标准。所有 Research/ 下的文献引用必须遵循。

---

## 排序规则

- **中文文献在前，英文文献在后**
- 中文按第一作者姓氏拼音升序
- 英文按第一作者姓氏字母升序
- 同一作者多篇按年份升序；同一年加 a, b, c 区分
- 各组独立编号（中文从 1 开始，英文从 1 开始）

---

## 著录格式

### 期刊论文 [J]

```
作者. 题名[J]. 期刊名, 年份, 卷(期): 页码.
```

**示例**：
- 中文：刘海洋. 电动装载机能量管理策略研究[J]. 机械工程学报, 2024, 60(5): 112-120.
- 英文：Smith J A. Energy management for hybrid electric vehicles[J]. IEEE Transactions, 2025, 32(4): 1023-1035.

### 学位论文 [D]

```
作者. 题名[D]. 保存地: 保存单位, 年份.
```

**示例**：
- 张三. 纯电动汽车热管理系统优化[D]. 北京: 清华大学, 2024.

### 专利 [P]

```
专利权人. 专利名: 专利号[P]. 公告日期.
```

**示例**：
- 北屿大学. 一种电动装载机能量热管理集成系统: CN123456789A[P]. 2024-05-15.

### 专著 [M]

```
作者. 书名[M]. 出版地: 出版社, 年份.
```

### 电子文献 [EB/OL]

```
作者. 题名[EB/OL]. 出版地: 出版者, 出版年(更新或修改日期)[引用日期]. 获取和访问路径.
```

---

## 文献类型标识表

| 文献类型 | 标识 |
|---|---|
| 期刊论文 | J |
| 学位论文 | D |
| 专利 | P |
| 专著 | M |
| 电子文献 | EB/OL |
| 会议论文 | C |
| 标准 | S |
| 报纸文章 | N |

---

## 引用注意事项

1. **作者**：3 人以下全部列出，3 人以上列前 3 人后加 "等"（中文）/ "et al"（英文）
2. **标点**：中文用全角符号（，。：；），英文用半角（, . : ;）
3. **页码**：起止页码用 "-"（英文）/ "—"（中文不一致时优先用半角）
4. **DOI**：期刊论文建议附 DOI（如果原文给出）
5. **大写**：英文作者姓名首字母大写，期刊名按原文（专有名词大写）
6. **BibTeX 字段**：用 `author`, `title`, `journal`, `year`, `volume`, `number`, `pages`, `doi` 标准字段

---

## BibTeX 输出示例

```bibtex
@article{smith2025energy,
  author = {Smith, John A. and Doe, Jane B.},
  title = {Energy Management for Hybrid Electric Vehicles: A Review},
  journal = {IEEE Transactions on Vehicular Technology},
  year = {2025},
  volume = {32},
  number = {4},
  pages = {1023--1035},
  doi = {10.1109/TVT.2025.123456}
}

@patent{campus2024electric,
  author = {北屿大学},
  title = {一种电动装载机能量热管理集成系统},
  number = {CN123456789A},
  year = {2024},
  month = {5},
  day = {15}
}
```
