"""digest_scan.py — 通过 chatlog (bestK v0.5.2) HTTP API 拉取近 7 天 P0/P1 微信群 + 公众号消息，
落盘到 Loom/raw/social/wechat/exports/<YYYY-MM-DD>/，并桥接为 social_adapter 可 ingest 的
digest_conversations.json。

前置：chatlog server 已在 http://127.0.0.1:5030 启动并完成解密（由 run_wechat_digest.ps1 负责）。
用法（由 run_wechat_digest.ps1 自动调用，亦可手动）：
    python digest_scan.py
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

CHATLOG_BASE = "http://127.0.0.1:5030"
# 可选昵称兜底：当 chatlog 未返回 isSelf 时，若 sender==本昵称则判为本人。
# 设置方式：环境变量 CHATLOG_ME_NAME=你的微信昵称（isSelf 可用时此配置不生效）。
ME_DISPLAY_NAME = os.environ.get("CHATLOG_ME_NAME", "").strip()

# --- P0/P1 微信群 (username, display_name) ---
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

# --- 公众号 (username, display_name) — chatlog v0.5.2 对公众号 total 恒为 0（硬限制，已搁置） ---
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


def _http_get(url):
    """GET url；清空代理避免本地请求被系统 HTTP 代理劫持；返回原始 bytes 解码文本。"""
    proxy = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with opener.open(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except urllib.error.URLError as e:
        raise RuntimeError(f"chatlog HTTP 请求失败: {e}")


def _parse_json_obj(text):
    """chatlog 接口有时返回 {code,data,msg}，有时直接是数组/对象；尽量抽出可解析对象。"""
    text = text.strip()
    if not text:
        return None
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        # 取第一个平衡 {...} 块（应对多块/尾随噪声）
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
        try:
            obj = json.loads(text[idx:end])
        except json.JSONDecodeError:
            return None
    if isinstance(obj, dict) and "data" in obj and not isinstance(obj.get("data"), (list, dict)):
        # {code,data,msg} 且 data 是标量 -> 无数据
        return obj.get("data")
    if isinstance(obj, dict) and "data" in obj:
        return obj["data"]
    return obj


def extract_msg_fields(m):
    """从 chatlog 单条消息对象容错提取 time/sender/content/type/is_self。
    chatlog v0.5.2 字段实测：Time/SenderName/Sender/TalkerName/Talker/Content/Type + isSelf。
    """
    if not isinstance(m, dict):
        return {"time": "", "sender": "", "content": str(m), "type": "", "is_self": None}
    ts = m.get("Time") or m.get("time") or m.get("CreateTime") or ""
    if not isinstance(ts, str):
        ts = str(ts)
    sender = (m.get("SenderName") or m.get("senderName")
              or m.get("Sender") or m.get("sender") or "")
    content = m.get("Content") or m.get("content") or ""
    if not isinstance(content, str):
        content = str(content)
    msg_type = m.get("Type") or m.get("type") or ""
    # 主路径：is_self（chatlog v0.5.2 返回 isSelf 字段）
    is_self = None
    for k in ("isSelf", "IsSelf", "is_self"):
        if k in m:
            v = m[k]
            if isinstance(v, str):
                is_self = v.strip().lower() in ("1", "true", "yes")
            else:
                is_self = bool(v)
            break
    via_nick = False
    # 昵称兜底：is_self 缺失且配置了本人昵称
    if is_self is None and ME_DISPLAY_NAME and sender == ME_DISPLAY_NAME:
        is_self = True
        via_nick = True
    return {"time": ts, "sender": sender, "content": content,
            "type": msg_type, "is_self": is_self, "via_nick": via_nick}


def fetch_talker_messages(talker):
    """分页拉取某 talker 近 7 天消息；返回原始消息列表。"""
    msgs = []
    page = 1
    limit = 200
    while True:
        params = urllib.parse.urlencode({
            "time": "last-7d",
            "talker": talker,
            "format": "json",
            "limit": limit,
            "page": page,
        })
        url = f"{CHATLOG_BASE}/api/v1/chatlog?{params}"
        try:
            text = _http_get(url)
        except RuntimeError as e:
            print(f"  [ERR] {talker}: {e}", flush=True)
            break
        obj = _parse_json_obj(text)
        if obj is None:
            break
        if isinstance(obj, dict):
            batch = obj.get("messages", []) or obj.get("items", []) or []
        elif isinstance(obj, list):
            batch = obj
        else:
            batch = []
        if not batch:
            break
        msgs.extend(batch)
        if len(batch) < limit:
            break
        page += 1
        if page > 10:  # 安全上限：每会话最多 2000 条
            break
    return msgs


def resolve_output_dir():
    """落盘到 D:/Projects/Poyi/Loom/raw/social/wechat/exports/<YYYY-MM-DD>/。
    从本文件位置推导 Poyi 根（Loom/skills/daily/scripts -> parents[4] = D:/Projects/Poyi）；失败回退 $TEMP。
    """
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        here = Path(__file__).resolve()
        poyi = here.parents[4]
        out = poyi / "Loom/raw/social/wechat/exports" / today
    except Exception:
        out = Path(os.environ.get("TEMP", "/tmp")) / "social_wechat_exports" / today
    out.mkdir(parents=True, exist_ok=True)
    return out, today


def to_conversations(results):
    """把 {talker:{name,count,messages}} 重塑为 social_adapter 可 ingest 的对话列表：
        [ {talker, name, count, messages:[{time,sender,content,type,is_self}, ...]}, ... ]
    social_adapter 从每条 message 抽 content(=我们的 content) 与 time(=我们的 time 字符串)，
    按目标日期过滤后产出 _insights.json。count=0 的会话（含公众号）无 messages，自动跳过。
    """
    convs = []
    for talker, info in results.items():
        msgs = info.get("messages") or []
        if not msgs:
            continue
        convs.append({
            "talker": talker,
            "name": info.get("name", talker),
            "count": info.get("count", len(msgs)),
            "messages": msgs,
        })
    return convs


def main():
    out_dir, today = resolve_output_dir()
    results = {}
    self_isSelf = 0
    self_nick = 0
    self_unknown = 0
    total_msgs = 0
    for talker, name in GROUPS.items():
        msgs_raw = fetch_talker_messages(talker)
        parsed = [extract_msg_fields(m) for m in msgs_raw]
        total_msgs += len(parsed)
        for p in parsed:
            if p["is_self"] is True:
                if p.get("via_nick"):
                    self_nick += 1
                else:
                    self_isSelf += 1
            elif p["is_self"] is None:
                self_unknown += 1
        results[talker] = {"name": name, "count": len(parsed), "messages": parsed}
        if not parsed:
            print(f"[skip] {name}: 0 条", flush=True)
        else:
            print(f"[OK]  {name}: {len(parsed)} 条", flush=True)

    raw_path = out_dir / "digest_raw.json"
    conv_path = out_dir / "digest_conversations.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    convs = to_conversations(results)
    with open(conv_path, "w", encoding="utf-8") as f:
        json.dump(convs, f, ensure_ascii=False, indent=2)
    print(f"\n落盘位置: {out_dir}", flush=True)
    print(f"  raw   : {raw_path}", flush=True)
    print(f"  bridge: {conv_path}  ({len(convs)} 个有内容的会话，已可被 extract_insights --source social 识别)", flush=True)
    print(f"\n本人识别: 消息总数={total_msgs}, 本人={self_isSelf}(isSelf) +{self_nick}(昵称兜底), 未知={self_unknown}", flush=True)
    if self_unknown == total_msgs and total_msgs > 0:
        print("  ⚠️ 全部消息 is_self 缺失：chatlog 未透传 isSelf，建议设置 CHATLOG_ME_NAME 或升级 chatlog。", flush=True)


if __name__ == "__main__":
    main()
