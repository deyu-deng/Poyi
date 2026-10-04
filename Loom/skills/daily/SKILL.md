---
name: daily
description: "消息中枢：聚合消息扫描、热点雷达、机会挖掘三个子模块。加载本 skill 后，Agent 按用户意图路由到对应子模块。触发词：'待办'、'热点'、'机会'、'今日要做'、'今天有什么活动'。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": ["profile"]}
---
# Daily Info — 每日信息中枢

> **三模块统一入口。原 message-digest / info-radar / opportunity-scout 已整合。**
> **加载本 skill 后，按用户意图选择对应子模块执行。**

---

## 子模块路由

| 用户意图 | 加载子模块 | 文件 |
|---|---|---|
| "今天要做什么"、"待办"、"DDL"、"提醒我" | digest | `modules/digest.md` |
| "有什么热点"、"AI 新工具"、"赛车新闻" | radar | `modules/radar.md` |
| "有什么比赛"、"讲座"、"招募"、"机会" | scout | `modules/scout.md` |
| 模糊（"今天怎么样"） | 三模块都跑 | 各自独立执行 |

---

## 三模块边界（严防重复）

| 内容类型 | digest（待办） | radar（热点） | scout（机会） |
|---|---|---|---|
| 考试时间 / 作业 DDL | ✅ | ❌ | ❌ |
| 填表 / 交材料 / 谈话 DDL | ✅ | ❌ | ❌ |
| 缴费 / 退款 DDL | ✅ | ❌ | ❌ |
| 课程 / 结课安排 | ✅ | ❌ | ❌ |
| 入党 / 党务内部通知 | ✅ | ❌ | ❌ |
| 支教 / 志愿活动安排 | ✅ | ❌ | ❌ |
| FSAE / 赛车报道 | ❌ | ✅ | ❌ |
| 固态电池 / 储能技术 | ❌ | ✅ | ❌ |
| AI / 新工具发布 | ❌ | ✅ | ❌ |
| 效率工具 / 学习方法 | ❌ | ✅ | ❌ |
| 设计 / 创意资源 | ❌ | ✅ | ❌ |
| 比赛报名通知 | ❌ | ❌ | ✅ |
| 科研 / SRTP 招募 | ❌ | ❌ | ✅ |
| 奖学金 / 评优申报 | ❌ | ❌ | ✅ |
| 讲座 / 论坛 / 科技节 | ❌ | ❌ | ✅ |
| 实践项目招募 | ❌ | ❌ | ✅ |
| 暑研 / 实习招募 | ❌ | ❌ | ✅ |

**黄金法则**：
- 有 DDL / 时间锚点 / 必须行动 → digest
- 纯新闻 / 知识 / 启发 → radar
- 可报名 / 可加入 / 需主动申请 → scout

---

## 推送节奏

| 模块 | 时间 | 频率 |
|---|---|---|
| digest | 20:00 | 每天 1 次（提前一晚知悉第二天任务） |
| radar | 07:30 | 每天 1 次（早晨充电） |
| scout | 12:00 | 每天 1 次（午间空档） |

---

## 共享依赖与自动化运行时 (True Automation)

所有子模块共享：
- **核心大脑** → 归属 `Manager` 主 Agent 托管
- **用户画像** → 自动挂载 `profile` skill 数据
- **路径规范** → 自动挂载 `filesystem` 强校验

> **重构声明 (2026-07-02)**：
> 原有的外部脆弱 Bash/Cron 依赖（以及对应的 `wechat-cli` 各种路径坑、MSYS `$TEMP` 解析错误等）已**被彻底废弃**。
> 目前系统升级为“真·事件驱动的高自动化原生运行时”。所有定时推送与轮询任务，由以下方式接管：
> 1. **主 Agent 原生 Schedule 工具**：通过直接使用系统原生 `@schedule` 功能下达周期性推送（07:30 radar, 12:00 scout, 20:00 digest）。
>
> 原 `poyi_watchdog.py` 文件系统守护进程已于 2026-10-04 删除（Win-only 死代码，无活动触发器）；`activity_state.md` 的同步暂由 Agent 在被唤醒时代替完成。

从此告别写死临时目录、外部 CLI 版本冲突的旧时代。

---

## 子模块文件清单

```
daily/
├── SKILL.md           ← 本文件（入口 + 路由）
├── modules/
│   ├── digest.md      ← 原 message-digest 完整内容（带公众号扫描）
│   ├── radar.md       ← 原 info-radar 完整内容
│   └── scout.md       ← 原 opportunity-scout 完整内容
├── data/
│   └── activity_state.md       ← 已报名活动状态（从 profile 迁移，digest/scout 读取）
├── references/
│   ├── wechat-cli-pitfalls.md  ← wechat-cli 实战踩坑（多 DB 分片、emoji 转义、启动方式、JSON 容错、**$TEMP 路径修正**）
│   └── cron-delivery-pitfalls.md  ← cron 模式限制（**$TEMP 路径修正**）
```

---

## 与其他 Skill 的关系

| 场景 | 调用链 |
|---|---|
| 早晨综合推送（待办+热点+机会） | `daily` → 三模块并行 |
| 单模块推送 | `daily` → 对应子模块 |
| 修改用户信息 | `profile`（唯一来源） |
| 写入文件路径决策 | `filesystem` |

