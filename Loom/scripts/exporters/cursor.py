"""Cursor 导出器 —— 占位"""

from typing import List, Dict, Any
from .base import BaseExporter


class CursorExporter(BaseExporter):
    name = "cursor"
    display_name = "Cursor (代码 AI)"

    def check_available(self) -> bool:
        # Cursor 已迁移至云端（hasMigratedComposerData=True），本地无数据
        return False

    def extract(self) -> List[Dict[str, Any]]:
        return []
