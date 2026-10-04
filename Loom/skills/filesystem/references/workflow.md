# Filesystem Skill — 文件操作工作流

> **本文是 filesystem §0 陷阱 0.7 的详细操作手册。**
> **任何文件操作任务（删除/重命名/移动/新建）都必须按这个流程走。**

---

## 为什么需要这个工作流

用户 2026-06-13 反复强调：

- "你可以现在问问我每个文件夹里面都是什么"
- "我觉得应该再问，再看，最后才动"
- "我觉得你应该扫描一下整个目录结构"

背景：用户电脑经过多年混乱整理，很多目录：
- **含义变了**（如 `D:/Software` 已装软件 vs `Cloud/Software` 破解版）
- **状态模糊**（如 `D:/Development/Home` dotfiles 是"烂尾了"还是"在用"？）
- **历史残留**（如 `D:/Cloud/Projects/Sandbox/Code/Hackathon/health-agent/.next` 是真的项目还是过期构建产物？）

**盲目行动 = 误删/误改**。

---

## 5 步标准流程

### 步骤 1: SCAN（强制）

**第一步必须是扫描，不是问问题**。扫描深度 ≥ 3 层。

```bash
# 错误：直接问用户
Agent: "你想怎么整理 D:/Cloud/Projects/Sandbox/Code/Hackathon？"
User: "...不知道。"

# 正确：先扫，看到什么再问
$ find D:/Cloud/Projects/Sandbox/Code/Hackathon -maxdepth 3 -type d
$ du -sh D:/Cloud/Projects/Sandbox/Code/Hackathon/
$ ls -la D:/Cloud/Projects/Sandbox/Code/Hackathon/
Agent: "Hackathon/ 下有 health-agent/ 子项目，44,400 文件，其中 .next/ 占大头。
        你想删 .next/ 还是整个 health-agent/？"
```

**扫描清单**：
- `find -maxdepth 3 -type d` 看 3 层结构
- `du -sh` 看大小（**绝不只看文件数**）
- `ls -la` 看 dotfiles（隐藏文件）
- `find -name "*.tmp" -o -name "*.bak" -o -name "*.crdownload"` 找垃圾

---

### 步骤 2: ASK（必要才问）

扫描完了之后，**只问不知道的**。已经知道的不要重复问。

**问之前先想**：

```
Agent 内部 checklist：
□ 用户给的信息够用吗？
□ 扫描结果能推断吗？
□ 这个信息会影响下一步吗？

如果三个都"是" → 不要问，直接做。
否则 → 用"对 X 你想怎么？"或"X 是 A 还是 B？"的形式问。
```

**问的格式**：

| ❌ 差的问法 | ✅ 好的问法 |
|---|---|
| "你想怎么处理？" | "A 方案（删除）或 B 方案（迁移到 X）你选哪个？" |
| "我可以帮你整理吗？" | "扫到了 7 类垃圾，按危险程度排序，你想从哪个开始？" |
| "你确定吗？"（没有上下文）| "BaiduNetdisk 42 GB，里面有 SolidWorks 安装包。这是你说的『长期收藏』还是『还没整理』？" |
| "Sandbox/ 下有空目录，要删吗？" | "Sandbox/ 是你主动维护的素材池（filesystem §0 陷阱 0.8），**不主动清理**。你有空目录的需求我可以做。" |

---

### 步骤 3: PROPOSE（先给方案）

不要直接动手。**给至少 3 个候选方案**让用户选：

```
Agent: "命名我有 3 个候选：
        A: filesystem (处理整台电脑的文件结构) — 推荐
        B: host (本机语义)
        C: structure (结构，但太抽象)
        你选哪个？"
```

**为什么至少 3 个**：1 个不够选择空间，2 个像在做选择题，3 个能体现你真的想过。

**带语义解释**：每个候选要说**为什么这个名字**。

---

### 步骤 4: PREVIEW（dry-run 必做）

**任何 mv/rm/rmdir 之前，必须 dry-run 给用户看清单**：

```bash
echo "===== Dry-run（不会真动）====="
echo "[mkdir]   D:\\Cloud\\Library\\CAD"
echo "[move]    D:\\Cloud\\Software\\AutoCAD → D:\\Cloud\\Library\\CAD\\AutoCAD"
echo "[rename]  D:\\Cloud\\Software\\SW2026 → D:\\Cloud\\Library\\CAD\\Solidworks2026"
echo "[rmdir]   D:\\Cloud\\Software (空后)"
echo
echo "回复 OK/go/执行 我才真动。"
```

**禁止**：直接执行 `rm -rf` 或批量 `mv`，然后才告诉用户。

**反例**（要避免）：
```
❌ Agent: [悄悄 mv 50 个文件]
   Agent: "整理好了。"
   User: "...你动了什么？"
   User: "我没说要动 XXX！"

✅ Agent: [打印 dry-run 清单]
   User: "OK"
   Agent: [执行]
   Agent: "✅ 全部完成。"
```

