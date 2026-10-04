# Scout 实战踩坑（2026-06-15 起 · 2026-06-16 扩展）

> SKILL.md 路由表指向 `modules/scout.md`；本文件存在 `references/` 下，由 skill_manage 可写。
> scout.md 引用本文的方式：按需在执行 scout 前 `skill_view daily references/scout-pitfalls.md` 加载。

---

## 1. 用户学年适配（关键 · 2026-06-15 scout 翻车现场）

profile「基本信息 → 学校/班级」字段（如 `2025 级本科生 / 工科试验2501` 推 `→ 大一`；`2024 级 → 大二`）是 **scout 第一过滤项**。绝大多数「机会」对低年级不适用，必须在 Step 3 排序前先按学年过滤，否则简报会被 N/A 条目淹没（2026-06-15 实战：扫到 5 条原始命中，过滤后只有 4 条独立可推荐项，且 1 条是已截止的示例问策）。

| 类别 | 适合阶段 | 大一处理 |
|---|---|---|
| 暑期夏令营（机械 / 化工 / 数科 / AI 院 / 人工智能学院等） | 大三在读 | **直接排除**，写进「显式排除」 |
| 各院推免 / 直博 / 优营 | 大三进入流程 | **直接排除** |
| 公毅计划党政机关暑期实践 | 2027 届硕博 + 高年级本科 | **直接排除** |
| 节能减排 / 挑战杯 / 互联网+ / 智能车 / RoboMaster | 全阶段可参加 | 保留 |
| SRTP（国创 / 省创 / 校 SRTP） | 大二起主力申报 | 保留「秋季批次预告」+ 鼓励暑假联系意向导师 |
| 志愿招募（典礼 / 赛事 / 迎新 / 支教） | 全阶段 | 保留 |
| 奖学金 / 评优 | 大二起 | 保留「知会」但不强推 |
| 实习 | 视项目而定 | 校招岗排除；保留科研助理 / 寒暑期早鸟项目 |

**做法**：
- 从 profile「基本信息」表取「学校/班级」字段（如 `工科试验2501` 推 `2025 级 → 大一`；`2024 级 → 大二`），在 Step 3 排序前先按上表过滤。
- 简报末尾**必须单列「显式排除（用户身份 / 阶段不匹配）」**——写明排除了哪些 + 理由。这本身就是对用户的价值信号（让他知道 cron 确实跑了，不是漏了），同时方便他自查是否需要更新 profile 中的年级字段。
- 如果 profile 没有年级字段（罕见），**默认按"大一"保守过滤**——宁可少推，不可推错。
- **学年映射不在 `scout_scan.py` 里硬编码**（2026-06-16 设计决策）：学年会随用户升级，词表写在脚本里是负债。学年过滤放在简报生成阶段（人工或脚本），用 profile「学校/班级」表做权威源。

---

## 2. 空结果 / 命中极少时的简报纪律

**症状**：用户阶段不匹配 + 期末季 + 公众号 [链接/文件] 占位符 凑在一起，导致 12 群 + 11 公众号全扫完只剩 3-4 条独立可推荐项。

**修正**：
- 简报开头加一句「⚠️ 本次扫描命中极少——原因是 XXX（窗口无新通知 / 用户阶段不匹配 / 期末季非招新季）」，**不要为了凑数塞 digest / radar 范畴的旧通知**。
- 即使命中少也要保留「显式排除」一节——这本身就是价值信号。
- 完整扫描元数据（覆盖了哪些群、命中几条、扫描耗时）放在最末，便于排查。
- **绝不静默给空报告**——空报告 = 用户不知道 cron 跑没跑 = 失职。

**2026-06-16 实测案例**：27 条原始命中 → 8 条独立可推荐项。其中：
- 5 条是已报名活动的例行通知（示例车队相关）→ 由 `scout_scan.py` 自动排除（`ALREADY_REGISTERED_KEYWORDS`）
- 6 条是公众号 `[链接]` 占位符（无法读到真实标题/URL）→ 简报中按 §3 模板标 ⚠️
- 3 条是"未来集市"这类已过期活动的预告/倒计时推送 → 按过期不推
- 1 条是英才计划结业仪式（非招募）→ 简报中明确说明

---

## 3. 公众号 `[链接/文件]` 占位符的简报处理模板

