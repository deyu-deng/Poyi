---
name: wiki-retrieve
description: "Loom 混合语义检索引擎：当 query 的确定性路径（hot→index→pages）不够时，用 BM25 稀疏检索 + 可选上下文前缀 + 可选稠密重排三层管线，从 wiki 召回最相关页面与段落。query 优先，retrieve 兜底。 触发词：语义检索、检索wiki、retrieve、搜知识库。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": ["query"]}
---
# wiki-retrieve: Loom 混合语义检索引擎

你是 Loom 织机的模糊检索器。当 query 技能的确定性路径（hot → index → pages）无法满足需求时，你通过 BM25 稀疏检索 + 可选上下文前缀 + 可选稠密重排的三层管线，从 wiki 中召回最相关的页面和段落。

与 query 技能明确分工：query 走确定性路径（已知结构），retrieve 走模糊语义路径（未知关键词 / 跨领域检索）。query 优先，retrieve 兜底。

---

## 依赖声明

- **query** 技能：retrieve 是其兜底路径，共享答案归档协议
- **ingest** 技能：每次 ingest 后触发 BM25 增量更新
- **poyi** 技能：wiki 目录结构和 index 格式

---

## 命令入口

| 命令 | 行为 |
|------|------|
| `/retrieve <query>` | 对 Loom/wiki/ 下所有 .md 文件执行三层混合检索，返回 final top-5 + 页码引用 |
| `/retrieve build-index` | 手动触发全量 BM25 索引重建（一般由 setup_retrieve.py 或 ingest 后自动触发） |
| `/retrieve status` | 查看索引状态（索引文件大小、覆盖文件数、最后更新时间） |

---

## 三层检索管线

### Layer 1: 稀疏层（BM25 — 始终在线）

**原理**：TF-IDF 倒排索引，对 Loom/wiki/ 下全部 .md 文件（排除 `.retrieve-bm25/` 自身、排除 `meta/` 目录）建立 BM25 索引。

**索引位置**：`Loom/wiki/.retrieve-bm25/`
- `index.pkl` — 序列化的 BM25 模型 + 词汇表 + 文档 ID 映射
- `manifest.json` — 索引元信息（文件数、最后更新时间、文件 hash 清单）

**得分 top-20**：BM25 召回得分最高的 20 个文档。

**分词策略**：
- 中文：jieba 精确模式分词
- 英文/混合：空格分割 + 小写化 + 去停用词
- Wikilinks 特殊处理：`[[Page Name]]` 中的 Page Name 作为完整 token 保留

**优雅降级**：BM25 索引不可用时（首次未构建），警告用户执行 `/retrieve build-index` 或运行 `setup_retrieve.py`。

### Layer 2: 上下文前缀层（可选 — 需 egress 同意）

**触发条件**：用户显式要求更深检索，或 Layer 1 结果置信度不足。

**流程**：
1. 将 Layer 1 的 top-20 候选页面内容（截断至每页 500 tokens）
2. 发送给外部 embedding 服务（如 OpenAI text-embedding-3-small 或本地 ollama）
3. 对每个页面生成上下文前缀（contextual prefix）：一段 ≤100 token 的自然语言摘要，描述该页面在 wiki 全局上下文中的角色
4. 将上下文前缀拼接到页面内容前
5. 重新计算 query 与增强后页面的 BM25 得分
6. 重排后输出 top-10

**安全约束**：
- 发送前必须通过 `ask_user` 询问用户是否允许将页面内容发送到外部 API
- 明确告知发送的 token 数量和目标服务
- 不得发送 frontmatter 中标记 `confidence: low` 或 `status: deprecated` 的页面

**优雅降级**：用户拒绝 → 跳过 L2，直接使用 L1 的 top-10 进入 L3。

### Layer 3: 密集层（cosine rerank — 可选）

**原理**：使用本地 ollama 模型（默认 `nomic-embed-text` 或 `bge-m3`）对 L2 输出的 top-10 做语义相似度重排。

**流程**：
1. 对 query 和 top-10 候选页面内容分别生成 embedding
2. 计算 cosine 相似度
3. 按相似度降序排列
4. 输出 final top-5 + 页码引用（从页面内容的 `## Section` 标题推断）

**Token 预算**：

| 层级 | 输入 | 输出 | 累计 token |
|------|------|------|------------|
| L1 (BM25) | query 文本 | top-20 文档 ID | ~200 |
| L2 (contextual prefix) | top-20 × 500 tokens = ~10k | top-10 重排 | ~10,000 |
| L3 (cosine rerank) | top-10 × 全文 embeddings | final top-5 + 页码 | ~5,000 |

**优雅降级**：ollama 不可用 → 跳过 L3，直接输出 L2 的 top-10 作为最终结果。

---

## 与 query 技能的分工

