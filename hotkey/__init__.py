"""
热键模块 - 处理全局热键管理和设置
"""

from .hotkey_manager import HotkeyManager
from .hotkey_handler import HotkeyHandler
from .hotkey_settings import HotkeySettingsDialog

__all__ = [
    'HotkeyManager',
    'HotkeyHandler', 
    'HotkeySettingsDialog'
]