#### 冲突检测（重命名场景必做）

重命名前**必须检测目标是否存在**：

```python
# ❌ 危险：直接 mv 会覆盖目标文件
mv "old.pdf.pdf" "old.pdf"  # 如果 old.pdf 已存在，会覆盖！

# ✅ 安全：先检测
import os
if os.path.exists("old.pdf"):
    print(f"⚠️  目标已存在：old.pdf")
    print(f"    选项 A：删除 .pdf.pdf 副本（保留 .pdf 正本）")
    print(f"    选项 B：手动对比两个文件哪个更新更完整")
else:
    print(f"✅ 安全重命名：.pdf.pdf → .pdf")
```

**用户原话**："第 1 个 `.pdf.pdf` 有冲突 FROM: ... TO: ... ← 这个文件已经存在！"

→ 必须**先报告冲突**，让用户选 A1/A2/A3 之一。

#### 扫描结果分类

把扫描结果按"处理方式"分组：

| 类别 | 处理方式 | 示例 |
|---|---|---|
| **A. 重复副本** | 删除（保留正本） | `.pdf.pdf` 与 `.pdf` 同时存在 |
| **B. 下载失败残留** | 直接删除 | `.crdownload` |
| **C. Office 临时锁** | 直接删除 | `~WRL2087.tmp` |
| **D. 旧版本备份** | 询问用户（保留或删） | `.bak` `.tmp` 文件 |
| **E. 待分类** | **不动**，让用户决定 | 空目录、过时文件等 |

**关键原则**：
- **E 类（待分类）绝不在本次清理中动** — 用户没明确说要动
- D 类必须列出每个文件 + 创建时间，让用户判断

---

### 步骤 5: WAIT + EXECUTE + VERIFY

#### 5a: WAIT（等确认）

**明确等待用户回复 "执行" / "OK" / "go" 才动**。

如果用户给了多个选项（如 A1 / A2 / A3）— 必须按选项分支处理，**不能擅自选一个**。

如果用户沉默 >1 分钟没回，**重新询问**而不是自动执行。

**用户回应处理**：

| 用户回应 | 含义 | Agent 动作 |
|---|---|---|
| "OK" / "执行" / "go" | 同意 | 立刻执行 |
| "等一下" | 想再看看 | 暂停，等明确指令 |
| "你看呢" / "你觉得呢" | 让我决定 | 主动给推荐方案（不是 dry-run） |
| "算了" / "不做" | 取消 | 不动，记录到 memory（如果用户重复取消类似操作） |
| "以后再说" / "以后我自己处理" | 不再追问 | 标记完成，下次不问 |

**特别注意**：**"以后我自己处理" 必须立即停止**，写入 memory 和 skill（filesystem §0 陷阱 0.10），**下次遇到同样话题不要主动提**。

#### 5b: EXECUTE（执行）

按 preview 清单逐项执行：

```bash
# 1a: 删除 .pdf.pdf 副本
rm "Research/01-SRTP/Lit/Patents/xxx.pdf.pdf"

# 1b: 重命名 .pdf.pdf → .pdf
mv "Research/01-SRTP/Lit/Patents/yyy.pdf.pdf" \
   "Research/01-SRTP/Lit/Patents/yyy.pdf"

# 2: 删除 .crdownload
rm "Courses/.../01-12.mp4.crdownload"
rm "Courses/.../01-14.mp4.crdownload"
rm "Courses/.../01-18.mp4.crdownload"

# 3: 删除 .tmp
rm "Courses/.../Homework/~WRL2087.tmp"
```

**每步 echo 进度**，让用户能跟踪：

```
✅ 步骤 1a 完成：删除 xxx.pdf.pdf (4.9 MB)
✅ 步骤 1b 完成：重命名 yyy.pdf.pdf → yyy.pdf
✅ 步骤 2 完成：删除 3 个 .crdownload (4.1 GB)
✅ 步骤 3 完成：删除 ~WRL2087.tmp (21 KB)
```

#### 5c: VERIFY（验证扫描）

执行完**必须再扫一次**，确认没漏：

```python
# 重新跑 Step 1 的扫描
# 应该返回 0 个结果（除非有未处理的类别）
```

输出：

```
✅ 验证扫描结果
  .pdf.pdf        ✅ 无残留
  .crdownload     ✅ 无残留
  ~*.tmp          ✅ 无残留
  .bak            ⚠️ 还有 1 个（用户保留）
```

---

## 实战模板（每次任务按这个格式）

