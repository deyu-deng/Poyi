# Cron 模式推送与交付坑（2026-06-15 digest 实测 · 2026-06-16 scout 扩展）

> ⚠️ 本文基于 Hermes cron 环境编写，Marvis 环境下需重新验证。

> **本文件聚焦 cron 模式下「简报怎么送到用户手里」+ 「次级工具调用为什么失败」**。
> wechat-cli 自身的字段解析坑已沉淀在 `wechat-cli-pitfalls.md`；scout 子模块专属坑在 `scout-pitfalls.md`；**MSYS 路径陷阱（跨 skill 通用）见 §F**。

---

## A. 飞书 / 微信 / Telegram 推送目标自动识别

**核心结论**：cron job 的 final response 会被系统自动投递到该 job 配置的 delivery target。**不要在 cron 里调 `hermes send` 投递到同一目标——会跳过。**

### A.1 症状

```bash
echo "test" | hermes send -t feishu
# 输出：
# Skipped send_message to feishu:oc_e3f931c56f52d91357a831885ada8491.
# This cron job will already auto-deliver its final response to that same
# target. Put the intended user-facing content in your final response
# instead, or use a different target if you want an additional message.
```

### A.2 根因

- 每个 cron job 在 `~/.hermes/cron/<jobname>.yaml`（或 jobs 表）里配置一个 `delivery.target`。
- 任务结束 → final response 被投递引擎自动 push 到 delivery target。
- `hermes send` 调 gateway 时会先查 job 元数据：若 `cmd target == delivery target`，跳过（避免同一条消息发两遍）。
- **用户口里说"推飞书 home channel" ≠ 配置里真有 home channel**——本次实测 `hermes send --list` 只有 Feishu DM（`oc_e3f...8491`），没有任何群聊 home channel。

### A.3 修正模式

| 用户意图 | 正确做法 |
|---|---|
| 把简报推到飞书 / 微信 / Telegram | **简报正文直接写在 final response 里**，让 cron 引擎自动投递 |
| 同一内容备份一份到不同平台 | 用 `--to <另一平台>`（如 `wechat:filehelper`），让目标 ≠ delivery target |
| 用户指定了"home channel"但配置里只有 DM | fallback：DM 也是用户本人，自动投递就是推到用户；简报里说"已通过飞书 DM 推送"即可，不要硬找群 channel |
| 想新增飞书群聊 home channel | 必须跑 `hermes gateway setup feishu` 完整流程（见 `hermes-gateway-setup` skill），改 `channel_directory.json` 不会被 lark-oapi 接受 |

### A.4 排查命令清单

```bash
# 看当前 cron 支持的所有目标
hermes send --list

# 看完整 channel_directory（含 DM/群/thread）
cat ~/.hermes/channel_directory.json

# 看具体 cron job 的 delivery 配置
cat ~/.hermes/cron/*.yaml
hermes status
```

### A.5 实测案例（2026-06-15 20:00 digest）

- 用户原话："20:00 整理成简报推给飞书 home channel"
- 实际配置：只有 Feishu DM（无 home channel）
- 正确动作：简报内容直接作为 final response → 系统投递到 DM → 用户收到
- 错误动作：`hermes send -t feishu "..."` → 跳过 + 报错

---

## B. execute_code 在 cron 模式下被 BLOCKED

### B.1 症状

```python
# 想在 execute_code 里跑循环 + subprocess 批量拉消息
from hermes_tools import terminal
for grp in GROUPS:
    terminal(f'...PYBIN... -m wechat_cli history {grp} ...')
# 报：
# BLOCKED: execute_code runs arbitrary local Python (including subprocess
# calls that bypass shell-string approval checks). Cron jobs run without
# a user present to approve it. Use normal tools instead, or set
# approvals.cron_mode: approve only if this cron profile is intentionally
# trusted.
```

### B.2 根因

