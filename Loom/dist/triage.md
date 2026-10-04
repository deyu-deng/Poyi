<!-- source: triage -->
---
name: triage
description: "通用文件分拣引擎：将任意目录的散落文件按 filesystem 决策树与 profile 上下文自动归类到目标路径。当用户要求整理 Inbox / Downloads、分拣或归类文件，或提供目录路径时触发。 触发词：整理文件、分拣、归类、清理目录、triage。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": ["filesystem", "profile"]}
---
# Triage — 通用文件分拣引擎

> 把任何目录里的散落文件按 filesystem 规则自动归类。零硬编码，全由 filesystem 决策树驱动。

---

## 触发词

「整理 Inbox」「整理 Downloads」「分拣」「归类文件」「triage」+ 目录路径

---

## 前置依赖

执行前必须先加载：
1. `filesystem` —— 决策树 + 路径规范 + 平台结构
2. `profile` —— 了解用户项目列表、课程列表，用于内容匹配

---

## 操作流程

### Step 1: 确定扫描目标

- 用户指定了目录 → 用指定目录
- 用户只说"整理"没有路径 → 默认 `D:/Inbox/`
- 上下文中有明确目录引用 → 用上下文目录

> 扫描 **`D:/Inbox`** 时，额外参考 [`references/inbox-rules.md (见附录 references/inbox-rules.md)`](references/inbox-rules.md (见附录 references/inbox-rules.md)) 的用户专属路由映射（真实课程目录、破解软件/安装包处理红线、命名规范）。该文件是 inbox-cleanup 合并进来的域知识。

### Step 2: 扫描目录

列出目标目录下所有文件（递归一层），记录：文件名、扩展名、大小、修改时间。

### Step 3: 逐文件分类

对每个文件：

1. **扩展名匹配** → 查 `references/classifier.md (见附录 references/classifier.md)` 得出文件类型
2. **filesystem 路由** → 按文件类型查 filesystem §3.1 决策树，结合 profile 中的项目/课程列表，给出建议目标路径
3. **内容兜底** → 文件名无法判断时（纯数字、哈希名），调 analyze_image / read_text 读内容，根据实际内容重新分类
4. **匹配失败** → 标记为"需人工判断"

### Step 4: 重命名检查

对每个已分类的文件，判断是否需要重命名：

**触发重命名的条件：**
- 纯数字文件名（如 `1783386342471009248.docx`）→ 微信导出，读内容取标题
- 哈希/随机字符串名（如 `49noawxwusp42cq...jpg`）→ 网盘下载，读内容取语义名
- 文件名含下划线 `_`（如 `C124720_单片机_MCU_规格书.pdf`）→ 违反 filesystem §2 命名规范，下划线改连字符
- 文件名含中文与英文混杂无分隔 → 加连字符
- 文件名无意义（如 `5tmw2rq4vjklqkey...`）→ 读内容后重命名

**重命名规则（严格遵循 filesystem §2）：**
- 一个词最佳，最多两个词
- 连字符 `-` 分隔，禁用下划线
- 禁用中英混杂
- 保留扩展名不变
- 可保留版本号、芯片型号等关键标识

**重命名来源优先级：**
1. 读取文件内容，取标题/主题等自然语义 → 翻译为 kebab-case 英文
2. 无法读内容时，从文件名中提取关键词重组
3. 完全无法判断 → 保持原名，标记 `[待重命名]`

### Step 5: 汇总确认

将所有文件按"目标目录"分组展示，包含重命名信息：

```
### 将移动到 D:/Cloud/Projects/Nuclide/Docs/Datasheets/
- stm32l496-datasheet.pdf ← C124720_单片机_MCU_STM32L496RGT6_规格书.pdf (3.3 MB)
- rt9080-datasheet.pdf ← C841192_线性稳压器_RT9080_规格书.pdf (258 KB)

### 将移动到 D:/Cloud/Courses/...
- mech-drawing-cad-answer.pdf ← 17-18夏_机械制图及CAD（答案1）.pdf (248 KB)

### 需确认后删除（安装包已安装？）
- CursorUserSetup-x64-3.9.16.exe (188 MB) [保留原名]

### 需人工判断
- [待重命名] 1783386342471009248.docx (17 KB) — 需读内容
```

用户确认后执行。

### Step 6: 执行 + 汇报

- 先重命名，再移动（`Rename-Item` → `Move-Item`）
- 重命名冲突：目标目录已有同名文件时加数字后缀
- 安装包类：提醒安装后删除，不主动删
- 最终汇报每个文件的"原名 → 新名 → 去向"，输出卡片

---

## 约束

- **禁止硬编码路径**：所有目标路径必须从 filesystem 决策树 + profile 推导，不能写死在 triage 里
- **先确认再移动**：移动操作属于中风险，必须汇总清单给用户确认
- **绝不删除用户文件**：不确定的文件宁可留在原地标"需人工判断"也不乱动
- **同名冲突**：目标目录已有同名文件时，自动加 `_副本` 后缀或询问用户
- **空目录清理**：移动完成后若源目录为空，询问是否删除空目录

