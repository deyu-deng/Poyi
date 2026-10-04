"""
统一 Exporter 接口 —— 每个平台导出器必须实现的基类。

约定：
- 每个 exporter 一个 .py 文件，放在 exporters/ 目录下
- 类名 = {Name}Exporter，继承 BaseExporter
- 实现 extract() → List[SessionDict]
- 新增平台 = 新增一个文件，aggregate_win.py 会自动发现
"""

import sys
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path


class SessionDict:
    """单次会话的标准结构"""
    agent: str          # 平台名（hermes/antigravity/doubao/...）
    session_id: str     # 唯一会话 ID
    title: str          # 会话标题
    model: str          # 使用的模型
    source: str         # 数据来源描述
    messages: List[Dict]  # [{"role":"user/assistant","content":"...","time":"ISO8601"},...]
    stats: Dict         # {"message_count": N, "tool_call_count": M}


class BaseExporter(ABC):
    """所有平台导出器的基类"""

    # 子类必须覆盖
    name: str = "unknown"        # 平台标识（用于日志和数据标记）
    display_name: str = "Unknown"  # 显示名称

    def __init__(self, looM_root: Path):
        self.looM_root = looM_root
        self.raw_dir = looM_root / "raw" / "chatlog" / "raw"

    @property
    def is_mac(self) -> bool:
        """平台探测：macOS (darwin) 返回 True。供各 exporter 选择数据源。"""
        return sys.platform == "darwin"

    @abstractmethod
    def check_available(self) -> bool:
        """检查数据源是否可用。返回 True 表示可以尝试提取。"""
        ...

    @abstractmethod
    def extract(self) -> List[Dict[str, Any]]:
        """
        提取对话数据。
        返回 session dict 列表，每个 session 包含 agent/session_id/title/model/source/messages/stats。
        如果不可用，返回空列表。
        """
        ...

    def get_source_description(self) -> str:
        """返回数据源的简短描述（用于日志）"""
        return f"{self.name} ({self.display_name})"
