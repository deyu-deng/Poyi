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