在 `wechat-cli-pitfalls.md §9` 已有技术细节。简报落地模板：

```markdown
**{标题}**（{来源} 06-XX HH:MM）
⚠️ 原文标题/URL 本地不可读（公众号 [链接/文件] 占位符），需自行点开「{公众号名}」公众号 {日期} 推文查看报名方式。
{简报对内容的一句话推测}
```

例（2026-06-15/16 实测）：
- 「2026 夏季毕业典礼志愿者招募」（北屿大学学生会 06-15 10:27）
- 「求是学院 / 北屿大学微学工 6 月推文两条」（求是学院 06-13/14、北屿大学微学工 06-15 11:55）
- 「书香北屿大学·开卷有益报告会」（北屿大学图书馆 06-09）
- 「我和我的导师 第14期」（北屿大学竺院人 06-12）

**不要为了"看起来完整"编造 URL**——daily 历史翻车：06-14 图书馆系列讲座曾因反查失败被迫标 ⚠️，反而比硬塞一条编造的链接更安全。

---

## 4. 示例车队/社团群转发类机会的去重原则

场景：用户已是该社团成员（如 示例车队），群内 06-08 ~ 06-09 反复转发的「示例问策第三期训练班」，老学长还在群里校验名单（叶俊豪 6/9："报名参加的和我说一声"），但官方截止已过（2026-04-20）。

**做法**：
- **保留**为「⚠️ 边缘机会」项，简报中写「官方截止已过 / 但社群内可能延期调剂 / 适合 XXX 方向 / 详情见群内 @XXX」。
- **不要**当 digest 推（无 DDL 紧迫性），也**不要**完全忽略（用户可能是受益人之一）。
- 措辞要诚实地标"边缘"，不要吹成"强烈推荐"——这是 cron 简报的底线：宁可少推，不可误导。

---

## 5. SRTP 节奏备忘（每年复用）

- **春季批次（校 SRTP 主申报）**：3-4 月开放，5 月立项。已过则不推。
- **秋季批次（国创 / 省创 / 校 SRTP 集中申报）**：9-10 月开放，11 月立项。
- **滚动申报**：部分院系支持常年申报 SRTP（如能动人 `http://www.doe.campus.edu.cn/` 通知）。
- 简报节奏：5-8 月（夏季）→ 在「科研与项目」一节放「SRTP 秋季批次 9-10 月开放」预告，提示用户暑假前联系导师。

---

## 6. 与本文件配套

- `wechat-cli-pitfalls.md` —— 工具层踩坑（JSON 解析、分片、占位符、cron 限制）
- `modules/scout.md` —— scout 流程定义（Step 1-3 + 输出格式）
- `modules/digest.md` —— 兄弟模块，scout 排除规则的反面
- `modules/radar.md` —— 兄弟模块，scout 排除规则的反面
- `scripts/scout_scan.py` —— cron 模式下 scout 扫描脚本（2026-06-16 新增，与 `digest_scan.py` 共享 30 通道清单）
- `references/cron-delivery-pitfalls.md §D2` —— scout cron 标准推送流程

---

## 7. scout_scan.py 脚本使用（2026-06-16 新增）

**目的**：把 `scout` cron 从"手工写简报 + 临时拼关键词"升级为"固定脚本扫描 + 关键词过滤 + 简报生成"。

**调用模板**（见 `cron-delivery-pitfalls §C` 完整解释）：

```bash
cd "C:/Users/xgbc/AppData/Local/Temp" && \
  "D:/Software/Marvis/MarvisAgent/1.0.1100.193/runtime/python311/python.exe" \
  "C:/Users/xgbc/AppData/Local/Temp/scout_scan.py"
```

**输出**：`$TEMP/scout_raw.json` 含 6 大字段：
- `scan_time` / `scan_window_start`：扫描元信息
- `total_groups` / `scout_hits_count` / `excluded_already_registered`：通道数与命中统计
- `by_category`：6 类关键词分类计数
- `results`：30 通道完整结果（含 error 状态）
- `scout_hits`：去重后真正可推荐的机会（已排除已报名活动的例行通知）

**与 digest_scan.py 的差异**：
- 关键词不同（scout 是"机会"语义，digest 是"DDL"语义）
- 多一道 `ALREADY_REGISTERED_KEYWORDS` 过滤（避免与 digest 重复）
- 多一道 `by_category` 分类计数输出（简报生成时按类取数）
- **不做**学年过滤（学年字段会变，硬编码在脚本里是负债；放在简报生成阶段做）

