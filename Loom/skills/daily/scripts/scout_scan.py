"""Cron-mode scout scan: pull P0/P1 wechat groups + 公众号 near 7 days, filter for opportunity keywords, save to JSON.

Usage (cron mode, no execute_code allowed):
    cd "C:/Users/xgbc/AppData/Local/Temp" && "<PYBIN>" "C:/Users/xgbc/AppData/Local/Temp/scout_scan.py"

Output: $TEMP/scout_raw.json  (also printed summary to stdout)

Companion to digest_scan.py — same 30-channel coverage, but filters messages for
opportunity keywords (比赛 / 科研 / 奖学金 / 讲座 / 实践 / 实习) and excludes
已报名活动 (now read from data/activity_state.md) 例行通知.

Handles the wechat_cli history quirks documented in:
  - references/wechat-cli-pitfalls.md §11  (messages: list[str] not list[dict])
  - references/wechat-cli-pitfalls.md §2   (multi-shard / --limit 200 / cross-check)
  - references/wechat-cli-pitfalls.md §9.5 (公众号 username 速查)
  - references/scout-pitfalls.md          (学年过滤、空结果纪律、占位符简报模板)
  - references/cron-delivery-pitfalls.md §F (MSYS 路径陷阱)
"""
import subprocess
import json
import os
import re
from datetime import datetime, timedelta

# TODO: macOS 适配 — PYBIN 自动检测
# 当前脚本为 Windows 设计。macOS 上无 wechat-cli / MarvisAgent 等价物，
# 以下逻辑优先从 MARVIS_PYBIN 环境变量读取，未设置时 fallback 到硬编码版本号。
# 更换 MarvisAgent 版本时需更新 fallback 中的版本号，或设置环境变量。
# ⚠️ cron 模式下 PYBIN 作为 subprocess.run cmd[0] 时必须用 D:/ 前斜杠盘符形式
# （MSYS 翻译只在 shell 层生效，subprocess 列表不翻译）。

def _detect_pybin():
    env_pybin = os.environ.get("MARVIS_PYBIN")
    if env_pybin:
        return env_pybin, os.path.join(os.path.dirname(os.path.dirname(env_pybin)), "Lib", "site-packages")
    # fallback — Windows only
    fallback_base = "D:/Software/Marvis/MarvisAgent/1.0.1100.219/runtime/python311"
    return os.path.join(fallback_base, "python.exe"), os.path.join(fallback_base, "Lib", "site-packages")

PYBIN, SITE = _detect_pybin()

# --- P0/P1 微信群 (username, display_name) — 与 digest_scan.py 保持完全一致
WECHAT_GROUPS = {
    "19416880228@chatroom": "工科试验2501入党积极分子",
    "32585334488@chatroom": "26春【晨曦启明】志愿者",
    "22785073235@chatroom": "1️⃣🟦2025🟦青禾四舍👑",
    "91143084472@chatroom": "2501班级群",
    "12121228217@chatroom": "工科试验2501",
    "18078014564@chatroom": "车辆2502班委群",
    "27078175275@chatroom": "示例车队 2026赛季大群",
    "60226711214@chatroom": "底盘车架",
    "32017243574@chatroom": "2026示例车队暑期社会实践",
    "74036572916@chatroom": "2026示例车队学生交流群",
    "14728426060@chatroom": "史纲第二小组",
    "91339174574@chatroom": "长风四连",
    "18428266328@chatroom": "🌠2025级能源本科生",
}

# --- 公众号 (username, display_name) — 与 digest_scan.py 保持完全一致
OFFICIAL_ACCOUNTS = {
    "gh_caca884246ed": "Beiyu能小源",
    "gh_f16d677bb8c1": "北屿大学青志",
    "gh_4db1f4ea5cce": "青禾青年",
    "gh_85d5c0bd629e": "青禾学园",
    "gh_98baa1984e29": "北屿大学求是学院",
    "gh_2dd7552ab054": "北屿大学竺院人",
    "gh_8099d495def9": "北屿大学体育与艺术",
    "gh_8073fd30429d": "北屿大学资助",
    "gh_968dd39a4e75": "智慧树共享课",
    "gh_35bec0400e19": "E志者EVA",
    "gh_5f7fc241ccc6": "求是情报站",
    "gh_d7b2a01d31bb": "北屿大学微学工",
    "gh_1d4245f2e96c": "北屿大学图书馆",
    "gh_1e35a12f9fbf": "北屿大学医院",
    "gh_ace8b2467173": "北屿大学学生会",
    "gh_e9d23a6bfef2": "北屿大学CC98论坛",
    "gh_87de9dd48ebe": "我就要在浙里要饭",
}

GROUPS = {**WECHAT_GROUPS, **OFFICIAL_ACCOUNTS}

# --- Scout 关键词（按类别）— 与 modules/scout.md Step 1 表对齐
SCOUT_KEYWORDS = {
    "比赛竞赛": ["大赛", "竞赛", "比赛", "选拔", "创新创业", "挑战杯", "节能减排", "互联网+", "智能车", "RoboMaster", "示例问策", "方程式", "赛车"],
    "科研与项目": ["招募", "课题组", "SRTP", "科研训练", "暑研", "进组", "国创", "省创", "导师"],
    "奖学金与评优": ["奖学金", "评优", "荣誉称号", "卓越", "英才", "国奖", "校奖", "学业优秀"],
    "讲座与活动": ["讲座", "论坛", "报告", "分享会", "沙龙", "研讨会", "科技节", "演讲", "对话"],
    "实践项目": ["社会实践", "暑期实践", "支教", "志愿", "调研", "三下乡", "实践队"],
    "实习就业": ["实习", "校招", "内推", "招聘", "企业开放日", "实习招募"],
}

