"""Extended 7-day digest scan to catch older announcements for tomorrow 2026-06-19."""
import subprocess, json, os, re
from datetime import datetime, timedelta

PYBIN = r"D:\Software\Marvis\MarvisAgent\1.0.1100.219\runtime\python311\python.exe"
SRC = r"C:\Users\xgbc\AppData\Local\Temp\wechat-cli-extract\wechat-cli-main"

# Pull from P0/P1 only for the extended window — keep total scan manageable
GROUPS = {
    "19416880228@chatroom": "工科试验2501入党积极分子",
    "32585334488@chatroom": "26春【晨曦启明】志愿者",
    "91143084472@chatroom": "2501班级群",
    "12121228217@chatroom": "工科试验2501",
    "18078014564@chatroom": "车辆2502班委群",
    "27078175275@chatroom": "示例车队 2026赛季大群",
    "60226711214@chatroom": "底盘车架",
    "32017243574@chatroom": "2026示例车队暑期社会实践",
    "14728426060@chatroom": "史纲第二小组",
    "91339174574@chatroom": "长风四连",
    "18428266328@chatroom": "2025级能源本科生",
    "85866310349@chatroom": "26春-云教室-教务答疑-2群",
    "30807322639@chatroom": "校园 AI 生态×创客松",
    "gh_caca884246ed": "Beiyu能小源",
    "gh_f16d677bb8c1": "北屿大学青志",
    "gh_4db1f4ea5cce": "青禾青年",
    "gh_85d5c0bd629e": "青禾学园",
    "gh_98baa1984e29": "北屿大学求是学院",
    "gh_2dd7552ab054": "北屿大学竺院人",
    "gh_8099d495def9": "北屿大学体育与艺术",
    "gh_8073fd30429d": "北屿大学资助",
    "gh_5f7fc241ccc6": "求是情报站",
    "gh_d7b2a01d31bb": "北屿大学微学工",
    "gh_1d4245f2e96c": "北屿大学图书馆",
    "gh_ace8b2467173": "北屿大学学生会",
}

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
    cmd = [PYBIN, "-m", "wechat_cli", "history", name, "--start-time", start, "--limit", "300"]
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC
    try:
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True,
                              timeout=60, encoding="utf-8", errors="ignore")
    except subprocess.TimeoutExpired:
        return {"name": name, "error": "timeout"}
    out = proc.stdout
    js = extract_first_json_object(out)
    if not js:
        idx = out.find("[")
        if idx >= 0:
            depth = 0
            end = -1
            for i, c in enumerate(out[idx:], start=idx):
                if c == "[":
                    depth += 1
                elif c == "]":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            if end > 0:
                js = out[idx:end]
    if not js:
        return {"name": name, "error": "no_json", "raw_head": out[:200]}
    try:
        data = json.loads(js)
    except json.JSONDecodeError as e:
        return {"name": name, "error": f"parse: {e}", "raw_head": js[:300]}
    msgs_raw = data.get("messages", []) if isinstance(data, dict) else data
    msgs = parse_messages(msgs_raw)
    return {"name": name, "count": len(msgs), "messages": msgs}


def main():
    start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    out_path = os.path.join(os.environ.get("TEMP", r"C:\tmp"), "digest_raw_2026-06-18_7d.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    results = {}
    for username, name in GROUPS.items():
        r = fetch_history(name, start)
        r["username"] = username
        results[username] = r
        if "error" in r:
            print(f"[ERR] {name}: {r['error']}", flush=True)
        else:
            last = r["messages"][-1] if r["messages"] else {}
            print(f"[OK]  {name}: count={r['count']} last={last.get('time','')}", flush=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {out_path}", flush=True)


if __name__ == "__main__":
    main()