<!-- source: campus -->
---
name: campus
description: "Beiyu 校园事务自动化脚本集：自动签到、作业待办、校园课堂语音转 Markdown、图书馆查询。位于 D://Tools//Scripts//Beiyu-live-better//。 触发词：北屿大学、Beiyu、校园事务、签到、校园课堂。"
metadata: {"version": "1.0.0", "owner": "sample-user", "last_validated": "2026-07-27", "deps": []}
---
# Beiyu-live-better 技能文档

## 概述

Beiyu-live-better 是一套帮助北屿大学学生自动化校园事务的 Node.js 脚本集，位于 `D:/Tools/Scripts/Beiyu-live-better/`。

## 安装与配置

- **包管理器**：pnpm
- **安装依赖**：`cd D:/Tools/Scripts/Beiyu-live-better && pnpm install`
- **环境变量**：`.env` 文件，已配置学号、密码、钉钉 Webhook

## 功能列表

### 学在北屿大学 (`courses.campus/`)

| 脚本 | 功能 | 启动命令 |
|------|------|---------|
| `autosign.js` | 自动签到（雷达+数字），持续守护 | `node ./courses.campus/autosign.js` |
| `todolist.js` | 生成作业待办列表 | – |
| `materialDown.js` | 下载课程素材 | – |
| `materialMaintainer.js` | 增量下载课程素材 | – |

### 校园课堂 (`classroom.campus/`)

| 脚本 | 功能 | 启动命令 |
|------|------|---------|
| `generateCourseMd.js` | 语音识别+PPT 生成 Markdown | – |
| `getVideoURL.js` | 获取课程视频链接 | – |

### 图书馆 (`lib.campus/`)

| 脚本 | 功能 | 启动命令 |
|------|------|---------|
| `bookList.js` | 查询已借阅图书并续借 | – |

## autosign.js 详解

### 启动方式

```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'D:/Tools/Scripts/Beiyu-live-better'; node ./courses.campus/autosign.js"
```

或双击 `D:/Tools/Scripts/启动签到.bat`。

### 签到逻辑

1. 每 **4 秒** 轮询 `courses.campus.edu.cn/api/radar/rollcalls`
2. **雷达签到**：
   - 先尝试配置地点（当前：东一教学楼 ZJGD1）
   - 失败则遍历所有预设信标点（紫金港东/西/段永平、玉泉、之江、华家池等）
   - 仍失败则用三点定位法反推目标坐标
3. **数字签到**：
   - 先通过接口获取正确码
   - 获取失败则批量并发暴力破解（每批 200 个，0000-9999）
   - 找到正确码后立即终止
4. 签到结果通过**钉钉**推送通知

### 预设签到地点

| 代码 | 位置 | 坐标 |
|------|------|------|
| ZJGD1 | 东一教学楼 | 120.089136, 30.302331 |
| ZJGX1 | 西教学楼 | 120.085042, 30.301730 |
| ZJGB1 | 段永平教学楼 | 120.077135, 30.305142 |
| ZJG4 | 紫金港大西区 | 120.073427, 30.299757 |
| YQ4 | 玉泉教四 | 120.122176, 30.261555 |
| YQ1 | 玉泉教一 | 120.123853, 30.262544 |
| YQ7 | 玉泉教七 | 120.120344, 30.263907 |
| YQSS | 玉泉宿舍 | 120.124001, 30.265735 |
| ZJ1 | 之江校区1 | 120.126008, 30.192908 |
| ZJ2 | 之江校区2 | 120.124267, 30.191390 |
| HJC1 | 华家池校区1 | 120.195939, 30.272068 |
| HJC2 | 华家池校区2 | 120.198193, 30.270419 |

## 执行原则

1. 用户说"启动签到"或类似指令时，直接执行 autosign.js，无需确认
2. 在新窗口中运行（守护进程），不阻塞主会话
3. 如遇依赖缺失，先 `pnpm install` 再启动
4. 停止方式：关闭对应 PowerShell 窗口
*（内容由AI生成，仅供参考）*
