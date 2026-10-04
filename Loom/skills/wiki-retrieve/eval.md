## Should trigger
- query 确定性路径不够时，要跑语义检索召回相关页面
- 用户想用 BM25 稀疏检索加稠密重排找段落
- 用户要从 wiki 召回最相关段落做兜底
- 用户要混合检索（稀疏+稠密）找知识

## Should not trigger
- 用户要直接查询 wiki 概念（用 query）
- 用户要可视化知识图谱（用 canvas）
- 用户要整理笔记（用 notes）
- 用户要归档对话（用 ingest）
