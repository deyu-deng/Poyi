#!/usr/bin/env bash
# test_net_probe.sh — 网络探测 + 重试 + 推送的对抗性测试
# 不触碰真实仓库/真实网络：所有副作用（探测命令、git 二进制）均用环境变量注入。
# 运行：bash Loom/scripts/tests/test_net_probe.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 网络逻辑已并入 collect_mac.sh；source 它只暴露函数、不执行主流程
# shellcheck source=../collect_mac.sh
source "$SCRIPT_DIR/../collect_mac.sh"

pass=0; fail=0
ok()  { echo "  ✅ $1"; pass=$((pass+1)); }
bad() { echo "  ❌ $1"; fail=$((fail+1)); }

# 全部测试用统一计数器 + 模式文件驱动的探测脚本（避免 fork 多次写文件竞态）
PROBE_SCRIPT="$(mktemp -t poyi_probe.XXXXXX.sh)"
cat > "$PROBE_SCRIPT" <<'EOF'
#!/usr/bin/env bash
# 行为由环境变量 POYI_PROBE_MODE / POYI_PROBE_CNT 控制
cnt_file="${POYI_PROBE_CNT:-/tmp/poyi_probe_cnt}"
n=$(cat "$cnt_file" 2>/dev/null || echo 0); n=$((n+1)); echo "$n" > "$cnt_file"
case "${POYI_PROBE_MODE:-up}" in
  up)     exit 0 ;;
  down)   exit 1 ;;
  flaky)  (( n >= 3 )) && exit 0 || exit 1 ;;          # 第 3 次才通
  slow)   sleep 30 ;;                                   # 模拟黑洞/慢网络，会被超时杀掉
  dns)    getent hosts no-such-host.invalid.example >/dev/null 2>&1; exit $? ;;
  closed) exec 3<>/dev/tcp/127.0.0.1/1 2>/dev/null; exit $? ;;  # 端口 1 必拒绝
esac
EOF
chmod +x "$PROBE_SCRIPT"

reset_probe() { echo 0 > "${POYI_PROBE_CNT:-/tmp/poyi_probe_cnt}"; }
probe_cnt()   { cat "${POYI_PROBE_CNT:-/tmp/poyi_probe_cnt}" 2>/dev/null || echo 0; }

# fake git：记录调用，按 FAKEGIT_PUSH_RC 决定 push 成败；
# FAKEGIT_BEHIND 模拟「本地落后远端」（merge-base --is-ancestor 返回 1）；
# FAKEGIT_REBASE_RC 模拟变基成败。
FAKEGIT="$(mktemp -t poyi_fakegit.XXXXXX.sh)"
cat > "$FAKEGIT" <<'EOF'
#!/usr/bin/env bash
echo "FAKEGIT $*" >> "${FAKEGIT_LOG:-/tmp/poyi_fakegit.log}"
_has() { local t="$1"; shift; for a in "$@"; do [ "$a" = "$t" ] && return 0; done; return 1; }
if _has push "$@";    then exit "${FAKEGIT_PUSH_RC:-0}"; fi
if _has merge-base "$@"; then exit "${FAKEGIT_BEHIND:-0}"; fi   # 1 => 本地落后远端
if _has rebase "$@";  then exit "${FAKEGIT_REBASE_RC:-0}"; fi
exit 0
EOF
chmod +x "$FAKEGIT"
reset_fakegit() { : > "${FAKEGIT_LOG:-/tmp/poyi_fakegit.log}"; }
fakegit_called() { grep -q "$1" "${FAKEGIT_LOG:-/tmp/poyi_fakegit.log}" 2>/dev/null; }
fakegit_called_push() { fakegit_called "push"; }
fakegit_called_rebase() { fakegit_called "rebase"; }
fakegit_called_fetch() { fakegit_called "fetch"; }

echo "=== 1. wait_for_network：对抗性场景 ==="

# T1 首次即通
export POYI_PROBE_MODE=up GIT_NET_PROBE="bash $PROBE_SCRIPT" GIT_NET_TIMEOUT=3 GIT_NET_MAX_TRIES=6 GIT_NET_BASE_WAIT=0
reset_probe
if wait_for_network; then ok "T1 网络首探即通过 (rc=0)"; else bad "T1 期望 rc=0"; fi
[ "$(probe_cnt)" = "1" ] && ok "T1 仅探测 1 次" || bad "T1 探测次数=$(probe_cnt) 期望 1"

# T2 持续离线 → 放弃
export POYI_PROBE_MODE=down GIT_NET_MAX_TRIES=3 GIT_NET_BASE_WAIT=0
reset_probe
if wait_for_network; then bad "T2 期望 rc=1"; else ok "T2 持续离线正确放弃 (rc=1)"; fi
[ "$(probe_cnt)" = "3" ] && ok "T2 探测满 3 次" || bad "T2 探测次数=$(probe_cnt) 期望 3"

# T3 抖动网络：前两次挂，第三次通
export POYI_PROBE_MODE=flaky GIT_NET_MAX_TRIES=5 GIT_NET_BASE_WAIT=0
reset_probe
if wait_for_network; then ok "T3 抖动网络第 3 次重试成功 (rc=0)"; else bad "T3 期望 rc=0"; fi
[ "$(probe_cnt)" = "3" ] && ok "T3 恰好探测 3 次后成功" || bad "T3 探测次数=$(probe_cnt) 期望 3"

# T4 慢/黑洞网络：被超时杀掉，不悬挂
export POYI_PROBE_MODE=slow GIT_NET_TIMEOUT=1 GIT_NET_MAX_TRIES=2 GIT_NET_BASE_WAIT=0
reset_probe
t0=$(date +%s)
if wait_for_network; then bad "T4 期望 rc=1"; else ok "T4 超时探测正确放弃 (rc=1)"; fi
t1=$(date +%s)
dt=$((t1 - t0))
if (( dt < 15 )); then ok "T4 未悬挂（耗时 ${dt}s < 15s，每次超时 1s×2）"; else bad "T4 疑似悬挂（耗时 ${dt}s）"; fi

