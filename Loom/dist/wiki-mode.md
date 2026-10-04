<!-- source: wiki-mode -->
---
name: wiki-mode
description: "Loom 方法论模式切换器：管理 wiki 底层目录拓扑，支持 generic/lyt/para/zettelkasten 四种组织方法论。切换模式只影响未来写入（不迁移已有文件），路由规则存于 Loom/.vault-meta/mode.json。 触发词：wiki模式、方法论切换、zettelkasten、para。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": []}
---
# wiki-mode: Loom 方法论模式切换器

你是 Loom 织机的组织哲学开关。你管理 wiki 的底层目录拓扑——不同组织方法论对应不同的文件路由规则、ingest 产物落点、index 生成结构。

模式决定 wiki 如何生长。切换模式不迁移已有文件，只影响未来写入。

---

## 依赖声明

- **poyi** 技能：wiki 脚手架和总体架构
- **ingest** 技能：新建页面的落盘路径受当前模式影响
- **create** 操作：默认写入路径由模式决定
- 模式配置存储于 `Loom/.vault-meta/mode.json`

---

## 命令入口

| 命令 | 行为 |
|------|------|
| `/wiki-mode` | 查看当前模式及其路由规则摘要 |
| `/wiki-mode set <mode>` | 切换到指定模式（更新 mode.json，不迁移文件） |
| `/wiki-mode list` | 列出所有可用模式及一句话描述 |

---

## 四种模式

### 模式 1: generic（默认）

基础分类式组织。按内容类型分目录。与当前 poyi 技能默认 wiki 结构一致。

**适用场景**：通用个人知识库、无特定方法论偏好。

**文件路由规则**：

| 操作 | 写入路径 |
|------|----------|
| ingest 新建 source 页 | `wiki/sources/<slug>.md` |
| ingest 新建 entity | `wiki/entities/<slug>.md` |
| ingest 新建 concept | `wiki/concepts/<slug>.md` |
| create 通用笔记 | `wiki/sessions/<slug>.md` |
| ingest 会话捕获 | `wiki/sessions/<slug>.md` |
| comparisons | `wiki/comparisons/<slug>.md` |

**目录结构**：
```
wiki/
├── index.md
├── log.md
├── hot.md
├── overview.md
├── sources/       # 资料来源页
├── entities/      # 实体页
├── concepts/      # 概念页
├── sessions/      # 对话/归档
├── comparisons/   # 对比页
├── meta/          # 元信息
└── review/        # 复习数据
```

---

### 模式 2: lyt (Linking Your Thinking)

Nick Milo 的 LYT 方法论。以 Map of Content（MOC）为中心，原子笔记平铺存储。

**适用场景**：重链接、重涌现结构、想先写后组织的知识工作者。

**文件路由规则**：

| 操作 | 写入路径 |
|------|----------|
| 新建 MOC（导航页） | `wiki/mocs/<topic>-moc.md` |
| ingest / create 原子笔记 | `wiki/notes/<YYYYMMDDHHMMSS>-<slug>.md` |
| ingest 会话捕获 | `wiki/notes/<YYYYMMDDHHMMSS>-session-<slug>.md` |

**目录结构**：
```
wiki/
├── index.md
├── log.md
├── hot.md
├── mocs/           # Map of Content 导航页
│   ├── home-moc.md
│   ├── physics-moc.md
│   └── ...
├── notes/          # 原子笔记（时间戳平铺）
│   ├── 20260630143000-量子纠缠.md
│   ├── 20260630143100-爱因斯坦.md
│   └── ...
├── meta/
└── review/
```

**index.md 生成规则**：列出所有 MOC，每个 MOC 下列出其首层链接（不展开深度）。

---

### 模式 3: para

Tiago Forte 的 PARA 方法论。按可操作性（actionability）四层分类。

**适用场景**：项目管理导向、有明确交付物、需要区分"当前"与"未来"。

**文件路由规则**：

| 操作 | 写入路径 | 说明 |
|------|----------|------|
| ingest 与活跃项目相关 | `wiki/projects/<project-slug>/sources/<slug>.md` | ingest 时若检测到与某项目相关则写入项目子目录 |
| ingest 通用 / 无归属 | `wiki/resources/<slug>.md` | 默认落入 resources |
| create 项目笔记 | `wiki/projects/<project-slug>/<slug>.md` | 手动创建时需指定项目 |
| create 领域笔记 | `wiki/areas/<area-slug>/<slug>.md` | 手动创建时需指定领域 |
| ingest 会话捕获 | `wiki/projects/<project-slug>/sessions/<slug>.md` 或 `wiki/resources/<slug>.md` | 有项目归属 → project；否则 → resources |

