"""
管理器模块 - 处理应用程序的各种管理功能
"""

from .window_manager import WindowManager
from .transparency_manager import TransparencyManager
from .tool_manager import ToolManager
from .tray_manager import TrayManager
from .config_manager import ConfigManager

__all__ = [
    'WindowManager',
    'TransparencyManager',
    'ToolManager',
    'TrayManager',
    'ConfigManager'
]
