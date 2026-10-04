"""Antigravity 导出器 —— 从 ~/.gemini/antigravity/conversations/*.db 解析 protobuf BLOB"""

import re
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .base import BaseExporter

# step_type 映射
_STEP_TYPE_USER_INPUT = 14
_STEP_TYPE_TOOL_CALL = 15
_STEP_TYPE_TOOL_RESULT = {8, 9}
_STEP_TYPE_THINKING = 98
_STEP_TYPE_SEARCH_WEB = 7
_STEP_TYPE_GENERATION = 23
_STEP_TYPE_PLANNING = 5
_STEP_TYPE_OTHER_TOOL = {17, 21, 33, 101, 132}


def _extract_text_from_blob(blob: bytes, min_len: int = 4) -> list:
    """从 protobuf / 二进制 BLOB 中提取可读文本。"""
    decoded = blob.decode("utf-8", errors="replace")
    pattern = re.compile(
        r"[\x20-\x7e\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u2000-\u206f"
        r"\u3400-\u4dbf\uf900-\ufaff]{" + str(min_len) + r",}"
    )
    matches = pattern.findall(decoded)

    def _is_noise(t: str) -> bool:
        # UUID / hex hash
        if re.match(r"^[0-9a-fA-F\-]{20,}$", t):
            return True
        # ISO date-like numbers
        if re.match(r"^[\-0-9]{10,}H[A-Za-z\s]*$", t):
            return True
        # sessionID 等 protobuf 字段名
        if t in ("sessionID", "chatId", "conversationId", "AbsolutePath",
                 "DirectoryPath", "SearchPath", "IsRegex", "EndLine", "StartLine",
                 "toolAction", "toolActionId", "toolSummary", "messageId",
                 "authorId", "authorName", "type", "version", "message",
                 "content", "text", "role", "title", "Query"):
            return True
        # protobuf 字段引用 (下划线开头 + 字母数字)
        if re.match(r"^_[a-zA-Z0-9]{15,}$", t):
            return True
        # 纯 ASCII 长 token（无空格无 CJK）
        if re.match(r"^[a-zA-Z0-9\-\$\"\+]{25,}$", t) and " " not in t:
            return True
        return False

    cleaned = [m for m in matches if not _is_noise(m)]

    def _sort_key(t: str) -> tuple:
        has_cjk = bool(re.search(r"[\u4e00-\u9fff]", t))
        return (1 if has_cjk else 0, len(t))

    cleaned.sort(key=_sort_key, reverse=True)
    return cleaned


def _extract_json_from_blob(blob: bytes) -> list:
    """从 BLOB 中提取 JSON 对象字符串。"""
    decoded = blob.decode("utf-8", errors="replace")
    pattern = re.compile(
        r"\{(?:[^{}]|\{[^{}]*\})*"
        r'"(?:DirectoryPath|AbsolutePath|Query|SearchPath|IsRegex|'
        r"toolAction|toolSummary|toolActionId|message|content|text|"
        r'role|chatId|sessionId|conversationId|title|EndLine|StartLine)"'
        r"(?:[^{}]|\{[^{}]*\})*\}"
    )
    return pattern.findall(decoded)


