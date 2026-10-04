# Poyi 双 Meta 对齐修复计划（2026-07-09）

> 本文件记录"Loom/meta 与 Vault/meta 各自乱套"的修复方案。前提是用户于 2026-07-09 拍板的两个决策。

## 一、已定前提

- **Q1 — 事实来源**：`AGENTS.md` = 系统权威（结构 / 命名 / 角色路由）。`Vault/meta` 只管**人的内容**（Persona / SOUL / Areas / computer-map），**不再重抄系统命名规范**。
- **Q2 — 设备基准**：双环境保留 + **分层**。`AGENTS.md` 改为平台中立（`<POYI_ROOT>` 占位符 / `mac:` `win:` 标注）；设备专属事实拆进 `Meta.mac.md` / `Meta.win.md`，各端 Agent 只改自己的文件。

## 二、分层模型

1. **共享内核（单一来源）= `AGENTS.md`**：结构 / 命名 / 角色一份 truth。两个 Agent 都遵守，不各写一套。
2. **设备覆盖层 = `Meta.mac.md` / `Meta.win.md`**：含各自 computer-map、账户、同步策略。各端 Agent 只改自己的，不在共享文件里写对方设备事实（避免合并冲突与交叉断言）。
3. **人的内容 = `Vault/meta` 的 Persona / SOUL / Areas**：归用户，不归任何 Agent。

> 仓库里 `computer-map.mac.json` / `computer-map.win.json` 已经是这种"各端各一份、同 schema 不同机"的模式，本计划把它推广到元配置层。

## 三、路径约定

- `<POYI_ROOT>`：macOS = `/Users/sample/Poyi`；Windows = `D:\Projects\Poyi`。
- 文档中一律用 `<POYI_ROOT>`，**禁止写死盘符**（设备覆盖层内显式标注平台者除外）。
- 旧引用 `D:\Cloud\Vault` 是 2026-06-25 拆分前的旧路径，当前 Windows 根 = `D:\Projects\Poyi`。

## 四、修复清单（P0 → P2）

### P0（宪法级，活文档）
- [ ] `Vault/meta/Meta.md`：§1 命名改为指向 AGENTS（删 PascalCase 表）；§3 修正 Win 根 `D:\Cloud\Vault`→`D:\Projects\Poyi`；修正 `Context/` 幽灵路径（`RULES.md`→已归档 `Loom/meta/archive/RULES.md`、`Persona.md`/`computer-map.*.json`→`Vault/meta/`）；指向 Meta.mac/win 覆盖层。
- [ ] 新建 `Vault/meta/Meta.mac.md`、`Vault/meta/Meta.win.md`（设备覆盖层）。
- [ ] `Vault/meta/INDEX.md`：`Knowledge/` 引用 → `Vault/notes/`。
- [ ] `Vault/meta/decisions.md`：Win 旧根 `D:\Cloud\Vault`→`D:\Projects\Poyi`；标注"4 顶层"结构为历史（见 AGENTS §1）。

### P1
- [ ] `AGENTS.md`：新增"平台与路径约定"段；§1 树 `/Users/sample/Poyi`→`<POYI_ROOT>`；§3 步骤八 `D:\Cloud\Courses\` 标注 Windows-only；§6 `manage_skills` 路径→`<POYI_ROOT>`；明确 Vault/meta 只管人内容、设备事实在覆盖层。
- [ ] `Loom/meta/propagation-map.md`：`D:\Projects\Poyi`→`<POYI_ROOT>`。
- [ ] `Loom/skills/INDEX.md`：YAML `knowledge_domains` 及引用 `D:\Projects\Poyi`→`<POYI_ROOT>`。

### P2（后续 / 可暂缓）
- [ ] 各 skill `SKILL.md` 内 `D:\Projects\Poyi` 示例改为 `<POYI_ROOT>` 或平台标注（`notes`/`wiki-retrieve`/`poyi`/`filesystem` references 等）。
- [ ] **冻结区不改动**：`Loom/meta/archive/*`（已归档）、`Loom/dist/*`（编译副本）、`Loom/wiki/concepts/*`（知识碎片）、`Loom/raw/chat-logs/digested/*`（历史摘要）。
- [ ] `computer-map.win.json` 在 Mac 端为死重：保留（设备覆盖层），但确保不被 Mac Agent 误用；考虑文档说明或 `.gitignore`。

## 五、提交策略

- 按 P0 / P1 分组提交，每组一个独立 commit，便于回看。
- 未跟踪的 `Loom/meta/contradiction-audit-2026-07-09.md` 待用户决定入库与否，本计划不自动提交它。
- 所有改动仅限活文档与新建覆盖层，不触碰冻结区。
