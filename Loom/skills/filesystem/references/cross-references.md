# Filesystem skill 交叉引用清单

> 任何更新 filesystem skill 时，先检查此清单避免遗漏。

---

## 与 inbox skill 的引用

> **2026-08-23 更新**：inbox skill 已并入 Loom 权威库时归档移除，以下引用为历史记录，目标文件已不存在，不再作为 active 引用。

### MSYS 路径陷阱（跨 skill 通用规则）

- **定义位置**：~~`inbox/references/cron-delivery-pitfalls.md §F`~~（inbox 已移除）
- **filesystem 应引用的位置**：§0 关键陷阱（在陷阱 0.11 之后加一条 0.12）
- **当前状态**：⚠️ 源已失效，规则已由 filesystem SKILL.md §0 陷阱覆盖
- **规则摘要**：脚本里出现 `/c/` `/d/` `/tmp/` 一律视为 bug，改用 `$TEMP` `%TEMP%` 或 `D:\\` 绝对路径
- **真实案例**：2026-06-15 20:11 inbox cron 把 `/c/tmp/` 解析为 `D:\\c\\tmp\\`，在 D 盘根创建了 `c/` 目录

---

## 与 profile skill 的引用

### 已通过 depends_on 显式声明

- filesystem 的 `metadata.depends_on` 写了 `user-profile（仅项目编号生成时）`
- 实际触发场景：用户在 filesystem 操作中提到"建项目 XX"→ 自动加载 profile 取学校/学院信息
- 当前状态：✅ 正常

---

## 与 project skill 的引用

### 通过 §3.2 决策树引用

- "我要新建一个项目？" → 调用 `project` skill
- filesystem §3.2 写了这一行
- 当前状态：✅ 正常

---

## 与 papers skill 的引用

### 通过 §4.2 决策树引用

- 科研项目结构（Research/{NN-主题}/Lit/...）详细规则在 `papers/schemas/folder-structure.md`
- filesystem §4.2 写了"详细见 papers skill"
- 当前状态：✅ 正常

---

## 维护规则

- 每次 filesystem SKILL.md 有大改 → 必须检查本清单
- 任何新加 §0 陷阱 → 确认是否需要 cross-reference
- 其他 skill 提到 filesystem → 反向更新本清单

---

*2026-06-15 创建*