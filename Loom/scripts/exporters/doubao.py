"""Doubao 导出器 —— 从 Local Storage 提取认证令牌，调用 API 拉取完整对话。

设计为凌晨自动运行（Doubao 未运行时文件可读）。
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from .base import BaseExporter

API_BASE = "https://api-normal.doubao.com"
REQUEST_DELAY = 1.5
PAGE_SIZE = 20
MAX_SESSIONS = 50


class DoubaoExporter(BaseExporter):
    name = "doubao"
    display_name = "Doubao (豆包)"

    def __init__(self, looM_root: Path):
        super().__init__(looM_root)
        self.localappdata = Path(os.environ["LOCALAPPDATA"])
        self.ls_leveldb = (
            self.localappdata / "Doubao" / "User Data" / "Default"
            / "Local Storage" / "leveldb"
        )

    def check_available(self) -> bool:
        if not self.ls_leveldb.exists():
            return False
        # 运行时也允许继续：extract() 内部会 kill 进程
        return True

    def extract(self) -> List[Dict[str, Any]]:
        if self._is_running():
            print("  [Doubao] Running, killing process...")
            self._kill_doubao()
            # 等锁释放
            for i in range(10):
                lock_file = self.ls_leveldb / "LOCK"
                if not lock_file.exists() or lock_file.stat().st_size == 0:
                    break
                time.sleep(1)

        auth = self._extract_auth()
        if not auth:
            print("  [Doubao] No auth tokens found")
            return []

        headers = self._build_headers(auth)

        all_convs = self._fetch_all_convs(headers)
        if not all_convs:
            return []

        conv_data = self._fetch_messages(headers, all_convs)
        if not conv_data:
            return []

        sessions = []
        today = datetime.now().strftime("%Y-%m-%d")

        for conv in conv_data:
            conv_id = conv["id"]
            title = conv.get("title", "")
            messages = conv["messages"]
            n_msgs = len(messages)

            # 确保每条消息 content 不为 None
            for m in messages:
                if m.get("content") is None:
                    m["content"] = ""

            sessions.append({
                "agent": "doubao",
                "session_id": conv_id,
                "title": title or f"Doubao chat {conv_id[:12]}",
                "model": "Doubao (ByteDance)",
                "source": f"API ({today})",
                "messages": messages,
                "stats": {
                    "message_count": n_msgs,
                    "tool_call_count": 0,
                },
            })

        print(f"  [Doubao] {len(sessions)} sessions, "
              f"{sum(s['stats']['message_count'] for s in sessions)} messages")

        return sessions

    def _is_running(self) -> bool:
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Doubao.exe"],
                capture_output=True, text=True,
            )
            return "Doubao.exe" in result.stdout
        except Exception:
            return False

    def _kill_doubao(self):
        """强制结束 Doubao.exe 进程。"""
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "Doubao.exe"],
                capture_output=True, text=True, timeout=15,
            )
            print("  [Doubao] Process killed")
        except Exception as e:
            print(f"  [Doubao] Kill failed: {e}")

    def _extract_auth(self) -> Optional[Dict[str, str]]:
        if not self.ls_leveldb.exists():
            return None

        try:
            import leveldb
            db = leveldb.LevelDB(str(self.ls_leveldb))
        except Exception as e:
            print(f"  [Doubao] Cannot open LevelDB: {e}")
            return None

        auth = {}
        target_keys = [
            "xmst", "SLARDARflow_web", "web_id", "user_unique_id",
            "device_id", "uid", "session", "token",
        ]

        for k_bytes, v_bytes in db.items():
            try:
                key = k_bytes.decode("utf-8", errors="replace")
            except Exception:
                continue

            if "_chrome://doubao" not in key:
                continue

            clean_key = key.split("\x00")[-1] if "\x00" in key else key

            for tk in target_keys:
                if tk in clean_key.lower():
                    try:
                        val = v_bytes.decode("utf-8", errors="replace")
                        auth[clean_key] = val
                    except Exception:
                        pass
                    break

        return auth if auth else None

    @staticmethod
    def _build_headers(auth: Dict[str, str]) -> Dict[str, str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Origin": "https://www.doubao.com",
            "Referer": "https://www.doubao.com/",
            "Content-Type": "application/json",
        }

        slardar = auth.get("SLARDARflow_web", "")
        if slardar:
            try:
                sd = json.loads(slardar) if isinstance(slardar, str) else slardar
                if "sessionId" in sd:
                    headers["X-Session-Id"] = sd["sessionId"]
                if "userId" in sd:
                    headers["X-User-Id"] = sd["userId"]
            except json.JSONDecodeError:
                pass

        xmst = auth.get("xmst", "")
        if xmst:
            headers["Cookie"] = f"xmst={xmst}"

        for key, header_name in [
            ("web_id", "X-Web-Id"),
            ("device_id", "X-Device-Id"),
            ("user_unique_id", "X-User-Unique-Id"),
        ]:
            if key in auth and auth[key]:
                headers[header_name] = auth[key]

        return headers

    @staticmethod
    def _api_request(endpoint: str, headers: Dict, body: dict = None) -> Optional[dict]:
        url = f"{API_BASE}{endpoint}"
        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            print(f"  [Doubao] HTTP {e.code} on {endpoint}: {body_text[:200]}")
            return None
        except Exception as e:
            print(f"  [Doubao] Error on {endpoint}: {e}")
            return None

    def _fetch_all_convs(self, headers: Dict) -> list:
        all_convs = []
        cursor = None

        while True:
            body = {"page_size": PAGE_SIZE}
            if cursor:
                body["cursor"] = cursor

            resp = self._api_request("/im/chain/recent_conv", headers, body)
            if not resp or resp.get("code") != 0:
                break

            data = resp.get("data", {})
            convs = data.get("conversations", data.get("items", []))
            has_more = data.get("has_more", False)
            next_cursor = data.get("cursor") or data.get("next_cursor")

            all_convs.extend(convs)
            print(f"  [Doubao] recent_conv page: {len(convs)} convs, has_more={has_more}")

            if MAX_SESSIONS > 0 and len(all_convs) >= MAX_SESSIONS:
                break
            if not has_more or not next_cursor:
                break

            cursor = next_cursor
            time.sleep(REQUEST_DELAY)

        return all_convs

    def _fetch_messages(self, headers: Dict, all_convs: list) -> list:
        results = []
        for i, conv in enumerate(all_convs):
            conv_id = conv.get("id", conv.get("conversation_id", ""))
            title = conv.get("title", conv.get("name", ""))

            if not conv_id:
                continue

            messages_raw = self._api_request(
                "/im/conversation/info", headers,
                {"conversation_id": conv_id},
            )
            if messages_raw and messages_raw.get("code") == 0:
                messages_raw = messages_raw.get("data", {}).get(
                    "messages", messages_raw.get("data", {}).get("items", [])
                )
            else:
                # 备用：chain/single
                resp = self._api_request(
                    "/im/chain/single", headers,
                    {"conversation_id": conv_id, "page_size": 200},
                )
                if resp and resp.get("code") == 0:
                    messages_raw = resp.get("data", {}).get("messages", [])
                else:
                    continue

            messages = []
            for m in messages_raw:
                messages.append({
                    "role": m.get("role", "unknown"),
                    "content": m.get("content", ""),
                    "brief": m.get("brief", ""),
                    "thinking": m.get("thinking", ""),
                    "tts": m.get("tts", m.get("content", "")),
                    "time": str(m.get("time", m.get("create_time", ""))),
                    "index": str(m.get("index", m.get("message_id", ""))),
                })

            print(f"  [Doubao] [{i+1}/{len(all_convs)}] {conv_id}: {len(messages)} msgs")
            results.append({"id": conv_id, "title": title, "messages": messages})
            time.sleep(REQUEST_DELAY)

        return results