| 维度 | query 技能 | retrieve 技能 |
|------|-----------|---------------|
| **路径** | 确定性：hot → index → pages | 模糊性：BM25 → prefix → cosine |
| **适用场景** | 已知关键词、结构化查找、"X 是什么" | 跨领域检索、未知术语、"和 Y 相关的所有内容" |
| **索引依赖** | 依赖 index.md 手工维护 | 依赖 BM25 自动索引 |
| **结果形式** | 综合答案 + 页面引用 | Top-K 文档 + 页码 + 片段 |
| **优先级** | 优先 | 兜底（query 无结果或用户显式 `/retrieve` 时调用） |

**路由规则**（在 poyi 编排器中实现）：
1. 用户问 "wiki 里有没有 X" → 先走 query
2. query 返回空或用户说"不够，再找找" → 自动切换到 retrieve
3. 用户显式 `/retrieve <query>` → 直接走 retrieve

---

## 索引更新协议

### 全量构建

```bash
python D:/Projects/Poyi/Loom/scripts/setup_retrieve.py --force
```

首次部署时运行，构建完整 BM25 索引。

### 增量更新（ingest 后自动触发）

每次 ingest 完成后，ingest 技能应触发增量更新：

```python
# 伪代码：ingest 最后一步
if new_pages_created:
    bm25_index.add_documents(new_page_paths)
    bm25_index.save("Loom/wiki/.retrieve-bm25/index.pkl")
    update_manifest(new_page_paths)
```

增量更新只处理新增/修改的页面，不解散重建全量索引。

---

## 输出格式

检索完成后输出：

```
## /retrieve "<query>"

**管线**: L1(BM25 top-20) → L2(contextual prefix top-10) → L3(cosine top-5)
**耗时**: 1.2s

### Top-5 结果

| # | 页面 | 相似度 | 关键段落（页码） |
|---|------|--------|------------------|
| 1 | [[量子纠缠]] | 0.94 | "量子纠缠是指..." （第 3 段） |
| 2 | [[EPR 悖论]] | 0.87 | "Einstein 提出..." （第 1 段） |
| 3 | [[贝尔不等式]] | 0.81 | "贝尔证明了..." （第 2 段） |
| 4 | [[量子信息]] | 0.76 | — |
| 5 | [[量子力学基础]] | 0.72 | — |

**建议**: 结果 1-3 高度相关，可直接阅读；结果 4-5 为领域背景页。
```

---

## 示例

### 用户：`/retrieve 量子纠缠的哲学含义`

```
管线已就绪。BM25 索引覆盖 47 个页面。

L1(BM25) → top-20 候选已召回
L2(contextual prefix) → 需要发送 ~8k tokens 到 OpenAI embedding API，是否允许？
```

（用户确认后）

```
L2 重排完成，top-10 进入 L3
L3(cosine via ollama/nomic-embed-text) → final top-5:

| # | 页面 | 相似度 |
|---|------|--------|
| 1 | [[量子纠缠]] | 0.94 |
| 2 | [[EPR 悖论]] | 0.87 |
| 3 | [[贝尔不等式]] | 0.81 |
| 4 | [[决定论与自由意志]] | 0.73 |
| 5 | [[哥本哈根诠释]] | 0.68 |
```

### 用户：`/retrieve build-index`

```
正在全量构建 BM25 索引...
扫描 Loom/wiki/ → 47 个 .md 文件
分词 → 建倒排索引 → 持久化
索引已保存至 Loom/wiki/.retrieve-bm25/index.pkl (47 文档, 1.2 MB)
清单已更新至 Loom/wiki/.retrieve-bm25/manifest.json
```

---

## 硬约束

- BM25 索引存储在 `Loom/wiki/.retrieve-bm25/`，不污染 wiki 内容目录
- L2 必须通过 `ask_user` 获取 egress 授权，不得假设同意
- 不得将 `frontmatter` 中 `confidence: low` 或 `status: deprecated` 的页面发送到外部 API
- 分词字典和停用词表不硬编码在 SKILL.md 中，通过脚本读取配置文件
- 检索结果不替代 query 技能的答案归档——retrieve 输出原样呈现，不自动合成答案

---

## 自举指令

首次加载本技能时：

1. 检查 `Loom/wiki/.retrieve-bm25/index.pkl` 是否存在
   - 不存在 → 提示用户运行 `python D:/Projects/Poyi/Loom/scripts/setup_retrieve.py --force` 构建索引
2. 检查 `Loom/wiki/.retrieve-bm25/manifest.json` 中的文件数是否与 wiki 实际 .md 文件数一致
   - 不一致 → 提示增量更新或全量重建
3. 测试 ollama 是否可用：`ollama list | findstr "nomic-embed-text/|bge-m3"`
   - 不可用 → 标记 L3 降级，后续检索仅走 L1 + 可选 L2
4. 输出当前检索管线状态（L1 就绪 / L2 需授权 / L3 降级）
