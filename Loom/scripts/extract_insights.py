#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_insights.py — 全量确定性洞察抽取框架（基础层组件三）

读取各数据源 `Loom/raw/<source>/` 下的原始捕获，逐条解析消息，分类为
decision / preference / project-mention / learning-mention / fact 等，
带原文片段 + 检测到的项目/领域，输出 `<source>/digested/<date>/_insights.json`。

设计要点：
- 确定性代码、无 LLM、无采样（有全量即用全文）。
- 源无关的通用分类/检测逻辑 + 源相关的「适配器」(adapter)：
  每个源原始格式不同（chatlog=会话 JSON、social=解密微信/钉钉、lifelog=转写稿…），
  适配器负责把原始数据归一为统一的 (meta, messages, machine, full_coverage) 会话流，
  其余抽取/分类完全共享。新增一个源 = 注册一个适配器，不改核心流程。
- 调度器 (dispatcher) 读 `data-sources.json`，按注册表遍历各源、各日期。
- 本步骤只产出"结构化洞察流"，仔细的逐条语义分析交给阶段二的 LLM 编辑引擎。
- 不修改任何笔记/项目文档，纯产出。

用法：
    python Loom/scripts/extract_insights.py [--source <id>] [--date YYYY-MM-DD] [--force]
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

POYI = Path("D:/Projects/Poyi")
RAW_ROOT = POYI / "Loom/raw"
DATA_SOURCES = RAW_ROOT / "data-sources.json"
INVENTORY = POYI / "Loom/meta/inventory.json"
OUT_SUFFIX = "_insights.json"
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# ---------- 分类正则（确定性预筛；精修交给 LLM 阶段）----------
LEARNING = re.compile(
    r"怎么学|学(一?下|什么|习|好)|教程|入门|理解|复习|笔记|搞懂|弄懂|掌握|基础|"
    r"\blearn\b|\btutorial\b|how to (use|learn|build|make|do)|知识点",
    re.I,
)
PREFERENCE = re.compile(
    r"我喜欢|我习惯|偏好|以后(都)?用|不用\s*\w+|更喜欢|习惯用|就用\s*\w+|倾向于|爱用|弃用|改用|一直用",
    re.I,
)
DECISION = re.compile(
    r"决定|确定(用|做|要)?|就(用|选|做)|选定|不(做|用)了|方案(定|选|确)|采用|敲定|定下来|用\s*\w+\s*吧",
    re.I,
)
FACT_MARK = re.compile(
    r"结论|原理|公式|API|配置|路径|账户|关键在于|本质是|等价于|"
    r"也就是说|总结一下|记住|固定|规范是|约定",
    re.I,
)

# ---------- 领域别名 -> 规范领域名 ----------
DOMAIN_ALIASES = {
    "人工智能": "人工智能 AI", "ai": "人工智能 AI", "机器学习": "人工智能 AI",
    "深度学习": "人工智能 AI", "大模型": "人工智能 AI", "llm": "人工智能 AI",
    "神经网络": "人工智能 AI", "提示工程": "人工智能 AI", "prompt": "人工智能 AI",
    "数学": "数学 Math", "微积分": "数学 Math", "线性代数": "数学 Math",
    "微分方程": "数学 Math", "高数": "数学 Math", "math": "数学 Math",
    "物理": "物理 Physics", "大学物理": "物理 Physics", "力学": "物理 Physics",
    "电磁": "物理 Physics", "physics": "物理 Physics",
    "工具": "工具 Tools", "illustrator": "工具 Tools", "premiere": "工具 Tools",
    "solidworks": "工具 Tools", "creo": "工具 Tools", "obsidian": "工具 Tools",
    "建模": "工具 Tools", "设计": "工具 Tools",
    "工程": "工程 Engineer", "工程图学": "工程 Engineer", "车辆": "工程 Engineer",
    "能源": "工程 Engineer", "机械": "工程 Engineer", "engineer": "工程 Engineer",
    "计算机": "计算机 Computer", "编程": "计算机 Computer", "代码": "计算机 Computer",
    "python": "计算机 Computer", "算法": "计算机 Computer", "数据结构": "计算机 Computer",
    "语言": "语言 Language", "英语": "语言 Language", "日语": "语言 Language",
    "单词": "语言 Language", "english": "语言 Language",
}

