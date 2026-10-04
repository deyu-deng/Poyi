<!-- source: profile -->
---
name: profile
description: "统一的用户画像 skill。daily 三模块（digest/radar/scout）共享的用户画像，作为唯一权威来源。被 daily 等 skill 引用，避免重复维护。 触发词：用户画像、我的偏好、profile、我是谁。"
metadata: {"version": "1.1.0", "owner": "sample-user", "last_validated": "2026-10-04", "deps": []}
---
# User Profile — 统一用户画像

> **本 skill 是 daily 三模块（digest/radar/scout）的共享用户画像。**
> **修改用户信息时只改这里，3 个模块自动生效。**
>
> ⚠️ **本文件当前是虚构示例人设**（Poyi 出厂自带样例画像）。真实部署时逐节替换成自己的事实，但**小节标题不要改** —— daily 各模块按标题取数据。

---

## 基本信息

| 维度      | 详情                  |
| ------- | ------------------- |
| 学校      | 北屿大学，2025 级本科生      |
| 学院      | 机械与能源学院              |
| 专业      | 机电工程（已分流）          |
| 年级      | 大一下册（暑假），即将升大二      |
| 班级      | 工科试验2501，2501 班级群 |
| 住宿      | 青禾学园 4 舍            |
| 设备 | Win 桌面：Marvis + Antigravity；Mac 笔记本（用户 sample）：Claude/Gemini（详见 `Vault/meta/profile/profile.md`） |
| 籍贯      | 示例省示例市             |
| GPA      | 4.0/5.0（示例值）             |
| 微信 wxid | wxid_sample0000001 |
| 钉钉 UID  | 1000000001          |
| 用户名（群内） | 小满等               |

---

## 组织与角色

| 组织 | 角色 | 群名 |
|---|---|---|
| 示例车队 | 底盘车架组成员 | `示例车队 2026赛季大群`、`2026示例车队学生交流群`、`底盘车架`、`2026示例车队暑期社会实践`、`赛车运动部门竞速部` |
| 培养联络 | 春夏批次 | `工科试验2501入党积极分子` |
| 晨曦启明支教 | 志愿者（对接白石洲小学） | `26春【晨曦启明】志愿者` |
| 军训连队 | 长风四连成员 | `长风四连` |
| 课程小组 | 第二小组成员 | `史纲第二小组` |
| 学生助理 | 勤工助学 | 钉钉「勤工助学」群 |

---

## 辅导员

| 姓名 | 职责 | 出现群 |
|---|---|---|
| 示例辅导员 A | 兼职辅导员，负责培养联络 | `工科试验2501入党积极分子` |
| 示例辅导员 B | 辅导员，第四团委 | `长风四连`（微信），钉钉第四团委群 |

---

## 兴趣领域

- 赛车/汽车工程（车队核心活动）
- AI/科技前沿（关注 AI 前沿周刊、模型观察、开源日报）
- 射击运动（射击社）
- 效率方法论、产品设计/创意工具
- 前沿科技社群（校园 AI 生态×创客松、鸿蒙开发者群）

---

## AI 工具与工作流

| 工具 | 角色 | 说明 |
|---|---|---|
| Marvis | 办公主力 | 文件管理、系统配置、本地桌面操作 |
| Antigravity | 编程主力 | IDE + 代码开发 |
| Hermes | 调研/编排/记忆 | 已停用，历史数据已归档 |

- 桌面 AI 三件套：Marvis + Antigravity + Hermes（Hermes 已退役）
- 自维护 skill 集（数量以 `Loom/skills/INDEX.md` 为准），位于 `<POYI_ROOT>/Loom/skills/`
- AI 交互风格：偏好"最小可行版本"先行、逐步迭代；跳过 AI 的多问题轰炸
- Antigravity 模型策略：日常用 Gemini 3.1 Pro (High)，复杂项目（架构/竞品分析/系统迁移）切换 Claude Sonnet 4.6 Thinking
- 代码开发工作流：AI 生成 implementation_plan.md → task.md → 逐步执行 → 编译验证（`hvigor assembleApp` 零错误硬要求）

---

## 项目

| 项目（Vault 官方名） | 说明 | 曾用名 |
|---|---|---|
| Vaelis | 全栈多智能体平台，官网 samplelab.example | SamplelabOS |
| FormulaStudentChassis | 示例车队车架设计 | Electric_Trolley |
| College2026Spring | 2026 春季学期课程 | — |
| SRTP | 工程机械热管理方向（Research/01-SRTP） | SRTP |

> 权威项目索引见 `Vault/projects/INDEX.md`

---

## 技术环境 (双端隔离配置)

### 🪟 Windows 桌面端 (主生产力)
- **知识管理**：Obsidian（`D:/Projects/Poyi`，vault 根；内含 `Vault/` 与 `Loom/`）
- **文献管理**：Zotero
- **CAD**：SolidWorks / Creo
- **Adobe**：Premiere / AE
- **WSL Ubuntu**：`D:/Development/Virtualization/`
- **协作软件数据**：`D:/Data/Collaboration/`
- **Cloudflare**：已配置 Pages + 自定义域名策略用于 Personal-Website
- **D 盘顶层结构**：
  `Archive/` (大档案), `Cloud/` (主仓库), `Data/` (缓存/配置), `Development/`, `Games/`, `Inbox/`, `Media/`, `Projects/`, `Software/` (软件安装强制在此)。

