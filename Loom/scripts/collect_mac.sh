#!/usr/bin/env bash
# collect_mac.sh — Mac 端 chatlog 采集 + 解析 + 推送全链路
# 触发：登录时（launchd RunAtLoad）+ 每 2 小时（StartInterval）+ 唤醒时（sleepwatcher 调 ~/.wakeup_collect）
# 职责边界：只采集 + 解析中间态，不跑 LLM 语义消化（那是 win 端的事）。
#
# 本文件被 tests/test_net_probe.sh `source` 时只暴露下方函数、不执行主流程
# （靠文件末尾的 `BASH_SOURCE[0] == $0` 守卫判断直接执行 vs 被 source）。

# ─────────────────────────────────────────────────────────────
# 网络就绪探测 + 带重试推送
# 默认用 `git ls-remote --heads origin` 探真实远端（与 push 同端点/鉴权）。
# 用 perl 的 alarm 实现可移植超时（macOS 无 GNU timeout）。
# 所有行为可由环境变量覆盖，便于对抗性测试：
#   GIT_NET_PROBE / GIT_NET_TIMEOUT / GIT_NET_MAX_TRIES / GIT_NET_BASE_WAIT / GIT_BIN
# ─────────────────────────────────────────────────────────────
git_net_probe() {
  local probe="${GIT_NET_PROBE:-git ls-remote --heads origin >/dev/null 2>&1}"
  local secs="${GIT_NET_TIMEOUT:-8}"
  # perl alarm 超时：perl 进程 exec 成 `bash -c "$probe"`，超时则 SIGALRM 杀掉该进程。
  perl -e 'alarm(shift); exec("bash","-c",shift)' "$secs" "$probe"
}

# 带重试的网络等待：返回 0 = 就绪，1 = 放弃（仍不可用）
wait_for_network() {
  local max="${GIT_NET_MAX_TRIES:-6}"
  local wait="${GIT_NET_BASE_WAIT:-3}"
  local i=0
  while (( i < max )); do
    if git_net_probe; then
      if (( i == 0 )); then
        echo "[net] $(date -u +%FT%TZ) 网络就绪（首次探测即通过）"
      else
        echo "[net] $(date -u +%FT%TZ) 网络就绪（第 $((i+1)) 次重试成功）"
      fi
      return 0
    fi
    i=$((i+1))
    if (( i < max )); then
      echo "[net] $(date -u +%FT%TZ) 网络未就绪（第 $i 次），${wait}s 后重试"
      sleep "$wait"
    fi
  done
  echo "[net] $(date -u +%FT%TZ) 网络探测 ${max} 次均失败，推迟推送"
  return 1
}

# 对齐远端：fetch origin main，若本地落后则变基到 origin/main（等价于 pull --rebase 的拆分）。
# 多机仓库（mac+win 都推 main）必须这一步：既避免 win 的新提交让我们非快进被拒，
# 也确保本机工作树能反映 windows 那边的最新更新（开盖即对齐）。
# 入参：$1 = 仓库根目录（默认 $ROOT）
# 返回：0 = 已对齐（含已是最新）；1 = fetch 失败（离线等）；2 = 变基冲突（已 abort）
sync_remote() {
  local root="${1:-$ROOT}"
  local gitbin="${GIT_BIN:-/usr/bin/git}"
  set +e
  "$gitbin" -C "$root" fetch origin main >/dev/null 2>&1
  local frc=$?
  set -e
  if [ "$frc" -ne 0 ]; then
    echo "[collect_mac] $(date -u +%Y-%m-%dT%H:%M:%SZ) fetch 失败（可能离线），跳过对齐"
    return 1
  fi
  if "$gitbin" -C "$root" merge-base --is-ancestor "origin/main" HEAD; then
    return 0   # 已是最新，无需变基
  fi
  # 本地落后：若有未提交改动先 stash，变基后再恢复，避免 rebase 因脏树直接失败
  local dirty=0
  if ! "$gitbin" -C "$root" diff --quiet HEAD -- "$root/Loom/raw/chatlog/"; then
    dirty=1
    "$gitbin" -C "$root" stash push -u -m "auto-sync-stash" -- "$root/Loom/raw/chatlog/" >/dev/null 2>&1
  fi
  echo "[collect_mac] $(date -u +%Y-%m-%dT%H:%M:%SZ) 本地落后远端，变基对齐 origin/main"
  set +e
  "$gitbin" -C "$root" rebase "origin/main"
  local rrc=$?
  set -e
  if [ "$rrc" -ne 0 ]; then
    "$gitbin" -C "$root" rebase --abort >/dev/null 2>&1
    echo "[collect_mac] $(date -u +%Y-%m-%dT%H:%M:%SZ) 变基冲突，已中止；请手动处理"
    return 2
  fi
  if [ "$dirty" -eq 1 ]; then
    set +e
    "$gitbin" -C "$root" stash pop >/dev/null 2>&1
    if [ $? -ne 0 ]; then
      echo "[collect_mac] $(date -u +%Y-%m-%dT%H:%M:%SZ) 还原暂存失败，请手动 git stash pop"
    fi
    set -e
  fi
  return 0
}

