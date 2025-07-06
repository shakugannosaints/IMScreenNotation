"""
文本样式配置模块
用于设置文本标注的字体、颜色、背景、边框等样式
"""

from .text_style_dialog import TextStyleDialog
from .ui_builder import TextStyleUIBuilder
from .event_handler import TextStyleEventHandler
from .theme_manager import TextStyleThemeManager
from .settings_manager import TextStyleSettingsManager

__all__ = [
    'TextStyleDialog',
    'TextStyleUIBuilder', 
    'TextStyleEventHandler',
    'TextStyleThemeManager',
    'TextStyleSettingsManager'
]