- `execute_code` 的设计前提是「用户在场 → 可以批准高风险操作」。
- cron 无人值守 → 安全策略直接拒绝 subprocess、network、file-write 之外的任意代码执行。
- 这不是 bug，是设计。`approvals.cron_mode: approve` 可以解锁，但默认锁。

### B.3 修正模式

| 场景 | 正确做法 |
|---|---|
| 写一次性扫描 / 过滤 / 报告生成脚本 | 用 `write_file` 写到 `$TEMP/digest_scan.py`，再用 `terminal` 调 `PYBIN` 跑 |
| 想边跑边改逻辑 | 写到文件后 `terminal(background=true, notify_on_complete=true)` 跑，结果回来读 stdout |
| 单纯想解析已读到的 JSON | 用 `read_file` 读 dump 文件，不要嵌 execute_code |
| 极简数据处理（≤3 个工具调用 + 简单 Python 字符串处理） | execute_code 可以跑（无 subprocess / 无 network），但批量循环必须走文件 |

### B.4 与 wechat-cli-pitfalls §10.1 的关系

`wechat-cli-pitfalls.md §10.1` 已经记录过一次。本节是 2026-06-15 digest 又一次撞坑，**确认是稳定限制而非偶发**，所以单独再沉淀一次，便于以后 cron 写 scan 脚本时直接抄答案。

---

## C. cron 模式下 `subprocess.run` `cmd[0]` 路径形式（wechat-cli-pitfalls §10.4 的延伸）

虽然路径坑主体在 §10.4，但 cron 模式下经常跨多个脚本复用 `PYBIN`，建议把所有 cron scan 脚本开头的 `PYBIN =` 都统一写成：

```python
# ✅ cron scan 脚本统一用这个形式（Windows 前斜杠盘符 + Python 字符串）
# PYBIN 自动检测：优先读 MARVIS_PYBIN 环境变量，fallback 见脚本内 _detect_pybin()
PYBIN = "{PYBIN_AUTO}"  # 占位符 — 实际值由脚本或环境变量确定
SITE  = "{PYBIN_AUTO}/../Lib/site-packages"

cmd = [PYBIN, "-m", "wechat_cli", "history", grp_name, "--start-time", start, "--limit", "500"]
env = os.environ.copy()
env["PYTHONPATH"] = SITE
proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120, encoding="utf-8", errors="ignore")
```

**为什么用 `D:/` 而不是 `D:\` 也不是 `/d/`**：

| 形式 | 适用 | 在 `subprocess.run(cmd=[...])` 里 |
|---|---|---|
| `D:/Software/...` | Python 列表元素 + Windows CreateProcess | ✅ 两种都通吃 |
| `r"D:\Software\..."` | Python 列表元素 + Windows CreateProcess | ✅ CreateProcess 接受；但作者可能误以为只能用 `\\` 反而绕弯 |
| `"/d/Software/..."` | bash shell 调用（MSYS 自动翻译） | ❌ CreateProcess 不会翻译 → `[WinError 2]` |
| `"/c/tmp/..."` | bash shell 临时文件路径 | ❌ Cron 跨盘污染 D:\c\（见 §F.1） |

**结论**：`PYBIN` 在 cron scan 脚本里**统一 `D:/` 形式**——既不被 MSYS 误翻译，Python 字符串也不需要 `\\` 双反斜杠转义。`digest_scan.py` 和 `scout_scan.py` 都用这个形式。

不要写：
- ❌ `PYBIN = "/d/Software/..."`（MSYS 翻译只在 shell 层生效，subprocess 列表不翻译）
- ❌ `cwd=` 相对路径或 `/d/...`（cwd 跨 MSYS/Windows 解析容易 267 错误）
- ❌ heredoc 字符串里的脚本路径用 `/c/tmp/x.py`（→ §F.1 跨盘污染）

**调用方式模板**（2026-06-16 scout 实测验证可用）：

```bash
# cd 到脚本所在目录 + 绝对路径调用；PYBIN 从环境变量或脚本内 _detect_pybin() 确定
cd "C:/Users/xgbc/AppData/Local/Temp" && \
  "{PYBIN_AUTO}" \
  "C:/Users/xgbc/AppData/Local/Temp/scout_scan.py"
