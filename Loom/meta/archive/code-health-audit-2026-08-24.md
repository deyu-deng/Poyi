# Poyi 代码健康审计报告（2026-08-24）

> 审计范围：`Loom/scripts/**`（含 exporters/、tests/）、`Loom/skills/**/SKILL.md` 引用与路径事实、`.gitignore`、采集链路端到端行为。
> 审计方法：全量阅读 + 实证验证（bucket_by_date 合成数据测试、verifier、doctor、bash -n、py_compile、test_net_probe.sh）。
> 红线遵守：未修改 Vault/** 笔记内容；未删除/移动 raw/ 与 digested/ 历史数据；未对 AGENTS.md / propagation-map 做破坏性改动；未执行任何 git push/reset --hard。

---

## 0. 重大发现：仓库 re-clone 导致管线代码丢失（新增 P0）

`git reflog` 显示本仓库在审计期间被**从 GitHub 重新克隆**（`HEAD@{4}: clone: from https://github.com/sample-user/Poyi.git`）。后果：

- 审计前期（2026-08-20 前后）存在于本地工作树的**抽取管线 4 文件从未 push**，随旧克隆一起丢失：
  `Loom/scripts/extract_insights.py`、`router.py`、`edit_engine.py`、`digest.py`，以及 `Loom/meta/governance/propagation-map.json`（v1.1）。
- 当时已实施的一批 P0/P1 修复随之全部丢失。**修复前的原件**保留在 `.audit-backup-2026-08-20/`（未跟踪目录，已加入 .gitignore，勿删）。
- 本轮审计已将所有可重新应用的修复重新落地（见 §2）；仅对已不存在文件的修复转为存档（见 §1 标注与 §3）。

**决策请求**：是否从 `.audit-backup-2026-08-20/` 恢复管线并重新实施修复，或确认放弃管线。这是用户级架构决策，Agent 不自行选择。

---

## 1. P0-P3 分级问题清单

图例：✅ 本轮已修 ｜ 📦 修复方案存档（目标文件已随 re-clone 丢失）｜ ⏸ 未处理（见 §3）

### P0 — 数据丢失 / 数据污染级

| # | 位置 | 问题 | 影响 | 状态 |
|---|---|---|---|---|
| P0-1 | `Loom/scripts/aggregate_mac.py:111` bucket_by_date | 无 `time` 的消息直接 `continue` 静默丢弃；而 `exporters/antigravity.py` 的 protobuf 抽取产出的消息**全部无 time** | Mac 端采集的 **Antigravity 整源对话 100% 丢失**，且无任何告警 | ✅ 已修（兜底分桶 + 导出器提供 fallback_time，见 §2.1/2.2） |
| P0-2 | `.audit-backup-2026-08-20/extract_insights.py`（原 `Loom/scripts/`） | DOMAIN_ALIASES 含短英文别名（如 `"ai"`），子串匹配命中 email/available 等 | ~50% 假领域检测，洞见被错误路由到笔记领域 | 📦 方案：删除短别名（当时已修，随 re-clone 丢失） |
| P0-3 | 原 `router.py` PARA 模式分支 | `startswith("projects/")`，但 inventory 路径带 `Vault/` 前缀 | PARA 模式排序完全失效，永不命中 | 📦 方案：改为 `startswith("Vault/projects/")` |
| P0-4 | 原 `edit_engine.py` is_noise() | 不检查消息 role，tool/assistant/system 内容当洞见写入 | 实测 2026-08-19 洞见 97% 来自非 user 角色；已污染 `Vault/projects/Aura/progress.md`（22 条垃圾编辑，**未清理**，红线：不动 Vault 内容） | 📦 方案：仅放行 role 以 user/me 开头的消息 + noise 标志优先 |
| P0-5 | 原 `edit_engine.py` _applied.json 写入 | 覆盖写而非追加 | 跨日期丢失幂等历史，重复应用风险 | 📦 方案：`old + new` 追加 |
| P0-6 | 原 `edit_engine.py` run_rollback() | 无路径深度检查 | 可把 `_claim_ledger.json` 恢复到 `D:/Projects/Poyi/` 仓库根 | 📦 方案：`len(rel.parts) < 2: continue` |
| P0-7 | 原 `digest.py` cleanup_snapshots() | `shutil.rmtree` 连同 `_applied.json`/`_claim_ledger.json` 一起删 | 成功事务销毁自身审计轨迹，回滚与对账永久失效 | 📦 方案：rmtree 前摘出账本、事后归位 |

### P1 — 功能性 bug

| # | 位置 | 问题 | 影响 | 状态 |
|---|---|---|---|---|
| P1-1 | `Loom/scripts/collect_mac.sh:145` | `--refresh` 不被 aggregate_mac.py 识别（只认 `--force`，`sys.argv` 子串判断静默忽略） | Mac 定时采集意图的强制重算静默降级 | ✅ 已修（改 `--force`） |
| P1-2 | 原 `router.py` | `skeleton/` 只读骨架路径未标记 blocked | 洞见可直接改写用户骨架笔记 | 📦 方案：skeleton 路径 `write_allowed=False` |
| P1-3 | 原 `router.py` decision 回退 | 未限定路径，可路由到 `Vault/meta/governance/decisions.md`（用户治理文件） | 治理文件被自动写入 | 📦 方案：回退限定 `Loom/wiki/**/decisions.md` |
| P1-4 | 原 `edit_engine.py` run_apply() | 目标文件不存在仍创建 | 陈旧 inventory 凭空复活幽灵文件 | 📦 方案：仅 tactics/ 与 Loom/wiki/ 允许新建 |
| P1-5 | `Loom/scripts/aggregate_mac.py:229-233` | 已消化日期删除 `_sessions_extract*.json` | 重跑不可复现（管线在场时影响 extract_insights） | ⏸ moot：管线已不存在，恢复管线时一并处理 |

### P2 — 规范性 / 跨设备

| # | 位置 | 问题 | 状态 |
|---|---|---|---|
| P2-1 | `Loom/scripts/collect_mac.sh:157` | `git commit` 未限定路径，launchd 自动提交可卷入用户手工 stage 的无关文件 | ✅ 已修（`-- "$ROOT/Loom/raw/chat-logs/"` 路径限定） |
| P2-2 | `Loom/scripts/compile.py:24` | `SKIP_SKILLS={"animation","notecraft"}` 两目录均已于 2026-08 归档/合并删除，属过时残留 | ✅ 已修（清空集合） |
| P2-3 | `Loom/scripts/manage_skills.py:16-17` | 硬编码 `D:\Projects\Poyi`；AGENTS §6 的 sync 命令在 Mac 端必然失效 | ✅ 已修（脚本相对定位 `__file__.parents[2]`，doctor 实测通过） |
| P2-4 | `Loom/scripts/aggregate_win.py:28,33` | 硬编码 `LOOM_ROOT`；`LOG_DIR=~/Logs` 在 ensure_dirs() 无条件创建家目录杂散目录（v4.0 已无日志写入） | ✅ 已修（相对定位 + LOG_DIR 归位 `Loom/scripts/logs/`（已在 .gitignore），顺带清理死 `import os`） |
| P2-5 | `Loom/skills/poyi/SKILL.md:10` | 硬编码 `D:/Projects/Poyi/AGENTS.md`，违反 AGENTS §0 `<POYI_ROOT>` 约定，Mac 端读取失败 | ✅ 已修（`<POYI_ROOT>` 占位 + 双端路径提示） |
| P2-6 | `Loom/skills/notes/SKILL.md:14,71-73` | `D:/Projects/Poyi/Vault/<学科名>/skeleton/` 层级错误（实际为 `Vault/notes/<领域>/`）；`D:/Cloud/Course` 应为 `Courses` | ✅ 已修（`<POYI_ROOT>/Vault/notes/<领域名>/skeleton/`；Course→Courses，实测 `D:/Cloud/Courses` 存在） |
| P2-7 | `Loom/skills/profile/SKILL.md:73,96` | "自维护 25 个 skill"（实际 22，计数漂移）+ `/Users/sample/...` 单端路径；`D:/Cloud/Vault/` 已于 2026-07 迁移至 `D:/Projects/Poyi` | ✅ 已修（计数改引 INDEX.md 为准；vault 根改 D:/Projects/Poyi 并注迁移史） |
| P2-8 | `.gitignore` | 缺编辑引擎账本（`_applied/_claim_ledger/_source_ledger.json`）与审计备份目录模式 | ✅ 已修（追加 4 条模式，账本规则在管线恢复后即生效） |
| P2-9 | `Loom/scripts/collect_mac.sh:126` | 版本钉死的 Mac Python 二进制路径（3.13.12），升级即断 | ⏸ 见 §3 |
| P2-10 | `Loom/scripts/poyi_daemon.py:14` | 硬编码 `D:/Projects/Poyi` | ⏸ 见 §3（生命周期不明） |
| P2-11 | 原 `digest.py` | `--mode` 默认值写死 generic（应运行时读 mode.json）；snapshot_phase 快照全部 302 文档而目标仅 ~5 个 | 📦 方案存档 |
| P2-12 | `Loom/scripts/setup_retrieve.py:195` | 默认 `--wiki-path` 硬编码（有 CLI 覆盖，实害低） | ⏸ 见 §3 |

### P3 — 低危 / 记录备查

| # | 位置 | 问题 | 状态 |
|---|---|---|---|
| P3-1 | `Loom/skills/poyi/SKILL.md:245` | 交叉项目引用模板硬编码 `/Users/sample/Poyi/Loom/`（模板被复制到其他项目后 Win 端失效） | ⏸ 记录 |
| P3-2 | `exporters/doubao.py` | `taskkill /F` 强杀 Doubao.exe 进程 | ⏸ 记录（可能是用户接受的工作方式，不擅改） |
| P3-3 | `Loom/scripts/verifier.py` | 缺 kebab-case 命名检查与 SKILL.md 硬编码路径检查 | ⏸ 增强项 |
| P3-4 | `Loom/skills/profile/SKILL.md` | 缺 `## 偏好` 章节（原 propagation-map.json 声明的 preference 落点；该 json 已丢失） | ⏸ 与管线决策绑定 |
| P3-5 | `Vault/notes/` 各领域 | 双轨制（skeleton 只读 + tactics 可写）中 tactics/ 目录尚未在任何领域落地 | ⏸ 规划性缺口 |
| P3-6 | `Loom/scripts/tests/test_net_probe.sh` T4 | Windows Git Bash 下 perl alarm/exec 语义差异导致 2/23 失败（超时杀不掉子进程）。测试目标环境为 macOS，在 Mac 上预期通过 | ⏸ 环境限制，记录 |

