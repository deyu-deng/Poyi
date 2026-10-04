写"清理类" skill 时，**不要假设 Agent 会自动 deep scan**。必须在 SKILL.md 里**明确写出**：
- 最小扫描深度（≥3）
- 必须用 `du -sh` 而非 `find -type f | wc -l`
- 必须用 `ls -la` 检查 dotfiles
- mv 前必须检查 `dst` 是否存在

## 8. Python `Path.iterdir()` 与 shell `ls` 不一致（Windows + MSYS 缓存陷阱）

**症状**（2026-06-15 Inbox 扁平化时踩到）：

```python
# Python 看到子目录存在
>>> list(Path(r"D:\Inbox\Received").iterdir())
[PosixPath('D:/Inbox/Received/2026_06_06_B4U7_session 1'), ...]
>>> list(Path(r"D:\Inbox\Received\2026_06_06_B4U7_session 1").iterdir())
[]   # ← 0 个文件！实际有 30+ 个

# 但 shell `ls -la` 看到
$ ls -la D:/Inbox/Received/2026_06_06_B4U7_session 1/
-rw-r--r--  ...  25-26年春夏大英V教学计划.doc
-rw-r--r--  ...  B4U1_sessions 1-2.pptx
... (30+ 文件)
```

**原因**：刚做完大批量 `mv` 操作，**Python `Path.iterdir()` 用的是 Windows 的目录快照缓存**，shell `ls` 直接走 syscall。两者不一致时**永远以 `ls -la` 为准**。

**修正做法**：

```python
# 方案 A：用 subprocess 调 ls
import subprocess
result = subprocess.run(["ls", "-la", str(p)], capture_output=True, text=True)

# 方案 B：用 os.scandir（比 Path.iterdir 更底层，但也有缓存问题）
import os
list(os.scandir(str(p)))

# 方案 C：彻底重置（最可靠）
import ctypes
ctypes.windll.kernel32.SetCurrentDirectoryW(str(p))  # 触发 Windows 重新读
# 然后再 Path.iterdir()

# 方案 D（最简单）：用 subprocess 跑 ls 而不是 Python
import subprocess
result = subprocess.run(["ls", str(p)], capture_output=True, text=True)
files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
```

**经验法则**：
- **大批量 mv/rm 操作后**，**用 `ls -la` 验证而不是 Python**
- 如果 Python 和 shell 不一致 → **相信 shell**，重新用 Python 重试前加个 sleep 或换 API
- 写 skill 时不要假设 Python 路径操作能替代 `ls`

## 9. `find ... | while read` 在 bash 子 shell 里跑（变量不传出）

**症状**（2026-06-15 Inbox 扁平化时踩到）：

```bash
# 在脚本里写
count=0
find Received/ -type f | while read f; do
  mv "$f" "/d/Inbox/$(basename $f)"
  count=$((count + 1))   # ← 改的是 while 子 shell 的 count，不是外层
done
echo "$count"   # ← 永远是 0！
```

**原因**：`while` 后的管道 (`|`) 是在**子 shell** 里跑的，子 shell 的变量修改**不会传回父 shell**。

**修正做法**：

```bash
# 方案 A：用 process substitution（bash 特性）
count=0
while read f; do
  mv "$f" "/d/Inbox/$(basename $f)"
  count=$((count + 1))
done < <(find Received/ -type f)
echo "$count"   # ← 正确！

# 方案 B：用最后一行 wc -l 统计
find Received/ -type f | wc -l

# 方案 C（最稳）：完全用 Python，不依赖 bash 变量
python -c "
from pathlib import Path
src = Path('Received')
files = [f for f in src.rglob('*') if f.is_file()]
for f in files:
    f.rename(Path('/d/Inbox') / f.name)
print(f'Moved {len(files)} files')
"
```

**经验法则**：
- 在 bash 里需要迭代 + 计数时，**用 process substitution 或 Python**
- `|` 之后是子 shell，变量传递要靠临时文件或 process substitution
- 写 skill 时的 cleanup 脚本，**优先用 Python 而非复杂 bash**