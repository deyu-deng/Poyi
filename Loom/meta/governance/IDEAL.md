# Poyi 理想态定义（IDEAL）

> **本文件是系统的「完成标准 / 靶子」。**
> 所有审计、修复、`/poyi lint`、重构都对照本文件判定「做没做完」，不再只修眼前症状、修完又烂。
> 具体差距与进度见 `gap-analysis.md` 与 AGENTS.md 末尾审计日志；本文件只定义「理想长什么样」。

---

## 第一性目的

Poyi 不是一个文件仓库，而是一个**能自我维持的个人知识操作系统**。价值链路：

```
无摩擦捕获（对话 / 想法 / 学习）
   → 变成可链接、可复利的知识
   → 主动辅助学习与项目管理
   → 用户永远不用操心它的结构
```

任何改动若违背这条链路（让人更操心结构、让知识更散落、让系统更靠手动），就是倒退。

---

## 五大理想属性与完成标准（满分 10）

### 1. 结构自洽 — target 9
- 所有活文档路径一律用 `<POYI_ROOT>`，无写死盘符；Windows-only 路径显式标注。
- 命名统一 **kebab-case**（新增内容遵守），不新增「人工智能 AI」式中英混合目录。
- 无幽灵目录、无缺失目录：`Loom/wiki/{concepts,comparisons,entities,sources}` 齐备。
- `AGENTS.md §1` 是物理结构唯一镜像，与 `ls` 实际结果逐项目一致。

### 2. 内容密度 — target 8
- 课程笔记是真内容（已达 ✅）。
- **知识复利层建成**：概念页互相 `[[链接]]`；wiki 子目录填充而非空壳。
- 每条笔记有实质内容；空壳 skeleton 仅允许显式标注「待 ingest」。

### 3. 管线运转 — target 9
- chatlog 消化**每日自动追平**，`digested/` 滞后 ≤ 1 天。
- Inbox 捕获自动发生，不靠手动搬运。
- 提醒 / 雷达 / 机会按 `inbox` skill 节奏自动触发。
- Hot Cache 自动刷新，不靠人手动跑。

### 4. 新鲜度 — target 9
- 所有时间敏感数据滞后 ≤ 1 天。
- journal 不断更；若断更，缺口在 1 天内补记。

### 5. 可信度 — target 9
- **单一事实源**：身份事实只在 `Loom/skills/profile/SKILL.md`；路径约定只在 `AGENTS.md §0`；内在画像只在 `Vault/meta/Persona.md`。禁止在第三处重复事实。
- 无自相矛盾：年级 / 专业 / 路径 / 技能数 / 项目数多处出现时必一致。
- 任何 agent 进入都能读到正确事实，不踩矛盾——且能知道去哪更新。

---

## 硬约束（不可违反）

1. **单一事实源** — 事实只在 profile，内在只在 Persona，路径只在 AGENTS §0。新增事实前先查这三处，不另立。
2. **平台中立** — 活文档一律 `<POYI_ROOT>`，禁止写死 `D:\` 或 `/Users/sample/`（设备专属事实进 `Meta.<os>.md`）。
3. **物理文件系统是最高权威** — 文档允许短暂过期，但接手任何任务前必须核验磁盘，不凭记忆下结论。
4. **可回退** — 结构变更必须 `git commit` 后才能结束；未提交改动会被同步冲掉（已踩过坑）。

---

## 当前状态速览（2026-07-12）

| 维度 | 现状 | 主要缺口 |
|---|---|---|
| 结构自洽 | ~8 | `verifier.py` 已接入 git pre-commit，自动守护「AGENTS §1 ↔ 磁盘」逐项目一致（原 §1 要求）；wiki 三目录已建 + INDEX 枢纽；部分 notes 目录名违反 kebab-case（历史遗留，不动以保 Obsidian 链接） |
| 内容密度 | ~7 | 复利层已建（wiki 三枢纽 + 概念互链）；三目录已填真实实体/来源页（SRTP/Cursor/Antigravity/Aminer），可继续加真实条目 |
| 管线运转 | ~8 | mac 端闭环已通：cursor 导出锁库已修；`aggregate_mac.py` 幂等聚合已建；launchd 每日 3:00 机械聚合已装并实测；WorkBuddy 每日 4:00 语义消化自动化已建；21 天全消化、lag=0。残留：语义消化依赖 WorkBuddy App 在 4:00 运行，否则滞后 ≤1 天；Win 脚本仍硬编码 `D:/`（非 mac 关键路径，待统一） |
| 神经系统（基础设施成熟度） | ~3 | 已补：`git pre-commit` + `verifier.py`（规格↔磁盘一致性审计，对应 claude-obsidian 的 verifier sub-agent / hooks）；系统脚本 15 个。仍缺：transport 抽象层、wiki-lock 多 writer 锁、hybrid retrieval（BM25+rerank）、Canvas 可视化、多 sub-agent（ingest/lint 独立 agent） |
| 新鲜度 | ~5 | journal 曾断更 26 天（已补）；hot cache 手动刷 |
| 可信度 | ~8 | 身份矛盾已修；`verifier.py` 自动拦截「项目数/技能数多处声明不一致」；D:\Projects\Poyi 残留收尾中（Win 脚本待统一） |

> 详细证据与逐项进度见最近一次审计报告。
