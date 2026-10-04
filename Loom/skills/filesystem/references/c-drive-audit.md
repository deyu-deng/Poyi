# C 盘审计手册

> 当用户说"扫一下 C 盘"或"C 盘又满了"时加载本文。
> 重点：**C 盘内容高度个性化，必须 scan → 报告 → 等指令，不要自作主张**。

## 与 D 盘审计的区别

| 维度 | D 盘（Cloud） | C 盘（系统） |
|---|---|---|
| Agent 熟悉度 | 高（已知结构） | 低（千人千面） |
| 误删代价 | 低（自己文件） | 高（系统/软件崩） |
| 大量已知规则 | 有（filesystem §4） | 几乎无 |
| 系统目录 | 无 | 有 Windows/Program Files 等禁区 |
| 风险 | 误删用户文件 | **破坏系统 / 触发软件不可用** |

## 必须执行的扫描动作（顺序敏感）

### 1. 先看 C 盘健康度

```bash
# 磁盘剩余
wmic logicaldisk get caption,freespace,size

# 顶层目录概览（只看顶层，不递归）
ls -la C:/
```

**必须排除**：`Windows/`、`Program Files/`、`Program Files (x86)/`、`ProgramData/`、`$Recycle.Bin/`、`Recovery/`、`System Volume Information/`、`PerfLogs/`、`Boot/`、`Config.Msi/`。

### 2. 用户主目录深扫

```bash
ls -la /c/Users/xgbc/        # 顶层隐藏目录（60+ 个是常态）
ls -la /c/Users/xgbc/AppData/Local/   # 经常 GB 级，但需要时间
ls -la /c/Users/xgbc/Desktop/ /c/Users/xgbc/Documents/ /c/Users/xgbc/Downloads/
```

⚠️ `AppData/Local/Packages/` 和 `AppData/Local/Microsoft/` 通常巨大且结构复杂，先 ls 不 rglob。

### 3. 立刻报告 4 件事

1. **磁盘剩余**
2. **顶层非系统目录清单**（用户通常会指着其中一个说"那是什么"）
3. **Desktop/Documents/Downloads 大小**
4. **AppData 总大小**（用 `du -sh` 不展开）

不要立刻提建议，等用户问。

## 高频"看起来像病毒但其实不是"的陷阱

> 2026-06-15 用户在 `C:\yyb/` 看到 `beacon_report.log` 后怀疑中毒。我差点过度反应。
> 实际上 `yyb/` 是**百度网盘的 P2P 加速组件**，不是木马。

**判断启发**：

| 现象 | 真实可能 | 不要立刻判为 |
|---|---|---|
| 目录名是 2-4 个随机字母（yyb、abc、xyz） | 内部组件代号 / 灰软 | 病毒（先看文件） |
| 目录里有 `uninstall.exe` | 合法软件 | 木马 |
| `beacon_report.log` 之类日志 | 内部日志（很多软件叫这名字） | C2 通信（看大小） |
| 0 字节日志 | 卸载残留 | 通信证据 |
| uninstall 顺手把其他软件卸了 | PUA bug | 恶意软件 |
| 时间戳是最近安装其他软件前后 | 捆绑安装 | 注入 |

**冷静原则**：先 ls 内容、查文件大小、看时间戳，**不要用"beacon"这种词吓用户**。

## Desktop 隐藏空间挖掘

很多用户不知道 Desktop 有**卸载备份残留**。

```bash
# 常见模式
ls -la /c/Users/xgbc/Desktop/ | grep -E "SW_Cleanup|Uninstall|Backup|Install"

# 这种往往 GB 级
du -sh /c/Users/xgbc/Desktop/SW_Cleanup_*
```

**2026-06-15 实测**：SolidWorks 卸载备份 `SW_Cleanup_Backup2_20260614_191605/` 占 34.14 GB，但用户以为"早就删了"。

## C 盘 vs D 盘的判断规则（重要 pitfall）

用户说"C 盘又满了"，不要直接去动 C 盘。**先问 3 个问题**：

1. **D 盘也满了吗？** — 如果 D 盘空，C 盘满了通常是 D 盘该装的不在 D 盘
2. **什么类型文件占得多？** — 系统更新？软件缓存？用户文件？
3. **哪些软件是必须留在 C 盘的？** — 浏览器、聊天工具通常只能在 C 盘

## 危险操作红线（绝不执行）