```

注意：
1. `cd` 到 TEMP 后脚本里 `os.environ['TEMP']` 才能解析到正确位置（虽然脚本里也用绝对路径，但输出 JSON 默认在 TEMP 根）
2. **不要**用 `cd "$TEMP" && python ...`——`$TEMP` 在 MSYS bash 里解析为 `/tmp`（即 `C:/tmp`），与用户实际 TEMP `C:/Users/xgbc/AppData/Local/Temp` 不一致
3. 第一次写时可能犯 `cd "$TEMP" && "D:/Users/..."` 拼错路径——结果就是 `can't open file: No such file or directory`，根因是路径写错（不是 PYBIN 问题）

---

## D. digest cron 推送流程（2026-06-15 实测版）

基于 A/B/C 三节的踩坑总结，digest cron 的标准流程应该是：

1. **加载 daily + profile skill**（profile 提供群 username 速查）
2. **terminal 跑 `digest_scan.py`**（写入 `$TEMP/digest_raw.json` 或 `%TEMP%\digest_raw.json`）
   - 脚本开头用 §C 的 `PYBIN = "D:/..."` 形式
   - `--limit 200` 起步；按 §2 校验 `messages[-1].time` vs `sessions.last_message.time`
   - 截断的群另起 `digest_repull/<safe_name>_3d.json` 复检
3. **terminal 跑过滤脚本**（grep / Python one-liner 提取明天 DDL）
   - 不要在 execute_code 里跑 —— 见 §B
4. **整理简报正文，写到 final response** —— 见 §A.3
   - **不要**额外 `hermes send -t <delivery target>`
   - 如果用户说"推 home channel"但配置只有 DM：fallback DM，**简报里如实说明"已通过飞书 DM 推送"**，不要假装有群 channel
5. **简报结尾加扫描元数据**（截断判断、复检时间、不可用通道）—— 让次日 cron 能对比

---

## D2. scout cron 推送流程（2026-06-16 实测版）

scout 与 digest 的差异：(1) 关键词是"机会"语义（比赛/招募/讲座/奖学金），(2) 必须按用户学年过滤（profile「学校/班级」→ 排除 N/A 项），(3) 空结果/极少命中时**不能静默给空报告**（见 `scout-pitfalls.md §2`）。基于此，scout cron 流程是：

1. **加载 daily + profile skill**——profile 的「学校/班级」字段（如 `工科试验2501` 推 `2025 级 → 大一`）是 scout 第一过滤项
2. **terminal 跑 `scout_scan.py`**（写入 `$TEMP/scout_raw.json`）—— 脚本在 `daily/scripts/scout_scan.py`，**与 digest_scan.py 共享相同的 30 通道清单**（13 群 + 17 公众号）
   - PYBIN 用 `D:/Software/.../python.exe`（**D:/ 前斜杠盘符**，见 §C + `wechat-cli-pitfalls §10.4`）
   - 脚本内已硬编码 `SCOUT_KEYWORDS`（6 大类）和 `ALREADY_REGISTERED_KEYWORDS`（profile 已报名活动关键词）
   - 输出含 `by_category` 分类计数 + `excluded_already_registered` 排除数
   - 调用前 `cd` 到 `$TEMP` 实际目录（不要用 `$TEMP` 环境变量在 MSYS 里），见 §C 调用模板
3. **terminal 跑简报生成脚本**（如 `parse_scout.py` 按类别打印）—— 同样**不要走 execute_code**（见 §B）
4. **按 scout-pitfalls §1 的学年过滤**再做一次人工/脚本过滤
   - **为什么不在 scout_scan.py 里硬编码学年**？学年字段会随用户升级，词表写在脚本里反而是负债。学年映射放在 profile「学校/班级」表，简报生成阶段做过滤。
