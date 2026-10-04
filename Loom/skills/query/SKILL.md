---
name: query
description: "Wiki 查询引擎：策略性读取、精准回答、主动归档让知识复利。三层查询（Quick/Standard/Deep）按复杂度匹配深度；优先 hot.md→index→页面，附 wikilink 引用，好答案归档回 wiki。 触发词：wiki查询、查wiki、query。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": []}
---
# query: Wiki 查询引擎

Wiki 已经完成了综合分析工作。策略性读取，精准回答，并将好答案归档回去让知识复利。

---

## 三层查询模式

按问题复杂度选择深度：

| 模式 | 触发 | 读取内容 | Token 成本 | 最适合 |
|------|------|---------|------------|--------|
| **Quick** | `query quick: ...` 或简单事实性问题 | hot.md + index.md only | ~1,500 | "X 是什么？"、日期查找、快速事实 |
| **Standard** | 默认（无标记） | hot.md + index + 3-5 页 | ~3,000 | 大多数问题 |
| **Deep** | `query deep: ...` 或 "thorough""comprehensive" | 全 wiki + 可选联网 | ~8,000+ | "对比 A vs B"、综合分析、差距分析 |

---

## Quick 模式

1. 读 `wiki/hot.md`。如果能回答问题，立即响应。
2. 不能则读 `wiki/index.md`。扫描描述找答案。
3. 在 index 摘要中找到就回复，不要打开任何页面。
4. 找不到则说："不在快速缓存中。作为标准查询运行？"

在 Quick 模式下不要打开单个 wiki 页面。

---

## Standard 查询工作流

1. **先读** `wiki/hot.md`。可能已有答案或直接相关上下文。
2. **读** `wiki/index.md`，找最相关页面（扫描标题和描述）。
3. **读**那些页面。沿 wikilinks 深度-2 追踪关键实体。不更深。
4. **综合**答案。用 wikilinks 引用来源：`(Source: [[Page Name]])`。
5. **主动归档**："这个分析似乎值得保存。是否保存为 `wiki/questions/answer-name.md`？"
6. 如果问题揭示**内容缺口**：说"Wiki 中关于 [子主题] 的信息不足。想找一个源吗？"

---

## Deep 模式

用于综合问题、对比，或"告诉我关于 X 的一切。"

1. 读 `wiki/hot.md` 和 `wiki/index.md`。
2. 识别所有相关 section（concepts, entities, sources, comparisons）。
3. 读每一页相关页面。不跳过。
4. 如果 wiki 覆盖不足，主动联网补充。
5. 综合全面答案，附完整引用。
6. 始终将结果归档为 wiki 页面。Deep 答案太宝贵不能丢失。

---

## Token 纪律

读取最少所需：

| 从……开始 | 成本（约） | 何时停止 |
|----------|-----------|----------|
| hot.md | ~500 tokens | 如果有答案 |
| index.md | ~1000 tokens | 如果可识别 3-5 相关页面 |
| 3-5 wiki 页面 | ~300 tokens/页 | 通常足够 |
| 10+ wiki 页面 | 昂贵 | 仅跨整个 wiki 的综合分析 |

如果 hot.md 已有答案，不读更多。

---

## Index 格式参考

全局 index (`wiki/index.md`) 的结构：

```markdown
## Domains
- [[Domain Name]]: description (N sources)

## Entities
- [[Entity Name]]: role (first: [[Source]])

## Concepts
- [[Concept Name]]: definition (status: developing)

## Sources
- [[Source Title]]: author, date, type

## Questions
- [[Question Title]]: answer summary
```

先扫描 section 标题确定阅读范围。

---

## Domain 子索引格式

每个 domain 目录有 `_index.md` 用于聚焦查找：

```markdown
---
type: meta
title: "Entities Index"
updated: YYYY-MM-DD
---
# Entities

## People
- [[Person Name]]: role, org

## Organizations
- [[Org Name]]: what they do

## Products
- [[Product Name]]: category
```

当问题限定在一个 domain 时使用子索引。窄查询不要读全局 index。

---

## 将答案归档

好答案应复利回到 wiki。不要让洞察消失在聊天历史中。

归档时的 frontmatter：

```yaml
---
type: question
title: "Short descriptive title"
question: "The exact query as asked."
answer_quality: solid
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [question, <domain>]
related:
  - "[[Page referenced in answer]]"
sources:
  - "[[wiki/sources/relevant-source.md]]"
status: developing
---
```

然后写回答正文。包含引用。链接每个提到的概念或实体。

归档后，在 `wiki/index.md` 的 Questions 下添加条目，追加 `wiki/log.md`。

---

## 缺口处理

如果 wiki 无法回答问题：

1. 明确说："Wiki 中关于此的信息不足，无法给出好答案。"
2. 识别具体缺口："我在 [子主题] 方面没有内容。"
3. 建议："想让我搜索这方面的一个源吗？我会帮你读进来。"
4. 不编造。如果问题是关于此 wiki 特定领域的内容，不从训练数据回答。

---

## How to think — 10 原则映射

| # | 原则 | 在此的应用 |
|---|------|-----------|
| 1 | OBSERVE (外) | 先读 hot.md，再读 index.md，再读特定页面。不跳过缓存。 |
| 2 | OBSERVE (内) | 我是否在从训练数据综合而非引用 wiki 页面？检查每个主张的来源。 |
| 3 | LISTEN | 用户的真实问题是什么？表层查询常是更深需求的代理。 |
| 4 | THINK | Quick/Standard/Deep 模式？匹配深度到问题复杂度，不匹配热忱。 |
| 5 | CONNECT (横) | 是否有遗漏的页面会改变答案？回答前交叉检查相关页面。 |
| 6 | CONNECT (系) | Hot cache + index 层叠为单一检索管线。 |
| 7 | FEEL | 引用具体页面，不模糊引用。未来的我想追溯到源页面。 |
| 8 | ACCEPT | Wiki 不能回答时明确说出来。不从训练数据编造。 |
| 9 | CREATE | 附引用的答案 + 如果值得保存主动归档。 |
| 10 | GROW | Wiki 不能回答的问题就是内容缺口——记录为 research 的输入。 |
