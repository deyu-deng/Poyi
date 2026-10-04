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
