<!-- source: save -->
---
name: save
description: "对话归档到 Wiki：取刚讨论的内容归档为永久 wiki 页面（synthesis/concept/source/decision/session 五型）。Wiki 复利——经常 save。含目标根目录决策、frontmatter 模板、保存 vs 跳过标准。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": []}
---
# save: 对话归档到 Wiki

好答案和洞察不应消失在聊天历史中。这个技能取刚刚讨论的内容，归档为永久 wiki 页面。

Wiki 复利。经常 save。

---

## 步骤 0：决定目标根目录

按顺序检查：

1. **用户显式覆盖。** 如果用户说"保存到这个项目的 wiki"/"保存到个人 vault"/指定路径，照做。
2. **项目入口文件声明 `/save` 规则。** 如果 AGENTS.md 或项目入口声明了个人 vault 目标（如 `/Users/sample/Poyi/Loom/`），那就是目标根目录。追加新笔记到 `/log/ingest-log.md` 顶部。
3. **默认。** 当前项目自身的 `wiki/` 目录。

---

## 笔记类型决策

从对话内容判断最合适的类型：

| 类型 | 文件夹 | 使用场景 |
|------|--------|----------|
| synthesis | wiki/questions/ | 多步分析、对比，或回答特定问题 |
| concept | wiki/concepts/ | 解释或定义一个想法、模式、框架 |
| source | wiki/sources/ | 对话中讨论的外部材料摘要 |
| decision | wiki/meta/ | 架构、项目或战略决策 |
| session | wiki/meta/ | 完整对话总结：涵盖一切讨论 |

如果用户指定了类型，用那个。否则根据内容选最匹配的。不确定时用 `synthesis`。

---

## Save 工作流

1. **扫描**当前对话。识别最有价值要保留的内容。
2. **询问**（如果未命名）："这个笔记应该叫什么？"名称保持简短、描述性。
3. **确定**笔记类型（用上方表格）。
4. **提取**对话中所有相关内容。重写为声明式现在时（不是"用户问了 X"而是内容本身）。
5. **创建**笔记于 `<root>/<folder>/Note Title.md`（按 Step 0）。完整 frontmatter。如果同名路径已存在，覆盖前先询问。
6. **收集链接**：识别对话中提到的所有 wiki 页面。添加到 frontmatter 的 `related`。
7. **更新** `wiki/index.md`。在相关 section 顶部添加新条目。
8. **追加** `wiki/log.md`。新条目在顶部：
   ```
   ## [YYYY-MM-DD] save | Note Title
   - Type: [note type]
   - Location: wiki/<folder>/Note Title.md
   - From: conversation on [brief topic description]
   ```
9. **更新** `wiki/hot.md` 反映新添加。
10. **确认**："Saved as [[Note Title]] in wiki/<folder>/."

---

## Frontmatter 模板

```yaml
---
type: <synthesis|concept|source|decision|session>
title: "Note Title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - <tag1>
status: developing
related:
  - "[[Any Wiki Page Mentioned]]"
sources:
  - "[[.raw/source-if-applicable.md]]"
---
```

对于 `question` 类型，添加：
```yaml
question: "The original query as asked."
answer_quality: solid
```

对于 `decision` 类型，添加：
```yaml
decision_date: YYYY-MM-DD
status: active
```

---

## 写作风格

- 声明式、现在时。写知识，不写对话。
- 不写："用户问了 X，Claude 解释了……"
- 写："X 通过 Y 工作。关键洞察是 Z。"
- 包含所有相关上下文。未来会话应能冷读此页。
- 用 wikilinks 链接每个提到的概念、实体或 wiki 页面。
- 适当引用来源：`(Source: [[Page]])`。

---

## 保存 vs 跳过

保存：
- 非显而易见的洞察或综合
- 附有理据的决策
- 花费显著努力的分析
- 可能再次引用的对比
- 研究发现

跳过：
- 机械 Q&A（查找性、答案明显的问题）
- 已在他处记录的设置步骤
- 无持久洞察的临时调试会话
- Wiki 中已有的任何内容

如果已在 wiki 中，更新已有页面而非创建副本。

---

## How to think — 10 原则映射

| # | 原则 | 在此的应用 |
|---|------|-----------|
| 1 | OBSERVE (外) | 读完整对话。识别实际决策和综合，非逐字转写。 |
| 2 | OBSERVE (内) | 我是否在 save-everything 模式？某些对话没有持久洞察；Skip 标准有它的理由。 |
| 3 | LISTEN | 用户指定了目标或类型吗？他们的显式覆盖第一；默认第二。 |
| 4 | THINK | 选目标根目录（Step 0），再选笔记类型，再选文件夹。 |
| 5 | CONNECT (横) | 这个内容是否已有 wiki 页面？更新 vs 新建是关键——重复污染 index。 |
| 6 | CONNECT (系) | Index + log + hot cache + frontmatter relations 全部一起更新——原子性很重要。 |
| 7 | FEEL | 未来我能冷读的文件名；支持搜索的 frontmatter。避免噪声淹没信号。 |
| 8 | ACCEPT | 某些对话不值得保存。尊重 Skip 标准；不归档一切。 |
| 9 | CREATE | 写笔记，追加到 log 顶部，更新 index，刷新 hot cache。 |
| 10 | GROW | 被跳过的 save 也是信号——什么阈值过滤了它们？随时间精炼类型表。 |