class AntigravityExporter(BaseExporter):
    name = "antigravity"
    display_name = "Antigravity (Gemini Code Assist)"

    def __init__(self, looM_root: Path):
        super().__init__(looM_root)
        self.conv_dir = Path.home() / ".gemini" / "antigravity" / "conversations"

    def check_available(self) -> bool:
        return self.conv_dir.exists()

    def extract(self) -> List[Dict[str, Any]]:
        if not self.check_available():
            return []

        db_files = sorted(self.conv_dir.glob("*.db"))
        if not db_files:
            return []

        all_results = []

        for db_path in db_files:
            cascade_id = db_path.stem
            try:
                conn = sqlite3.connect(str(db_path))
                conn.row_factory = sqlite3.Row
            except Exception as e:
                print(f"  [Antigravity] Cannot open {db_path.name}: {e}")
                continue

            try:
                meta_rows = conn.execute("SELECT * FROM trajectory_meta").fetchall()
            except Exception:
                meta_rows = []

            if not meta_rows:
                conn.close()
                continue

            for meta in meta_rows:
                trajectory_id = meta["trajectory_id"]

                try:
                    steps = conn.execute(
                        "SELECT idx, step_type, status, step_payload FROM steps ORDER BY idx"
                    ).fetchall()
                except Exception:
                    steps = []

                if not steps:
                    continue

                messages, tool_count, conv_text = self._process_steps(steps)

                title = self._build_title(conv_text)

                output = {
                    "agent": "antigravity",
                    "session_id": trajectory_id,
                    "cascade_id": cascade_id,
                    "title": title,
                    "model": "Gemini (Antigravity)",
                    "trajectory_type": meta["trajectory_type"],
                    "source": meta["source"],
                    # protobuf payload 抽不出逐条消息时间，用 db 文件 mtime 作会话级兜底，
                    # 供 aggregate 的 bucket_by_date 归档（否则整源消息会被静默丢弃）
                    "fallback_time": datetime.fromtimestamp(
                        db_path.stat().st_mtime
                    ).isoformat(),
                    "messages": messages,
                    "stats": {
                        "message_count": len(messages),
                        "tool_call_count": tool_count,
                        "total_steps": len(steps),
                    },
                }

                all_results.append(output)
                print(
                    f"  [Antigravity] {cascade_id}: {len(steps)} steps, "
                    f"{len(messages)} msgs, {tool_count} tools"
                )

            conn.close()

        return all_results

    def _process_steps(self, steps) -> tuple:
        messages = []
        tool_count = 0
        conv_text = []

        def _fallback_text(texts_list: list, max_items: int = 3) -> str:
            """拼接文本片段作为 fallback content"""
            return " ".join(texts_list[:max_items])

        for step in steps:
            idx = step["idx"]
            stype = step["step_type"]
            blob = step["step_payload"]

            if blob is None:
                continue

            texts = _extract_text_from_blob(blob, min_len=4)
            jsons = _extract_json_from_blob(blob)

            # === 用户输入 ===
            if stype == _STEP_TYPE_USER_INPUT:
                user_texts = [t for t in texts if len(t) > 5]
                content = ""
                for t in user_texts:
                    cleaned = t.strip("\"").strip("'").strip()
                    if len(cleaned) > 3:
                        content = cleaned
                        break
                if not content and texts:
                    content = texts[0].strip("\"").strip("'").strip()
                if not content:
                    content = _fallback_text(texts)
                if content:
                    messages.append({
                        "role": "user",
                        "content": content,
                        "step_index": idx,
                        "step_type": stype,
                    })
                    conv_text.append(content)

            # === 工具调用 ===
            elif stype == _STEP_TYPE_TOOL_CALL:
                tool_count += 1
                msg = {"role": "tool", "step_index": idx, "step_type": stype}
                if jsons:
                    try:
                        info = json.loads(jsons[0])
                        msg["tool_action"] = info.get("toolAction", "")
                        msg["tool_summary"] = info.get("toolSummary", "")
                        msg["tool_params"] = {
                            k: v for k, v in info.items()
                            if k not in ("toolAction", "toolSummary")
                        }
                        # content = tool_summary 优先，降级到 tool_action
                        msg["content"] = info.get("toolSummary") or info.get("toolAction") or ""
                    except json.JSONDecodeError:
                        msg["content"] = _fallback_text(texts)
                else:
                    msg["content"] = _fallback_text(texts)
                messages.append(msg)

            # === 网络搜索 ===
            elif stype == _STEP_TYPE_SEARCH_WEB:
                tool_count += 1
                msg = {
                    "role": "tool", "tool_name": "search_web",
                    "step_index": idx, "step_type": stype,
                }
                if jsons:
                    try:
                        info = json.loads(jsons[0])
                        msg["query"] = info.get("Query", "")
                        msg["tool_summary"] = info.get("toolSummary", "")
                        msg["content"] = info.get("Query") or info.get("toolSummary") or ""
                    except json.JSONDecodeError:
                        msg["content"] = _fallback_text(texts)
                else:
                    msg["content"] = _fallback_text(texts)
                messages.append(msg)

            # === 工具结果 ===
            elif stype in _STEP_TYPE_TOOL_RESULT:
                msg = {"role": "tool_result", "step_index": idx, "step_type": stype}
                if jsons:
                    try:
                        info = json.loads(jsons[0])
                        msg["tool_summary"] = info.get("toolSummary", "")
                        msg["tool_action"] = info.get("toolAction", "")
                        msg["content_preview"] = info.get("message") or info.get("text") or ""
                    except json.JSONDecodeError:
                        msg["content_preview"] = _fallback_text(texts)
                else:
                    msg["content_preview"] = _fallback_text(texts)
                # content = content_preview || text fragments
                msg["content"] = (msg.get("content_preview") or _fallback_text(texts))
                messages.append(msg)

            # === 助手生成 ===
            elif stype == _STEP_TYPE_GENERATION:
                # 用更宽松的阈值：CJK >= 8 char 或英文 >= 15 char
                meaningful = [
                    t for t in texts
                    if (re.search(r"[\u4e00-\u9fff]", t) and len(t) >= 8)
                    or (not re.search(r"[\u4e00-\u9fff]", t) and len(t) >= 15)
                ]
                content_text = " ".join(meaningful[:10]) if meaningful else _fallback_text(texts, 5)
                if content_text.strip():
                    messages.append({
                        "role": "assistant",
                        "content": content_text[:4000],
                        "step_index": idx,
                        "step_type": stype,
                    })

            # === 思考 ===
            elif stype == _STEP_TYPE_THINKING:
                content_text = _fallback_text(texts, 5)
                if content_text.strip():
                    messages.append({
                        "role": "system",
                        "content": content_text[:2000],
                        "step_index": idx,
                        "step_type": stype,
                    })

            # === 规划 ===
            elif stype == _STEP_TYPE_PLANNING:
                content_text = _fallback_text(texts, 5)
                if content_text.strip():
                    messages.append({
                        "role": "system",
                        "content": content_text[:2000],
                        "step_index": idx,
                        "step_type": stype,
                    })

            # === 其他工具 ===
            elif stype in _STEP_TYPE_OTHER_TOOL:
                tool_count += 1
                msg = {"role": "tool", "step_index": idx, "step_type": stype}
                if jsons:
                    try:
                        info = json.loads(jsons[0])
                        msg["tool_action"] = info.get("toolAction", "")
                        msg["tool_summary"] = info.get("toolSummary", "")
                        msg["content"] = info.get("toolSummary") or info.get("toolAction") or ""
                    except json.JSONDecodeError:
                        msg["content"] = _fallback_text(texts)
                else:
                    msg["content"] = _fallback_text(texts)
                messages.append(msg)

            # === 未知类型 ===
            else:
                content_text = _fallback_text(texts, 5)
                if content_text.strip():
                    messages.append({
                        "role": "unknown",
                        "content": content_text[:1000],
                        "step_index": idx,
                        "step_type": stype,
                    })

        return messages, tool_count, conv_text

    @staticmethod
    def _build_title(conv_text: list) -> str:
        if not conv_text:
            return ""
        raw_title = conv_text[0].strip("\"").strip("'")
        raw_title = re.sub(r"<[^>]+>", "", raw_title)
        raw_title = re.sub(r"^[a-zA-Z0-9\-\$]+", "", raw_title).strip()
        return raw_title[:60].replace("\n", " ").strip()
