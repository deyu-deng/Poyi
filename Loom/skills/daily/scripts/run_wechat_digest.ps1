# -*- coding: utf-8 -*-
# run_wechat_digest.ps1 - 微信管道一键全自动入口
#
# 职责：
#   1. 从 passphrase.txt 读取微信密钥（dbKey / imageXorKey / imageAesKey）
#   2. 生成 chatlog.json 配置（version=4 + 参数）
#   3. 启动 chatlog server（无界面，--auto-decrypt 解密本地库），常驻
#   4. 等待服务就绪后跑 digest_scan.py 落盘 social/wechat/exports/<日期>/
#   5. 跑 extract_insights --source social 路由到 digested/_insights.json
#
# 用法（无需手动开任何软件）：
#   powershell -ExecutionPolicy Bypass -File run_wechat_digest.ps1
#
# 说明：本脚本位置无关——POYI_ROOT 由脚本自身路径推导，仓库迁到任何目录都能直接用。
#       CONFIG 中带 (需核对) 的项请在你机器上确认后填好。

# ===================== CONFIG（按需核对） =====================
$CHATLOG_EXE   = "D:/Tools/wechat/chatlog/chatlog.exe"      # chatlog 二进制
$WORK_DIR      = "D:/Tools/wechat/chatlog"                  # chatlog.json / 日志落点
$PASSPHRASE    = "D:/Tools/wechat/keys/passphrase.txt"      # 密钥文件（UTF-8，ReadWxKey 输出）
$PYTHON        = "C:/Users/xgbc/.workbuddy/binaries/python/versions/3.13.12/python.exe"
$HTTP_ADDR     = "127.0.0.1:5030"
# WeChat 数据目录：留空则自动探测；手动填可跳过探测（例：C:/Users/xgbc/Documents/WeChat Files\xxxx_c19c）
$WECHAT_DATA_DIR = ""
# =============================================================

# --- 由脚本自身路径推导仓库根（位置无关，适配仓库迁移） ---
$POYI_ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$DIGEST_SCRIPT  = Join-Path $POYI_ROOT 'Loom\skills\daily\scripts\digest_scan.py'
$EXTRACT_SCRIPT = Join-Path $POYI_ROOT 'Loom\scripts\extract_insights.py'

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Write-Log($msg) { Write-Host $msg -ForegroundColor Cyan }

# --- 读密钥（UTF-8 显式读，避免 GBK 乱码导致密钥不匹配） ---
function Read-Keys {
    # 候选路径：配置项优先，其次常见位置（keys/ 子目录）
    $candidates = @($PASSPHRASE, "D:/Tools/wechat/keys/passphrase.txt", "D:/Tools/wechat/chatlog/passphrase.txt")
    $found = $null
    foreach ($c in $candidates) { if (Test-Path $c) { $found = $c; break } }
    if (-not $found) { throw "passphrase.txt 不存在（已尝试: $($candidates -join ', ')）" }
    Write-Log "读取密钥: $found"
    $lines = [System.IO.File]::ReadAllLines($found, [System.Text.Encoding]::UTF8)
    $k = @{ dbKey=""; imageXorKey=""; imageAesKey="" }
    foreach ($ln in $lines) {
        $t = $ln.Trim()
        if ($t -match '^(dbKey|data_key)\s*[=:]\s*(.+)$')                 { $k.dbKey = $Matches[2].Trim() }
        elseif ($t -match '^(imageXorKey|image_xor_key)\s*[=:]\s*(.+)$')  { $k.imageXorKey = $Matches[2].Trim() }
        elseif ($t -match '^(imageAesKey|image_aes_key|img_key)\s*[=:]\s*(.+)$') { $k.imageAesKey = $Matches[2].Trim() }
    }
    # 兜底：若整行就是 64-hex（无 key= 前缀），按顺序赋值
    if (-not $k.dbKey) {
        $hexLines = $lines | Where-Object { $_ -match '^[0-9a-fA-F]{32,}$' }
        if ($hexLines.Count -ge 1) { $k.dbKey = $hexLines[0].Trim() }
        if ($hexLines.Count -ge 2) { $k.imageXorKey = $hexLines[1].Trim() }
        if ($hexLines.Count -ge 3) { $k.imageAesKey = $hexLines[2].Trim() }
    }
    if (-not $k.dbKey) { throw "passphrase.txt 中未找到 dbKey" }
    return $k
}

