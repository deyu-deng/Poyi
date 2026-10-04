---
name: ingest
description: "知识入库器：把外部源（文件/URL/图片）与正在进行的对话都写入 wiki 并交叉引用一切。源吞入支持 Delta 去重、矛盾检测、批量；会话捕获支持五型分类（synthesis/concept/source/decision/session）与保存 vs 跳过判断。所有写入用 Obsidian Flavored Markdown。触发词：ingest、吞入、处理文件/网页/PDF、归档进知识库、整理聊天记录进知识库、对话归档、保存对话、存这次讨论、save。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": []}
---
# ingest: 源文件吞入

读取源文件，写入 wiki，交叉引用一切。单个源通常触及 8-15 个 wiki 页面。

**语法标准**：所有写入使用 Obsidian Flavored Markdown。Wikilinks 使用 `[[Note Name]]`，callout 使用 `> [!type] Title`，嵌入使用 `![[file]]`，属性使用 YAML frontmatter。

---

## Delta 追踪

吞入前检查 `.raw/.manifest.json`，避免重复处理未变化的源。

```json
{
  "sources": {
    ".raw/articles/slug-2026-04-08.md": {
      "hash": "abc123",
      "ingested_at": "2026-04-08",
      "pages_created": ["wiki/sources/slug.md", "wiki/entities/Person.md"],
      "pages_updated": ["wiki/index.md"]
    }
  }
}
```

流程：
1. 计算文件 hash：`md5 -q <file>`（macOS）或 `md5sum`（Linux）。
2. 检查 manifest 中是否已有相同 hash。有则跳过，报告"已吞入（未变化）。使用 force 可重新吞入。"
3. 吞入完成后记录 `{hash, ingested_at, pages_created, pages_updated}`。

用户说"force ingest"或"重新吞入"时跳过 delta 检查。

---

## URL 吞入

触发：用户传入 `https://` 开头的 URL。

步骤：
1. 抓取页面全文。
2. **清洗**（可选）：如果有 `defuddle` 命令可用，运行 `defuddle [url]` 剥离广告、导航和杂波，通常节省 40-60% token。未安装则直接用原始内容。
3. 从 URL 路径末尾派生 slug（小写、空格转连字符、去查询参数）。
4. 保存到 `.raw/articles/[slug]-[YYYY-MM-DD].md`，带 frontmatter：
   ```markdown
   ---
   source_url: <url>
   fetched: YYYY-MM-DD
   ---
   ```
5. 按「单源吞入」流程继续处理（文件已位于 `.raw/`）。

---

## 图片/视觉吞入

触发：用户传入图片文件（`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`, `.avif`）。

步骤：
1. 读取图片，提取所有文字（OCR）、识别关键概念、实体、图表、数据。
2. 保存描述到 `.raw/images/[slug]-[YYYY-MM-DD].md`：
   ```markdown
   ---
   source_type: image
   original_file: <原始路径>
   fetched: YYYY-MM-DD
   ---
   # Image: [slug]
   [完整描述、转录文字、可见实体等]
   ```
3. 若图片不在 vault 内，复制到 `_attachments/images/[slug].[ext]`。
4. 按「单源吞入」流程处理描述文件。

使用场景：白板照片、截图、图表、信息图、文档扫描件。

---

## 单源吞入（10 步流程）

触发：用户放入 `.raw/` 的文件，或粘贴内容。

1. **完整读取**源文件。不跳读。
2. **与用户讨论**关键收获。问："应该强调什么？粒度如何？"如果用户说"直接吞"，跳过此步。
3. **创建 source 页面**于 `wiki/sources/`。使用 source frontmatter schema（见下方）。引用 `references/frontmatter.md` 的完整 schema。
4. **创建或更新 entity 页面**：为每个提到的人物、组织、产品、仓库创建一页。
5. **创建或更新 concept 页面**：为重要思想、框架创建一页。
6. **更新相关 domain 页面**及其 `_index.md` 子索引。
7. **更新 `wiki/overview.md`**，如果整体图景发生变化。
8. **更新 `wiki/index.md`**：为所有新页面添加条目。
9. **更新 `wiki/hot.md`**：反映本次 ingest 的上下文。
10. **追加 `wiki/log.md`**（新条目在顶部）：
    ```markdown
    ## [YYYY-MM-DD] ingest | Source Title
    - Source: `.raw/articles/filename.md`
    - Summary: [[Source Title]]
    - Pages created: [[Page 1]], [[Page 2]]
    - Pages updated: [[Page 3]], [[Page 4]]
    - Key insight: 一句话概括新内容
    ```
11. **检测矛盾**。如果新信息与已有页面冲突，在两页都添加 `> [!contradiction]` callout。

---

## 批量吞入

触发：用户拖入多个文件，或说"全部吞入"。

步骤：
1. 列出所有待处理文件，与用户确认。
2. 逐个处理每个源（走完整单源流程），但源间交叉引用推迟到第 3 步。
3. 全部完成后执行**交叉引用通行证**：检查新页面之间、新页面与已有页面之间的遗漏链接。
4. 最终一次性更新 index、hot cache、log。
5. 报告："处理了 N 个源。创建了 X 页面，更新了 Y 页面。以下是找到的关键连接。"

批量吞入交互较少。超过 30 个源时预期处理时间较长，每 10 个源与用户确认一次。

---

## 会话捕获模式（原 save）

除外部源外，ingest 也捕获**正在进行的对话**——把刚讨论出的值得留存的内容归档为永久 wiki 页面。这是 wiki 复利的核心习惯：**经常捕获**。

