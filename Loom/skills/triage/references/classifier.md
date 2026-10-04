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
