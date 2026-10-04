# Poyi Skill 内容规范与结构标准 (v1.1)

> 基准：Claude **Agent Skills 开放标准** + Claude Code 扩展字段
> 定位：Poyi 全部 skill 的**唯一写法标准**。新建 / 改写 skill 必须遵守。AGENTS.md 为系统权威，本规范是其子规范。
> 由来：agents 直接写的 skill 又烂又重复（腐烂度审计 2.6/10）。本规范用于治本——给 agent 一个必须套用的模板，并据此 retrofit 现有 22 个活跃 skill（animation raw-arsenal 已归档 `_archive/`，不计入活跃数）。

---

## 1. 标杆：Claude 官方怎么写（提取自官方文档）

- **SKILL.md 是核心**：每个 skill 是一个目录，至少含 `SKILL.md`。
- **frontmatter 只两个必填字段**：`name`、`description`。
  - `name`：≤64 字符，仅小写字母 / 数字 / 连字符，无 XML 标签，无保留词 `anthropic`/`claude`。
  - `description`：≤1024 字符，非空，无 XML 标签。**第三人称**，写"做什么 + 何时用 + 触发词"。这是**发现字段**——Claude 据此从 100+ 技能里挑正确的那个。
- **可选字段（官方开放标准 + Claude Code 扩展，认可）**：`allowed-tools`、`license`、`metadata`、`model`、`context`、`agent`、`user-invocable`、`disable-model-invocation`、`hooks`、`argument-hint`。参数通过 `$ARGUMENTS` 占位符传递（无 `arguments` 字段）。`metadata` 是官方规定的客户端扩展机制（string→string map）——Poyi 若有自定义数据应放这里，而非新增自由字段。"何时用"信息直接写进 `description`，不另设字段。
- **渐进式披露**：`SKILL.md` 正文 **<500 行**；详细内容拆到 `references/`（或 `reference.md`）；可执行脚本放 `scripts/`（执行不载入上下文）。引用只一层深；长参考文件（>100 行）顶部加目录。
- **命名**：推荐动名词（`processing-pdfs`）或名词短语（`pdf-processing`）；避免 `helper`/`utils`/`tools` 等模糊名，`documents`/`data`/`files` 等通用名，及保留词。
- **反模式（禁用）**：Windows 反斜杠路径、堆砌多种方案、深层嵌套引用、时效硬编码、模糊描述、脚本裸崩不处理异常、假设依赖已装。

---

## 2. Poyi 标准（对齐官方，废弃四角色）

### 2.1 Frontmatter —— 唯一允许的字段

**必填（官方）**
| 字段 | 约束 |
|---|---|
| `name` | kebab-case，同目录名，≤64 字符 |
| `description` | 第三人称，做什么+何时用+触发词，≤1024 字符 |

**可选（官方开放标准 + Claude Code 扩展，认可）**
| 字段 | 用途 |
|---|---|
| `allowed-tools` | 技能回合内预授权工具（Poyi 已在 `poyi` 使用，语法正确） |
| `license` | 技能许可证（官方可选字段） |
| `metadata` | **官方扩展机制**：string→string map，存放 Poyi 自定义数据；新增自由字段一律走这里，不另造顶层字段 |
| `model` / `context` / `agent` | Claude Code 子代理 / 模型覆盖 |
| `user-invocable` / `disable-model-invocation` | 调用权限控制 |
| `hooks` / `argument-hint` | 生命周期钩子 / 参数补全提示 |

**禁止（非官方自由字段，必须删除）**
```
role  version  type  created  status  title  when_to_use
scope  layer  supersedes  source  x-role  x-depends-on
以及任何其他非上述"可选"表的顶层字段
```
> 注：`metadata` 与 `license` 是官方可选字段，**不在禁止之列**（见上表）。`when_to_use` **不是真实字段**——"何时用"必须写进 `description` 本身，不要另设字段。
> **四角色路由系统已废弃（用户决策 2026-07-27）**。`role`/`x-role` 一律删除，技能不再按 `Librarian`/`Manager`/`Tutor`/`Engineer` 分类；路由完全靠官方标准的 `name` + `description` 语义匹配。`version`/`type`/`created`/`status`/`title` 一律删除——审计病灶③，对路由零价值。`x-depends-on` 也删：编排依赖改为在正文中自然语言描述，不进 frontmatter。Poyi 若有自定义数据，放进官方 `metadata` map，而非新增自由字段。

### 2.2 description 写法（最关键的质量杠杆）

- **第三人称**陈述句；**必须含**功能 + 触发场景 / 关键词。
- ❌ 差：`"英语学习增强器：用户问英语表达时，先检索 Vault..."`（标签式 + 一二人称）
- ✅ 好：`"检索 Vault 知识库锚点解释英语表达，并将学习痕迹沉淀到 Loom/wiki/english-data/。当用户询问英语用法、地道表达或想积累语料时触发。"`
- 中文技能用中文描述，但严守「第三人称 + 触发词」原则。