# --- 探测 WeChat 数据目录（_c19c 后缀） ---
function Resolve-DataDir {
    if ($WECHAT_DATA_DIR) { return $WECHAT_DATA_DIR }
    $docs = [System.Environment]::GetFolderPath('MyDocuments')
    $base = Join-Path $docs 'WeChat Files'
    if (Test-Path $base) {
        $c19 = Get-ChildItem $base -Directory -Recurse -ErrorAction SilentlyContinue |
               Where-Object { $_.Name -match '_c19c$' } | Select-Object -First 1
        if ($c19) { return $c19.FullName }
        $acct = Get-ChildItem $base -Directory -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($acct) { return $acct.FullName }
    }
    throw "无法自动探测 WeChat 数据目录，请在 CONFIG 手动设置 `$WECHAT_DATA_DIR"
}

# --- 生成 / 合并 chatlog.json ---
function Ensure-ChatlogConfig($keys, $dataDir) {
    $cfgPath = Join-Path $WORK_DIR 'chatlog.json'
    $cfg = @{ version = 4; platform = "windows"; data_dir = $dataDir;
              data_key = $keys.dbKey; img_key = $keys.imageAesKey;
              http_addr = $HTTP_ADDR; auto_decrypt = $true }
    $cfg.image_xor_key = $keys.imageXorKey
    $cfg | ConvertTo-Json -Depth 3 | Out-File -FilePath $cfgPath -Encoding utf8
    Write-Log "已写入 chatlog.json -> $cfgPath"
}

# --- 启动 chatlog server（无界面常驻，输出写日志） ---
function Start-ChatlogServer {
    if (-not (Test-Path $CHATLOG_EXE)) { throw "chatlog.exe 不存在: $CHATLOG_EXE" }
    $logPath = Join-Path $WORK_DIR 'chatlog_server.log'
    $logErr  = Join-Path $WORK_DIR 'chatlog_server.err'
    $p = Start-Process -FilePath $CHATLOG_EXE `
        -ArgumentList "server","--addr",$HTTP_ADDR,"--work-dir",$WORK_DIR,"--auto-decrypt" `
        -NoNewWindow -PassThru `
        -RedirectStandardOutput $logPath -RedirectStandardError $logErr
    Write-Log "chatlog server 启动 (pid=$($p.Id))，日志 -> $logPath"
    return $p
}

# --- 等待服务就绪 ---
function Wait-Ready($timeoutSec=120) {
    $url = "http://$HTTP_ADDR/api/v1/contact"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    while ($sw.Elapsed.TotalSeconds -lt $timeoutSec) {
        try {
            $r = Invoke-WebRequest -Uri $url -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
            if ($r.StatusCode -eq 200) { Write-Log "chatlog 服务就绪"; return $true }
        } catch { }
        Start-Sleep -Seconds 2
    }
    return $false
}

# ===================== MAIN =====================
try {
    Write-Log "== 微信管道启动 =="
    Write-Log "POYI_ROOT = $POYI_ROOT"
    $keys = Read-Keys
    $dataDir = Resolve-DataDir
    Write-Log "数据目录: $dataDir"
    Ensure-ChatlogConfig $keys $dataDir
    $server = Start-ChatlogServer
    if (-not (Wait-Ready)) {
        Write-Log "chatlog 服务在 120 秒内未就绪，请查看 chatlog_server.log / .err"
        exit 1
    }
    Write-Log "== 拉取并落盘 digest =="
    & $PYTHON $DIGEST_SCRIPT
    if ($LASTEXITCODE -ne 0) { throw "digest_scan.py 失败 (exit=$LASTEXITCODE)" }
    Write-Log "== 路由 insights =="
    $today = (Get-Date).ToString('yyyy-MM-dd')
    & $PYTHON $EXTRACT_SCRIPT --source social --date $today --force
    if ($LASTEXITCODE -ne 0) { throw "extract_insights.py 失败 (exit=$LASTEXITCODE)" }
    Write-Log "== 完成。chatlog server 保持常驻（pid=$($server.Id)） =="
} catch {
    Write-Host "失败: $_" -ForegroundColor Red
    exit 1
}
