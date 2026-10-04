"""Windsurf 导出器 —— 从 state.vscdb 提取对话元数据"""

import sqlite3
import json
import glob
import os
from pathlib import Path
from typing import List, Dict, Any

from .base import BaseExporter


class WindsurfExporter(BaseExporter):
    name = "windsurf"
    display_name = "Windsurf (Cascade AI)"

    def __init__(self, looM_root: Path):
        super().__init__(looM_root)
        self.appdata = Path(os.environ["APPDATA"])
        self.global_db = self.appdata / "Windsurf" / "User" / "globalStorage" / "state.vscdb"
        self.ws_glob = str(
            self.appdata / "Windsurf" / "User" / "workspaceStorage" / "*" / "state.vscdb"
        )

    def check_available(self) -> bool:
        return self.global_db.exists() or bool(glob.glob(self.ws_glob))

    def extract(self) -> List[Dict[str, Any]]:
        all_dbs = [self.global_db] if self.global_db.exists() else []
        all_dbs.extend([Path(p) for p in glob.glob(self.ws_glob) if Path(p).exists()])

        if not all_dbs:
            return []

        results = []
        keys_of_interest = [
            "chat.ChatSessionStore.index",
            "chat.modelsControl",
            "chat.participantNameRegistry",
            "agentSessions.state.cache",
            "agentSessions.model.cache",
            "agentSessions.readDateBaseline2",
            "windsurf.cascadeViewContainerId.state",
            "windsurf.cascadeViewContainerId.state.hidden",
            "windsurf.cascadeViewContainerId.numberOfVisibleViews",
        ]

        for db_path in all_dbs:
            try:
                conn = sqlite3.connect(str(db_path))
            except Exception as e:
                print(f"  [Windsurf] Cannot open {db_path}: {e}")
                continue

            metadata = {}
            for key in keys_of_interest:
                try:
                    row = conn.execute(
                        "SELECT value FROM ItemTable WHERE key=?", (key,)
                    ).fetchone()
                    if row and row[0]:
                        try:
                            val = row[0].decode("utf-8")
                            try:
                                metadata[key] = json.loads(val)
                            except json.JSONDecodeError:
                                metadata[key] = val[:500]
                        except UnicodeDecodeError:
                            metadata[key] = f"<binary {len(row[0])} bytes>"
                except Exception:
                    pass

            conn.close()

            parent = db_path.parent.name
            source = "globalStorage" if db_path == self.global_db else f"workspaceStorage/{parent}"

            if metadata:
                output = {
                    "agent": "windsurf",
                    "session_id": f"windsurf_{source}",
                    "title": f"Windsurf {source} metadata",
                    "model": "Windsurf Cascade (Codeium cloud)",
                    "source": source,
                    "messages": [{
                        "role": "metadata",
                        "content": json.dumps(metadata, ensure_ascii=False, indent=2),
                        "note": "Full conversation content stored on Codeium servers",
                    }],
                    "stats": {
                        "message_count": 0,
                        "metadata_keys": len(metadata),
                    },
                }
                results.append(output)
                print(f"  [Windsurf] {source}: {len(metadata)} keys")

        return results
