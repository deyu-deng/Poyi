# Skill 使用频率审计与裁剪建议

> 日期: 2026-07-25 · 路线: B（保守裁剪 + 标准化）
> 数据源: `Loom/raw/chatlog/`（30 个每日 digested 摘要 + 4 平台 raw exports，约 109 个 digest 文件 + exports）

## 0. TL;DR

- 30 天聊天日志审计完成。**25 个 Loom 技能中仅 `research` 与 `autoresearch` 是真重复**，其余 4 个"疑似重复"经核查均为独立能力。
- **最大发现**：系统实际最高频的 4 个技能（`message-digest` / `opportunity-scout` / `info-radar` / `humanizer`，合计 722 次/30天）**根本不在 `Loom/skills/` 索引里** —— 索引与现实严重脱节。
- 频率数据噪杂，无法据此单独砍技能；裁剪只能基于"能力重复"论证（这正是 route B 的正确之处）。

## 1. 方法 & 信号分级

| 等级 | 含义 | 可靠性 |
|---|---|---|
| L0 干净 | 显式 `使用 X skill` / 斜杠命令 | 无歧义 |
| L1 中等 | 技能名即触发短语（ingest/lint/save/think…） | 较可靠 |
| L2 噪杂 | 技能名 = 日常词汇（poyi/notes/papers/english…） | 不可靠 |

## 2. 频率证据表（25 个 Loom 技能）

| 技能 | 原始提及 | 干净触发 | 判定 |
|---|---|---|---|
| poyi | 16378 | /poyi ×52 | 核心编排器，必留 |
| research | 5730 | /research ×3 | 与 autoresearch 重复 |
| notes | 3635 | — | 噪杂；但 notes 有独立职责 |
| papers | 3516 | — | 噪杂 |
| english | 2821 | /english ×6 | 留 |
| inbox | 1977 | — | 噪杂 |
| filesystem | 1220 | — | Engineer 核心 |
| review | 1097 | /review ×3 | 留 |
| animation | 1044 | — | Misc |
| think | 823 | — | poyi 编排 |
| campus | 751 | — | 特定词 |
| canvas | 719 | — | 独立可视化 |
| query | 690 | — | 检索层 1 |
| lint | 648 | — | poyi 编排 |
| ingest | 610 | — | poyi 编排 |
| save | 596 | — | poyi 编排 |
| profile | 549 | — | Manager |
| notecraft | 417 | — | 特定词 |
| newproject | 389 | — | Manager |
| exam | 282 | — | Tutor |
| autoresearch | 215 | /research ×3 | 与 research 重复（fuller 实现） |
| defuddle | 162 | — | 网页清洗，独立 |
| wiki-mode | 140 | — | 模式切换 |
| wiki-retrieve | 115 | — | 检索层 2（retrieve 兜底） |
| inbox-cleanup | 40 | — | Manager |

> 注：原始提及含大量日常词汇噪声（如 `poyi`=16378 多为"Poyi 系统"聊天），仅作参考，不能据此砍。

## 3. 关键发现

### 3.1 索引与现实脱节（最严重）
4 个最高频技能**未登记**于 `Loom/skills/`：
- `message-digest` ×449（marvis 每日消化）
- `opportunity-scout` ×176
- `info-radar` ×97
- `humanizer` ×8（另有文件名提及）

合计 722 次/30天，远超任何 Loom 技能。它们只出现在 digested 日志与 `dist/`，不在 `skills/` 目录。需确认：是 marvis-native（应排除在 Poyi 索引外），还是应登记进 `Loom/skills/` + `INDEX.md`。

### 3.2 唯一干净的 Loom 触发
`/poyi`×52, `/english`×6, `/review`×3, `/research`×3。其余 Loom 技能无斜杠/显式触发，靠 poyi 自然语言编排或日常词汇提及。

### 3.3 poyi 是编排器
`poyi/SKILL.md:140-145` 触发表：`ingest/query/lint/save/research/think` 经 NL 触发；`:241` 强制 `wiki-retrieve` 在每次 ingest/save 调用。故这些子技能"无斜杠触发"≠未使用。

### 3.4 频率噪杂，不能单独砍
除 poyi 外，无技能有可靠频率信号。route B 正确：裁剪只能基于"能力重复"论证。

## 4. 裁剪结论（逐个论证，非 blanket）

| 候选 | 核查结论 | 处置 |
|---|---|---|
| research ≈ autoresearch | 两者描述完全一致（Karpathy autoresearch 循环，3 轮，归档 wiki） | ✅ 合并 research→autoresearch |
| wiki-retrieve vs query | wiki-retrieve 自述"query 优先，retrieve 兜底"，两层检索 | ❌ 保留 |
| defuddle vs ingest | 清洗 vs 入库，相邻独立 | ❌ 保留 |
| canvas | 独立可视化引擎，自有 `/canvas` | ❌ 保留 |
| notes vs notecraft | 批量课程笔记规范化(Engineer) vs 双轨学习流(Tutor) | ❌ 保留 |

→ **仅 1 个真重复。25 → 24。**

## 5. 治理缺口

- `manage_skills.py` 仅 `sync`/`create`，**无 `delete` 子命令**，与 AGENTS.md §6 冲突。
- 删除实操：`rm` 目录 + 手动清理 `poyi/SKILL.md:144`、`INDEX.md` 详细条目 + `sync` 自动刷新表格。`sync` 读取现存目录重建表格，故删目录后 `sync` 即从表格剔除 research（合规）。
- 建议后续给 `manage_skills.py` 补 `delete` 子命令。

## 6. 建议执行顺序

1. （先决）确认 cron 4 技能归属 → 决定索引补漏还是排除
2. 执行 research→autoresearch 合并（24 技能）
3. frontmatter 标准化（病灶③）留专项

## 7. 待用户补充

- Marvis 提到"这里还有信息" —— 若其手中有更干净的频率数据，请提供，可替换本报告的 L2 噪杂信号。