**目录结构**：
```
wiki/
├── index.md
├── log.md
├── hot.md
├── projects/       # 有 deadline、有终点的活跃任务
│   ├── srtp/
│   └── plobi-os/
├── areas/          # 责任区，持续维护、无终点
│   ├── 物理 Physics/
│   └── 人工智能 AI/
├── resources/      # 参考库（无直接行动关联的储备知识）
└── archives/       # 封存区（已完成/冷置的项目和领域）
```

**index.md 生成规则**：按 P-A-R-A 四层分组，每组下列出子项和最新 5 条笔记。

---

### 模式 4: zettelkasten

卢曼卡片盒方法。完全扁平化，无子目录，按时间戳原子化。

**适用场景**：纯原子化思维、追求涌现链接、无预设分类框架。

**文件路由规则**：

| 操作 | 写入路径 |
|------|----------|
| 所有写入（ingest/create） | `wiki/<YYYYMMDDHHMMSSffffff>-<slug>.md` |

**目录结构**：
```
wiki/
├── index.md
├── log.md
├── hot.md
├── 20260630143000000001-量子纠缠.md
├── 20260630143100000002-爱因斯坦.md
├── 20260630143200000003-On the Electrodynamics.md
├── ...（全平铺）
├── meta/
└── review/
```

**index.md 生成规则**：按域标签聚合（从 frontmatter `tags` 提取），每个 tag 下列出最新 10 条。

**时间戳精度**：微秒级（`ffffff`），防止批量写入碰撞。

---

## 模式配置文件

存储于 `Loom/.vault-meta/mode.json`：

```json
{
  "version": "1.0.0",
  "current_mode": "generic",
  "switched_at": "2026-06-30T00:00:00",
  "history": [
    {"mode": "generic", "set_at": "2026-06-27T00:00:00", "reason": "initial scaffolding"}
  ]
}
```

每次切换追加一条 history 记录，保留完整切换轨迹。

---

## 影响范围

切换模式后，以下操作的行为发生变化：

| 受影响操作 | 变化说明 |
|------------|----------|
| **ingest** | 新建页面的落盘路径按新模式路由 |
| **create**（手动建笔记） | 默认路径变化；某些模式需要额外参数（如 para 模式需要指定 project/area） |
| **index 生成** | `index.md` 的结构和分组方式随模式变化 |
| **query** | 检索路径不同（lyt 先查 MOC，zettelkasten 按 tag 聚合） |
| **lint** | 检查规则不同（para 检查 project→archives 流转合理性，zetelkasten 检查命名规范） |

---

## 硬约束

- **切换模式不自动迁移已有文件**。旧文件保留在原路径。如需迁移，用户需显式要求并确认批量移动。
- 首次从 generic 切换到其他模式时，必须警告用户：索引结构会变化，已有页面不会自动迁移。
- 切换模式后必须重建 `wiki/index.md`。
- 模式信息写入 `Loom/.vault-meta/mode.json`，不写入 Vault（Vault 不可见 Loom 内部状态）。

---

## 示例

### 用户：`/wiki-mode`

输出：

```
当前模式：generic（基础分类式）

路由规则：
  sources  → wiki/sources/
  entities → wiki/entities/
  concepts → wiki/concepts/
  sessions → wiki/sessions/
  comparisons → wiki/comparisons/

模式历史：
  2026-06-27  generic  initial scaffolding
```

### 用户：`/wiki-mode set lyt`

输出：

```
已切换到 LYT 模式。

路由变更：
  原子笔记 → wiki/notes/<timestamp>-<slug>.md
  MOC 导航 → wiki/mocs/<topic>-moc.md

已有文件未迁移（12 个页面保留在 wiki/entities/、wiki/concepts/ 等原位置）。
index.md 已重建为 MOC 导航视图。

如需迁移已有文件，请显式要求。
```

---

## 自举指令

首次加载本技能时：

1. 检查 `Loom/.vault-meta/` 目录是否存在
   - 不存在 → 创建目录，写入默认 `mode.json`（`current_mode: "generic"`）
2. 检查当前 wiki 结构与 mode.json 是否一致
   - 不一致 → 提示用户当前目录结构看起来像「X 模式」，但配置文件写的是「Y 模式」，询问是否需要修正配置
3. 输出当前模式摘要（路由规则）
4. 此后 `poyi` 技能的 scaffold 操作在创建 wiki 结构前，首先查询本技能获取当前模式