---

## changelog

### 2026-06-18 v1.5.0（digest cron 实测沉淀）

- **新增「关键路径声明」表**：旧 SKILL/module 文档散落 6 处过期路径（vault 位置、Marvis venv 版本、wechat-cli 调用方式、缺失 pip 依赖、DDL/Calendar 子目录），统一集中到本节，下次写脚本前查本表，不去翻历史 changelog。
- **新坑 #1**：vault 实际位于 `D:/Cloud/Vault/`（不是 `D:/Cloud/ObsidianVault/`），且 vault 下**没有 `DDL/` 和 `Calendar/` 子目录**——digest 的 Obsidian DDL/ICS 子通道默认不可用，简报里必须如实写 `📭 暂无明日待办`（仅微信侧待办），不要去别处找或编造。详见 `modules/digest.md`「Obsidian vault 路径」段。
- **新坑 #2**：Marvis Python venv 已升级到 `1.0.1100.219`，旧版 `1.0.1100.193` 路径不存在。详见 `references/wechat-cli-pitfalls.md §12`。
- **新坑 #3**：wechat-cli 源码不在 `Scripts/wechat-cli.exe`——它在 `AppData/Local/Temp/wechat-cli-extract/wechat-cli-main/` 下，**且 venv 里没有装** `click` / `pycryptodome` / `zstandard` 三件依赖，首次跑必须先 `pip install`。详见 `references/wechat-cli-pitfalls.md §12`。
- **新坑 #4**：公众号 `--limit 200` 在 7 天窗口下经常返回 0 条（公众号发文频率低，N=200 仍只覆盖 1-2 篇文章）。**digest 扫描公众号必须 `--limit 300+`**；公众号 `[链接]` 占位符截断 URL 与 scout 一样无解，简报里点明让用户自查原文。详见 `references/wechat-cli-pitfalls.md §9`（已扩 digest 视角）。
- **新坑 #5**：`executive_code` 在 cron 模式下被 BLOCKED（已有 §10.1），本次踩到新现象——`hermes_tools.terminal()` 在 cron 模式下**可以**用于跑 subprocess，但**返回字符串长度被截断到 50KB**，长 scan 输出要用 `write_file` 落盘 + `read_file` 分页读。已在 cron-delivery-pitfalls.md §B.5（待补）。 [Hermes-era]
- **脚本冗余清理**：保留 `scripts/digest_scan.py` 作为权威模板；本次新增的 `scripts/digest_run_2026-06-18.py` 和 `scripts/digest_run_2026-06-18_7d.py` 是带日期的临时跑批副本，下次 digest 跑前**优先复用 `digest_scan.py`**，不要复制 06-18 的副本（路径硬编码了 1.0.1100.193）。

### 2026-06-15 v1.4.0

- **关键 bug 修复**：cron 临时输出路径 `/c/tmp/` `C:/tmp/` → `$TEMP`（避免 MSYS 在 cwd=D 盘时错误解析为 `D:/c/tmp/`）
- 修改 5 处路径引用：`scripts/digest_scan.py`、`references/cron-delivery-pitfalls.md`（2 处）、`references/wechat-cli-pitfalls.md`（1 处）
- 清除错误产生的 `D:/c/` 目录（4 KB 残留）

### 2026-06-14 cron 实战要点

scout / digest 跑在 cron 模式时不要用 `execute_code`（被 BLOCKED），改用 `terminal` 调 `C:/tmp/*.py`；不要 `hermes send` 到 cron 自动投递的目标 channel，把简报内容直接写在 final response 里。详见 `references/wechat-cli-pitfalls.md` §10。 [Hermes-era]

- **1.3.0** 2026-06-14 scout cron 实战沉淀两条新坑：(1) 公众号消息的 `[链接]` 占位符——本地数据库不存真实 URL，需用 `web_search "site:libweb.campus.edu.cn ...` 反查（scout 报告必须给可点链接）；(2) cron job 模式 3 个隐性限制——`execute_code` 被 BLOCKED（改用 `terminal` 调 Python 脚本）、`hermes send` 自动跳过与 cron 投递目标相同的 channel（直接把内容写在 final response）、`subprocess.run` 在 MSYS Python 下 `cwd` 相对路径会触发 `[WinError 267]`。详见 `references/wechat-cli-pitfalls.md` §9 / §10。 [Hermes-era]
- **1.2.0** ⚠️ **关键坑更新**：wechat-cli `history` 单次调用只看一个 message_*.db 分片，`--limit 60` 在活跃群会截断丢失近期通知（2026-06-13 20:00 cron 翻车现场：漏掉「未来学习中心人脸门禁 24:00 截止」4 小时前才反查发现）。新增规则：`--limit 200` 是默认起点；每次拉完必须对照 sessions 列表的 `last_message.time` 校验是否被截断；`search` 命令不可靠（落旧分片），改用 history + Python 关键词过滤。详见 `references/wechat-cli-pitfalls.md` §2 / §3 / §8。
- **1.1.0** 公众号从"排除"改为"必扫"（实战发现北屿大学微学工等带直接行动项）；紧急判定扩展为"今天 ≤ 24h 倒计时也算紧急"；新增 references/wechat-cli-pitfalls.md 沉淀 6 条踩坑。