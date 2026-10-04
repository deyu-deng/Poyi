"""Chat log exporters for aggregation pipeline.

Each exporter is a subclass of BaseExporter implementing:
- check_available() -> bool
- extract() -> List[Dict[str, Any]]
"""

from pathlib import Path
from .base import BaseExporter
from .hermes import HermesExporter
from .marvis import MarvisExporter
from .antigravity import AntigravityExporter
from .windsurf import WindsurfExporter
from .doubao import DoubaoExporter
from .cursor import CursorExporter
from .workbuddy import WorkbuddyExporter

__all__ = [
    "BaseExporter",
    "HermesExporter",
    "MarvisExporter",
    "AntigravityExporter",
    "WindsurfExporter",
    "DoubaoExporter",
    "CursorExporter",
    "WorkbuddyExporter",
]

# 导出器注册表：按 display_name 排序，方便遍历
EXPORTER_REGISTRY = [
    HermesExporter,
    MarvisExporter,
    AntigravityExporter,
    WindsurfExporter,
    DoubaoExporter,
    CursorExporter,
    WorkbuddyExporter,
]


def create_all_exporters(looM_root: Path) -> list:
    """按注册顺序创建所有导出器实例。"""
    return [cls(looM_root) for cls in EXPORTER_REGISTRY]
