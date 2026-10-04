#!/usr/bin/env python3
"""
Mac 版 chatlog 聚合脚本 —— 通过统一 exporters 框架抽取 + 信号分离。

设计（与 Windows aggregate_win.py 对齐，使用 mac 目录布局）:
- 输入: 由 exporters/ 框架从各本地源（Marvis / Antigravity / WorkBuddy ...）实时抽取
- 输出: Loom/raw/chatlog/digested/<YYYY-MM-DD>/summary.md
                            digested/<YYYY-MM-DD>/_pending_digestion.json   (AI 语义消化信号)
                            digested/<YYYY-MM-DD>/_sessions_extract.json   (供语义消化读取的精简抽取)

每个导出格式解析为规范会话:
  {agent, session_id, title, model, source, messages:[{role, content, time}], stats}
消息按 time 分桶到日期。一个跨天会话会拆到多个日期。

语义消化（decisions/knowledge/preferences.json + 语义摘要）由 AI 完成:
  - Windows 上由 Marvis 定时任务完成;
  - Mac 上由本仓库的 WorkBuddy 自动化 / agent 读取 _pending_digestion.json 后完成。

幂等: 若某日期已存在 decisions.json（已完成语义消化），跳过该日期。
用法:
  python3 aggregate_mac.py            # 用各本地源聚合
  python3 aggregate_mac.py --force    # 强制重算（仍保留已存在的 decisions.json 日期）
"""

import json
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── 路径（脚本相对定位，不写死用户目录）──────────────────
SCRIPT = Path(__file__).resolve()
POYI_ROOT = SCRIPT.parents[2]            # .../Loom/scripts -> Poyi
LOOM_ROOT = SCRIPT.parents[1]            # .../Loom
CHAT = POYI_ROOT / "Loom" / "raw" / "chatlog"
DIGESTED = CHAT / "digested"

# exporters 框架与本脚本同目录
sys.path.insert(0, str(SCRIPT.parent))
from exporters import EXPORTER_REGISTRY  # noqa: E402


def norm_date(ts):
    """把各种时间戳规整为 YYYY-MM-DD，失败返回 None。"""
    if not ts:
        return None
    s = str(ts).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s).strftime("%Y-%m-%d")
    except Exception:
        pass
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").strftime("%Y-%m-%d")
    except Exception:
        return None


def _text(content, limit=None):
    """把可能是 list/dict 的 content 转成纯文本字符串。"""
    if isinstance(content, str):
        t = content
    elif isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict):
                parts.append(c.get("text") or c.get("content") or "")
            else:
                parts.append(str(c))
        t = "\n".join(p for p in parts if p)
    elif isinstance(content, dict):
        t = content.get("text") or content.get("content") or json.dumps(content, ensure_ascii=False)
    else:
        t = str(content)
    if limit:
        t = t[:limit]
    return t


def collect_sessions():
    """通过 exporters 框架从各本地源抽取会话。

    跨平台安全：单个源初始化/抽取抛错（如 Win 专属源在 Mac 上读 APPDATA 失败）
    不影响其他源。check_available() 返回 False 的源自动跳过。
    """
    sessions = []
    for cls in EXPORTER_REGISTRY:
        try:
            exp = cls(LOOM_ROOT)
        except Exception as e:
            print(f"[{cls.__name__}] 初始化失败，跳过: {e}")
            continue
        try:
            if not exp.check_available():
                print(f"[{exp.name}] 源不可用，跳过")
                continue
            got = exp.extract() or []
            print(f"[{exp.name}] 提取 {len(got)} 个会话")
            sessions.extend(got)
        except Exception as e:
            print(f"[{exp.name}] 提取失败: {e}")
    return sessions


def bucket_by_date(sessions):
    """返回 {date: [per-day-session-record]}。

    无时间戳的消息（如 Antigravity protobuf 抽取）归入会话兜底日期
    （会话内最早可定位的日期，其次导出器提供的 fallback_time），
    不再静默丢弃——否则整源数据会在分桶环节全部丢失。
    """
    by_date = defaultdict(list)
    for s in sessions:
        per_day = defaultdict(lambda: {"n": 0, "user": 0, "first_user": None, "samples": []})
        dated = [d for d in (norm_date(m.get("time")) for m in s["messages"]) if d]
        fallback_day = min(dated) if dated else norm_date(s.get("fallback_time"))
        for m in s["messages"]:
            day = norm_date(m.get("time")) or fallback_day
            if not day:
                # 连兜底日期都无法定位（无任何时间线索），只能跳过
                continue
            rec = per_day[day]
            rec["n"] += 1
            if m["role"] == "user":
                rec["user"] += 1
                if rec["first_user"] is None:
                    rec["first_user"] = _text(m["content"], 300)
                if len(rec["samples"]) < 3:
                    rec["samples"].append(_text(m["content"], 300))
        for day, rec in per_day.items():
            by_date[day].append({
                "agent": s["agent"],
                "session_id": s["session_id"],
                "title": s["title"],
                "model": s["model"],
                "source": s["source"],
                "n_messages": rec["n"],
                "n_user": rec["user"],
                "first_user_msg": rec["first_user"] or "",
                "user_samples": rec["samples"],
            })
    return by_date