```markdown
## [阶段 1: SCAN]
- 扫描: `find D:/Target -maxdepth 3 -type d`
- 大小: `du -sh D:/Target/*`
- 关键发现:
  - /A/ 子目录 50 个文件，200 MB
  - /B/ 有 .crdownload 42 GB（重要！）

## [阶段 2: ASK]
- 问: B 的 42 GB 是...？
- 答: "我自己处理"

## [阶段 3: PROPOSE]
- 方案 A: ...
- 方案 B: ...
- 推荐: A

## [阶段 4: PREVIEW]
- [mkdir] /A/
- [move] /B/x → /A/x
- [rm] /B/y

## [阶段 5: WAIT]
- 用户: OK
- 执行: [全部完成]
```

---

## 用户已知的"主动维护"目录

以下目录**绝不**进入清理清单（参考 SKILL.md §0 陷阱 0.8）：

| 目录 | 跳过原因 |
|---|---|
| `D:\Cloud\Projects\Sandbox\*` | 用户素材池，含空占位 |
| `D:\Cloud\Archive\Password\*` | 用户自管的密码文件（待迁移 Bitwarden 但时机由用户决定） |
| `D:\Cloud\Media\Music\Song\*` | 400 个艺术家目录，个人音乐库 |
| `D:\Cloud\Games\*` | 个人游戏目录 |
| `D:\Cloud\Archive\*` 的大部分 | 用户没明确说要动 |

**反例**：

```
❌ 扫描 D:\Cloud 全树后建议删除 Sandbox/Code/Hackathon/ 下 v1/v2/v3 文件
   → 用户立刻说："你不要管了。我就是喜欢这样"
```

---

## 大小判断（什么时候值得清理）

| 单文件大小 | 建议 |
|---|---|
| < 1 MB | 低优先级（除非是大量累积） |
| 1-100 MB | 中优先级（preview + 等确认） |
| > 100 MB | 高优先级（必须 preview + 详细说明） |
| > 1 GB | **必须先确认文件性质**（视频？数据集？真实下载？） |

**陷阱**：`.crdownload` 文件常常看起来大但实际是"下载到一半的失败"。要明确说明：

```
"3 个 .crdownload 总计 4.1 GB，但这些都是 2025 年（去年）的微积分录像课未完成下载，建议直接删除"
```

不要让用户以为 4.1 GB 是有价值的数据。

---

## 反模式速查

| ❌ 反模式 | ✅ 正确 |
|---|---|
| 直接 `rm -rf` | 先 dry-run |
| "我帮你删了 X" | "我建议删 X，请确认" |
| 自动判断"应该删" | 用户没说就不动 |
| 把空目录列进"建议清理" | 空目录可能是用户的占位 |
| 跳过 preview 因为"看起来很安全" | **永远 preview** |
| "我重命名了 11 个文件，你看下效果" | preview 时**先检测目标冲突**，再让用户选 |

---

## 完成报告模板

清理完成后，输出：

```
✅ 清理完成（{YYYY-MM-DD}）

执行：
- 🗑️ 删除 N 个 .pdf.pdf 副本（M MB）
- 📝 重命名 N 个文件（M MB）
- 🗑️ 删除 N 个 .crdownload（M GB）
- 🗑️ 删除 N 个 .tmp（M KB）

跳过（按用户决定保留）：
- ⏭️ Drawing2.bak（用户决定保留）

释放空间：X.X GB
验证扫描：0 个残留（除保留项）

后续建议：
- 还有 6 个 .bak 文件未处理，需要时再清理
- Sandbox/ 下仍有空目录，建议保留
```

---

## 不要做的事

- ❌ 跳过 SCAN 直接问"你想怎么整理"
- ❌ PROPOSE 时只给 1 个方案（这不是提议，是通知）
- ❌ PREVIEW 时只给"我会创建 X 目录"（不说清楚删什么、改什么、移到哪）
- ❌ 用户没回复就执行
- ❌ 用户说"等一下"还继续动
- ❌ 用户说"以后再说"还重复问

---

## 写 Skill 时的元教训

任何 cleanup 类 skill 必须在 SKILL.md 里**明确写出**这 5 步流程，并在 reference 文件里给出**具体命令模板**。

不要假设 Agent 会自动遵循 —— 必须有：

```markdown
## 工作流（强制）

### 步骤 1: 扫描
```bash
# 至少 3 层
find D:/Target -maxdepth 3 -type d
du -sh D:/Target/*
ls -la D:/Target/
```

### 步骤 2: 询问
- 只问扫描后**还不知道**的信息
- 给 3 个候选方案 + 推荐

### 步骤 3: Dry-run
- 打印每个 mv/rm 的具体目标
- 告诉用户"回复 OK 才动"

### 步骤 4: 执行
- 用户说 OK 后**一次性执行**
- 不分批

### 步骤 5: 验证
- 再跑一次 find/du -sh
- 对比前后差异
```

---

## 元信息

- **合并时间**：2026-06-15
- **来源**：
  - `cleaning-checklist.md`（清理细节、冲突检测、用户已知目录、大小判断）
  - `scan-then-ask-workflow.md`（5 步通用流程）
- **保留独立**：技术踩坑见 `scan-rules.md`；具体命令配方见 `cleanup-recipes.md`

---

*（本文档沉淀自 2026-06-13 长会话的 3 次清理操作（.pdf.pdf/.crdownload/.tmp）+ 2026-06-15 多次 C 盘清理的实战经验。）*