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