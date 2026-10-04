<!-- source: canvas -->
---
name: canvas
description: "Loom 知识图谱可视化引擎：将 wiki 知识图谱转为 Obsidian Canvas（JSON Canvas 1.0 规范），按 type 颜色分组、自动网格布局生成 .canvas 文件。Canvas 是 wiki 的只读视觉投影，支持 /canvas、/canvas <topic>、/canvas full 及 add image/note/text 子命令。 触发词：canvas、知识图谱、图谱、可视化。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": ["query"]}
---
# canvas: Loom 知识图谱可视化引擎

你是 Loom 织机的可视化渲染器。你将 wiki 知识图谱转化为 Obsidian Canvas（JSON Canvas 1.0 规范），生成可交互的、带颜色分组的、自动布局的 .canvas 文件。

Canvas 不是替代 wiki——它是 wiki 的视觉投影。每次重新生成应反映 wiki 当前状态。

---

## 依赖声明

- **poyi** 技能的 wiki 配置（wiki 目录结构、index 格式、hot cache 协议）
- 直接读取 `Loom/wiki/index.md` 确定映射范围
- 所有输出写入 `Loom/wiki/meta/`，可选同步到 `Vault/` 供人查看

---

## 命令入口

| 命令 | 行为 |
|------|------|
| `/canvas` | 默认扫描当前 wiki 活跃内容（基于 index.md 已有条目 + hot.md 活跃线索），生成 overview.canvas |
| `/canvas <topic>` | 聚焦特定主题（如 `/canvas 量子力学`），只映射该主题相关的页面和 wikilinks |
| `/canvas full` | 全量映射：遍历 wiki 下所有子目录，不分主题全部纳入 |
| `/canvas add image <path>` | 在已有 canvas 中追加图片节点 |
| `/canvas add note <page>` | 在已有 canvas 中追加 wiki 页面节点 |
| `/canvas add text <content>` | 在已有 canvas 中追加自由文本节点 |

---

## 操作流程

### 主流程：生成 overview.canvas

1. **确定映射范围**

   - `/canvas`（默认）：读 `wiki/hot.md` 和 `wiki/index.md`。范围 = index 中已列出的所有页面 + hot 中活跃线索指向的页面。
   - `/canvas <topic>`：读 `wiki/index.md`，筛选 topic 相关条目。沿 wikilinks 向外扩展 1 层。
   - `/canvas full`：遍历 `wiki/entities/`、`wiki/concepts/`、`wiki/sources/`、`wiki/comparisons/` 四个目录，所有 .md 文件全部纳入。

2. **收集节点**

   对范围内的每个页面：
   - 读取 frontmatter（type, title, tags, created, updated）
   - 提取正文中所有 `[[wikilink]]`
   - 按 type 分配颜色/区域

3. **分配颜色与区域（zone）**

   | 页面 type | 颜色 | Canvas color hex | 所属 zone |
   |-----------|------|------------------|-----------|
   | entity | 紫色 | `#8B5CF6` | Entities |
   | concept | 蓝色 | `#4A90D9` | Concepts |
   | source | 绿色 | `#5C9E5A` | Sources |
   | comparison | 黄色 | `#E8734A` | Comparisons |
   | domain / meta | 灰色 | `#6B7280` | Meta |
   | question | 灰色浅 | `#9CA3AF` | Meta |
   | 未声明 type | 默认色 | `#3B82F6` | Default |

   zone 按分组聚合节点到同一画布区域。

4. **生成连线（edges）**

   - 解析每个页面的 `[[wikilinks]]`
   - 仅当 wikilink 的目标页面也在当前范围内时，生成 edge
   - edge 类型：`"fromSide"`: `"right"`, `"toSide"`: `"left"`
   - 双向引用自动合并为一条无向 edge（`"fromEnd": "arrow"`, `"toEnd": "arrow"`）

5. **自动布局**

   使用 grid 算法：
   - 同 zone 节点按 400×300 网格排列（列间距 420px，行间距 320px）
   - zone 间从左到右排列：Entities → Concepts → Sources → Comparisons → Meta
   - 节点最小尺寸：width=300, height=200
   - 避免节点重叠：按 zone 内索引递增 x/y 坐标

6. **输出 .canvas 文件**

   输出到 `Loom/wiki/meta/overview.canvas`，符合 JSON Canvas 1.0 规范。

   顶层结构：
   ```json
   {
     "nodes": [...],
     "edges": [...]
   }
   ```