_NOISE_TITLES = re.compile(
    r"定时任务执行|message-digest|info-radar|opportunity-scout|自动采集同步", re.I
)

# 通用词项目名：系统自身等 ubiquitous 词，作子串匹配会全量误标，排除
EXCLUDE_PROJECTS = {"poyi"}


def load_inventory():
    if INVENTORY.exists():
        d = json.loads(INVENTORY.read_text(encoding="utf-8"))
        projects = [re.sub(r"[^a-z0-9]", "", p.lower()) for p in d.get("projects", [])]
        # 去掉过短易误伤的项目名（如 kit）与通用词（如 poyi）
        projects = [p for p in projects if len(p) >= 4 and p not in EXCLUDE_PROJECTS]
        return projects
    return []


PROJECTS_NORM = load_inventory()


def detect(text: str):
    """返回 (project_or_None, domain_or_None)。"""
    low = text.lower()
    norm = re.sub(r"[^a-z0-9]", "", low)
    proj = None
    for p in PROJECTS_NORM:
        if p and p in norm:
            proj = p
            break
    dom = None
    for alias, canon in DOMAIN_ALIASES.items():
        if alias.lower() in low:
            dom = canon
            break
    return proj, dom


def classify(content: str, is_user: bool):
    """返回该消息应产生的洞察类型列表（可能多个）。"""
    out = []
    if LEARNING.search(content):
        out.append("learning-mention")
    if PREFERENCE.search(content):
        out.append("preference")
    if DECISION.search(content):
        out.append("decision")
    proj, _ = detect(content)
    if proj:
        out.append("project-mention")
    # fact：要求耐久标记，且不是纯提问
    if FACT_MARK.search(content) and "?" not in content and "？" not in content:
        out.append("fact")
    return out


def snippet(text: str, n: int = 600) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:n]


def source_dir(conf: dict) -> Path:
    """source 配置里的 folder 相对 POYI 根，返回绝对路径。"""
    return POYI / conf["folder"]


# =========================================================================
# 适配器：把各源原始数据归一为统一会话流
#   每个适配器返回 [(meta_dict, messages_list, machine, full_coverage), ...]
#   meta_dict 至少含 session_id / title / agent；messages 为 [{role, content}, ...]
# =========================================================================

def chatlog_adapter(conf: dict, date: str):
    """AI 平台聊天：Mac 采样 + Win 全量（逻辑与重构前 load_sessions 一致）。"""
    folder = source_dir(conf)
    digested = folder / "digested"
    raw = folder / "raw"
    sessions = []

    # Mac：_sessions_extract.json（采样）+ 可能 _full 伴侣
    mac_ext = digested / date / "_sessions_extract.json"
    mac_full = digested / date / "_sessions_extract_full.json"
    if mac_ext.exists():
        recs = json.loads(mac_ext.read_text(encoding="utf-8"))
        full_map = {}
        if mac_full.exists():
            for r in json.loads(mac_full.read_text(encoding="utf-8")):
                full_map[r.get("session_id")] = r.get("messages", [])
        for r in recs:
            sid = r.get("session_id")
            if sid in full_map and full_map[sid]:
                sessions.append((r, full_map[sid], "mac", True))
            else:
                sessions.append((r, pseudo_messages(r), "mac", False))

    # Win：raw/{date}/*-win_*.json（全量消息）
    raw_dir = raw / date
    if raw_dir.exists():
        for fp in sorted(raw_dir.glob("*-win_*.json")):
            try:
                r = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                continue
            msgs = r.get("messages", [])
            sessions.append((r, msgs, "win", bool(msgs)))

    return sessions


def chatlog_dates(conf: dict):
    """chatlog 的日期来自 digested/ 与 raw/ 下的日期目录并集。"""
    folder = source_dir(conf)
    dates = set()
    for base in (folder / "digested", folder / "raw"):
        if base.exists():
            for d in base.iterdir():
                if d.is_dir() and DATE_RE.match(d.name):
                    dates.add(d.name)
    return dates


def pseudo_messages(rec: dict):
    """Mac 采样记录 -> 伪消息列表（仅 user 样本）。"""
    msgs = []
    if rec.get("first_user_msg"):
        msgs.append({"role": "user", "content": rec["first_user_msg"]})
    for s in rec.get("user_samples", []) or []:
        if s and s not in (msgs[0]["content"] if msgs else ""):
            msgs.append({"role": "user", "content": s})
    return msgs


