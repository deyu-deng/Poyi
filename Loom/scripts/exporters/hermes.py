"""Hermes 导出器 —— 从 state.db SQLite 直接读取"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .base import BaseExporter


class HermesExporter(BaseExporter):
    name = "hermes"
    display_name = "Hermes (本地终端 AI)"

    def __init__(self, looM_root: Path):
        super().__init__(looM_root)
        self.db_path = Path.home() / ".hermes" / "state.db"

    def check_available(self) -> bool:
        return self.db_path.exists()

    def extract(self) -> List[Dict[str, Any]]:
        if not self.check_available():
            return []

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        sessions = conn.execute(
            "SELECT * FROM sessions ORDER BY started_at"
        ).fetchall()
        results = []

        for sess in sessions:
            sess_id = sess["id"]
            msgs = conn.execute(
                "SELECT * FROM messages WHERE session_id=? AND active=1 "
                "ORDER BY timestamp",
                (sess_id,),
            ).fetchall()

            output = {
                "agent": "hermes",
                "session_id": sess_id,
                "title": sess["title"] or "",
                "source": sess["source"],
                "model": sess["model"] or "unknown",
                "started": datetime.fromtimestamp(sess["started_at"]).isoformat(),
                "ended": (
                    datetime.fromtimestamp(sess["ended_at"]).isoformat()
                    if sess["ended_at"] else None
                ),
                "messages": [],
                "stats": {
                    "message_count": sess["message_count"] or 0,
                    "tool_call_count": sess["tool_call_count"] or 0,
                    "input_tokens": sess["input_tokens"] or 0,
                    "output_tokens": sess["output_tokens"] or 0,
                },
            }

            for m in msgs:
                output["messages"].append({
                    "role": m["role"],
                    "content": m["content"] or "",
                    "time": datetime.fromtimestamp(m["timestamp"]).isoformat(),
                    "tool_name": m["tool_name"],
                    "tool_call_id": m["tool_call_id"],
                })

            results.append(output)
            print(f"  [Hermes] {sess['title'][:40]}: {len(msgs)} msgs")

        conn.close()
        return results
