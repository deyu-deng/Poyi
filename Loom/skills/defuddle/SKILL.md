---
name: defuddle
description: "网页清洗器：剥除广告/导航/页脚/社交按钮，输出纯净 Markdown，节省 40-60% token。基于 kepano/defuddle-cli。触发词：defuddle、清洗网页、剥广告、clean url"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": ["ingest"]}
---
# defuddle: 网页清洗器

Defuddle 提取网页正文内容，丢弃广告、Cookie 横幅、导航栏、相关文章、页脚、社交分享按钮。输出为纯净 Markdown。

在 URL 摄入前使用。典型网页可节省 40-60% token，产出更干净的 wiki 页面。

---

## 安装

```bash
npm install -g defuddle-cli
```

验证：`defuddle --version`

---

## 用法

### 直接清洗 URL
```bash
defuddle https://example.com/article
```
输出纯净 Markdown 到 stdout。

### 保存到 raw/
```bash
defuddle https://example.com/article > /Users/sample/Poyi/Loom/raw/articles/article-slug-$(Get-Date -Format 'yyyy-MM-dd').md
```

### 加 frontmatter
先用 defuddle 清洗，再手动补 frontmatter：
```markdown
---
source_url: https://example.com/article
fetched: YYYY-MM-DD
---
[defuddle 输出内容]
```

---

## 何时使用

**使用 defuddle：**
- 摄入新闻文章、博客、文档页面
- 页面有大量周边内容
- 需要在长文章上控制 token 用量

**跳过 defuddle：**
- 源已是纯净 Markdown 或 PDF
- 页面是仪表盘、应用、结构化数据
- 文章够短，直接处理即可

---

## 回退

如果 defuddle 未安装：用 `web_fetch` 直接抓取，内容略脏但仍可用。

---

## 与 ingest 的集成

ingest 技能在处理 URL 时会自动检查 defuddle 是否可用。无需在 ingest 前手动运行 defuddle。
要手动清洗并保存后再 ingest：
1. 运行上述保存命令
2. 然后：`ingest /Users/sample/Poyi/Loom/raw/articles/[slug].md`
*（内容由AI生成，仅供参考）*