def _wechat_role_is_me(msg: dict) -> bool:
    """微信视角：优先 is_self（chatlog bestK v0.5.2 的 /api/v1/chatlog 每条消息返回 isSelf
    字段，前端据此左右对齐本人气泡），命中即本人（role=user）；其次兼容旧 is_sender 等字段；
    都缺失时保守判 False（他人/other），不再把 sender 昵称误当本人标志。
    """
    # 主路径：is_self（来自 chatlog 的 isSelf / digest_scan 透传）
    for k in ("is_self", "IsSelf", "isSelf"):
        if k in msg:
            v = msg[k]
            if isinstance(v, str):
                return v.strip().lower() in ("1", "true", "yes", "me")
            return bool(v)
    # 兼容旧字段（理论上 chatlog v0.5.2 不会走到这里）
    for k in ("is_sender", "IsSender", "from_me"):
        if k in msg:
            v = msg[k]
            if isinstance(v, str):
                return v.strip() in ("1", "true", "True", "me")
            return bool(v)
    return False


def _msg_text(msg: dict) -> str:
    if isinstance(msg, str):
        return msg
    if not isinstance(msg, dict):
        return ""
    for k in ("content", "Content", "text", "msg", "content_str"):
        if k in msg and isinstance(msg[k], str):
            return msg[k]
    return ""


def _msg_date(msg: dict, fallback: str) -> str:
    """从消息时间戳推导日期（兼容秒/毫秒）。"""
    ts = None
    for k in ("timestamp", "Timestamp", "create_time", "time", "datetime"):
        if k in msg:
            ts = msg[k]
            break
    if ts is None:
        return fallback
    try:
        ts = float(ts)
    except (TypeError, ValueError):
        # 已是日期字符串？
        if isinstance(ts, str) and DATE_RE.match(ts[:10]):
            return ts[:10]
        return fallback
    # 微信/钉钉多为毫秒
    if ts > 1e12:
        ts /= 1000.0
    try:
        import datetime as _dt
        return _dt.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
    except Exception:
        return fallback


def social_adapter(conf: dict, date: str):
    """微信/钉钉等社交媒体：解密导出（db/decrypted json）。
    支持常见解密导出形态：
      - {"messages":[{role/content|is_sender/timestamp/talker...}]}
      - [{"talker"/"conversation":..., "messages":[...]}]（多会话）
    目前为 best-effort 解析，待真实样本校验；任一文件失败不影响其他文件。
    """
    folder = source_dir(conf)
    sessions = []
    for sub in ("wechat", "dingtalk"):
        sdir = folder / sub
        if not sdir.exists():
            continue
        for fp in sorted(sdir.rglob("*.json")):
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                continue
            convs = []
            if isinstance(data, list):
                convs = data
            elif isinstance(data, dict):
                if "messages" in data:
                    convs = [data]
                elif "conversations" in data:
                    convs = data["conversations"]
            for conv in convs:
                if not isinstance(conv, dict):
                    continue
                msgs = conv.get("messages", [])
                if not isinstance(msgs, list):
                    continue
                talker = conv.get("talker") or conv.get("talker_name") \
                    or conv.get("conversation") or conv.get("name") or "unknown"
                sid = conv.get("session_id") or talker
                out_msgs = []
                for m in msgs:
                    if not isinstance(m, (dict, str)):
                        continue
                    content = _msg_text(m)
                    if not content or len(content) < 4:
                        continue
                    is_me = _wechat_role_is_me(m) if isinstance(m, dict) else False
                    role = "user" if is_me else "other"
                    if _msg_date(m, date) != date:
                        continue
                    out_msgs.append({"role": role, "content": content})
                if out_msgs:
                    meta = {"session_id": sid, "title": talker, "agent": sub}
                    sessions.append((meta, out_msgs, "win", True))
    return sessions


def social_dates(conf: dict):
    """social 原始未按月目录切分，需扫描导出文件从消息时间戳推导日期。"""
    folder = source_dir(conf)
    dates = set()
    for sub in ("wechat", "dingtalk"):
        sdir = folder / sub
        if not sdir.exists():
            continue
        for fp in sorted(sdir.rglob("*.json")):
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                continue
            convs = data if isinstance(data, list) else data.get("conversations", []) \
                if isinstance(data, dict) and "conversations" in data else \
                ([data] if isinstance(data, dict) and "messages" in data else [])
            for conv in convs:
                if not isinstance(conv, dict):
                    continue
                for m in conv.get("messages", []) or []:
                    if isinstance(m, dict):
                        d = _msg_date(m, "")
                        if d:
                            dates.add(d)
    return dates