---

## 2. 已实施改动清单（本轮 10 文件，均为 git 跟踪文件）

**统一回滚方式**：`git checkout -- <文件>`（HEAD=8cd595a 即修前原状）。⚠️ 工作树另有**用户自己的未提交改动**（`Loom/skills/filesystem/**` 6 文件、`Vault/projects/Vaelis/**` 3 文件、`_pending_digestion.json`），与本次审计无关，回滚时务必按文件点名，勿整树操作。

| # | 文件 | 改动 | 动机 | 风险 |
|---|---|---|---|---|
| 1 | `Loom/scripts/aggregate_mac.py` | bucket_by_date 增加 `fallback_day`：无 time 消息归入会话最早可定位日期，其次会话级 `fallback_time` | 修复 Antigravity 整源静默丢失（P0-1） | 低：有 time 的会话行为逐字节不变；已用合成数据 4 场景实测通过（含混合会话、全无时间会话不崩溃） |
| 2 | `Loom/scripts/exporters/antigravity.py` | 会话记录新增 `fallback_time`（db 文件 mtime 的 ISO 串）+ 补 `datetime` import | 为 P0-1 兜底提供时间锚点 | 低：新增字段不影响既有消费者（聚合端此前根本读不到该源）；mtime 是最后活动时间的近似，会话跨天时可能整体归入最后一天——可接受的近似，好过全丢 |
| 3 | `Loom/scripts/collect_mac.sh` | ① `--refresh`→`--force`；② commit 加 `-- "$ROOT/Loom/raw/chat-logs/"` 路径限定 | P1-1 旗标不识别；P2-1 自动提交卷入无关文件 | 低：bash -n 通过；test_net_probe.sh 21/23（2 失败为 T4 Windows 环境问题，与本次改动无关——改动均在 `BASH_SOURCE` 守卫的主流程块内，被 source 时不执行） |
| 4 | `Loom/scripts/compile.py` | `SKIP_SKILLS` 清空 | 两技能目录已删除，跳过名单成幽灵配置（P2-2） | 无：`SKIP_DIR_PREFIXES=("_",)` 仍拦截 `_archive` 等 |
| 5 | `Loom/scripts/manage_skills.py` | SKILLS_DIR/AGENTS_MD 改 `__file__` 相对定位 | AGENTS §6 的 sync 命令双端可用（P2-3） | 低：Win 端解析结果与原值完全一致；`doctor` 实测 22 技能 0 ERROR |
| 6 | `Loom/scripts/aggregate_win.py` | LOOM_ROOT 相对定位；LOG_DIR 由 `~/Logs` 改 `Loom/scripts/logs`；删除死 `import os` | 消除家目录杂散文件夹副作用；路径规范（P2-4） | 低：v4.0 已无日志写入，LOG_DIR 仅剩 mkdir；编译通过 |
| 7 | `.gitignore` | 追加 `**/_applied.json`、`**/_claim_ledger.json`、`**/_source_ledger.json`、`.audit-backup-*/` | 防本机审计/账本产物与备份目录入库（P2-8） | 无 |
| 8 | `Loom/skills/poyi/SKILL.md` | `D:/Projects/Poyi/AGENTS.md` → `<POYI_ROOT>/AGENTS.md`（附双端实路径） | AGENTS §0 占位符约定（P2-5） | 无 |
| 9 | `Loom/skills/notes/SKILL.md` | 3 处路径：skeleton 定位、Course→Courses（教材路径×2） | 对齐物理现实（P2-6，`D:/Cloud/Courses` 实测存在） | 无 |
| 10 | `Loom/skills/profile/SKILL.md` | 2 处：skill 计数改引 INDEX.md + `<POYI_ROOT>`；Obsidian 根 `D:/Cloud/Vault/`→`D:/Projects/Poyi` | 消除计数漂移与过时迁移前路径（P2-7） | 无 |

