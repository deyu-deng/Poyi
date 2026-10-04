# 矛盾对账审计报告 · 2026-07-09

> 发现人：WorkBuddy（Craft 模式核对）
> 方法：以物理文件系统为权威，交叉比对 `AGENTS.md` / `README.md` / `Loom/skills/INDEX.md` / `Vault/projects/INDEX.md` 的声明。
> 结论：**声明层与物理层、以及各声明文件之间，存在系统性不一致。**

---

## 一、顶层结构：AGENTS.md §1 描述的目录大量不存在（幽灵目录）

| AGENTS.md §1 声称的顶层项 | 实际是否存在 | 备注 |
|---|---|---|
| `.beacon/` | ❌ 不存在 | 幽灵目录 |
| `.UTSystemConfig/` | ❌ 不存在 | 幽灵目录 |
| 顶层 `.claude/` | ❌ 不存在 | 实际在 `Loom/.claude` |
| 顶层 `.claudian/` | ❌ 不存在 | 实际在 `Loom/.claudian` |
| `.obsidian/` | ✅ 存在 | 一致 |
| `Loom/` `Vault/` `AGENTS.md` `README.md` `.gitignore` | ✅ 存在 | 一致 |
| `.workbuddy/` | ✅ 存在（但非 Poyi 设计内，属 WorkBuddy） | 未在任何索引登记 |

**结论**：AGENTS.md §1 把 `Loom/` 下的 `.claude`、`.claudian` 错挂到了顶层，并凭空列出了 `.beacon/`、`.UTSystemConfig/`。

---

## 二、Loom/output/ 是幽灵目录

- AGENTS.md §1 声称 `Loom/output/`（"衍生输出 reports/slides 目前均为空"）。
- 实际 `Loom/` 下没有 `output/`，只有 `dist/` 和 `wiki/reports`。
- **结论**：该目录声明与磁盘不符。

---

## 三、技能数量自相矛盾（四处数字互不一致）

| 来源 | 声称的技能数 | 实际 |
|---|---|---|
| `Loom/skills/INDEX.md` frontmatter `total_skills` | 23 | — |
| `README.md` | "23 个技能" | — |
| `AGENTS.md` §2 | "原 23 个细碎技能" | — |
| `AGENTS.md` SKILL_TABLE 实际引用的技能名 | 25 个 | — |
| `INDEX.md` YAML 视图列出的条目 | 20 个 | — |
| 磁盘 `Loom/skills/` 真实目录数（不含 INDEX.md） | — | **25 个** |

**结论**：23 / 25 / 20 / 25 四个数字互相打架，且没有一个与磁盘真实数量（25）完全对齐。

---

## 四、5 个 wiki 技能"被反复引用但索引里查无此项"

- AGENTS 表格与 INDEX 更新日志反复提到 `autoresearch`、`canvas`、`defuddle`、`wiki-mode`、`wiki-retrieve`（"Wiki 核心技能编号 14-23"）。
- 这些目录**确实存在于磁盘**，但 `INDEX.md` 的 YAML 视图（20 条）里**没有**它们——YAML 只列了 `poyi/ingest/query/lint/save/research/think` 等 7 个 wiki 系。
- **结论**：索引的"机读视图"漏登记了 5 个真实存在的技能，导致按索引遍历会漏掉它们。

---

## 五、命名规范被系统自己打破（kebab-case 规则形同虚设）

声明（`AGENTS.md` §5 + `INDEX.md` §命名规则）：必须 kebab-case、≤1 词、禁 PascalCase、禁中英混杂、禁空格、必要时 ≤2 词。

实际违反处：

1. **`Loom/skills/NoteCraft/`** —— PascalCase；索引里叫 `notecraft`。目录名既违反 kebab-case，又与索引条目名不一致。
2. **`Vault/notes/`** 下全是 `人工智能 AI` / `数学 Math` / `语言 Language` / `工具 Tools` / `物理 Physics` / `工程 Engineer` / `计算机 Computer` —— 含空格 + 中英混杂，直接违反规则。
3. **`Vault/projects/claude-obsidian-source/`** —— 3 词 kebab，违反"≤2 词"。
4. AGENTS 自己的审计日志（2026-07-02）已承认曾存在 `RULES.md` 用 PascalCase 与 kebab-case 冲突并"移入 archive"，但 `NoteCraft` 这个矛盾仍留在活跃区未被修。

---

## 六、项目清单不一致（影子项目）

- AGENTS.md §1 与 `Vault/projects/INDEX.md` 都说 **7 个项目**：`aura / chassis / lab / prism / srtp / vaelis / website`。
- 实际磁盘有 **9 个**：`aura, chassis, claude-obsidian-source, lab, plobi-os, prism, srtp, vaelis, website`。
- `plobi-os` 与 `claude-obsidian-source` 两个目录存在，但在 AGENTS 与 Projects INDEX 里都**未登记**（无 plan.md 引用、无 INDEX 条目）—— 属"影子项目"。

---

## 七、路径环境错配（Windows 路径写在 Mac 机器上）

- `INDEX.md` YAML 中 `english` 技能的 `knowledge_domains` 及多处引用使用 `D:\Projects\Poyi\Vault\notes\...` Windows 绝对路径（更新日志称"从 macOS 改为 Windows"）。
- 但本机是 macOS，真实路径是 `/Users/sample/Poyi/Vault/notes/...`，且目录名带空格。
- **结论**：任何按索引路径去读取的操作都会失败；索引与运行环境脱节。

---

## 八、SOUL.md 定位歧义

- AGENTS §5 声明 "SOUL.md 位于 `Vault/meta/SOUL.md`"（成立）。
- 但 `Vault/meta/` 同时还有 `Meta.md`，且 WorkBuddy 自身 `~/.workbuddy/SOUL.md` 也存在。AGENTS 未说明 `Meta.md` 与 `SOUL.md` 的关系，易混淆"系统灵魂"该读哪个。

---

## 九、审计日志本身可能夸大

AGENTS §6 审计日志（2026-07-01 / 07-02）声称已完成全量物理盘点、P0–P3 全链清零、健康度评估。但上述 8 类矛盾在最新文件里依然存在，说明审计结论与现状不符，或后续改动未回写索引。

---

## 建议修复优先级

| 优先级 | 问题 | 修复动作 |
|---|---|---|
| P0 | 七、路径环境错配 | 将 `D:\Projects\Poyi\...` 改为 `/Users/sample/Poyi/...` |
| P0 | 三/四、技能索引漏登 + 数量矛盾 | 重算 INDEX.yaml，补齐 5 个 wiki 技能，校正 total_skills |
| P1 | 一/二、幽灵目录 | AGENTS §1 与磁盘对齐，删 `.beacon`/`.UTSystemConfig` 声明、修正 `.claude`/`.claudian` 层级、去掉 `output/` |
| P1 | 六、影子项目 | 决定 `plobi-os`/`claude-obsidian-source` 是否登记，登记则补 INDEX，否则归档 |
| P2 | 五、命名规范 | 统一 `NoteCraft`→`notecraft`；`Vault/notes` 重命名为 kebab-case；评估 `claude-obsidian-source` 命名 |
| P2 | 八、SOUL.md 歧义 | 澄清 `Meta.md` 与 `SOUL.md` 职责 |

> 注：修复命名（`NoteCraft`、`Vault/notes/*`）会牵涉大量内部交叉引用，需配套改索引与技能内路径，建议先做影响评估再执行。