# 尝试推送：先等网络，再对齐远端（win 可能已推过/期间又推），最后 push。
# 入参：$1 = 仓库根目录（默认 $ROOT）
# 返回：0 = 推送成功；1 = 网络不可用/未推；2 = 远端拒绝或变基冲突
try_push() {
  local root="${1:-$ROOT}"
  local gitbin="${GIT_BIN:-/usr/bin/git}"
  if ! wait_for_network; then
    echo "[collect_mac] $(date -u +%Y-%m-%dT%H:%M:%SZ) 网络不可用，跳过推送，下次触发重试"
    return 1
  fi
  # 推送前再对齐一次（防本脚本运行期间 win 又推了）。对齐失败则不推送。
  sync_remote "$root" || return $?
  # 注意：collect_mac.sh 主流程以 `set -e` 运行，本函数也被其 source 后调用；
  # 此处用 `set +e` 包裹，确保 push 非零退出能落入失败分支而非直接终止脚本。
  set +e
  "$gitbin" -C "$root" push
  local rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then
    echo "[collect_mac] $(date -u +%Y-%m-%dT%H:%M:%SZ) 已提交并推送"
    return 0
  else
    echo "[collect_mac] $(date -u +%Y-%m-%dT%H:%M:%SZ) 推送失败（远端拒绝/认证等），下次重试"
    return 2
  fi
}

# ─────────────────────────────────────────────────────────────
# 主流程：仅「直接执行」时运行；被 source（测试）时不跑。
# ─────────────────────────────────────────────────────────────
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -euo pipefail

  PY=/Users/sample/.workbuddy/binaries/python/versions/3.13.12/bin/python3
  ROOT=/Users/sample/Poyi
  AGG="$ROOT/Loom/scripts/aggregate_mac.py"
  LOGDIR="$ROOT/Loom/scripts/logs"
  mkdir -p "$LOGDIR"

  # 自包含落盘日志（无论被 launchd 还是 wakeup 调用都有记录）
  exec >> "$LOGDIR/collect-$(date -u +%Y%m%d).log" 2>&1

  echo "[collect_mac] $(date -u +%Y-%m-%dT%H:%M:%SZ) 开始：先对齐远端（windows 最新更新）"
  # 开盖第一步：无论本机是否有新数据，都先把本地对齐 windows 那边的更新。
  # 离线则跳过往后走（后续 try_push 仍会在有变化时重试对齐+推送）。
  if wait_for_network; then
    sync_remote "$ROOT" || true
  else
    echo "[collect_mac] $(date -u +%Y-%m-%dT%H:%M:%SZ) 网络不可用，跳过对齐，仅本地采集"
  fi

  echo "[collect_mac] $(date -u +%Y-%m-%dT%H:%M:%SZ) 聚合 + 抽取当日消息"
  "$PY" "$AGG" --force
  echo "[collect_mac] $(date -u +%Y-%m-%dT%H:%M:%SZ) 聚合完成"

  # 仅当有实际变化时才提交 + 推送，避免空 commit 刷远端。
  # 只同步采集产物（digested/ 中间态），代码改动由手动 commit 处理。
  GIT=/usr/bin/git
  GIT_BIN="${GIT_BIN:-$GIT}"
  # 先 stage（含未跟踪的新日期目录），再比对暂存区，才能捕获「新增日期」这类纯新增。
  # 仅用 `git diff` 会漏掉未跟踪文件，导致新会话日永不提交。
  "$GIT" -C "$ROOT" add "$ROOT/Loom/raw/chatlog/"
  if ! "$GIT" -C "$ROOT" diff --cached --quiet -- "$ROOT/Loom/raw/chatlog/"; then
    TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    # 路径限定提交：即使索引里残留其他已暂存文件，也只提交采集产物，
    # 防止 launchd 自动提交把用户手工 stage 的无关改动一并带上远端。
    "$GIT" -C "$ROOT" commit -m "chore(chatlog): 自动采集同步 $TS" -- "$ROOT/Loom/raw/chatlog/"
    # 推送前先等网络就绪（开盖瞬间 WiFi 常未连上），就绪后再 push；
    # 仍失败（离线/远端拒绝）不阻断采集，下次触发重试。
    try_push "$ROOT"
  else
    echo "[collect_mac] $(date -u +%FT%TZ) 无变化，跳过提交"
  fi
fi