---

## 文件结构

```
triage/
├── SKILL.md               ← 本文件
└── references/
    └── classifier.md      ← 扩展名 → 文件类型映射表
```

---

## changelog

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-07-27 | 1.1.0 | 新增 Step 4 重命名检查：自动识别需重命名文件，按 filesystem §2 规范生成新名 |
| 2026-07-27 | 1.0.0 | 初始创建 |


---
## 附录: references/inbox-rules.md

# D:/Inbox 专用路由域知识

> 来源：原 `inbox-cleanup` skill（已合并进 triage）。这是用户 **D:/Inbox** 专用的真实目录映射与规则，作为 triage 在扫描 D:/Inbox 时的补充路由参考。
> 注意：以下路径是真实目录，**课程/工具目录变化时需同步更新本文件**。`triage` 主流程仍以 filesystem 决策树为准，本文件仅补全 Inbox 特有的硬编码映射与红线（如破解软件处理）。

## 核心流程

```
扫描 D:/Inbox → 按决策树预分类 → 读不确定文件的内容 → 列出方案 → 用户拍板 → 派发 file-agent 执行
```

---

## 目录路由决策树

对 D:/Inbox 下每个文件/子目录，依次走以下分支：

```
1. 破解版大型软件安装包？
   → 删除（移至回收站）。特征：SolidWorks/DaVinci/CAD/Adobe 等带 Crack/破解/Premium/Studio 字眼的 zip/exe/rar
   例外：kugou 等用户明确要求保留的 → D:/Cloud/Library/

2. 免费软件安装包？
   → 删除。特征：blender/node/conda/python/Trae/VSCode 等官方免费安装包，已安装即无用

3. 课程相关文件（课件 PPT、作业 DOCX、试卷 PDF、教材 PDF、乐谱）？
   → 核对 Courses 目录，映射到对应课程子目录：
   - D:/Cloud/Courses/2026春夏-大学英语V/  → Slides/ Notes/ Syllabus/ Handouts/ Readings/
   - D:/Cloud/Courses/2026春夏-大学物理(甲)I/  → Slides/ Exams/ Textbook/
   - D:/Cloud/Courses/2026春夏-萨克斯/  → Music/
   - D:/Cloud/Courses/2026夏-机械制图与CAD/  → Slides/ Homework/ Textbook/
   - D:/Cloud/Courses/2025秋冬-工程图学/  → Slides/ Homework/
   无法确定对应课程？→ 读文件内容判断

4. 已有课程目录中存在的重复文件？
   → 删除 Inbox 中的副本

5. 科研论文 PDF？
   → D:/Cloud/Research/

6. APK 文件？
   → 删除

7. 便携工具/脚本（zip/js/ps1/xpi/bat/exe 小工具）？
   → 按子类归入 D:/Tools/：
   - 系统工具 → D:/Tools/System/
   - 网络工具 → D:/Tools/Network/
   - 用户脚本 → D:/Tools/Scripts/
   - Zotero 插件(xpi) → D:/Tools/
   - Dev 工具 → D:/Tools/Dev/
   如果目标目录已有同名内容，zip 等安装包直接删除

8. 组织/行政文档（评议表、申请表等）？
   → D:/Cloud/Archive/Organizations/

9. 无法自动判定的文件？
   → 读取内容（文本→read_text，PDF→file-agent read_file，图片→analyze_image），列出判断建议供用户拍板
   原则：
   - .md 文件 → Vault 里是否合适？
   - 书籍 PDF → 课程读物还是个人收藏？
   - 证书/签名文件 → 开发用还是误下载？
```

---

## 目标目录结构速查

### D:/Cloud/Courses/（所有课程文件）

| 课程目录 | 子目录 |
|---------|--------|
| 2026春夏-大学英语V | Slides/ Notes/ Syllabus/ Handouts/ Readings/ |
| 2026春夏-大学物理(甲)I | Slides/ Exams/ Textbook/ |
| 2026春夏-萨克斯 | Music/ |
| 2026夏-机械制图与CAD | Slides/ Homework/ Textbook/ |
| 2025秋冬-工程图学 | Slides/ Homework/ |
| 2025秋冬-微积分(甲)I | （按实际结构） |
| 2025秋冬-C程序设计基础 | （按实际结构） |
| 2026春夏-人工智能基础A | （按实际结构） |
| 2026春-常微分方程 | （按实际结构） |
| ... | ... |

### D:/Tools/

| 子目录 | 典型内容 |
|--------|---------|
| System/ | WizTree, Geek 等系统工具 |
| Network/ | Clash, v2rayN, xzzd, Motrix 等 |
| Scripts/ | Beiyu-live-better, campus-learning-assistant, 用户脚本 |
| Dev/ | 开发工具 |
| Media/ | 媒体处理工具 |

