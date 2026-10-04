## Should trigger
- 用户要跑一次 wiki 健康检查，找孤立页和死链
- 每周定时执行 wiki lint，输出 lint-report
- 用户发现 wiki 有命名违规，想做 10 项检查
- 想在自动修复前先看 frontmatter 缺口报告

## Should not trigger
- 用户要把新文件吞入 wiki（用 ingest）
- 用户想新建项目目录（用 project）
- 用户要查询某个 wiki 页面（用 query）
- 用户要可视化知识图谱（用 canvas）