### 2.3 命名
- kebab-case 小写（当前已合规）。可选优化为动名词，非强制。

### 2.4 正文与结构
- `SKILL.md` 正文 **<500 行**（当前 0/25 超标，保持）。
- **路径一律正斜杠 `/`**（修复 10/25 的反斜杠跨平台污染）。
- 详细内容拆 `references/`；脚本 `scripts/`。引用只一层深；长文件顶部加目录。
- 标准目录：
  ```
  skill/
  ├── SKILL.md        # 名称 + 描述 + 精简指令
  ├── eval.md         # 触发/不触发用例（离线 eval 回路，强制）
  ├── references/     # 按需载入的详细材料
  └── scripts/        # 可执行脚本（执行不载入）
  ```

### 2.5 反模式（禁用清单）
反斜杠路径 · 堆砌选项 · 深层嵌套引用 · 时效硬编码 · 模糊描述/名称 · 脚本不处理异常 · 假设依赖已装 · **AIGC 水印块（已清，禁止再出现）**。

---

## 3. 规范模板（agent 新建 skill 必须套用）

```yaml
---
name: <skill-name>
description: <第三人称：做什么 + 何时用 + 触发词>
allowed-tools: <可选，如 Read Write Edit Grep Glob>
---
# <Skill 名>

## 概述
<一句话说清解决什么、何时用>

## 用法
<核心步骤 / 伪代码 / 脚本调用>

## 参考
- 详见 [references/xxx.md](references/xxx.md)（按需载入）
- 触发/不触发用例见 `eval.md`（见下）

## eval.md 模板（强制，新建 skill 必带）

```markdown
## Should trigger
- 用户说"xxx"
- 用户丢来一段资料要入库
- ...（≥3 条真实意图）

## Should not trigger
- 用户只是问"xxx"（应由 YYY 处理）
- ...
（≥3 条易误触发场景）
```

> `manage_skills.py eval` 离线启发式校验：should-trigger 需命中 description 触发词或 token 重叠≥2；should-not-trigger 不得含触发词。每条用 `- ` 列表。
```

---

## 4. 当前差距（2026-07-25 扫描）

| 指标 | 结果 |
|---|---|
| 活跃 skill 数 | **22**（animation 归档 `_archive/`，notecraft 并入 notes） |
| 非标准 frontmatter 字段 | **0/22** ✅（已批量去 cruft） |
| 正文 Windows 反斜杠 | **0/22** ✅（11 文件已翻正斜杠） |
| 正文超 500 行 | 0/22 ✅ |
| 重复技能 | `research` 已合并进 `autoresearch` |
| 四角色 | **已废除**（AGENTS §2 / INDEX / manage_skills 全扁平化） |
| eval.md 覆盖 | **22/22** ✅（全部活跃 skill 已带，新建 skill 强制带） |

---

## 5. 执行记录（2026-07-27 已落地）

- ✅ 批准本规范为 Poyi skill 唯一标准（用户决策：不要四角色，太麻烦了）。
- ✅ 批量去 cruft：25 个 `SKILL.md` 删除全部非标准字段（`triage` 补建缺失 frontmatter）。
- ✅ 修反斜杠：11 文件正文 `\`→`/`。
- ✅ 合并 `research`→`autoresearch`（唯一真重复，25→25 实际去重）。
- ✅ 修订配套：AGENTS.md §2 / INDEX.md 去四角色、改扁平清单；`manage_skills.py` 删 `LEGACY_ROLE_MAP`、补 `delete`、sync 强制校准 frontmatter（自愈）。
- 注：`description` 的"第三人称 + 触发词"提质为持续编辑项，新建 skill 时由 §3 模板保证。

---

## 6. 给 agent 的硬规则（写入新建流程）

> 任何 agent 新建或修改 skill 前，必须先读本文件并套用 §3 模板。
> 禁止在非标准 frontmatter 字段里写任何东西。禁止反斜杠路径。禁止模糊 description。
> 不确定技能是否重复时，先查 INDEX.md 与 §4，再动手。
> **新建 / 修改 skill 必须带 `eval.md`**（§3 模板）：`## Should trigger` 与 `## Should not trigger` 各 ≥3 条，由 `manage_skills.py eval` 离线校验；缺 eval 视为不合格。

---

## 7. 生命周期治理（P1，已落地 2026-07-27）

技能不是写完就完事——需要版本、归属、过期扫描与依赖声明，否则会再次腐烂。