# T5 DNS 解析失败 → 视为离线
export POYI_PROBE_MODE=dns GIT_NET_TIMEOUT=3 GIT_NET_MAX_TRIES=2 GIT_NET_BASE_WAIT=0
reset_probe
if wait_for_network; then bad "T5 期望 rc=1"; else ok "T5 DNS 失败视为离线 (rc=1)"; fi

# T6 端口拒绝（目标可达但服务未开）→ 视为离线
export POYI_PROBE_MODE=closed GIT_NET_TIMEOUT=3 GIT_NET_MAX_TRIES=2 GIT_NET_BASE_WAIT=0
reset_probe
if wait_for_network; then bad "T6 期望 rc=1"; else ok "T6 端口拒绝视为离线 (rc=1)"; fi

echo "=== 2. try_push：端到端对抗性场景 ==="

# T7 网络通但远端拒绝 push → rc=2，且确实尝试了 push
export POYI_PROBE_MODE=up GIT_NET_PROBE="bash $PROBE_SCRIPT" GIT_NET_TIMEOUT=3 GIT_NET_MAX_TRIES=6 GIT_NET_BASE_WAIT=0
export GIT_BIN="$FAKEGIT" FAKEGIT_PUSH_RC=1
reset_probe; reset_fakegit
rc=0; try_push /tmp >/dev/null 2>&1 || rc=$?
[ "$rc" = "2" ] && ok "T7 远端拒绝返回 rc=2" || bad "T7 rc=$rc 期望 2"
fakegit_called_push && ok "T7 确实发起了 push" || bad "T7 未发起 push"

# T8 网络通 + push 成功 → rc=0
export FAKEGIT_PUSH_RC=0
reset_probe; reset_fakegit
rc=0; try_push /tmp >/dev/null 2>&1 || rc=$?
[ "$rc" = "0" ] && ok "T8 推送成功返回 rc=0" || bad "T8 rc=$rc 期望 0"
fakegit_called_push && ok "T8 发起了 push" || bad "T8 未发起 push"

# T9 网络不通 → 不发起 push，rc=1（离线不浪费一次 push 尝试）
export POYI_PROBE_MODE=down GIT_NET_MAX_TRIES=2 GIT_NET_BASE_WAIT=0
reset_probe; reset_fakegit
rc=0; try_push /tmp >/dev/null 2>&1 || rc=$?
[ "$rc" = "1" ] && ok "T9 离线返回 rc=1" || bad "T9 rc=$rc 期望 1"
if fakegit_called_push; then bad "T9 离线时不应发起 push"; else ok "T9 离线未发起 push（省一次失败尝试）"; fi

# T10 抖动网络第 3 次通 + push 成功 → rc=0（重试期间网络恢复）
export POYI_PROBE_MODE=flaky GIT_NET_MAX_TRIES=5 GIT_NET_BASE_WAIT=0 FAKEGIT_PUSH_RC=0
reset_probe; reset_fakegit
rc=0; try_push /tmp >/dev/null 2>&1 || rc=$?
[ "$rc" = "0" ] && ok "T10 抖动恢复后推送成功 (rc=0)" || bad "T10 rc=$rc 期望 0"

# T11 本地落后远端（win 已推）→ 先 fetch + 变基再 push，rc=0
export POYI_PROBE_MODE=up GIT_NET_PROBE="bash $PROBE_SCRIPT" GIT_NET_TIMEOUT=3 GIT_NET_MAX_TRIES=6 GIT_NET_BASE_WAIT=0
export FAKEGIT_PUSH_RC=0 FAKEGIT_BEHIND=1 FAKEGIT_REBASE_RC=0
reset_probe; reset_fakegit
rc=0; try_push /tmp >/dev/null 2>&1 || rc=$?
[ "$rc" = "0" ] && ok "T11 落后远端变基后推送成功 (rc=0)" || bad "T11 rc=$rc 期望 0"
fakegit_called_fetch  && ok "T11 发起 fetch"   || bad "T11 未 fetch"
fakegit_called_rebase && ok "T11 发起 rebase"  || bad "T11 未 rebase"
fakegit_called_push  && ok "T11 发起 push"    || bad "T11 未 push"

# T12 落后远端 + 变基冲突 → 中止变基，rc=2（不污染仓库）
export FAKEGIT_BEHIND=1 FAKEGIT_REBASE_RC=1 FAKEGIT_PUSH_RC=0
reset_probe; reset_fakegit
rc=0; try_push /tmp >/dev/null 2>&1 || rc=$?
[ "$rc" = "2" ] && ok "T12 变基冲突返回 rc=2" || bad "T12 rc=$rc 期望 2"
if fakegit_called_push; then bad "T12 冲突时不应 push"; else ok "T12 冲突中止未 push（安全）"; fi

# 清理
unset POYI_PROBE_MODE GIT_NET_PROBE GIT_NET_TIMEOUT GIT_NET_MAX_TRIES GIT_NET_BASE_WAIT GIT_BIN FAKEGIT_PUSH_RC FAKEGIT_BEHIND FAKEGIT_REBASE_RC
rm -f "$PROBE_SCRIPT" "$FAKEGIT" "${POYI_PROBE_CNT:-/tmp/poyi_probe_cnt}" "${FAKEGIT_LOG:-/tmp/poyi_fakegit.log}"

echo
echo "=== 结果：$pass 通过 / $fail 失败 ==="
[ "$fail" = "0" ] && exit 0 || exit 1
