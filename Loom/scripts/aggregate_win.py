#!/usr/bin/env python3
"""
Win 版日清聚合脚本 v4.0 —— 导出 + 信号分离。

exporters/ 目录下每个平台一个独立 .py 文件，实现 BaseExporter 统一接口。
aggregate_win.py 退化为调度器：遍历导出器 → 写入 raw/ → 写统计摘要 → 发信号。
新增平台 = 新增 exporters/{Name}Exporter 文件即可，无需修改本脚本。

v4.0 变更：Phase 2 正则消化已移除。AI 语义消化由 Marvis 定时任务接管，
本脚本仅负责导出和写入 _pending_digestion.json 信号文件。
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Force stdout/stderr to use UTF-8 to prevent GBK encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


# ── 路径配置（脚本相对定位，与 aggregate_mac.py 对齐；AGENTS §0 禁止写死盘符）──
_SCRIPT = Path(__file__).resolve()
LOOM_ROOT = _SCRIPT.parents[1]              # .../Loom/scripts -> Loom
CHAT_LOGS = LOOM_ROOT / "raw" / "chatlog"
RAW = CHAT_LOGS / "raw"
DIGESTED = CHAT_LOGS / "digested"
SCRIPTS = LOOM_ROOT / "scripts"
LOG_DIR = SCRIPTS / "logs"

TODAY = datetime.now().strftime("%Y-%m-%d")
RAW_TODAY = RAW / TODAY
DIGESTED_TODAY = DIGESTED / TODAY
LOCK_FILE = DIGESTED_TODAY / "summary.md"

_INVALID_FILENAME_CHARS = '<>:"/\\|?*'


def safe_filename(s: str, maxlen: int = 120) -> str:
    s = ''.join(ch if ord(ch) >= 32 or ch in '\n\r\t' else '_' for ch in s)
    s = s.replace('\r', '').replace('\n', '').replace('\t', ' ')
    for ch in _INVALID_FILENAME_CHARS:
        s = s.replace(ch, '_')
    s = s.replace(' ', '_')
    while '__' in s:
        s = s.replace('__', '_')
    return s[:maxlen]


def ensure_dirs():
    RAW_TODAY.mkdir(parents=True, exist_ok=True)
    DIGESTED_TODAY.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


# ── 调度器 ────────────────────────────────────────────────

def run_exporters():
    """遍历所有导出器，返回 session 列表。"""
    from exporters import create_all_exporters

    exporters = create_all_exporters(LOOM_ROOT)
    all_results = []

    for exp in exporters:
        try:
            available = exp.check_available()
            if not available:
                print(f"[{exp.display_name}] unavailable, skipping")
                continue

            print(f"[{exp.display_name}] extracting...")
            sessions = exp.extract()

            for sess in sessions:
                title = sess.get("title", "untitled")[:60]
                agent = sess["agent"]
                sid = sess["session_id"]

                fname = safe_filename(
                    f"{agent}-win_{sid}_{title}.json", maxlen=150
                )
                filepath = RAW_TODAY / fname

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(sess, f, ensure_ascii=False, indent=2)

                all_results.append(sess)
                n_msgs = len(sess.get("messages", []))
                print(f"  -> {fname} ({n_msgs} msgs)")

        except Exception as e:
            print(f"[{exp.display_name}] ERROR: {e}")

    return all_results


# ── 摘要 ──────────────────────────────────────────────────

def digest():
    """写统计摘要 + 发 AI 消化信号。"""
    all_sessions = _load_all_raw_sessions()

    if not all_sessions:
        print("[Digest] No sessions")
        with open(DIGESTED_TODAY / "summary.md", "w", encoding="utf-8") as f:
            f.write(f"# 对话摘要 {TODAY}\n\n- 无会话数据\n")
        return

    total_msgs = sum(len(s["messages"]) for s in all_sessions)
    total_sessions = len(all_sessions)
    agents_used = set(s["agent"] for s in all_sessions)

    # 统计摘要
    agent_counts = defaultdict(int)
    for s in all_sessions:
        agent_counts[s["agent"]] += 1

    lines = [
        f"# 对话摘要 {TODAY}",
        "",
        f"- 代理: {', '.join(sorted(agents_used))}",
        f"- 会话数: {total_sessions}",
        f"- 消息总数: {total_msgs}",
        "",
        "## 各代理会话数",
    ]

    for agent, count in sorted(agent_counts.items()):
        agent_sessions = [s for s in all_sessions if s["agent"] == agent]
        agent_msgs = sum(len(s["messages"]) for s in agent_sessions)
        lines.append(f"- **{agent}**: {count} 会话, {agent_msgs} 消息")

    lines.append("")
    lines.append("## 会话明细")
    for s in all_sessions:
        title = s.get("title", "")[:60]
        n = len(s["messages"])
        lines.append(f"- [{s['agent']}] {title} ({n} msgs) — `{s['session_id'][:40]}`")

    lines.append("")
    lines.append("---")
    lines.append(f"_AI 语义摘要待 Marvis 定时任务补全_")

    with open(DIGESTED_TODAY / "summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # 发信号给 Marvis AI 消化管线
    signal = {
        "date": TODAY,
        "session_count": total_sessions,
        "message_count": total_msgs,
        "agents": sorted(agents_used),
    }
    with open(DIGESTED_TODAY / "_pending_digestion.json", "w", encoding="utf-8") as f:
        json.dump(signal, f, ensure_ascii=False, indent=2)

    print(f"[Digest] summary.md + _pending_digestion.json -> {DIGESTED_TODAY}")


def _load_all_raw_sessions():
    all_sessions = []
    if not RAW_TODAY.exists():
        return all_sessions

    json_files = list(RAW_TODAY.glob("*.json"))
    print(f"[Digest] Scanning {len(json_files)} JSON files in {RAW_TODAY}")

    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, PermissionError, OSError) as e:
            print(f"[Digest] Skipping {jf.name}: {e}")
            continue

        if isinstance(data, dict) and "agent" in data and "messages" in data:
            all_sessions.append(data)
        else:
            print(f"[Digest] Skipping {jf.name}: not a valid session file")

    return all_sessions


# ── Main ──────────────────────────────────────────────────

if __name__ == "__main__":
    force_run = "--force" in sys.argv or "-f" in sys.argv
    if LOCK_FILE.exists() and not force_run:
        print(f"[Skip] Already aggregated today ({TODAY})")
        sys.exit(0)


    print(f"=== Chat Logs Aggregation {TODAY} (Win) v4.0 ===\n")
    ensure_dirs()

    # 遍历导出器
    results = run_exporters()

    agents_found = set(r["agent"] for r in results)
    print(f"\n--- Total: {len(results)} sessions from {len(agents_found)} agents: {agents_found} ---\n")

    # 消化
    digest()

    # 日锁
    if not LOCK_FILE.exists():
        with open(LOCK_FILE, "w", encoding="utf-8") as f:
            f.write(f"# 对话摘要 {TODAY}\n\n- 聚合完成\n")

    print(f"\nDone. Raw -> {RAW_TODAY}")
    print(f"Digested -> {DIGESTED_TODAY}")
