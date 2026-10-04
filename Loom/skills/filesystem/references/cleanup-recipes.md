# Cleanup Recipes — 10 个可复用的清理/重命名/移动配方

> 本文是 filesystem §5.3 的实战 cookbook。每个 recipe 都按 `dry-run → 确认 → 执行` 流程写。

## Recipe 1：清理历史临时文件（.tmp / .crdownload / .bak）

**场景**：磁盘有大量过时文件占用空间。

```bash
# Dry-run: 列出可疑文件
find D:/Cloud -type f \( -name "*.tmp" -o -name "*.crdownload" -o -name "*.bak" -o -name "*~*.tmp" \)
find D:/Cloud -type f -name "*.pdf.pdf"  # 双后缀
find D:/Cloud -type f -empty             # 空文件
```

**典型发现**（2026-06-15 实测）：
- 3 个 `.crdownload` 占 **4.1 GB**（2025 年未完成的课程视频下载）
- 2 个 `.pdf.pdf`（双后缀）
- 1 个 `~WRL2087.tmp`（Word 异常关闭）

**执行**：
```bash
# ⚠️ 必须先 dry-run 给用户看清单
# ⚠️ .crdownload 可能是大文件，要用 du -sh 看
# ⚠️ 询问用户保留/删除每个 .bak

# 示例：删除 .crdownload + .tmp + .pdf.pdf 副本
find D:/Cloud -name "*.crdownload" -delete
find D:/Cloud -name "~*.tmp" -delete
find D:/Cloud -name "*.pdf.pdf" -exec bash -c '
  f="$1"
  new="${f%.pdf}"
  if [ ! -f "$new" ]; then mv "$f" "$new"; fi
' _ {} \;
```

## Recipe 2：修复 .pdf.pdf 双后缀（带冲突检查）

```bash
find D:/Cloud -name "*.pdf.pdf" | while read f; do
  new="${f%.pdf}"
  if [ -f "$new" ]; then
    # 目标 .pdf 已存在 → 这是下载副本，删
    echo "🗑️  DEL $f (target $new exists)"
    rm "$f"
  else
    echo "📝  RENAME $f → $new"
    mv "$f" "$new"
  fi
done
```

## Recipe 3：批量重命名（含子目录前缀防冲突）

**场景**：合并多个目录到同一个根，文件可能同名。

```python
from pathlib import Path

inbox = Path(r"D:\Inbox")
prefixes = {"Browser": "browser", "Installers": "installer"}

for sub, prefix in prefixes.items():
    p = inbox / sub
    if not p.exists():
        continue
    for f in p.rglob("*"):
        if f.is_file():
            target = inbox / f.name
            if target.exists() and target != f:
                target = inbox / f"{prefix}-{f.name}"
            f.rename(target)
```

## Recipe 4：递归扁平化（任何子目录 → 根）

**场景**：用户说"懒得分类，扁平化"。

```bash
# ⚠️ 先 dry-run 看每个文件的目标
cd D:/Inbox && \
echo "===== 全部子目录内容预览 =====" && \
find . -mindepth 2 -type f | head -20 && \
echo "===== 同名冲突检查 =====" && \
find . -mindepth 2 -type f -exec basename {} \; | sort | uniq -c | sort -rn | awk '$1>1{print}' | head
```

**Python 版（更可靠）**：
```python
from pathlib import Path

src_root = Path(r"D:\Inbox\Received")
inbox = Path(r"D:\Inbox")

files = sorted([f for f in src_root.rglob("*") if f.is_file()],
               key=lambda x: len(x.parts), reverse=True)
existing = {f.name for f in inbox.iterdir() if f.is_file()}

for f in files:
    target_name = f.name
    if f.name in existing:
        sub = f.relative_to(src_root).parts[0]
        target_name = f"{sub}-{f.name}"
    f.rename(inbox / target_name)
    existing.add(target_name)
```

## Recipe 5：合并 Finance + Invoice 为 Finance

```bash
# 假设 Invoice/ 里有 PDF，Finance/ 为空
mv D:/Cloud/Archive/Invoice/*.pdf D:/Cloud/Archive/Finance/
rmdir D:/Cloud/Archive/Invoice/
```

## Recipe 6：建 Organizations/ + 嵌套 Horizon-Racing-Team

```bash
mkdir -p D:/Cloud/Archive/Organizations/Horizon-Racing-Team
mv D:/Cloud/Archive/Horiizon_Racing_Team/*.pdf D:/Cloud/Archive/Organizations/Horizon-Racing-Team/
rmdir D:/Cloud/Archive/Horiizon_Racing_Team/
```