# 已报名活动（来自 profile「已报名活动」表）— 群内例行通知排除
# 注意：这些只是"提示词"，命中后整条消息不计入 scout_hits，但同时会打上"已报名"标记方便人审
ALREADY_REGISTERED_KEYWORDS = {
    "示例车队", "底盘车架", "暑期社会实践", "晨曦启明", "入党积极分子",
    "史纲第二小组", "军训", "长风四连",
}

# --- Parse "messages" which is list[str] not list[dict]  (pitfalls §11)
LINE_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?)\] (.*?): (.*)$", re.S)


def parse_messages(messages_raw):
    out = []
    for line in messages_raw:
        if not isinstance(line, str):
            line = str(line)
        m = LINE_RE.match(line)
        if m:
            ts, sender, content = m.group(1), m.group(2), m.group(3)
            out.append({"time": ts, "sender": sender, "content": content})
        else:
            out.append({"time": "", "sender": "", "content": line})
    return out


def extract_first_json_object(text):
    """Find first balanced {...} block. Avoids 'Extra data' from multi-block stdout (pitfalls §11)."""
    idx = text.find("{")
    if idx < 0:
        return None
    depth = 0
    end = -1
    for i, c in enumerate(text[idx:], start=idx):
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end < 0:
        return None
    return text[idx:end]


def fetch_history(name, start):
    cmd = [PYBIN, "-m", "wechat_cli", "history", name, "--start-time", start, "--limit", "200"]
    env = os.environ.copy()
    env["PYTHONPATH"] = SITE
    try:
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True,
                              timeout=60, encoding="utf-8", errors="ignore")
    except subprocess.TimeoutExpired:
        return {"name": name, "error": "timeout"}
    out = proc.stdout
    js = extract_first_json_object(out)
    if not js:
        return {"name": name, "error": "no_json_object", "raw_head": out[:200]}
    try:
        data = json.loads(js)
    except json.JSONDecodeError as e:
        return {"name": name, "error": f"parse: {e}", "raw_head": js[:300]}
    msgs_raw = data.get("messages", [])
    msgs = parse_messages(msgs_raw)
    return {"name": name, "count": len(msgs), "messages": msgs}


def classify_message(content):
    """返回 (命中的类别列表, [(类别, 关键词), ...])"""
    hits = []
    matched_kws = []
    for cat, kws in SCOUT_KEYWORDS.items():
        for kw in kws:
            if kw in content:
                if cat not in hits:
                    hits.append(cat)
                matched_kws.append((cat, kw))
                break  # 一个类别只记一次
    return hits, matched_kws


def is_already_registered_notification(content):
    """是否为已报名活动的例行通知（应排除，不计入 scout_hits）"""
    for kw in ALREADY_REGISTERED_KEYWORDS:
        if kw in content:
            return True
    return False


def main():
    start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    out_path = os.path.join(os.environ.get("TEMP", r"C:\tmp"), "scout_raw.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    results = {}
    scout_hits = []           # 去重后真正可推荐的机会
    excluded_count = 0        # 因已报名活动被排除的命中数

    for username, name in GROUPS.items():
        r = fetch_history(name, start)
        r["username"] = username
        results[username] = r

        if "error" in r:
            print(f"[ERR] {name}: {r['error']}", flush=True)
            continue

        last = r["messages"][-1] if r["messages"] else {}
        print(f"[OK]  {name}: count={r['count']} last={last.get('time','')}", flush=True)

        for msg in r["messages"]:
            content = msg.get("content", "")
            if not content or len(content) < 5:
                continue
            hits, matched_kws = classify_message(content)
            if not hits:
                continue
            if is_already_registered_notification(content):
                excluded_count += 1
                continue
            scout_hits.append({
                "source": name,
                "username": username,
                "time": msg.get("time", ""),
                "sender": msg.get("sender", ""),
                "content": content[:300],  # 截断过长内容
                "categories": hits,
                "matched": [kw for _, kw in matched_kws],
            })

    # 按类别分组输出
    from collections import defaultdict
    by_cat = defaultdict(list)
    for h in scout_hits:
        for cat in h["categories"]:
            by_cat[cat].append(h)

    output = {
        "scan_time": datetime.now().isoformat(),
        "scan_window_start": start,
        "total_groups": len(GROUPS),
        "scout_hits_count": len(scout_hits),
        "excluded_already_registered": excluded_count,
        "by_category": {cat: len(items) for cat, items in by_cat.items()},
        "results": results,
        "scout_hits": scout_hits,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n=== Scout 命中: {len(scout_hits)} 条（已报名排除 {excluded_count} 条）===", flush=True)
    for cat in ["比赛竞赛", "科研与项目", "奖学金与评优", "讲座与活动", "实践项目", "实习就业"]:
        if cat in by_cat:
            print(f"\n--- {cat} ({len(by_cat[cat])} 条) ---", flush=True)
            for h in by_cat[cat][:8]:
                print(f"  [{h['time']}] {h['source']} | {h['sender']} | kws={h['matched']}", flush=True)
                print(f"    {h['content'][:120]}", flush=True)
    print(f"\nSaved to {out_path}", flush=True)


if __name__ == "__main__":
    main()