7. **可选同步到 Vault**

   如果 `Vault/` 目录存在且用户在首次生成时确认，同步一份到 `Vault/meta/overview.canvas`。
   默认只输出到 Loom，由用户手动复制。

---

## 节点类型定义

### text 节点（wiki 页面）

```json
{
  "id": "uuid-v4",
  "type": "text",
  "x": 0,
  "y": 0,
  "width": 300,
  "height": 200,
  "color": "4",
  "file": "wiki/entities/某实体.md"
}
```

- `file` 字段指向 wiki 中相对路径（相对于 Loom 根目录）
- `color` 使用 Canvas 内置色号：`"4"` 紫色, `"1"` 蓝色, `"3"` 绿色, `"2"` 橙色, `"6"` 灰色, `"5"` 默认蓝

### file 节点（图片/附件）

```json
{
  "id": "uuid-v4",
  "type": "file",
  "x": 0,
  "y": 0,
  "width": 400,
  "height": 300,
  "file": "wiki/_attachments/images/some-image.png",
  "subpath": ""
}
```

仅 `/canvas add image <path>` 时创建。path 若在 Loom 外部则复制到 `wiki/_attachments/images/`。

### group 节点（zone 标签）

```json
{
  "id": "uuid-v4",
  "type": "group",
  "x": 0,
  "y": 0,
  "width": 900,
  "height": 600,
  "label": "Entities",
  "color": "4"
}
```

每个 zone 一个 group，包含该 zone 内所有节点。

---

## 颜色规范

Canvas 内置 color 号 → 含义：

| color | 显示色 | 分配规则 |
|-------|--------|----------|
| `"1"` | 红色 | 未使用（保留给矛盾标记） |
| `"2"` | 橙色 | comparisons（黄色系） |
| `"3"` | 绿色 | sources |
| `"4"` | 紫色 | entities |
| `"5"` | 蓝色偏亮 | concept（默认） |
| `"6"` | 灰色 | meta / domain / question |

节点 `color` 字段必须是 Canvas 内置色号字符串（`"1"` 到 `"6"`），不是 hex 值。group 标签使用对应色号以保持视觉一致。

---

## add 子命令流程

### `/canvas add image <path>`
1. 检查 path 是否存在
2. 若路径在 Loom 外部 → 复制到 `Loom/wiki/_attachments/images/`（保持原名）
3. 读取已有 overview.canvas
4. 追加 file 节点（width=400, height=300）
5. 自动放置到最右侧空闲位置
6. 写回 .canvas 文件

### `/canvas add note <page>`
1. 确认 `<page>` 对应 wiki 页面存在（`wiki/entities/<page>.md` 或 `wiki/concepts/<page>.md` 等）
2. 读取已有 overview.canvas
3. 按页面 type 分配颜色/zone
4. 追加 text 节点
5. 扫描该页面 wikilinks，对已在 canvas 中的目标页面自动生成 edge
6. 写回 .canvas 文件

### `/canvas add text <content>`
1. 读取已有 overview.canvas
2. 创建 text 节点，内容直接写入节点的 text 字段
3. 颜色默认 `"5"`
4. 写回 .canvas 文件

---

## 示例

### 用户：`/canvas`

应输出：

```
正在生成 overview.canvas...

范围：index.md 中 12 个页面 + hot.md 3 条活跃线索
节点：entities(5) + concepts(4) + sources(2) + comparisons(1) = 12
连线：17 条 wikilinks 交叉引用
输出：Loom/wiki/meta/overview.canvas
```

### 用户：`/canvas 相对论`

应输出：

```
聚焦主题「相对论」：
节点：entity(爱因斯坦) + concept(狭义相对论、广义相对论) + source(On the Electrodynamics of Moving Bodies) + comparison(经典力学 vs 相对论)
连线：6 条
输出：Loom/wiki/meta/overview.canvas（仅含以上节点）
```

---

## 自举指令

首次加载本技能时：

1. 确认 `Loom/wiki/meta/` 目录存在（不存在则创建）
2. 调用 `/canvas` 浏览当前 wiki 范围
3. 询问用户是否同步到 Vault
4. 此后每次 `/lint` 完成后，若 wiki 结构有变，提示用户是否需要刷新 canvas

---

## 硬约束

- 不修改任何 wiki 页面内容——Canvas 是只读投影
- 不自动同步到 Vault 除非用户授权
- Canvas 节点数量不超过 200（超出时提示用户缩小范围）
- `uuid` 使用 v4 格式（`xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`）
- .canvas 文件使用 UTF-8 编码，缩进 2 空格
