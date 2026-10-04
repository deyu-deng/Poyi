# dist/ — Loom Skill 编译产物目录

> 单一事实源 = `skills/`，本目录由 `python Loom/scripts/compile.py` 生成，请勿手改（本 README 除外）。

## 用途

`dist/` 存放 **编译后的单文件 skill**，供外部系统消费：

1. **宿主 Agent 注入** — 把 `dist/*.md` 注册为上下文文件，供所接入的 Agent 工具直接加载。
2. **跨平台分发** — 单文件格式便于拷贝到其他环境 / Claude Code / 其它 LLM 工具。
3. **平台标注保留** — 子文件里的 `<!-- platform: xxx -->` 编译后保留在附录中。

## 与 `skills/` 的关系

| 维度 | `skills/<name>/SKILL.md` | `dist/<name>.md` |
| ---- | --- | --- |
| 格式 | 多文件（主文件 + references/ 等子文件） | 单文件（主文件 + 内联附录） |
| 引用方式 | `references/foo.md`（分散） | 正文加 `(见附录 ...)` 标注 + 附录全文 |
| 可编辑性 | 直接编辑 | 不可直接编辑（重新编译会覆盖） |

**`dist/` 是编译产物，不是源文件。** 任何修改必须先在 `skills/` 中修改，再重跑 `python Loom/scripts/compile.py`。

## 当前文件清单（22 个）

| 文件 | 大小 | 来源 skill | 附录数 |
| ---- | --- | --- | --- |
| `autoresearch.md` | 8.1 KB | `skills/autoresearch/` | 1 个 |
| `campus.md` | 3.4 KB | `skills/campus/` | 无 |
| `canvas.md` | 7.8 KB | `skills/canvas/` | 无 |
| `daily.md` | 59.2 KB | `skills/daily/` | 5 个 |
| `defuddle.md` | 2.0 KB | `skills/defuddle/` | 无 |
| `english.md` | 7.1 KB | `skills/english/` | 无 |
| `exam.md` | 4.9 KB | `skills/exam/` | 无 |
| `filesystem.md` | 59.2 KB | `skills/filesystem/` | 5 个 |
| `ingest.md` | 13.1 KB | `skills/ingest/` | 无 |
| `lint.md` | 6.4 KB | `skills/lint/` | 无 |
| `notes.md` | 5.3 KB | `skills/notes/` | 无 |
| `papers.md` | 17.4 KB | `skills/papers/` | 5 个 |
| `poyi.md` | 10.7 KB | `skills/poyi/` | 无 |
| `profile.md` | 8.6 KB | `skills/profile/` | 无 |
| `project.md` | 21.2 KB | `skills/project/` | 无 |
| `query.md` | 5.8 KB | `skills/query/` | 无 |
| `review.md` | 4.4 KB | `skills/review/` | 无 |
| `save.md` | 5.1 KB | `skills/save/` | 无 |
| `think.md` | 10.6 KB | `skills/think/` | 无 |
| `triage.md` | 12.8 KB | `skills/triage/` | 2 个 |
| `wiki-mode.md` | 8.5 KB | `skills/wiki-mode/` | 无 |
| `wiki-retrieve.md` | 8.4 KB | `skills/wiki-retrieve/` | 无 |

## 维护规则

- `skills/<name>/SKILL.md` 或引用子文件被修改后，必须重跑 `python Loom/scripts/compile.py`。
- 不要手动编辑 `dist/*.md` — 下次编译会覆盖。
- 已跳过编译：`animation`（已移至 `skills/_archive/`，不再计入活跃 skill）。
- 本清单由磁盘实测生成（2026-10-04），此前手写版残留了已改名技能对应的旧产物行。