5. **简报正文直接写在 final response**（§A.3）—— 末尾必带「显式排除」节 + 扫描元数据；命中极少时开头点明原因
   - 推送通道：飞书 DM（配置中无 home channel 时，fallback DM，简报里如实写"已通过飞书 DM 推送"）
   - 公众号 `[链接]` 占位符命中按 `scout-pitfalls §3` 模板处理，不要编造 URL
   - 简报纪律：`# 机会雷达 · {日期}` 标题 + 6 类分组（比赛/科研/奖学金/讲座/实践/实习，最多 8 条），不凑数

**与 digest 的关键差异表**：

| 维度 | digest | scout |
|---|---|---|
| 关键词语义 | 紧急/时间锚点（DDL/缴费/谈话） | 机会/可报名（招募/讲座/奖学金） |
| 第一过滤项 | 时间紧迫度 | 用户学年（profile 字段） |
| 已报名活动处理 | 「已报名追踪」小节（保留追踪变动） | 直接排除（避免与 digest 重复） |
| 空结果处理 | 仍要列明日 DDL 概要（哪怕 0 条） | **绝不给空报告**——要点明原因（窗口无新通知 / 期末季非招新季 / 学年不匹配） |
| 脚本 | `scripts/digest_scan.py` | `scripts/scout_scan.py` |
| 简报结尾 | DDL 列表 + 扫描元数据 | 「显式排除」节 + 扫描元数据 |

---

## F. MSYS 路径陷阱（**跨 skill 通用规则**，2026-06-15 升华为通用规则）

> ⚠️ **本节是所有 skill 都必须遵守的通用规则，不只是 daily**。filesystem、campus、其他 cron 输出脚本也适用。

### F.1 现象（2026-06-15 实测）

```bash
# daily/scripts/digest_scan.py docstring 原写：
"$PYBIN" /c/tmp/digest_scan.py

# 当 cron 在 D:\ 工作目录跑：
$ hermes cron run digest
# → /c/tmp/digest_scan.py 被 MSYS bash 翻译为 D:\c\tmp\digest_scan.py
# → 自动创建 D:\c\ 目录 + D:\c\tmp\ 子目录
# → 污染 D 盘根目录
```

后来在 D:\ 看到一个 `D:\c\tmp\digest_2026-06-16.md`——这就是 daily cron 输出的"误投"。

### F.2 根因