**简报生成时记得做的事**：
1. 按 §1 学年过滤再筛一次 `scout_hits`
2. 按 §2 空结果纪律开头点明原因
3. 按 §3 模板处理 `[链接]` 占位符
4. 末尾必带「显式排除」节 + 扫描元数据
5. 飞书 DM fallback 时简报里如实写"已通过飞书 DM 推送"（见 `cron-delivery-pitfalls §A.3`）

---

## 8. 2026-06-16 实战新增坑位

### 8.1 PYBIN 形式：写脚本时不要被 `digest_scan.py` 误导

`scripts/digest_scan.py` 早期版本的 docstring 写的是 `PYBIN="/d/Software/..."`（MSYS 路径），body 里却用 `PYBIN = r"D:\Software\..."`（Python 字符串路径）——两种都不算错，但**初学者复制 docstring 到 `subprocess.run(cmd=[PYBIN, ...])` 列表里**时，会遇到 `[WinError 2] 系统找不到指定的文件`。

**修正**（已写入 `cron-delivery-pitfalls §C`）：cron scan 脚本**统一用 `D:/` 前斜杠盘符**——
- ✅ `PYBIN = "D:/Software/.../python.exe"`（Windows CreateProcess 接受，Python 字符串不需要 `\\` 转义，跨 MSYS/Windows 一致）
- ⚠️ `PYBIN = r"D:\Software\...\python.exe"`（也能跑，但易让作者误以为必须用 `\\` 反而绕弯）
- ❌ `PYBIN = "/d/Software/..."`（MSYS 翻译只在 shell 层生效，subprocess 列表不翻译 → `[WinError 2]`）

`scout_scan.py` 开头的 `PYBIN` 注释里把这个权衡直接写出来，避免下一个写脚本的人重新踩。

### 8.2 `$TEMP` 在 MSYS bash 与 Windows 实际路径不一致

**症状**：写 `cd "$TEMP" && "D:/Software/.../python.exe" "C:/Users/xgbc/AppData/Local/Temp/scout_scan.py"` 时，bash 解析 `$TEMP = /tmp`（即 `C:/tmp`），`cd` 到了 `C:/tmp` —— 与脚本里 `os.environ['TEMP']` 解析到 `C:/Users/xgbc/AppData/Local/Temp` **不一致**。

**影响**：
- 脚本能跑（绝对路径调用）
- 但如果脚本里有 `open('relative.json')` 就会落在 `C:/tmp` 而不是用户 TEMP
- 简报里"扫描元数据"记录的 `out_path` 也会与实际不一致

**修正**（已写入 `cron-delivery-pitfalls §C 调用模板`）：
- 调用时**直接用绝对路径** `cd "C:/Users/xgbc/AppData/Local/Temp"` 或 `cd $HOME/AppData/Local/Temp`（跨平台）
- 脚本内部 `os.environ.get("TEMP", r"C:\tmp")` 已有 fallback，正常用就行
- **不要** `cd "$TEMP"`——这是 cron 跨盘污染的另一个变种

### 8.3 `can't open file: No such file or directory` 排查三步走

**症状**：`scout_scan.py` 第一次跑报这个错（2026-06-16 实测栽过）。

**排查顺序**（按概率从高到低）：
1. **路径写错**——`cd` 路径和 `python.exe` 参数路径拼错了（最常见）。**检查**：`echo "脚本存在吗"` + 试着用绝对路径。
2. **PYBIN 形式错**——`/d/Software/...` 在 `subprocess.run(cmd=[...])` 里不会被翻译。**检查**：改成 `D:/Software/...` 形式。
3. **权限 / 软链**——极少见，本次未遇到。

**反面教材**（2026-06-16 我自己犯的）：
```bash
# 错误：cd 到 $TEMP（=/tmp 即 C:/tmp）+ 用了 D:/Users/...（盘符写错）
cd "$TEMP" && "D:/Software/.../python.exe" "D:/Users/xgbc/AppData/Local/Temp/scout_scan.py"
#                                     ^^^^^ 这里应该是 C:/Users/... 不是 D:/
# → can't open file 'D:\\Users\\xgbc\\AppData\\Local\\Temp\\scout_scan.py': No such file
```