### 🍎 Mac 笔记本端 (移动/轻量/原生AI)
- **系统用户**：`sample`
- **知识管理**：Obsidian (`/Users/sample/Poyi`，vault 根；内含 `Vault/` 与 `Loom/`)
- **AI 编排**：Claude / Gemini (`~/.claudian` 配置文件)
- **特殊规则**：不可运行 Windows 专属的 `.exe` 或依赖 `D:/` 盘硬编码的脚本，必须做严格的环境探针。

### 命名规范 (双端通用)
- kebab-case 强制，禁下划线，禁中英混杂（权威规则见 `filesystem` skill §2）
- 项目编号 `{NN-Name}/`，课程 `{YYYY学期-课程名}/`，事件 `{YYYYMMDD-事件名}/`

---

## 工作偏好

- **preview-before-commit**：任何文件操作必须先列清单
- **保守清理**：磁盘/文件清理选最安全方案，宁可少清不冒数据风险
- **直接行动**：给出方案后直接开工，不需要二次确认
- **命名强迫**：见上方命名规范
- 网络限制：不在北屿大学校园网，`*.campus.edu.cn` 需 VPN

---

## 重要公众号订阅

| 公众号 | 用途 |
|---|---|
| 青禾青年 | 学园通知 |
| 北屿能小源 | 能源学院通知 |
| 北屿大学学生会 | 校级活动 |
| 北屿大学青志 | 志愿者服务 |
| 北屿大学微学工 | 学工通知 |
| 北屿大学图书馆 | 图书馆通知 |
| 北屿大学体育与艺术 | 体艺活动 |
| 北屿大学医院 | 校医院通知 |
| 北屿大学敬文人 | 敬文书院 |

---

## 群聊 username 速查（精确匹配用）

> 下表群号是**示例值**，与 `daily/scripts/*.py` 里的字典一一对应。本机要恢复可用的真实映射，见不入库的 `Loom/skills/daily/data/identity.local.json`；该文件缺席时 digest / scout 扫不到任何群 —— 真实群号永远不进公开仓库。

| 群名 | username |
|---|---|
| 工科试验2501入党积极分子 | 19416880228@chatroom |
| 26春【晨曦启明】志愿者 | 32585334488@chatroom |
| 1️⃣🟦2025🟦青禾四舍👑 | 22785073235@chatroom |
| 示例车队 2026赛季大群 | 27078175275@chatroom |
| 2026示例车队学生交流群 | 74036572916@chatroom |
| 2026示例车队暑期社会实践 | 32017243574@chatroom |
| 底盘车架 | 60226711214@chatroom |
| 赛车运动部门竞速部 | 25254299957@chatroom |
| 长风四连 | 91339174574@chatroom |
| 史纲第二小组 | 14728426060@chatroom |
| 2501班级群 | 91143084472@chatroom |

---

## 更新机制

### 触发条件
用户说「更新 profile」或「更新画像」时触发。

### 执行流程
1. Agent 逐节询问用户：「基本信息」「组织与角色」「辅导员」「兴趣领域」「公众号订阅」是否有变更
2. 用户确认变更内容后，Agent 修改对应章节
3. 修改完成后更新 frontmatter `version`（递增 patch 号），并在本文件末尾追加 changelog 条目（日期 + 变更摘要）
4. 若涉及群聊 username 变更，需同步告知用户更新 daily/scripts 中对应字典

### 特别说明
- **「已报名活动」已迁移到 `daily/data/activity_state.md`**，profile 不再维护该数据。活动状态变更请更新 daily 侧文件。
- **兴趣领域和公众号订阅属于操作偏好层**（非用户画像核心数据），但因其被 daily/radar 等模块引用，仍在 profile 中维护。
- **真实身份标识不进仓**：群号、wxid、钉钉 UID 等属本机私有配置，仓库内只保留示例值。

---

## 引用方式

被以下 skill 引用：
- `daily/modules/digest.md` —— 微信/钉钉扫描 + 待办追踪（已报名活动改读 `daily/data/activity_state.md`）
- `daily/modules/radar.md` —— 校外热点搜索
- `daily/modules/scout.md` —— 校内机会挖掘（已报名活动改读 `daily/data/activity_state.md`）
- `AGENTS.md` —— 入口文件，从中提取用户称呼和核心身份摘要

互补文件（本 profile 不重复维护的内容）：
- `Vault/meta/profile/profile.md` —— 内在画像（技能评分、情绪模式、核心价值观、弱点、长期愿景）
- `Vault/projects/INDEX.md` —— 项目索引（权威项目列表）
- `Loom/raw/chatlog/digested/*/preferences.json` —— 每日偏好原子条目（仅本机，不入仓）

---

## Changelog

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-10-04 | 1.1.0 | 去真实化：整份画像改为虚构示例人设。真实群号/wxid/钉钉 UID/辅导员实名/班级号/宿舍/籍贯/GPA 全部换成示例值；真实映射迁至不入库的 `daily/data/identity.local.json`；互补引用由已废弃的 `Persona.md` 修正为 `Vault/meta/profile/profile.md`。 |
| 2026-06-30 | 1.2.0 | 从 Hermes Win 端历史对话消化：补全各章；新增「AI 工具与工作流」「项目」「技术环境」「工作偏好」四章；新增互补文件引用 |