**关键**：修正目录名拼写错误（Horiizon_Racing_Team → Horizon-Racing-Team）+ 加命名约束（kebab-case）。

## Recipe 7：按类别分组（Cloud/Software/ → Cloud/Library/）

```bash
# 先建类别目录
mkdir -p D:/Cloud/Library/{CAD,Media,Game,Dev}

# 移动（带重命名）
mv D:/Cloud/Software/AutoCAD D:/Cloud/Library/CAD/AutoCAD
mv D:/Cloud/Software/SW2026 D:/Cloud/Library/CAD/Solidworks2026  # 改全名
mv D:/Cloud/Software/Davinci D:/Cloud/Library/Media/Davinci-Resolve
mv D:/Cloud/Software/foobar2000 D:/Cloud/Library/Media/foobar2000
mv D:/Cloud/Software/Guitarpro8 D:/Cloud/Library/Media/Guitar-Pro-8
rmdir D:/Cloud/Software/
```

## Recipe 8：改通用名（Data/Classin → Data/OnlineClass）

```bash
# ⚠️ 先确认 Data/ 下没有 OnlineClass/（否则冲突）
if [ -d D:/Data/OnlineClass ]; then
  echo "❌ 目标已存在，需先合并"
  exit 1
fi
mv D:/Data/Classin D:/Data/OnlineClass
```

## Recipe 9：修复目录名拼写错误

```bash
# 如 Horiizon_Racing_Team → Horizon-Racing-Team
mv D:/Cloud/Archive/Horiizon_Racing_Team D:/Cloud/Archive/Horizon-Racing-Team
```

## Recipe 10：清理嵌套空目录（像 Netdisks/Netdisks/ 这种）

```bash
# 先看嵌套结构
find D:/Inbox/Netdisks/ -type d

# 如果 Netdisks/Netdisks/BaiduNetdisk/ 都是空的，删整个
rm -rf D:/Inbox/Netdisks/
```

## Recipe 11：rmdir 失败的 4 种原因 + 处理

| 报错 | 真实原因 | 解决 |
|---|---|---|
| `Directory not empty` | 深层有文件（漏扫）| `find $dir -mindepth 1 -maxdepth 3` 重扫 |
| `Permission denied` | 目标已存在（mv 时） | 先 `rmdir` 空目标，再 `mv` |
| `Permission denied` | 源/目标跨盘 | 用 `rsync -a` 或 `cp -r` |
| `Permission denied` | 文件被进程占用 | 关闭占用进程或重试 |

## Recipe 12：批量安全 trash（mv 到 trash 目录，7 天后再真删）

```bash
trash_root=D:/Data/Cache/trash-$(date +%Y%m%d)
mkdir -p "$trash_root"

# 软删除（mv 到 trash）
for target in ...; do
  mv "$target" "$trash_root/"
done

# 7 天后清理 trash
# （写个 cron 每天跑 find /d/Data/Cache -name "trash-*" -mtime +7 -exec rm -rf {} \;）
```

## Recipe 13：大目录清理（>10 GB）的 mv 而非 cp -r

```bash
# ❌ cp -r 会超时（MSYS 默认 60s）
# ✅ 同盘用 mv（瞬间完成，因为是 rename 系统调用）

# 验证同盘
src_disk=$(df D:/A | tail -1 | awk '{print $NF}')
dst_disk=$(df D:/B | tail -1 | awk '{print $NF}')
if [ "$src_disk" = "$dst_disk" ]; then
  mv D:/A D:/B/A  # 同盘，安全
else
  rsync -a --progress D:/A/ D:/B/A/  # 跨盘
fi
```

## Recipe 14：student-style → professional-style 重命名

```python
import re
from pathlib import Path

def kebab(name):
    s = re.sub(r'([a-z])([A-Z])', r'\1-\2', name).lower()
    s = re.sub(r'[_\s]+', '-', s)
    return re.sub(r'-+', '-', s).strip('-')

# Guitarpro8 → Guitar-Pro-8
# Visual Studio Code2025 → VSCode2025（保留版本号是手动判断）
```

## 元教训

写 cleanup 流程时**永远先 dry-run**：

```bash
# 标准模板
echo "===== Dry-run ====="
for src in ...; do
  dst=...
  if [ -e "$dst" ]; then
    echo "❌ $dst 已存在"
  else
    echo "✅ $src → $dst"
  fi
done

echo
echo "回复 OK/go/执行 才真动"
```

**永远用 mv 而非 cp -r**（同盘情况下）。
**永远先 ls -la 再 rmdir**（避免漏扫 dotfiles 和深层子目录）。