def write_day(day, records):
    day_dir = DIGESTED / day
    day_dir.mkdir(parents=True, exist_ok=True)

    total_msgs = sum(r["n_messages"] for r in records)
    total_sessions = len(records)
    agents = sorted(set(r["agent"] for r in records))
    agent_counts = defaultdict(int)
    for r in records:
        agent_counts[r["agent"]] += 1

    # summary.md
    lines = [
        f"# 对话摘要 {day}",
        "",
        "## 概览",
        f"- 总会话数: {total_sessions}",
        f"- 总消息数: {total_msgs}",
        f"- 来源代理: {', '.join(agents)}",
        "",
        "## 各代理会话数",
    ]
    for agent in agents:
        a_recs = [r for r in records if r["agent"] == agent]
        a_msgs = sum(r["n_messages"] for r in a_recs)
        lines.append(f"- **{agent}**: {len(a_recs)} 会话, {a_msgs} 消息")

    lines.append("")
    lines.append("## 会话明细")
    for r in sorted(records, key=lambda x: (x["agent"], x["title"])):
        clue = (r["first_user_msg"] or "")[:120].replace("\n", " ")
        lines.append(f"- [{r['agent']}] {r['title']} ({r['n_messages']} msgs, 用户 {r['n_user']}) — `{r['session_id'][:40]}`")
        if clue:
            lines.append(f"  - 线索: {clue}")

    lines.append("")
    lines.append("---")
    lines.append("_AI 语义摘要待生成（读取 _pending_digestion.json 后由 AI 补全 decisions/knowledge/preferences.json）_")
    (day_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    # _pending_digestion.json (信号)
    signal = {
        "date": day,
        "session_count": total_sessions,
        "message_count": total_msgs,
        "agents": agents,
    }
    (day_dir / "_pending_digestion.json").write_text(
        json.dumps(signal, ensure_ascii=False, indent=2), encoding="utf-8")

    # _sessions_extract.json (供语义消化读取)
    (day_dir / "_sessions_extract.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[聚合] {day}: {total_sessions} 会话, {total_msgs} 消息, agents={agents}")


def main():
    force = "--force" in sys.argv

    sessions = collect_sessions()
    # 去重：同 (agent, session_id) 保留消息多的（marvis 等多份导出可能共享 conversation_id）
    best = {}
    for s in sessions:
        k = (s["agent"], s["session_id"])
        if k not in best or len(s["messages"]) > len(best[k]["messages"]):
            best[k] = s
    sessions = list(best.values())
    if not sessions:
        print("未加载到任何会话数据。")
        return

    by_date = bucket_by_date(sessions)
    if not by_date:
        print("没有任何带时间戳的会话，无法分桶。")
        return

    print(f"\n=== 聚合 {len(by_date)} 个日期 ===")
    done = 0
    skipped = 0
    for day in sorted(by_date.keys()):
        day_dir = DIGESTED / day
        if day_dir.joinpath("decisions.json").exists():
            # 已完成语义消化 → 跳过（保留现有 summary.md 不覆盖）
            skipped += 1
            # 顺手清理遗留的 pending 信号与 extract（已消化日期不需要）
            for junk in ("_pending_digestion.json", "_sessions_extract.json"):
                jp = day_dir / junk
                if jp.exists():
                    jp.unlink()
            print(f"[跳过] {day}: 已语义消化")
            continue
        if force and day_dir.joinpath("summary.md").exists():
            # --force 重算：先清掉旧的自动产物，再重写
            for junk in ("summary.md", "_pending_digestion.json", "_sessions_extract.json"):
                day_dir.joinpath(junk).unlink(missing_ok=True)
        write_day(day, by_date[day])
        done += 1

    print(f"\n完成: 新建/更新 {done} 天, 跳过 {skipped} 天（已消化）。")
    print(f"Digested -> {DIGESTED}")


if __name__ == "__main__":
    main()
