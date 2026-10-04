<!-- source: lint -->
---
name: lint
description: "Wiki 健康检查：每 10-15 次 ingest 或每周运行，执行 10 项检查（孤立页、死链、过期主张、缺失页、frontmatter 缺口、命名违规、写作风格等）。输出 lint-report，自动修复前先询问；附 Dataview 仪表盘与 Canvas 地图。 触发词：lint、wiki体检、死链检查、知识库健康。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": ["ingest"]}
---
# lint: Wiki 健康检查

每 10-15 次 ingest 后，或每周运行一次。自动修复前先询问。将 lint 报告输出到 `wiki/meta/lint-report-YYYY-MM-DD.md`。

---

## Lint 检查项（10 项）

按顺序执行：

1. **孤立页面**。没有任何入站 wikilinks 指向的 wiki 页面。
2. **死链接**。指向不存在页面的 wikilinks。
3. **过期主张**。已被更新源推翻或更新了的老断言。
4. **缺失页面**。在多页中提到但没有自己页面的概念或实体。
5. **缺失交叉引用**。页面中提到了实体但没有链接。
6. **Frontmatter 缺口**。缺少必需字段（type, status, created, updated, tags）的页面。
7. **空白 section**。标题下没有内容的段落。
8. **过期 index 条目**。`wiki/index.md` 中指向已改名或已删除页面的条目。
9. **命名规范违反**。文件名未用 Title Case with spaces、文件夹未用 lowercase-dash、wikilinks 未精确匹配文件名。
10. **写作风格问题**。非声明式现在时、缺源引用、缺 `> [!gap]` 标注的不确定性、缺 `> [!contradiction]` 标注的矛盾。

---

## 命名规范

| 元素 | 规范 | 示例 |
|------|------|------|
| 文件名 | Title Case with spaces | `Machine Learning.md` |
| 文件夹 | lowercase-dash | `wiki/data-models/` |
| Tags | 小写、层级式 | `#domain/architecture` |
| Wikilinks | 精确匹配文件名 | `[[Machine Learning]]` |

文件名在 vault 中必须唯一。Wikilinks 无路径工作依赖文件名唯一。

---

## 写作风格检查

Lint 时标记违反以下风格的页面：

- 非声明式现在时（"X basically does Y" → 应为 "X does Y"）
- 主张缺源引用（`(Source: [[Page]])`）
- 不确定性未用 `> [!gap]` 标注
- 矛盾未用 `> [!contradiction]` 标注

---

## Lint 报告格式

创建于 `wiki/meta/lint-report-YYYY-MM-DD.md`：

```markdown
---
type: meta
title: "Lint Report YYYY-MM-DD"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [meta, lint]
status: developing
---

# Lint Report: YYYY-MM-DD

## Summary
- Pages scanned: N
- Issues found: N
- Auto-fixed: N
- Needs review: N

## Orphan Pages
- [[Page Name]]: no inbound links. Suggest: link from [[Related Page]] or delete.

## Dead Links
- [[Missing Page]]: referenced in [[Source Page]] but does not exist. Suggest: create stub or remove link.

## Missing Pages
- "concept name": mentioned in [[Page A]], [[Page B]], [[Page C]]. Suggest: create a concept page.

## Frontmatter Gaps
- [[Page Name]]: missing fields: status, tags

## Stale Claims
- [[Page Name]]: claim "X" may conflict with newer source [[Newer Source]].

## Cross-Reference Gaps
- [[Entity Name]] mentioned in [[Page A]] without a wikilink.

## Stale Index Entries
- "[[Old Name]]" in index points to deleted page. Suggest: remove entry.

## Naming Convention Violations
- `bad-filename.md` should be `Bad Filename.md`.
- [[wrong-link-name]] should be [[Correct Name]].

## Writing Style Issues
- [[Page Name]]: non-declarative tone, missing source citations.
```

---

## Dataview 仪表盘

创建或更新 `wiki/meta/dashboard.md`，包含以下 Obsidian Dataview 查询：

````markdown
---
type: meta
title: "Dashboard"
updated: YYYY-MM-DD
---
# Wiki Dashboard

## Recent Activity
```dataview
TABLE type, status, updated FROM "wiki" SORT updated DESC LIMIT 15
```

## Seed Pages (Need Development)
```dataview
LIST FROM "wiki" WHERE status = "seed" SORT updated ASC
```

## Entities Missing Sources
```dataview
LIST FROM "wiki/entities" WHERE !sources OR length(sources) = 0
```

## Open Questions
```dataview
LIST FROM "wiki/questions" WHERE answer_quality = "draft" SORT created DESC
```
````

---

## Canvas 地图

创建或更新 `wiki/meta/overview.canvas`，生成可视化域地图：

```json
{
  "nodes": [
    {
      "id": "1",
      "type": "file",
      "file": "wiki/overview.md",
      "x": 0, "y": 0,
      "width": 300, "height": 140,
      "color": "1"
    }
  ],
  "edges": []
}
```

每个域页面一个节点。用边连接有显著交叉引用的域。颜色映射到 CSS 方案：1=蓝，2=紫，3=黄，4=橙，5=绿，6=红。节点颜色根据页面 type 使用对应的 graph view 颜色。

---

## 自动修复前置

始终先展示 lint 报告。询问："应该自动修复，还是逐项审查？"

可安全自动修复的：
- 添加缺失 frontmatter 字段（含占位值）
- 为缺失实体创建 stub 页面
- 为未链接的提及添加 wikilinks
- 移除过期 index 条目
- 修复命名违规

需要审查后修复的：
- 删除孤立页面（可能故意隔离）
- 解决矛盾（需要人工判断）
- 合并重复页面

---

## How to think — 10 原则映射

| # | 原则 | 在此的应用 |
|---|------|-----------|
| 1 | OBSERVE (外) | 扫描每一页、每个 wikilink、每个 frontmatter 块。不因大小或表面明显而跳过。 |
| 2 | OBSERVE (内) | 我是否偏向"看起来没问题"？假装你是一个恶意读者，在找真正的问题。 |
| 3 | LISTEN | 用户在本会话中提到具体担忧了吗？优先处理那些而非通用检查。 |
| 4 | THINK | 哪些检查重要？按严重性分层（BLOCKER / HIGH / MEDIUM / LOW），不按修复容易程度。 |
| 5 | CONNECT (横) | 孤儿 + 死链 + frontmatter 缺口的模式常共现。聚类发现揭示根因。 |
| 6 | CONNECT (系) | Dataview 仪表盘 + Canvas 概览 — 多重 lint 表示面。 |
| 7 | FEEL | Lint 报告应赋权而非羞辱。可操作项胜过详尽目录。 |
| 8 | ACCEPT | 某些 lint 发现是刻意为之（设计性孤立、有意 stub）。标记，不强制。 |
| 9 | CREATE | Lint 报告写入 `wiki/meta/lint-report-YYYY-MM-DD.md`，分层发现。 |
| 10 | GROW | 重复出现的 lint 发现 → 流程改进目标，非一次性修复。 |
