---
type: audit
title: "Poyi 系统对抗性审计报告"
date: 2026-07-01
auditor: 第一性原则对抗性测试
scope: D:\Projects\Poyi 全系统
severity_distribution:
  critical: 3
  medium: 5
  minor: 2
  passed: 10
overall_score: 70
---

# Poyi 系统对抗性审计报告

> **审计方法**：从第一性原则出发，不相信任何文档声明，一切以实际文件系统验证为准。采用对抗性测试方法，主动寻找不一致、缺失、虚假声明。
>
> **审计范围**：物理结构、技能系统、知识系统、自举协议、数据一致性、Git版本控制、腐烂度审计机制
>
> **整体评分**：**70/100** — 系统骨架真实有效，但内容层与自举层存在明显缺陷

---

## 一、审计结论摘要

Poyi 系统**不是虚假项目**，核心骨架真实存在，有完整的 Git 历史和实际使用痕迹。但系统在**内容完整性**和**自举可用性**方面存在显著缺陷，尤其是 Wiki 知识库几乎为空，自举协议存在断点。

| 维度 | 评分 | 说明 |
|---|---|---|
| 系统真实性 | 85/100 | 核心结构真实存在，不是空壳项目 |
| 系统完整性 | 60/100 | 多处结构不一致，内容层薄弱 |
| 自举可用性 | 70/100 | 8步协议可走通7步，但有关键断点 |
| 审计机制有效性 | 80/100 | 腐烂度审计在运作，问题确实在被修复 |
| **整体有效性** | **70/100** | 骨架完整，内容待充实 |

---

## 二、严重问题（🔴 Critical）

### 2.1 Wiki 知识库几乎为空

**问题**：整个 `Loom/wiki/` 目录只有 **12 个文件**，`index.md` 显示所有核心分类（域、实体、概念、源、问题、对比）全部标注"暂无条目，待 ingest"。

**影响**：Poyi 系统定位为"第二大脑"和"知识库"，但核心知识层几乎没有内容。Wiki 系统目前只有骨架，没有血肉。

**证据**：
- `wiki/index.md` 所有分类均为"暂无条目"
- 实际只有 english-data/ 和 review/ 两个目录有少量内容
- 对比分析、实体、概念等核心分类完全为空

---

### 2.2 自举协议存在关键断点

**问题**：AGENTS.md 自举协议第五步明确要求"检查 `Loom/chat-logs/marvis/` 目录 → 按日期找到最近对话"，但该目录**实际不存在**。

**影响**：新 Agent 严格按照自举协议执行时，会在第五步遇到文件不存在的错误，导致接管流程中断。

**证据**：
- `Test-Path "D:\Projects\Poyi\Loom\chat-logs\marvis"` → False
- chat-logs 实际只有 digested/、raw/、scripts/ 三个目录

---

### 2.3 AGENTS.md 结构描述严重不完整

**问题**：作为"唯一事实来源"的 AGENTS.md，其物理结构描述与实际文件系统存在多处不一致：

| 位置 | AGENTS.md 声称 | 实际情况 |
|---|---|---|
| Loom/wiki | 只有 english-data/、review/、meta/ | 还有 comparisons/、concepts/、entities/、sources/ 四个目录 |
| Loom/chat-logs | 有 marvis/、chatgpt/、openai/、windsurf/ 等 | 只有 digested/、raw/、scripts/ 三个目录 |

**影响**：AGENTS.md 作为"单一事实来源"的权威性受损，新 Agent 基于此文件的决策会出现偏差。

---

## 三、中等问题（🟡 Medium）

### 3.1 技能索引路径引用不一致

**问题**：`Loom/skills/INDEX.md` 中 filesystem 技能的 references 字段列出的文件路径（如 `workflow.md`）与实际路径（`references/workflow.md`）不符。

**影响**：按 INDEX.md 路径查找会找不到文件。

---

### 3.2 SRTP 项目缺少 plan.md

**问题**：7 个项目中有 6 个同时拥有 `plan.md` 和 `progress.md`，但 **srtp 项目只有 progress.md，缺少 plan.md**。

**影响**：违反"每个项目含 plan.md（项目计划）和 progress.md（进度代办）"的约定。

---

### 3.3 存在未索引的参考文件

**问题**：`filesystem/references/` 下有 `self-update.md` 文件，但 `INDEX.md` 的 references 列表中未包含此文件。

**影响**：技能索引不完整，Agent 可能遗漏重要参考。

---

### 3.4 Hermes 历史归档目录不存在

**问题**：decay-audit 报告中提到 `Loom/chat-logs/raw/hermes-win/` 是"Hermes 历史归档，保留"，但该目录实际不存在。

**影响**：审计报告的准确性存疑，可能是已删除但未更新审计记录。

---

### 3.5 inbox/shared 目录不存在

**问题**：decay-audit 报告指出 `inbox/SKILL.md` 引用了 `shared/README.md`，但 `inbox/shared/` 目录不存在。此问题在 6 月 30 日审计后**仍未修复**。

---

## 四、轻微问题（🟢 Minor）

### 4.1 animation 和 NoteCraft 没有 SKILL.md

**说明**：这是设计上的差异，不是 bug：
- animation 是 raw-arsenal 类型，入口是 `INDEX.md`
- NoteCraft 入口是 `README.md`，还有子技能 `note-merge`

INDEX.md 中已有明确说明，不影响使用，但与"所有技能都有 SKILL.md"的直觉假设不符。

