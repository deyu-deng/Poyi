
---
title: log
created: 2026-07-06 00:25:55
---

# Wiki 变更日志

## 2026-07-06 00:25:55 — AI Ingest 首次运行

- 原料：`2026-07-05/knowledge.json`（aggregate_win.py v4.0 产出，7域54会话21130条消息）
- 类型：全量首次填充
- 创建页面：Agent-数字分身.md, 私域内容运营.md, Poyi-系统审计.md, Courses-模块化管理.md, Loom-消化管线.md, 定时任务生态.md, HarmonyOS-开发.md
- 清理：删除 Phase 1 中 v5 正则脚本遗留的 261 个低质量 .md 文件
- 规范：claude-obsidian Karpathy LLM Wiki 架构
*（内容由AI生成，仅供参考）*

## 2026-08-16 — Poyi 每日消化（Mac+Win 合并）首次运行
- 原料：digested/2026-08-16/_sessions_extract.json（20 会话，Mac+Win 合并）
- 提炼：decisions 7 / preferences 3 / knowledge 8
- 写回：decisions.json / preferences.json / knowledge.json
- 说明：统一聚合脚本 aggregate_unified.py 取代双机互相覆盖的旧架构；此前回流自 2026-07-06 停滞，今日恢复。


## 2026-08-12 — 新项目立项：Stithy（编程语言系统）

- 创建 Vault/projects/Stithy/：plan.md（六阶段路线图）+ progress.md + research.md
- 定位：从零完全手写编译器 + VM + GC，AI 仅顾问不代写，长期项目
- 技术方向：先字节码后 JIT；HM 类型推断起步；目标自举

## 2026-08-12 — 命名定案：Forge → Stithy

- 语言名与项目名统一为 Stithy（古英语"铁砧/铁匠铺"，/ˈstɪði/，与 Forge 同源）
- 全库检索验证无编程语言占用；弃用 Whetstone / Tuyere
- 项目目录 Forge → Stithy，plan.md / progress.md / research.md / INDEX.md / AGENTS.md 同步更新
- 宏伟目标定案：性能对标 C/Rust、自举、零依赖手写（不用 LLVM 后端）

## 2026-08-14 — 实现语言定案：Rust

- Stithy 实现语言拍板 Rust（所有权 + 模式匹配适合 AST 与 VM，生态成熟）
- progress.md / plan.md / research.md / INDEX.md 同步更新

## 2026-08-17 — 项目文档模板重构：三件套 + 英文标题

- newproject skill Step 6 模板重构：标准区块标题统一英文单词（Goal / Roadmap / Milestones / Status / Decisions / Risks / References / Sprint / Log / Notes / TODO）
- 三件套职责重新切分：plan.md（蓝图，删命名史/自举原理）· progress.md（看板：Status + Sprint + 倒序 Log）· research.md（Notes + TODO）
- README 模板「一句话目标」同步改为 Goal
- Stithy 三件套按新模板重排；Poyi / Nymo 补齐 research.md
- INDEX.md 全项目补 research.md 链接；dist 重新编译