**验证汇总**：py_compile 全过（9 个脚本）｜bash -n 过｜verifier.py 全绿（exit 0）｜manage_skills.py doctor 22 技能 0 ERROR｜bucket_by_date 合成测试 4 场景全过｜test_net_probe.sh 21/23（失败项见 P3-6）。

---

## 3. 未处理项与原因

1. **管线 4 文件的全部 P0/P1 修复（P0-2~P0-7、P1-2~P1-4、P2-11）**——目标文件已随 re-clone 从仓库消失。重新落地前需要用户决策（恢复管线 vs 放弃）。恢复时的修复清单已完整存档于 §1；修前原件在 `.audit-backup-2026-08-20/`。
2. **`Vault/projects/Aura/progress.md` 的 22 条垃圾编辑**——属 Vault 用户数据，红线明确禁止修改；建议用户确认后手动清理或授权 Agent 处理。
3. **`collect_mac.sh` 钉版 Python 路径（P2-9）**——Mac 端环境事实，Win 端无法验证改动；建议 Mac 端改用 `command -v python3` 探测链。
4. **`poyi_daemon.py` 硬编码路径（P2-10）**——该脚本在历史提交中经历过"移除又恢复"，生命周期状态不明，不宜擅动。
5. **`setup_retrieve.py` 默认路径（P2-12）**——有显式 CLI 参数可覆盖，实害低，列为 P3 顺手项。
6. **doubao.py 强杀进程（P3-2）**——工作方式取舍，需用户表态。
7. **verifier.py 检查项增强（P3-3）**——超出本次"修复"范围，属新功能开发。
8. **profile `## 偏好` 章节 / tactics 目录落地（P3-4/5）**——依赖管线（propagation-map.json 已丢）与用户对双轨制的推进决策。
9. **AGENTS.md / propagation-map 的结构性更新**——红线要求先提案：本次无需改动 AGENTS §1（结构未变）；若决定恢复管线，需同步在 AGENTS §4 场景四中恢复 digest 链路描述。

---

## 4. 建议的下一步

1. **决策管线去留**（§0）：恢复 → 按 §1 存档方案重实施修复并重新生成 propagation-map.json；放弃 → 归档 `.audit-backup-2026-08-20/` 并从 AGENTS §4 场景四移除 digest 描述。
2. **提交本轮 10 文件修复**（pre-commit verifier 已验证通过；注意只 stage 本报告点名的文件，避开用户自己的 filesystem/Vaelis 未提交改动）。
3. Mac 端下次拉取后，`collect_mac.sh` 的 `--force` 与路径限定提交立即生效；Antigravity 会话将首次进入 digested 分桶。