---

### 4.2 wiki/meta 内容单薄

**说明**：`wiki/meta/` 目录下只有一个 `decisions-2026-06-29.md` 文件，与"仪表盘、lint 报告、约定文档"的定位相比内容较少。

---

## 五、验证通过项（✅ Passed）

### 5.1 技能系统真实有效
- ✅ 23 个技能目录全部存在，数量与声明一致
- ✅ 21 个技能有完整的 SKILL.md（animation 和 NoteCraft 除外，属设计差异）
- ✅ inbox 三模块（digest/radar/scout）文件全部存在
- ✅ papers 技能的 schemas 和 projects 文件全部存在
- ✅ filesystem 技能的 7 个 references 文件全部存在（在 references/ 子目录下）
- ✅ NoteCraft 子技能 note-merge 存在
- ✅ 技能总文件数：126 个

---

### 5.2 项目系统完整
- ✅ 7 个项目目录全部存在（aura/chassis/lab/prism/srtp/vaelis/website）
- ✅ 6 个项目同时拥有 plan.md 和 progress.md
- ✅ 项目索引文件存在且内容详细

---

### 5.3 Git 版本控制真实有效
- ✅ .git 目录真实存在，不是空壳
- ✅ 有完整的提交历史（至少 10 条可追溯）
- ✅ 有远程仓库 origin/main，确实在同步
- ✅ 提交信息有意义（vault backup、digest-apply、feat 等）
- ✅ 当前有未提交的变更，说明系统在活跃使用

---

### 5.4 腐烂度审计机制在有效运作
- ✅ decay-audit-2026-06-30.md 报告内容详实（14850 字节）
- ✅ 报告中发现的严重问题**已被修复**：
  - profile 中 skill 数量从"8个"更新为"23个" ✅
  - profile 中 skill 位置从 `D:\Cloud\Vault\Skills\` 更新为 `D:\Projects\Poyi\Loom\skills\` ✅
  - SOUL.md 已从 Hermes 配置更新为通用人格入口 ✅
  - sync-strategy.md（Hermes 时代遗留）已删除 ✅
- ✅ 审计机制有闭环：发现问题 → 修复问题

---

### 5.5 其他验证通过项
- ✅ 日记 17 篇，与 AGENTS.md 声明一致
- ✅ .beacon 数据库真实存在（.beacon.db + WAL 文件）
- ✅ 配置目录齐全：.claude、.obsidian、.UTSystemConfig
- ✅ Vault 元文件齐全：SOUL.md、Persona.md、semester-spring-2026.md
- ✅ 对话日志存在：digested 和 raw 目录都有按日期的子目录
- ✅ 全系统文件总数：1096 个，不是空壳项目

---

## 六、自举协议可执行性评估

按照 AGENTS.md 中的 8 步自举协议逐一测试：

| 步骤 | 名称 | 可执行性 | 说明 |
|---|---|---|---|
| 1 | 结构核验 | ✅ 可执行 | 顶层目录基本吻合，细节有差异 |
| 2 | 元信息层 | ✅ 可执行 | propagation-map.md 和 decay-audit 都存在 |
| 3 | 技能系统 | ✅ 可执行 | INDEX.md 存在，23 个技能基本齐全 |
| 4 | Wiki 知识碎片 | ⚠️ 部分可执行 | index.md 存在但内容几乎为空 |
| 5 | 对话记忆 | 🔴 不可执行 | marvis 目录不存在，协议断点 |
| 6 | Vault 项目区 | ✅ 可执行 | INDEX.md 存在，7 个项目齐全 |
| 7 | Vault 元文件 | ✅ 可执行 | SOUL.md、Persona.md 都存在 |
| 8 | 按需深入 | ✅ 可执行 | 各领域笔记目录存在 |

**结论**：8 步协议中 **6 步完全可执行，1 步部分可执行，1 步不可执行**。自举协议整体可用，但第五步需要修复。

---

## 七、修复优先级建议

### P0（立即修复）
1. **修复自举协议第五步**：要么创建 marvis 目录，要么更新 AGENTS.md 中的自举协议描述
2. **补全 AGENTS.md 物理结构**：将实际存在但未声明的目录加入结构描述

### P1（近期修复）
3. **补全 srtp 项目的 plan.md**
4. **修复技能索引中的路径引用不一致**
5. **处理 inbox/shared 目录不存在的问题**

### P2（长期改进）
6. **充实 Wiki 知识库内容**：这是系统核心价值所在，目前太薄弱
7. **补全未索引的参考文件到 INDEX.md**
8. **验证 decay-audit 中提到的 hermes-win 目录状态**

---

## 八、最终评价

Poyi 系统是一个**真实存在且在活跃维护的个人知识管理系统**，不是虚假项目或空壳。它有完整的技能体系、项目管理、Git 版本控制和自我审计机制。

但系统目前处于**"骨架已立，血肉待填"**的阶段：
- ✅ 架构设计完整且合理
- ✅ 工程化程度较高（技能系统、审计机制、Git 工作流）
- ⚠️ 知识内容层严重不足
- ⚠️ 自举协议有瑕疵

对于一个处于发展初期的个人知识系统来说，70 分是一个**合格且有潜力**的分数。核心架构没有问题，主要短板在内容积累和细节打磨。

---

*审计完成时间：2026-07-01*
*审计方法：第一性原则对抗性测试 + 全文件系统扫描验证*