### 7.1 metadata 强制字段（frontmatter 的 `metadata` map 内，不新增顶层字段）
- `version`：语义化版本（如 `1.2.0`），每次实质改动 +1。
- `owner`：责任人 / agent 名（如 `sample-user`）。
- `last_validated`：最近一次 `manage_skills.py eval` 通过的日期（ISO `YYYY-MM-DD`）。
- `deps`：本技能显式依赖的其他 skill 名数组（如 `["filesystem"]`）；用于组合编排与悬空检测。

### 7.2 ⚠️ metadata 必须写成单行 inline-JSON（sync 存活关键）
`manage_skills.py` 的 frontmatter 解析是**朴素**的：`parse_frontmatter` 只保留单行 `key: value`，`build_frontmatter` 只按 `ALLOWED_KEYS` 重建并原样回填 `metadata` 字符串。
→ **嵌套 YAML（多行 map / list）会在 `sync` 时被抹掉。** 唯一安全写法：把四个字段压成一行 inline-JSON 挂在 `metadata:` 下（合法 YAML flow-mapping，值为字符串，被原样保留）：

```yaml
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": ["filesystem"]}
```

读取用 `parse_metadata()`：`json.loads` 容错解回 dict。新增字段直接往这个 JSON 里加，别另造顶层键。

### 7.3 `manage_skills.py doctor`（已实现）
离线健康扫描，分级输出 ERROR / WARN / INFO：
- **ERROR**：缺 `eval.md`；缺 `metadata`；`version`/`owner`/`last_validated` 任一缺失。
- **WARN**：`last_validated` 超 90 天；`deps` 指向不存在的 skill（悬空）。
- **INFO**：`description` 无显式 `触发词：` 标记（非阻断，靠 eval 的 token 重叠兜底）。
- 实测（2026-07-27）：22 技能，0 ERROR，0 WARN，13 INFO。

### 7.4 入库闭环
新建 / 修改 skill 后跑 `manage_skills.py sync && manage_skills.py eval && manage_skills.py doctor`，eval 0 警告、doctor 0 ERROR/WARN 方可入库。

---

## 8. 度量边界与跨技能门禁（2026-08-16 落地）

> 第一性原理复盘结论：治理门禁（eval/doctor）度量的是「是否符合规范」，不是「能否把事做成」。
> 本节能把度量从「像不像 skill」推到「会不会撞车」，但**能力冒烟测试**（薄/外部脚本类 skill 实际跑通）仍未建——这是下一步杠杆，不是本文件范围。

### 8.1 触发词声明式约定（消除 13 个 INFO）
- 全部 22 个 skill 的 `description` 必须含显式 `触发词：` 段（已补完，doctor 的 INFO 已归零）。
- 格式约束：`触发词：` 后接 `、` 分隔的 token；**token 内不得含空格**（否则 `extract_triggers` 按 `\s` 拆碎，产生伪 token / 误撞）；单个 token 长度 ≤10（防描述里误吞的散文片段被当成触发词）。
- 语义重叠但模态不同的 skill，用**不同 token** 区分，而非共用（见 §8.3）。

### 8.2 跨技能门禁（A，已并入 doctor，不新建文件）
- `manage_skills.py` 新增 `scan_trigger_collisions()`：收集每个 skill 的显式触发 token，**两个 skill 精确声明同一 token 即报 WARN**（路由歧义）。
- 已在 doctor 末尾输出「跨技能触发词碰撞」段；当前 22 技能 **0 碰撞**。
- 设计原则：**直接并入已有 doctor，不另起测试 harness / 不新建测试文件**。

### 8.3 已解决的真实相撞
- `filesystem` 摘除 `建项目`（2026-08-16）：`newproject` 才是「建项目」执行层，`filesystem` 仅决策层（路由到 newproject）。两者不再争同一 token。

### 8.4 治理红线（用户 2026-08-16 明确：合并为主、能不新建就不新建）
1. **语义重叠优先合并**，而非保留二者或新建第三个。
2. **扩能力优先编辑已有 skill / 已有脚本**；不新建 skill、不新建独立脚本文件——新门禁/新检查一律并入 `manage_skills.py`。
3. 任何「新建」动作须先在 skill-standard 留痕并说明理由。

### 8.5 合并优先的待办（下一步，未执行）
- **`save ⊂ ingest`**：`save`（对话归档）本质是 `ingest`（文件/URL/图片/聊天记录吞入）的模态子集；`ingest` 描述已声明「整理聊天记录进知识库」。建议将 `save` 合并进 `ingest`（删 `save/` 目录 + 改 `poyi/SKILL.md` 引用 + sync 重建表格）。当前仅澄清边界：`save` 触发词限定为「对话归档 / 保存对话 / 存这次讨论」，与 `ingest` 的「文件/URL」明确分流。
- `query` / `wiki-retrieve`：已用 `deps` 显式（`wiki-retrieve → query`），`query` 为只读主路径、`wiki-retrieve` 为语义兜底，边界清晰，暂不合并。
