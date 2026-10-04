---
INDEX_version: 0.1.0
last_updated: 2026-06-19
owner: sample-user
status: raw-arsenal
source_repo: https://github.com/vibe-motion/skills
source_stars: 721
source_forks: 52
source_commit: 2026-06-19T11:51:04Z
ingestion_date: 2026-06-19
---

# Skills/animation · 索引

> **目的**：存放「代码驱动动画」领域的原作者仓库快照，供**慢慢消化/转化**。
> **当前状态**：raw-arsenal（原始源码，未转化）。**不当作 skill 使用**，仅作参考资产。
> **12 个子模块原样保留**——来源是 `https://github.com/vibe-motion/skills`。

---

## 这个仓库里有什么

12 个 skill，全部是**视频/动画/视觉特效类**。作者是 vibe-motion（GitHub 组织），作品偏 **Remotion 视频渲染 + Three.js + SVG/Canvas**。

**两种性质分类**（按学习价值，已读全部 SKILL.md 后判断）：

### 🏆 方法论 / 重型工具（学价值高）

| # | 模块 | 类型 | 学到什么 | 备注 |
|---|---|---|---|---|
| 1 | `disney-animation-rule-skill/` | 📖 方法论 | 12 原则 + 工程化规则（deterministic frame evaluation、phase blocking、tuning by perception） | 写一切动画代码的指导 |
| 2 | `pixel2motion/` | 🧠 重型工具链 | logo 矢量化 + 动画 choreograph + motion QA（probe / ink-delta sweep / final-frame contract） | Playwright + headless Chrome 全套 |
| 3 | `svg-assembly-animator/` | 🎬 SVG→HTML 动画 | 反向逻辑（零件先打散再组装）+ GSAP elastic.out/back.out + 帧序列导出 | GSAP/JSZip/Canvas via CDN |

### 🥈 可复用代码片段（30-115 行，吃透模式）

| # | 模块 | 核心模式 | 行数 |
|---|---|---|---|
| 4 | `remotion-3d-ticker/assets/VerticalTicker.tsx` | **无限循环滚动**：`items + items` 复制 + `0%→-50%` + 透视 + 渐变遮罩 | 92 |
| 5 | `remotion-vinyl-player/assets/VinylPlayer.tsx` | 无限旋转 + 无缝 marquee + 进度条映射 | 115 |

### 🥉 完整渲染器（已验证可跑）

| # | 模块 | 用途 | 实测 |
|---|---|---|---|
| 6 | `light-spotlight-render/` | Python 模板替换，输出聚光灯扫字 HTML 动画 | ✅ 已验证（见下） |
| 7 | `claude-typer/` | 远程 Remotion 服务 `laosunwendao.com` 渲染打字机动画 | 🟡 远程依赖 |
| 8 | `procedural-fish-render/` | clone + pnpm + Remotion 渲染程序鱼 | 🟡 需外部 repo |
| 9 | `ruler-progress-render/` | clone + npm + Remotion 渲染尺子进度 | 🟡 需外部 repo |
| 10 | `threejs-earth-render/` | clone + Puppeteer + ffmpeg 渲染地球航线 GIF/MP4 | 🟡 需外部 repo |
| 11 | `wechat-2d-render/` | clone + pnpm + Remotion 渲染微信聊天动画 | 🟡 需外部 repo |
| 12 | `remotion-3d-ticker/`（整体） | 上面 #4 的完整打包（含 .gif 演示 26MB） | 🟡 demo 资产 |

---

## 已做的验证（不是空口断言）

**`light-spotlight-render/`** —— 完整跑通：

```bash
cd /Users/sample/Poyi/Loom/skills/animation/vibe-motion-arsenal/light-spotlight-render
python scripts/render_light_spotlight.py --label-text "test-spotlight" --output test.html
```

→ 生成 3.4KB 单文件 HTML 动画，浏览器打开能看到聚光灯扫字效果。验证日期 2026-06-19。

**其余 11 个未跑**——它们的 SKILL.md 都硬编码 `/usr/local/bin/python3`、查 `~/.agents/skills/`/`~/.claude/skills/`/`~/.codex/skills/`（macOS/Linux 路径），跟 Windows + Agent 环境不直接兼容。要用需改路径。

---

## 转化路径（待做，不要现在就动）

按你 `Skills/INDEX.md` 的设计哲学，未来转化的方向：

### 候选 1：方法论提炼 → 笔记
- 读 `disney-animation-rule-skill/references/` 全部 3 个 md
- 提炼出"代码驱动动画 · 检查清单" → `/Users/sample/Poyi/Vault/工程 Engineer/` 或 `Context/` 下

### 候选 2：模式代码片段 → 笔记 + 自有资产
- `remotion-3d-ticker/assets/VerticalTicker.tsx` 92 行无限滚动模式 → 自己写一份独立的「HTML/CSS 无限滚动 demo」
- `remotion-vinyl-player/assets/VinylPlayer.tsx` 旋转 + marquee + 进度条模式 → 同上

### 候选 3：可执行工具 → 注册成新 skill
- `light-spotlight-render/` 验证过的 HTML 动画生成器 → 转成 Agent 库可执行 skill
  （注意命名硬约束：≤ 1 词，禁下划线）

### 候选 4：暂不转化
- 8 个 Remotion 类一次性渲染器（clone + install 几百 MB）——不是日常工具，**学一次模式就够**，不必变 skill

---

## 维护规则

- **本文件夹是只读快照**——修改原作者文件前先在 `Context/` 下复制一份工作副本
- 修改原作者文件 → 记录 `modified_files.md`，便于对照 diff
- 真正消化后 → 移动到 `Context/` 或提炼到 `Knowledge/工程 Engineer/`，本目录保留作历史

---

## 文件清单（30MB 总）

| 路径 | 大小 | 关键文件 |
|---|---|---|
| `vibe-motion-arsenal/` | 30M | — |
| ├─ `README.md` + `README.en.md` | — | 作者原仓库介绍 |
| ├─ `disney-animation-rule-skill/` | 24K | SKILL.md + 3 个 references |
| ├─ `light-spotlight-render/` | 161K | SKILL.md + scripts/render_light_spotlight.py + assets/template |
| ├─ `svg-assembly-animator/` | 16K | SKILL.md + assets/animation_template.html + 1 reference |
| ├─ `pixel2motion/` | 348K | SKILL.md + 4 个 scripts + 3 个 references |
| ├─ `remotion-3d-ticker/` | 26M | SKILL.md + 1 tsx + 26MB demo.gif |
| ├─ `remotion-vinyl-player/` | 1.2M | SKILL.md + 1 tsx + demo gif |
| ├─ `claude-typer/` | 21K | SKILL.md + 1 py + agents/openai.yaml |
| ├─ `procedural-fish-render/` | 12K | SKILL.md + 1 py |
| ├─ `ruler-progress-render/` | 8K | SKILL.md + 1 sh |
| ├─ `threejs-earth-render/` | 2M | SKILL.md + 2 script + earth.gif |
| └─ `wechat-2d-render/` | 532K | SKILL.md + 1 sh + demo gif |

---

## 更新日志

### 2026-06-19 (v0.1.0) — 初版入库

- 从 `https://github.com/vibe-motion/skills` 拉取最新 main 分支（commit `2026-06-19T11:51:04Z`）
- 12 个子模块全部原样复制到 `vibe-motion-arsenal/`
- 完成轻量分类索引 + 转化路线规划
- 验证 1 个：`light-spotlight-render/` 实测跑通
- 不修改任何原作者文件