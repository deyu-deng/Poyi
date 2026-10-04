# social / wechat 采集：chatlog 工具来源与本地存档

> 本文档为**权威说明**，置于 `Loom/skills/daily/references/`（进 git，双机同步）。
> `Loom/raw/social/` 下的数据目录按隐私分级为 private（不进 git），故工具来源与采集约定集中记于此，避免随 social/ 丢失。

## 1. chatlog 工具身份
- **功能**：本地解密微信 4.x 桌面端数据库，提供 HTTP API（默认 `127.0.0.1:5030`）+ MCP，供 AI 助手读取**自己的**聊天数据。Apache-2.0。
- **我们使用的版本**：**bestK fork v0.5.2**（二进制内印有 `github.com/sjzar/chatlog` 路径——它是 sjzar/chatlog 的下游 fork）。
- 关键接口：`GET /api/v1/chatlog?time=last-7d&talker=...&format=json`（返回消息含 `isSelf` 字段，用于区分本人/他人）。

## 2. ⚠️ 上游风险（重要）
- 原始仓库 **`github.com/sjzar/chatlog` 已被删除**（多个第三方教程已提示改用 fork）。
- 因此 bestK fork 也可能随时消失——**必须本地存档源码**，不能只依赖远程。

## 3. 源码与二进制本地存档（防丢）
| 项目 | 路径 | 说明 |
|---|---|---|
| 运行二进制 | `D:/Tools/wechat/chatlog/chatlog.exe` | v0.5.2，约 33MB，运行用 |
| Release 包 | `D:/Tools/wechat/chatlog/chatlog_0.5.2_windows_amd64.zip` | 约 12MB，备份 |
| 源码（bestK @ v0.5.2） | `D:/Tools/wechat/chatlog-src` | `git clone --branch v0.5.2`，commit `0825df31964182257e0d91b29a719f12e4f8b0bb` |
| 源码镜像（imldy fork） | `D:/Tools/wechat/chatlog-src-imldy` | 第二手备份（main 分支） |

- 上述均在 `D:/Tools`（Poyi 仓库外，不进 git）。即便 Poyi 仓库丢失，工具仍在；但 `D:/Tools` 本身不在任何同步/备份中，建议另行备份，或靠下方 GitHub fork 重新 clone。
- **重新获取**：`git clone --branch v0.5.2 https://github.com/bestK/chatlog.git`

## 4. 数据落盘约定（social/wechat）
- `exports/<YYYY-MM-DD>/digest_raw.json`：`digest_scan.py` 全量产物（`{talker:{name,count,messages}}`）。
- `exports/<YYYY-MM-DD>/digest_conversations.json`：桥接文件，`social_adapter` 直接 ingest。
- `exports/media/`：chatlog 运行时本地媒体缓存（图片/视频/语音），**非管线产物，建议不进 git，可定期清理**。
- `digested/<date>/_insights.json`：`extract_insights --source social` 产出（private，不进 git）。

## 5. 接入管线（一键）
`run_wechat_digest.ps1` → 启动 chatlog server 解密 → `digest_scan.py` 落盘 `exports/` → `extract_insights --source social` 路由到 `_insights.json` → 下游 Vault notes。

## 6. 本人角色判定（已解决）
chatlog v0.5.2 的 `/api/v1/chatlog` 返回 `isSelf` 字段，`social_adapter` 据其判 `role=user`（本人）/ `other`（他人），已闭环（`digest_scan.py` 抽 `isSelf` 透传，`extract_insights.py` 的 `_wechat_role_is_me` 优先识别）。无需昵称匹配。
