# Skill 命名流程（含合并/改名安全步骤）

> 本文是 filesystem §0 陷阱 0.2 的详细操作手册。

## 命名原则（用户 2026-06-13 拍板，2026-06-15 扩展）

1. **一个词最佳**
2. 必须多词时 kebab-case
3. **不超过两个词**
4. 命名要反映"真实用途"，不是程序员审美
5. **可读 > 简短**（用户原话"能不能不要用单词缩写"）
6. **避开母公司品牌名**（iOS/Apple/Windows/Microsoft 都是品牌）

## 建/改 skill 名的安全步骤

### Step 1: 列候选（不要直接定名）

不要直接定名。给用户**至少 3 个候选**，每个带语义解释。

```
❌ 错的：
   Agent: "决定叫 cloudfiles"  → 用户立刻否决

✅ 对的：
   Agent: "候选 A: filesystem (处理整台电脑的文件结构)
         候选 B: host (本机语义)
         候选 C: structure (结构，但太抽象)
         我推荐 A，但听你的。"
   → 用户："我用 A 吧"
```

**用过的差名字**（用户否决过的）：

| 名字 | 否决理由 |
|---|---|
| `cloud-file-orchestrator` | 太长（3 个词）|
| `cloudfiles` | "Cloud 是个错误认知边界，skill 处理整台电脑"|
| `host`、`sign`、`papers`、`notes`、`exam`、`profile`、`scaffold` | "太随意" |
| `OC`、`IosTools`、`Ios` | "能不能不要用单词缩写" + "iOS 也是品牌名呀" |
| `cloudfile` | "你这个名字取得也太随意了吧" |

### Step 2: 等用户拍板

**用户没选之前不要动手**。

### Step 3: 检查命名合规

```
✅ 一个词（或最多两个词）
✅ 没下划线
✅ 没中英混杂
✅ ≤ 10 字符（建议，不是硬约束）
✅ 不和 D 盘已有目录同名（Cloud/Software/ 不能叫 Cloud/Library/ 之前类似冲突）
✅ 不含品牌名（Apple/iOS/Microsoft/Adobe 等）
✅ 不缩写（除非缩写是行业通用术语如 PDF、URL）
```

### Step 4: 改名操作（**绝不要 replace_all**）

1. `git mv`（如果有 git）/ 直接 mv 目录
2. 改 SKILL.md frontmatter `name:` 字段
3. 改 INDEX.md
4. **逐个 patch** 引用该 skill 的地方（grep -rn "旧名" 找出来，逐个替换）
5. **绝不要 `replace_all`** — 会破坏 `supersedes:` 字段、§0 标题、历史段落，造成"filesystem 合并 filesystem"这种自指废话

### Step 5: 验证

- `grep -r "旧名" 整个 Loom/skills/` 应该返回 0
- `skill_view 新名` 能正确加载
- `skill_view 旧名` 应该报错（不存在）

## 合并两个 skill 的安全步骤

### Step 1: 写出统一心智模型（**必须先做**）

合并前**先写出合并后这个 skill 帮 Agent 做什么**（一句话）。

```
❌ 致命错误：先起名再合并
   Agent: "合并叫 cloudfiles"
   User: "你这个名字取得也太随意了吧？Cloud 是你的理解偏差"

✅ 正确流程：
   Agent: "这个 skill 帮 Agent 了解整台电脑（至少 D 盘）的文件结构"
   User: "用 filesystem"
   → 名字从心智模型推导，不凭空捏造
```

### Step 2: 检查职责是否真的重叠

- ❌ 名字像但职责不同 → 不合并
- ✅ 同一心智模型的不同尺度 → 可以合并（如 host-context 是 filesystem 的全局视角）

### Step 3: 合并 SKILL.md 内容

- 合并去重（公共部分写一份）
- 保留各自独特部分
- 更新版本号（合并算 minor 升级）

### Step 4: 物理合并

- 移动 / 复制文件
- 删除被合并的 skill 目录
- 更新所有引用方

### Step 5: 验证

- 加载测试
- 引用方也能正确加载
- INDEX.md 同步

## Skill 命名时容易踩的认知陷阱

### 陷阱 A：凭程序员审美起名

`papers`、`notes`、`exam`、`profile`、`scaffold` 都太"程序员化"——用户觉得"太随意"。

**修正**：名字要让**用户能直觉理解做什么**，不需要懂技术术语。

### 陷阱 B：用品牌名当通用名

`IosTools`、`AndrowsData`、`DingTalk-exporter` 都含品牌名——用户觉得"也是品牌名呀"。

**修正**：用**类型/用途**而不是**品牌**命名（`MobileTools`、`Collab`、`ChatExporter`）。

### 陷阱 C：缩写以图简短

`OC`、`Ios` 缩写——用户说"能不能不要用单词缩写"。

**修正**：完整拼写（`OnlineClass`、`iOS` 但要避开 → `MobileTools`）。

### 陷阱 D：名字和已有目录冲突

`Cloud/Software/` 和 `D:/Software/` 名字雷同——用户觉得"和 D 盘根目录里的 Software 雷同了"。

**修正**：起新名（`Cloud/Library/` 而不是 `Cloud/Software/`）。


## 批量替换的陷阱

⚠️ 用 `replace_all` 批量替换字符串时，会破坏语义位置：

| 字段 | 替换前 | 替换后（错误） |
|---|---|---|
| `supersedes:` | `supersedes: cloud-file-orchestrator + host-context` | `supersedes: filesystem + filesystem` |
| 章节标题 | `## §0 filesystem 合并由来` | `## §0 filesystem 合并由来`（自指废话）|
| 历史段落 | `由 cloud-file-orchestrator + host-context 合并` | `由 filesystem + filesystem 合并` |

**正确做法**：
- 先 `grep` 列受影响行（`grep -rn "旧名" 目标目录`）
- 确认替换语义安全后**逐个 patch**
- 不要盲目 `replace_all`

## 历史教训

| 日期 | 错误 | 教训 |
|---|---|---|
| 2026-06-13 | 起名 "cloud-file-orchestrator"（3 词）| 问用户再命名 |
| 2026-06-13 | 提议合并后用 "cloudfiles" | 先写心智模型再起名 |
| 2026-06-15 | 先定名再问 "Library 还是 Stash" | 应该先列 3-5 个候选让用户选 |
| 2026-06-15 | 起名 "OC" | 用户不要缩写 |
| 2026-06-15 | 用 "IosTools" | iOS 是品牌，改 MobileTools |
| 2026-06-13 | replace_all 批量替换造成自指 | 逐行 patch |
| 2026-06-13 | 合并时先用 "cloudfiles" | 先合并还是先起名？先起心智模型 |

## 用户原话引用（保留）

> "你先告诉我filesystem里面对Archieve文件夹的定义" — 提示 Agent 不要凭印象，先看现状

> "你这个名字取得也太随意了吧？Cloudfile是你之前的理解偏差了，现在这个skill不只是处理Cloud文件夹了，是处理整个电脑" — 提醒名字要反映真实心智

> "iOS也是品牌名呀" — 品牌不止主流品牌，子品牌也算

> "能不能不要用单词缩写" — 可读 > 简短

> "我觉得应该再问，再看，最后才动" — scan → ask → preview → wait 工作流