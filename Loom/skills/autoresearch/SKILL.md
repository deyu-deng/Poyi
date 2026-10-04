---
name: autoresearch
description: "自主研究循环：接收一个主题，执行迭代网页搜索与抓取，合成发现并全部归档到 wiki（concepts/entities/sources + 综合页 Research: Topic）。基于 Karpathy autoresearch，最大 3 轮，带 web 安全卫生与成本预算。 触发词：自主研究、调研、research、深度研究、查资料。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": ["ingest"]}
---
# autoresearch: 自主研究循环

你是研究 Agent。接收一个主题 → 执行迭代网页搜索 → 合成发现 → 全部归档到 wiki。用户拿到的是 wiki 页面，不是聊天回复。

基于 Karpathy 的 autoresearch 模式：`program.md` 配置目标与约束，循环跑到深度上限，输出直接进入知识库。

---

## Poyi 适配说明

原始 claude-obsidian 版本依赖 Claude Code 的 WebFetch/WebSearch 工具和 wiki-lock 并发控制。Poyi 版本适配：

- **搜索**：`web_search`（替换 WebSearch）
- **抓取**：`web_fetch`（替换 WebFetch），优先用 `defuddle` 清洗
- **写入**：直接文件系统 `write_file`（替换 transport 层）
- **并发**：跳过 wiki-lock（Poyi 单 Agent 顺序执行，无竞争）
- **路由**：`wiki-mode` skill 管理 wiki 目录拓扑
- **边界选择**：跳过 `boundary-score.py`（不适用），直接走话题选择 C 路径

---

## 开始前

读取 `references/program.md` 加载研究目标与约束。此文件可用户配置。

---

## 话题选择

当用户说 `/autoresearch [topic]` 或"研究一下 X"时，使用给定话题原样执行。

当无显式话题时，直接问："研究什么主题？"

---

## 研究循环

```
Input: topic

Round 1. 广撒网
1. 将 topic 拆解为 3-5 个不同搜索角度
2. 每个角度：2-3 次 web_search 查询
3. 每个角度前 2-3 条结果：web_fetch 抓取全文
4. 从每篇提取：关键断言、实体、概念、开放问题

Round 2. 填补缺口
5. 识别 Round 1 缺失或矛盾之处
6. 定向搜索每个缺口（最多 5 次查询）
7. 抓取每个缺口的顶部结果

Round 3. 合成检验（可选，缺口仍存时）
8. 若主要矛盾或缺失片段仍存在：再做一次定向搜索
9. 否则：进入归档

最大轮数：3（由 program.md 设定）。达到深度上限或最大轮数时停止。
```

---

## Web 安全卫生

每次 web_fetch 前和写入前应用以下防护：

1. **URL 验证**：仅允许 `http(s)://`，拒绝 `file://`、`javascript:`、`data:`、内网地址
2. **内容消毒**：写入前剥离 `<script>`/`<iframe>`/`<style>`；转义 `[[` 和 `]]` 防止注入 wikilink；拒绝正文内 `---` YAML 分隔符；截断到 ~50KB
3. **成本预算**：完整研究最多 3轮×5源×3角度≈45 次 web_fetch。研究高频/深度话题前告知用户成本预期
4. **失败处理**：抓取失败（超时/4xx/5xx/内容过大）→ 记录 URL+原因到 wiki/log.md，继续循环。不要中止。不要静默吞掉——每个跳过的源都是需要记录的事实

---

## 归档结果

研究完成后，创建以下页面：

**wiki/concepts/**。每个重要概念一页
- 检查 index 先：更新已有概念页而非创建重复

**wiki/entities/**。每个重要人物/组织/产品一页
- 检查 index 先：更新已有实体页

**wiki/sources/**。每个主要参考源一页
- 使用 source frontmatter（type, source_type, author, date_published, url, confidence, key_claims）
- 正文：源摘要及其对主题的贡献

**wiki/questions/**。一篇主合成页 `Research: [Topic]`
- 此为最终产物，所有发现汇总于此
- 段式：Overview, Key Findings, Entities, Concepts, Contradictions, Open Questions, Sources
- 完整 frontmatter，related 链接到本次创建的所有页面

---

## 合成页模板

```markdown
---
type: synthesis
title: "Research: [Topic]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - research
  - [topic-tag]
status: developing
related:
  - "[[本次创建的每个页面]]"
sources:
  - "[[wiki/sources/Source 1]]"
  - "[[wiki/sources/Source 2]]"
---

# Research: [Topic]

## Overview
[2-3 句总结]

## Key Findings
- Finding 1 (Source: [[Source Page]])
- Finding 2 (Source: [[Source Page]])

## Key Entities
- [[Entity Name]]: 角色/意义

## Key Concepts
- [[Concept Name]]: 一行定义

## Contradictions
- [[Source A]] 说 X。[[Source B]] 说 Y。[哪个更可信及原因]

## Open Questions
- [研究未完全回答的问题]
- [需要更多源的缺口]

## Sources
- [[Source 1]]: author, date
- [[Source 2]]: author, date
```

---

## 归档后

1. 更新 `wiki/index.md`。新页面加入对应分类
2. 在 `wiki/log.md` 顶部追加：
   ```
   ## [YYYY-MM-DD] autoresearch | [Topic]
   - Rounds: N
   - Sources found: N
   - Pages created: [[Page 1]], [[Page 2]], ...
   - Synthesis: [[Research: Topic]]
   - Key finding: [一句话]
   ```
3. 更新 `wiki/hot.md` 加入研究摘要

---

## 向用户报告

研究完成后报告：

```
Research complete: [Topic]

Rounds: N | Searches: N | Pages created: N

Created:
  wiki/questions/Research: [Topic].md (synthesis)
  wiki/sources/[Source 1].md
  wiki/concepts/[Concept 1].md
  wiki/entities/[Entity 1].md

Key findings:
- [Finding 1]
- [Finding 2]
- [Finding 3]

Open questions filed: N
```

---

## 约束

遵循 `references/program.md` 中的限制：
- 最大轮数（默认 3）
- 每会话最大页面数（默认 15）
- 置信度评分规则
- 源偏好规则

若约束与完整性冲突：遵守约束，在 Open Questions 中标注省略内容。
*（内容由AI生成，仅供参考）*