- MSYS bash（Git Bash 那一套）会把 `/c/`、`/d/` 当成"盘符 + 路径"的别名
- `/c/tmp/x` = `<当前工作盘>:\\c\\tmp\\x`
- 当 cron 工作目录是 `C:\` 时，`/c/tmp/x` = `C:\c\tmp\x`（用户预期位置）
- 当 cron 工作目录是 `D:\` 时，`/c/tmp/x` = `D:\c\tmp\x`（**污染**！）
- 你**不知道 cron 当前在哪个盘跑**——所以 `/c/` `/d/` 都是危险路径

### F.3 通用规则（**所有 skill 写路径时**）

| 场景 | ✅ 正确 | ❌ 错误 |
|---|---|---|
| 临时文件 | `$TEMP/x.py` `%TEMP%\\x.py` `os.environ['TEMP']` | `/c/tmp/x.py` `/d/tmp/x.py` |
| 脚本解释器 | `"D:/Software/Marvis/.../python.exe"` | `"/d/Software/Marvis/..."` |
| 工作目录 | `cwd=r"D:\\Cloud\\..."` | `cwd="/d/Cloud/..."` |
| Windows API 调用 | `D:/...` 正斜杠（CreateProcess 接受） | `D:\\...` 反斜杠（要写 `\\\\`） |
| `hermes_tools.terminal()` 调用 | `"$PYBIN $TEMP/scan.py"` | `"$PYBIN /c/tmp/scan.py"` |
| `subprocess.run(cmd=[...])` | `cmd[0] = "D:/.../python.exe"` | `cmd[0] = "/d/.../python.exe"` |

**记忆口诀**：
- **绝对路径用 Windows 风格**（`C:\\` `D:\\` 或 `$TEMP` `%TEMP%`）
- **永远不要在 Python 列表/shell heredoc 字符串里用 MSYS 路径**（`/c/` `/d/`）
- **`$TEMP` 是 Windows 标准环境变量**，`/c/tmp/` 是 MSYS 别名——**只信任前者**

### F.4 跨 skill 影响

| Skill | 是否受影响 | 修复位置 |
|---|---|---|
| daily cron 输出 | ✅ 已修（v1.3.2 changelog + 本节 §F） | `daily/scripts/digest_scan.py` + `daily/scripts/scout_scan.py`（2026-06-16 新增） |
| filesystem generate-map.py | ❌ 不受影响（只用 `D:\` 绝对路径） | 不需要改 |
| campus 自动签到 | ⚠️ 检查中（脚本内有 `/d/Tools/Scripts/` 路径） | 待审计 |
| 其他 future skill | ⚠️ 新建时遵守本节 | 写 skill 时把本节抄过去 |

### F.5 修复检测（写 skill / 脚本时自检清单）

写任何涉及 `terminal()` / `subprocess.run()` / `write_file(绝对路径)` 的代码前，**grep 这 3 个危险模式**：

```bash
grep -nE '/[cd]/[a-z]|/tmp/|"C:\\\\\\\\|"D:\\\\\\\\' my_script.py
# 命中任何一行 = 有问题
```

或者用 filesystem skill 的 generate-map.py 风格的硬规则："**脚本里出现 `/c/` `/d/` `/tmp/` 一律视为 bug**"。

### F.6 真实事故案例（2026-06-15）

| 时间 | 现象 | 原因 |
|---|---|---|
| 20:11 | D:\c\ 目录被创建，含 digest_2026-06-16.md | daily cron 把 `/c/tmp/` 解析为 `D:\c\tmp\` |
| 20:11 → 22:38 | D:\c\ 持续存在，被用户发现 | 没人清理 |
| 22:38 | 用户问"D 盘为什么有 1temp" | inode 检测到目录 |
| 23:xx | 修复：所有 `/c/tmp/` 引用改为 `$TEMP/` | daily v1.3.2 + 本节 §F |

**教训**：**一次坑坑两次**——cron-delivery-pitfalls.md §B.3 写了修复但**没解释为什么**，filesystem skill 也不知道这规则。升华为 §F 后，下次任何 skill 作者写路径时必须先看这节。

---

## E. 变更日志

- **2026-06-16 v1.2**（scout 扩展）：
  - 新增 §D2「scout cron 推送流程」—— 把 2026-06-16 scout cron 实测沉淀为可复用流程，包含与 digest 的差异表。
  - 新增 `scripts/scout_scan.py`——30 通道扫描 + 6 类关键词过滤 + 已报名活动排除。PYBIN 形式与 `digest_scan.py` 保持一致。
  - §C 代码示例从 `r"D:\"` 改为 `D:/` 前斜杠盘符，并加为什么/什么时候的对比表——避免下一个写脚本的人误以为只能用 `\\` 形式。
  - §C 新增「调用方式模板」+ 两条易错点（`$TEMP` 在 MSYS 解析为 `/tmp`、`cd` 后路径拼错）—— 2026-06-16 scout 第一次调用时栽过。
  - §F.4 跨 skill 影响表新增 `daily/scripts/scout_scan.py`。
- **2026-06-15 v1.1**：新增 §F「MSYS 路径陷阱」，把分散在 §B.3 和 changelog 的路径坑**升华为通用规则**（覆盖 daily + filesystem + campus + 未来 skill）。原 §B.3 表格保留"为什么用 $TEMP"的具体例子，§F 是抽象规则。引用：filesystem skill 应在 §0 陷阱或 references 加引用本节。
- **2026-06-15 v1.0**：创建本文件，沉淀 §A 飞书自动投递跳过、§B execute_code cron BLOCKED、§C subprocess.run 路径统一规范、§D digest cron 标准流程。