# 注册表：source id -> (adapter, dates_fn)
ADAPTERS = {
    "chatlog": (chatlog_adapter, chatlog_dates),
    "social": (social_adapter, social_dates),
}


# =========================================================================
# 通用抽取（源无关）
# =========================================================================

def process_date(conf: dict, date: str, force: bool) -> dict:
    folder = source_dir(conf)
    out_dir = folder / "digested" / date
    out_path = out_dir / OUT_SUFFIX

    if out_path.exists() and not force:
        return {"date": date, "source": conf["id"], "skipped": True}

    adapter, _dates_fn = ADAPTERS.get(conf["id"], (None, None))
    if adapter is None:
        return {"date": date, "source": conf["id"], "skipped": True, "reason": "no_adapter"}

    sessions = adapter(conf, date)
    insights = []
    for r, msgs, machine, fc in sessions:
        sid = r.get("session_id")
        title = r.get("title") or ""
        agent = r.get("agent") or conf["id"]
        noise = bool(_NOISE_TITLES.search(title))
        for m in msgs:
            if not isinstance(m, dict):
                continue
            content = m.get("content") or ""
            if not content or len(content) < 4:
                continue
            role = m.get("role", "user")
            is_user = role.lower().startswith("u") or role.lower() == "me"
            types = classify(content, is_user)
            proj, dom = detect(content)
            for t in types:
                conf_level = "high" if (t in ("learning-mention", "preference", "decision")) else "low"
                insights.append({
                    "date": date,
                    "source": conf["id"],
                    "agent": agent,
                    "machine": machine,
                    "session_id": sid,
                    "session_title": title,
                    "noise": noise,
                    "insight_type": t,
                    "role": role,
                    "text": snippet(content),
                    "confidence": conf_level,
                    "full_coverage": fc,
                    "detected": {"project": proj, "domain": dom},
                })

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(insights, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = Counter(i["insight_type"] for i in insights)
    return {
        "date": date,
        "source": conf["id"],
        "sessions": len(sessions),
        "insights": len(insights),
        "full_coverage_sessions": sum(1 for *_, fc in sessions if fc),
        "counts": dict(counts),
    }


def load_sources():
    if not DATA_SOURCES.exists():
        return []
    d = json.loads(DATA_SOURCES.read_text(encoding="utf-8"))
    return d.get("sources", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="仅处理指定 source id（默认全部已注册适配器）")
    ap.add_argument("--date", help="仅处理指定日期 YYYY-MM-DD")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的 _insights.json")
    args = ap.parse_args()

    sources = load_sources()

    total = 0
    full_total = 0
    type_total = Counter()
    skipped = 0
    no_adapter = 0
    for conf in sources:
        sid = conf["id"]
        if args.source and sid != args.source:
            continue
        if sid not in ADAPTERS:
            no_adapter += 1
            print(f"[skip] {sid}: 无适配器（未实现采集/解析）")
            continue
        _adapter, dates_fn = ADAPTERS[sid]
        if args.date:
            dates = [args.date]
        else:
            dates = sorted(dates_fn(conf))
        if not dates:
            print(f"[skip] {sid}: 无可用日期（raw/digested 均无数据）")
            continue
        for date in dates:
            res = process_date(conf, date, args.force)
            if res.get("skipped"):
                skipped += 1
                if res.get("reason") == "no_adapter":
                    continue
                print(f"[skip] {sid}/{date}: 已存在（--force 可覆盖）")
                continue
            total += res["insights"]
            full_total += res["full_coverage_sessions"]
            type_total.update(res["counts"])
            print(f"[ok] {sid}/{date}: sessions={res['sessions']} "
                  f"(full={res['full_coverage_sessions']}) insights={res['insights']} "
                  f"{res['counts']}")

    print(f"\n合计: insights={total}, 全量覆盖会话={full_total}, 类型={dict(type_total)} "
          f"(跳过已存在={skipped}, 无适配器源={no_adapter})")


if __name__ == "__main__":
    main()