| 操作 | 风险 |
|---|---|
| 删除 `C:\Windows\`, `C:\Program Files\`, `C:\Program Files (x86)\`, `C:\ProgramData\` | 系统崩溃 |
| 删除 `C:\Users\xgbc\AppData\` 全部 | 所有软件配置丢失，需重装 |
| 删除 `C:\Users\Public\` | 共享文件丢失 |
| 删除注册表相关文件 | 软件失能 |
| 在 `C:\Users\xgbc\` 内 `rm -rf .*` | **所有 dotfiles（含 .ssh/、.gitconfig）丢失** |

## 操作 C 盘前的强制 dry-run

即使是删 1 个文件：

```bash
echo "===== Dry-run ====="
echo "[rm] /c/Users/xgbc/Desktop/SW_Cleanup_Backup2/"
echo "  预估大小: $(du -sh /c/Users/xgbc/Desktop/SW_Cleanup_Backup2/ 2>/dev/null | cut -f1)"
echo "  预计释放: 34 GB"
echo
echo "回复 OK/go/执行 我才真动"
```

不要被"C 盘满了"的紧迫感推动跳过 dry-run。

## 真实案例（2026-06-15）

**场景**：用户说"C 盘存储告急，可能有些软件本应装在 D 盘"。

**发现**：
1. `Desktop/` 占 35 GB — 全是 SolidWorks 卸载残留（`SW_Cleanup_Backup2_20260614_191605/`，含百度网盘未完成下载 16.7 GB）
2. `C:\yyb/` 不是病毒，是百度网盘 P2P 加速组件的目录
3. uninstall yyb 把 QQ 一起卸了 — 百度网盘 PUA bug

**处理**：
1. 先扫描 Desktop，发现 `SW_Cleanup_Backup2_20260614_191605/` 占 34 GB
2. 确认是 SolidWorks 卸载备份（用户已装好 SolidWorks）
3. 用户拍板"直接删" → 删除整个目录
4. 释放 34 GB

**结论**：先发现桌面隐藏的"卸载备份"目录（30+ GB 级别），是 C 盘空间释放的**第一手选项**——比动 AppData 安全。

## C 盘 → D 盘迁移候选清单（标准建议）

| 类型 | 迁移目标 | 可行性 |
|---|---|---|
| 软件安装包（已下载） | `D:\Cloud\Library\{category}/` | ✅ 完全可行 |
| 软件缓存（Adobe、钉钉、微信等） | `D:\Data\Cache\{软件}/` | ⚠️ 软件要支持改缓存路径 |
| 软件数据库（聊天记录、Zotero） | `D:\Data\Collaboration/{软件}/` 或 `D:\Data\Literature/` | ⚠️ 需要 Symlink，复杂 |
| dotfiles（`.bashrc`、`.gitconfig`、`.ssh/`） | `D:\Development\Home/`（已存在） | ⚠️ 需要修改 $HOME 或 PATH |
| 用户文件（Desktop/Documents/Downloads） | `D:\Cloud\` 对应分类 | ⚠️ 需要用户主动迁移，软链有兼容性问题 |
| XboxGames 数据 | `D:\Games\` | ⚠️ Xbox 不支持自由移动 |
| OneDrive 缓存 | `D:\Data\CloudDrive/` | ✅ 可在 OneDrive 设置里改 |

**铁律**：**不能简单 cp/move** AppData 内容——会破坏注册表关联。要用 mklink（Junction）。

## C 盘审计后建议的输出格式

```markdown
## C 盘审计报告

### 磁盘
- C 盘剩余: XX GB / 总 XX GB
- D 盘剩余: XX GB / 总 XX GB

### 顶层（15 个非系统目录）
| 目录 | 大小 | 角色判断 |
|------|------|----------|
| Autodesk/ | X GB | AutoCAD 残留，**应移 D 盘** |
| KingsoftData/ | X MB | WPS 缓存 |
| ... | | |

### 用户主目录（/c/Users/xgbc/）
- Desktop/: 35 GB（**主嫌疑**：卸载备份残留）
- Documents/: 32 MB
- Downloads/: 0
- AppData/Local/: X GB（**主嫌疑 2**）

### 建议下一步
按风险从低到高：
1. 删除 Desktop 卸载备份（释放 35 GB）
2. 清理 OneDrive 缓存
3. 迁移 OneDrive 到 D 盘
4. 清理 AppData/Local/Microsoft/Windows/Explorer/

每步都需要单独确认。
```

## 与 filesystem SKILL.md 的关系

- **filesystem §1 命名规则** —— 不变
- **filesystem §3 决策树** —— 仍以 Cloud/ 为主，C 盘条目最少
- **filesystem §5.3 修复命令** —— 适用于 D:/Cloud，D 盘用法不同
- **本文** —— C 盘特化，**加载 filesystem skill 后必须额外加载本文**

## 元教训

写 C 盘相关 skill 时要时刻记着：

1. **用户对 C 盘有强烈感情（可能含珍贵文件）**——比 D 盘谨慎 10 倍
2. **C 盘"看起来像病毒但其实不是"的陷阱很多**——冷静分析
3. **Desktop 是 C 盘隐藏空间的"重灾区"**——先扫 Desktop
4. **任何 mv/rm 之前必须 dry-run**——绝对不要凭感觉
5. **不要因为"C 盘满了"就急着清理**——先问清楚用户痛点