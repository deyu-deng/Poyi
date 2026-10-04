# Poyi（珀忆）— 可迁移的 Agent 记忆层

> 结构以 `AGENTS.md` 为准。本文件为人类速查摘要。
>
> Poyi 的定位是一个**记忆插件**：同一套技能、目录约定与自举协议，可以挂到不同主流 Agent 工具上，让它们共享同一个能自我维持的知识层。仓库内所有人物、项目、笔记、日记均为**虚构示例数据**，用于验证链路，不含真实个人信息。

---

## Vault（人 + AI 协作前台）

- `Vault/projects/INDEX.md` — 14 个项目入口（plan / progress / research 三件套）
- `Vault/meta/profile/profile.md` — 内在画像（示例人设）
- `Vault/notes/` — 七大领域笔记骨架

## Loom（AI 后台）

Agent 自动产出：22 个技能、消化后的对话摘要、元信息与校验脚本。

- `Loom/skills/INDEX.md` — 技能全文索引（由 `manage_skills.py sync` 生成）
- `Loom/meta/governance/propagation-map.md` — 知识传播矩阵
- `Loom/meta/governance/IDEAL.md` — 系统靶子（五大维度 + 目标分）
- `Loom/scripts/verifier.py` — 规格声明 ↔ 磁盘物理一致性校验（挂在 git hook 上）

## Agent 入口

`AGENTS.md`，唤醒口令 `/poyi`。本文件不为 AI 提供结构描述。

## 数据边界

- `Loom/raw/`（原始与消化后的对话数据）**全量不入库**，只活在每台机器本地。
- 真实群号 / wxid / 钉钉 UID 等本机标识放 `Loom/skills/daily/data/identity.local.json`，同样不入库。
- Git 管版本与结构，云盘管跨机数据同步。