触发：用户说"保存这段""归档对话""/save""存这次讨论"，或你判断某段对话有非显而易见的洞察、决策、分析时主动建议捕获。

### 目标根目录决策（Step 0）

按顺序检查：

1. **用户显式覆盖。** 如果用户说"保存到这个项目的 wiki"/指定路径，照做。
2. **项目入口文件声明规则。** 如果 AGENTS.md 或项目入口声明了个人 vault 目标（如 `/Users/sample/Poyi/Loom/`），那就是目标根目录。
3. **默认。** 当前项目自身的 `wiki/` 目录。

### 笔记类型决策（五型）

从对话内容判断最合适的类型：

| 类型 | 文件夹 | 使用场景 |
|------|--------|----------|
| synthesis | wiki/questions/ | 多步分析、对比，或回答特定问题 |
| concept | wiki/concepts/ | 解释或定义一个想法、模式、框架 |
| source | wiki/sources/ | 对话中讨论的外部材料摘要 |
| decision | wiki/meta/ | 架构、项目或战略决策 |
| session | wiki/meta/ | 完整对话总结：涵盖一切讨论 |

如果用户指定了类型，用那个。否则根据内容选最匹配的。不确定时用 `synthesis`。

### 会话捕获工作流

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

### 会话捕获 Frontmatter 模板

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

### 写作风格

- 声明式、现在时。写知识，不写对话。
- 不写："用户问了 X，Claude 解释了……"
- 写："X 通过 Y 工作。关键洞察是 Z。"
- 包含所有相关上下文。未来会话应能冷读此页。
- 用 wikilinks 链接每个提到的概念、实体或 wiki 页面。
- 适当引用来源：`(Source: [[Page]])`。

### 保存 vs 跳过

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

### How to think — 10 原则映射（会话捕获）

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
| 10 | GROW | 被跳过的保存也是信号——什么阈值过滤了它们？随时间精炼类型表。 |

---

## 上下文窗口纪律

Token 预算很重要：

- 先读 `wiki/hot.md`。如果已有相关上下文，不重读完整页面。
- 读 `wiki/index.md` 找已有页面，再创建新页面。
- 每次 ingest 最多读 3-5 个已有页面。需要 10+ 说明你在读太宽。
- 用精确编辑做小改动。不要为改一个字段重读整个文件。
- wiki 页面保持简短：100-300 行。超过 300 行就拆分。
- 用搜索定位特定内容，不读完整页面。

---

## 矛盾检测

> 注意：`[!contradiction]` callout 类型是自定义 callout，定义在 `.obsidian/snippets/vault-colors.css` 中（由 scaffold 自动安装）。启用 snippet 时以红棕色和警告三角图标渲染。缺少 snippet 时 Obsidian 回退到默认 callout 样式，页面仍可用。

当新信息与已有 wiki 页面矛盾时：

在已有页面添加：
```markdown
> [!contradiction] Conflict with [[New Source]]
> [[Existing Page]] claims X. [[New Source]] says Y.
> Needs resolution. Check dates, context, and primary sources.
```

在新 source 页面引用：
```markdown
> [!contradiction] Contradicts [[Existing Page]]
> This source says Y, but existing wiki says X. See [[Existing Page]] for details.
```

不静默覆盖旧主张。标注后让用户决定。

---

## Source Frontmatter Schema

```yaml
---
type: source
title: "Source Title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - tag1
status: developing
related:
  - "[[Related Page]]"
sources:
  - "[[.raw/articles/filename.md]]"
source_type: article | paper | clip | transcript | book | video
author: "Author Name"
date_published: YYYY-MM-DD
confidence: high | medium | low
key_claims:
  - "Claim 1"
  - "Claim 2"
---
```

---

## 禁止事项

- **`.raw/` 下的源文件不可变。** 绝不要修改用户放入 `.raw/` 的文件。`.raw/.manifest.json` 和 `address_map` 是 ingest 自己维护的唯二例外。
- 不创建重复页面。创建前务必检查 index 和搜索。
- 不跳过 log 条目。每次 ingest 必须记录。
- 不跳过 hot cache 更新。它让下次会话保持快速。

---

## How to think — 10 原则映射

| # | 原则 | 在此的应用 |
|---|------|-----------|
| 1 | OBSERVE (外) | 提取前完整读取源文件。长源不断捷径。 |
| 2 | OBSERVE (内) | 我是否偏向源的框架？我的不同意在哪？记录为 contradiction callout。 |
| 3 | LISTEN | 用户的源选择意图——什么让这篇源值得吞入，用户想提取什么？ |
| 4 | THINK | 哪些实体值得建页？哪些概念？什么交叉引用？什么与已有页面的矛盾？ |
| 5 | CONNECT (横) | 这篇源的主张 vs wiki 中已有来源。矛盾是最高信号的发现。 |
| 6 | CONNECT (系) | index + log + hot cache + frontmatter relations 全部一起更新。 |
| 7 | FEEL | 一页在 6 个月后仍有用的页面。跳过填充；偏好综合而非转录。 |
| 8 | ACCEPT | 不是每个主张都值得写入 wiki。编辑判断是 ingest 的一部分，不是待移除的 bug。 |
| 9 | CREATE | source + entity + concept 页面，完整 frontmatter；交叉引用；需要的 contradiction callout。 |
| 10 | GROW | ingest 中途发现的矛盾是最有价值的 wiki 信号。归档为后续跟进的问题，不沉默。 |
