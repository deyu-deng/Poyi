"""Marvis 导出器 —— 从 data.db SQLite 读取"""

import sqlite3
import glob
import os
from pathlib import Path
from typing import List, Dict, Any

from .base import BaseExporter


class MarvisExporter(BaseExporter):
    name = "marvis"
    display_name = "Marvis (桌面 AI 助手)"

    def __init__(self, looM_root: Path):
        super().__init__(looM_root)
        if self.is_mac:
            # Mac: ~/Library/Application Support/com.tencent.mac.marvis/MarvisData/User/<id>/database/data.db
            base = Path.home() / "Library" / "Application Support" / "com.tencent.mac.marvis"
            self.db_glob = str(base / "MarvisData" / "User" / "*" / "database" / "data.db")
        else:
            # Windows: %APPDATA%/Tencent/Marvis/User/<id>/database/data.db
            appdata = Path(os.environ.get("APPDATA", ""))
            self.db_glob = str(appdata / "Tencent" / "Marvis" / "User" / "*" / "database" / "data.db")

    def check_available(self) -> bool:
        dbs = glob.glob(self.db_glob)
        return any(os.path.getsize(p) > 100 * 1024 for p in dbs)

    def extract(self) -> List[Dict[str, Any]]:
        db_paths = glob.glob(self.db_glob)
        valid_dbs = [p for p in db_paths if os.path.getsize(p) > 100 * 1024]

        if not valid_dbs:
            return []

        all_results = []

        for db_path in valid_dbs:
            user_id = Path(db_path).parent.parent.name
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row

            conversations = conn.execute(
                "SELECT * FROM conversations ORDER BY created_at"
            ).fetchall()

            for conv in conversations:
                conv_id = conv["conversation_id"]
                msgs = conn.execute(
                    "SELECT * FROM messages WHERE conversation_id=? "
                    "ORDER BY message_seq",
                    (conv_id,),
                ).fetchall()

                if not msgs:
                    continue

                tool_count = sum(1 for m in msgs if m["tool_name"])

                output = {
                    "agent": "marvis",
                    "session_id": conv_id,
                    "user_id": user_id,
                    "title": conv["title"] or "",
                    "model": "",
                    "source": str(db_path),
                    "started": conv["created_at"],
                    "updated": conv["updated_at"],
                    "messages": [],
                    "stats": {
                        "message_count": len(msgs),
                        "tool_call_count": tool_count,
                    },
                }

                for m in msgs:
                    output["messages"].append({
                        "role": m["role"],
                        "content": m["content"] or "",
                        "time": m["created_at"],
                        "tool_name": m["tool_name"],
                        "tool_call_id": m["tool_call_id"],
                    })

                all_results.append(output)
                print(f"  [Marvis] {conv['title'][:40]}: {len(msgs)} msgs")

            conn.close()

        return all_results
