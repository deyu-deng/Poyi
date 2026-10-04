"""WorkBuddy 导出器 —— 从 ~/.workbuddy/projects/<project>/*.jsonl 读取。

每个 jsonl 文件即一个会话。相比其他源，WorkBuddy 的 transcript 额外包含：
  - reasoning 事件（AI 思考过程，等价于退役 Hermes 的 reasoning_content）
  - function_call / function_call_result（工具调用链路）

Mac-only：Win 端无 WorkBuddy 本地数据，check_available 返回 False。
逻辑由旧 export_workbuddy.py 平移而来，规范化 schema 与其他源对齐。
"""

import json
import glob
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

from .base import BaseExporter


def _extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, dict):
                t = p.get("text") or p.get("input") or ""
                if t:
                    parts.append(t)
        return "\n".join(parts)
    return ""


class WorkbuddyExporter(BaseExporter):
    name = "workbuddy"
    display_name = "WorkBuddy (本机 CLI 助手)"

    def __init__(self, looM_root: Path):
        super().__init__(looM_root)
        if self.is_mac:
            self.projects_dir = Path.home() / ".workbuddy" / "projects"
        else:
            self.projects_dir = None

    def check_available(self) -> bool:
        if not self.is_mac:
            return False
        return bool(self.projects_dir) and self.projects_dir.exists()

    def extract(self) -> List[Dict[str, Any]]:
        if not self.check_available():
            return []

        # 同 conv 可能在多个 project 目录出现，靠编排层按 (agent, session_id) 去重保留最多
        results = []
        for jf in sorted(glob.glob(str(self.projects_dir / "*" / "*.jsonl"))):
            sess = self._export_file(os.path.basename(jf), jf)
            if sess:
                results.append(sess)

        print(f"  [WorkBuddy] {len(results)} 个会话")
        return results

    def _export_file(self, fname: str, path: str) -> Dict[str, Any]:
        conv_id = os.path.splitext(fname)[0]
        try:
            with open(path, encoding="utf-8") as f:
                events = [json.loads(line) for line in f if line.strip()]
        except (OSError, json.JSONDecodeError):
            return None
        if not events:
            return None

        # reasoning 按 messageId 配对到后续 assistant 消息
        reasoning_by_msg: Dict[str, str] = {}
        title = None
        models = set()
        for ev in events:
            t = ev.get("type")
            pd = ev.get("providerData") or {}
            if t == "reasoning":
                mid = pd.get("messageId")
                chunks = []
                for p in ev.get("rawContent") or []:
                    if isinstance(p, dict) and p.get("type") == "reasoning_text":
                        chunks.append(p.get("text", ""))
                if mid:
                    reasoning_by_msg[mid] = reasoning_by_msg.get(mid, "") + "\n".join(chunks)
                if pd.get("model"):
                    models.add(pd["model"])
            elif t == "message":
                if pd.get("model"):
                    models.add(pd["model"])
            elif t == "ai-title":
                title = ev.get("title") or ev.get("data") or title

        messages = []
        for ev in events:
            if ev.get("type") != "message":
                continue
            role = ev.get("role")
            if role not in ("user", "assistant"):
                continue
            pd = ev.get("providerData") or {}
            mid = pd.get("messageId")
            ts = ev.get("timestamp")
            time = None
            if ts:
                try:
                    time = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat()
                except Exception:
                    time = None
            messages.append({
                "role": role,
                "content": _extract_text(ev.get("content")),
                "time": time,
                "message_seq": ev.get("id"),
                "event_seq_anchor": None,
                "tool_call_id": None,
                "response_id": mid,
                "tool_name": None,
                "reasoning_content": (reasoning_by_msg.get(mid) or None),
            })

        if not messages:
            return None

        head = messages[0]["content"][:60].replace("\n", " ").strip() or "workbuddy-session"
        return {
            "agent": "workbuddy",
            "session_id": conv_id,
            "title": title or head,
            "model": sorted(models) or ["unknown"],
            "source": path,
            "messages": messages,
            "stats": {
                "message_count": len(messages),
                "tool_call_count": sum(1 for e in events if e.get("type") == "function_call"),
                "models": {m: {"calls": 0, "thinking_tokens": 0, "total_tokens": 0} for m in sorted(models)},
                "total_tokens": 0,
            },
        }
