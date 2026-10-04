# Digest Module — 每日待办提取

> 原 message-digest 模块。用户画像已迁移到 `profile` skill。

---

## 加载指引

执行本模块前必须先加载：
1. `profile` —— 用户基本信息、组织角色、群聊 username
2. `filesystem` —— 路径规范（如需写入文件）

---

## 前置条件

- wechat-cli 已配置微信数据库密钥（`C:\Users\xgbc\.wechat-cli\`）
- 微信数据库路径：`D:\Data\Collaboration\WeChat\xwechat_files\wxid_sample0000001_c19c\db_storage`
- wechat-cli 路径：`D:\Software\Marvis\MarvisAgent\1.0.1100.219\runtime\python311\Scripts\wechat-cli.exe`
- 钉钉数据库路径：`D:\Data\Cache\DingTalk\e34da8455d4779ae5786_v3\DBFiles\dingtalk.db`（V3 加密）
- dingtalk-exporter 路径：`D:\Tools\dingtalk-exporter\`

---

## 加载用户已报名活动

加载 `profile` skill 后，从「已报名活动」表读取，扫描时额外关注这些群中的**变动型消息**：
- 时间提前/推迟/取消（如"支教结课提前至今晚"）
- 地点变更（如"改到蓝四辅楼203"）
- 新增要求（如"带铅笔"、"填表后私戳"）
- 临时安排（如"今天傍晚来紫金港"）

---

## 操作流程

### Step 1: 获取微信会话列表

```
wechat-cli sessions --limit 50
```

返回 JSON 数组，含 chat / username / is_group / last_message / time 字段。

### Step 2: 筛选目标群聊

按以下优先级筛选（**具体群名 username 见 profile「群聊 username 速查」**）：

**P0（必扫）：**
- 入党/党务相关群（`工科试验2501入党积极分子`）
- 支教群（`26春【晨曦启明】志愿者`）
- 宿舍群（`1️⃣🟦2025🟦青禾四舍👑`）
- 班级群（`2501班级群`）

**P1（有活动时扫）：**
- 车队群（`示例车队 2026赛季大群`、`底盘车架`、`2026示例车队暑期社会实践`）
- 课程群（`史纲第二小组`）
- 军训群（`长风四连`）

**P2（按需）：**
- 车队交流群（`2026示例车队学生交流群`、`赛车运动部门竞速部`）
- 其他群（`26长沙家教优选29群` 等）

**排除规则：** 外卖/奶茶群、纯表情/闲聊群、公众号（is_group=false）

### Step 3: 批量拉取近期消息

对每个目标群执行：

```
wechat-cli history "群名" --start-time "YYYY-MM-DD" --limit 50
```

参数说明：
- `--start-time`：必填，防止拉取数月前的旧消息；默认扫描最近 5-7 天
- `--limit`：默认 50 条，活跃群可增至 100
- 群名含 emoji 或特殊字符时**必须**用双引号包裹
- 同一批次无依赖的调用可并行 5 个

返回 JSON：
```json
{
  "chat": "群名",
  "messages": [
    "[2026-06-11 19:07] 发送者: 消息内容",
    ...
  ]
}
```

### Step 4: 解析消息提取待办

逐条扫描消息，命中以下模式时标记为待办：

| 模式 | 关键词/特征 | 示例 |
|---|---|---|
| @所有人 | `@所有人` | 群公告、重要通知 |
| 时间锚点 | 日期词（6月/本周/明天/周五/今晚等）+ 具体时刻 | "明晚8:25后"、"周五结课" |
| 考试安排 | 四六级/CET/期末/考试 + 时间/地点/准考证 | "6月13日六级笔试" |
| 行动词 | 截止/报名/提交/确认/填报/私戳/填写/携带/登录/申请 | "请于6月15日前登录..." |
| 党务材料 | 思想汇报/谈话/考察/登记表/培养/入党 | "交一篇思想汇报，落款六月初" |
| 活动通知 | 结课/入院/仪式/团日/暑期实践/例会/组会 | "本周五结课" |
| 地点+动作 | 辅楼/教室/车库/值班台 + 行动词 | "蓝四辅楼203" |
| 文件+DDL | [文件] + 日期约束 | "史纲小组打分表.docx" "期末表单7.2前提交" |

**优先级判定：**
| 级别 | 条件 |
|---|---|
| 紧急 | DDL ≤ 3 天内（含今天） |
| 近期 | DDL ≤ 7 天内 |
| 可关注 | DDL > 7 天 或 无明确 DDL |

### Step 5: 钉钉消息扫描（补充通道）

钉钉数据库为 V3 加密格式，需先通过 dingtalk-exporter 解密后才能读取。

解密逻辑（PBKDF2-SHA1）：UID + salt → PBKDF2-SHA1("666DingT", 1000) → MD5[:16]

消息表：`tbmsg_000` ~ `tbmsg_127`，content 字段为 JSON，需解析 `content` / `senderNick` / `createdAt` 字段。

关键钉钉群（来自 profile 角色）：
- 第四团委（辅导员示例辅导员 B）
- 青禾25级志愿者交流群2群
- 勤工助学
- 大学英语Ⅴ
- 2025级能源本科生群

---

## 输出格式

适配手机端阅读，使用竖排紧凑列表，禁止表格（太宽需要左右滑动）：

```
## 待办汇总（截至 {日期}）

### 紧急 · {日期/今天/明天}

**{emoji} {任务标题}**（{来源群}）
{一行说明}。{补充：时间/地点/带什么}
{链接（如有）}

### 近期 · {DDL}

**{emoji} {任务标题}**（{来源群}）
{操作说明}

### 可关注

**{任务标题}**（{来源群}）
{备注}
```

**emoji 映射：** 党务/材料 ⏰ | 结课/考试 📚 | 退款/缴费 💰 | 活动/报名 📢 | 车队 🏎️ | 支教 🎓

---

## 推送策略

- 频率：每天 1 次，**晚上 20:00** 推送（提前一晚知悉第二天任务）
- 去重：与 daily/radar（热点）和 daily/scout（机会）严格不重叠
- 来源标注：微信/钉钉（注明群名）

---

## 已知局限

1. wechat-cli history 默认按插入顺序返回，需 `--start-time` 过滤
2. 公众号消息是 is_group=false，需单独关注（如青禾青年、Beiyu能小源，关注列表见 profile）
3. 消息中链接/文件需额外 `web_fetch` 获取详情
4. 图片仅显示 `[图片]`，需 `--media` 参数解析
5. 钉钉需先解密再扫描，流程较长
6. 微信消息可能被撤回，history 无法捕获撤回后的内容

---

## 配置路径速查

| 项目 | 路径 |
|---|---|
| wechat-cli 配置 | `C:\Users\xgbc\.wechat-cli\` |
| 微信数据目录 | `D:\Data\Collaboration\WeChat\xwechat_files\wxid_sample0000001_c19c\db_storage` |
| 微信安装 | `D:\Software\Tencent\Weixin\Weixin.exe` |
| 钉钉数据库 | `D:\Data\Cache\DingTalk\e34da8455d4779ae5786_v3\DBFiles\dingtalk.db` |
| dingtalk-exporter | `D:\Tools\dingtalk-exporter\` |