### D:/Cloud/Library/（破解版长期收藏）
- 仅保留用户明确指定的低版本软件（如 kugou）

### D:/Cloud/Research/
- 01-SRTP/ 02-AI数学验证/

---

## 命名规范

1. **空格优先，不用下划线**：`B4U1 Session 1-2.pptx` 而非 `B4U1_Session_1-2.pptx`
2. **去掉冗余后缀**：`科普文章作业.docx` 而非 `3250105066_林小满_科普文章作业(1).docx`
3. **英文 Title Case**：`Graphic medicine.pptx` → `Graphic Medicine.pptx`（Slides/Handouts 类文件）
4. **中文保持原意**：`教学计划.doc`、`期中作文反馈.docx`
5. **乐谱/教材保持原名**：不动
6. **已有课程目录中的文件保留现有命名风格**：不强行统一（如大学物理的 `01-01 质点运动学.pdf` 格式不变）

---

## 执行要点

1. **先加载 filesystem**：确保目录路径和红线约束正确
2. **扫描要全**：`Get-ChildItem "D:/Inbox" -Recurse -Depth 1` 确保不漏子目录
3. **判断题要自己读内容**：不要拿文件名猜测，PDF/图片/docx 不能直接 read_text 的，派 file-agent 或用 analyze_image
4. **归类不确定的先列清单给用户拍板**：不要自作主张删用户的文件
5. **目标已有 → 跳过不覆盖**：Inbox 中的重复文件删除即可
6. **确认后派发 file-agent**：一次性把所有移动/删除/重命名操作打包，减少往返
7. **删除走回收站**：不使用永久删除
8. **最后检查**：确认 Inbox 只剩用户要求保留的文件


---
## 附录: references/classifier.md

# Classifier — 文件类型映射表

> 扩展名 → 文件类型 → filesystem §3.1 决策树分支

## 文档类

| 扩展名 | 类型 | 决策树分支 |
|---|---|---|
| `.pdf` | 文档 | → 按文件名/内容进一步判断：含论文标题/DOI → Research；含课程名 → Courses；含芯片型号/规格书 → Projects/{项目}/Docs |
| `.docx` / `.doc` | Office 文档 | → 按内容判断课程/项目/科研/其他 |
| `.pptx` / `.ppt` | Office 文档 | → 同上 |
| `.xlsx` / `.xls` / `.csv` | Office 文档 | → 同上 |
| `.md` | Markdown | → Vault 或 Projects/{项目}/Docs |
| `.txt` | 文本 | → 同上 |

## 图片类

| 扩展名 | 类型 | 决策树分支 |
|---|---|---|
| `.jpg` / `.jpeg` / `.png` / `.gif` / `.webp` / `.bmp` / `.svg` | 图片 | → 文件名含 `IMG_`/`DCIM` → 手机照片，归 Media；含 `Screenshot`/`截图` → 课程/项目截图 |

## 音视频类

| 扩展名 | 类型 | 决策树分支 |
|---|---|---|
| `.mp4` / `.mov` / `.avi` / `.mkv` | 视频 | → Movies/ 或 Courses/{课}/Slides |
| `.mp3` / `.wav` / `.flac` / `.aac` | 音频 | → Music/ 或 Courses/{课}/Slides |

## 安装包类

| 扩展名 | 类型 | 决策树分支 |
|---|---|---|
| `.exe` / `.msi` | Windows 安装包 | → 已装软件保留安装包的 → Library；临时下载 → 确认安装后删除 |
| `.dmg` | macOS 安装包 | → Downloads 或 Library |
| `.zip` / `.rar` / `.7z` / `.tar.gz` | 压缩包 | → 临时 → 解压后删除；长期收藏 → Archive |

## 代码/配置类

| 扩展名 | 类型 | 决策树分支 |
|---|---|---|
| `.py` / `.js` / `.ts` / `.c` / `.cpp` / `.java` / `.go` | 代码 | → 属于哪个项目？→ Projects/{项目}/Code |
| `.json` / `.yaml` / `.toml` / `.ini` / `.cfg` | 配置 | → 项目配置 → Projects/{项目}；其他 → 询问用户 |
| `.ipynb` | Notebook | → Projects 或 Sandbox |

## 规格书/数据手册类

识别规则（不依赖扩展名）：
- 文件名含芯片型号模式（字母+数字，如 `STM32L496RGT6`、`RT9080`）
- 文件名含 `规格书` / `datasheet` / `数据手册` / `参考手册`

→ 判断归属项目 → Projects/{项目}/Docs/Datasheets/

## 无法自动分类

以下情况触发内容读取（analyze_image 或 read_text）：
- 纯数字文件名（如 `1783386342471009248.docx`）→ 读内容后按标题归类
- 无意义哈希文件名（如 `49noawxwusp42cq...`）→ 读内容后归类
- 无法匹配任何分类规则 → 询问用户

