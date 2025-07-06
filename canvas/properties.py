"""
Canvas properties and settings management
"""
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject
from typing import Union, List, Optional


class CanvasProperties(QObject):
    """管理画布的各种属性和设置"""
    
    def __init__(self):
        super().__init__()
        # 绘图相关属性
        self.current_tool = 'line'  # Default tool
        self.current_color = QColor(255, 0, 0, 255)  # Default drawing color (red)
        self.current_thickness = 3  # Default drawing thickness
        self.current_opacity = 1.0  # Default drawing opacity
        self.canvas_color = QColor(0, 0, 0, 0)  # Default transparent background
        self.canvas_opacity = 0.0  # Default fully transparent
        self.single_draw_mode = False  # New attribute for single draw mode
        
        # 文本相关属性
        self.text_font_family = "Arial"
        self.text_font_size = 16
        self.text_font_bold = False
        self.text_font_italic = False
        self.text_color = QColor(255, 0, 0, 255)  # 默认红色
        self.text_background_color = None  # 默认透明背景
        self.text_border_color = None  # 默认无边框
        self.text_border_enabled = True  # 默认启用边框
        self.text_border_width = 1
        self.text_padding = 5

    # 文本相关属性的 setter 方法
    def set_text_font_family(self, font_family: str) -> None:
        """设置文本字体族"""
        self.text_font_family = font_family

    def set_text_font_size(self, font_size: int) -> None:
        """设置文本字体大小"""
        self.text_font_size = font_size

    def set_text_font_bold(self, bold: bool) -> None:
        """设置文本是否粗体"""
        self.text_font_bold = bold

    def set_text_font_italic(self, italic: bool) -> None:
        """设置文本是否斜体"""
        self.text_font_italic = italic

    def set_text_color(self, color: Union[QColor, str, List[int]]) -> None:
        """设置文本颜色"""
        if isinstance(color, str):
            self.text_color = QColor(color)
        elif isinstance(color, list) and len(color) >= 3:
            if len(color) == 3:
                self.text_color = QColor(color[0], color[1], color[2])
            else:
                self.text_color = QColor(color[0], color[1], color[2], color[3])
        elif isinstance(color, QColor):
            self.text_color = color

    def set_text_background_color(self, color: Union[QColor, str, List[int], None]) -> None:
        """设置文本背景颜色"""
        if color is None:
            self.text_background_color = None
        elif isinstance(color, str):
            self.text_background_color = QColor(color)
        elif isinstance(color, list) and len(color) >= 3:
            if len(color) == 3:
                self.text_background_color = QColor(color[0], color[1], color[2])
            else:
                self.text_background_color = QColor(color[0], color[1], color[2], color[3])
        elif isinstance(color, QColor):
            self.text_background_color = color

    def set_text_border_color(self, color: Union[QColor, str, List[int], None]) -> None:
        """设置文本边框颜色"""
        if color is None:
            self.text_border_color = None
        elif isinstance(color, str):
            self.text_border_color = QColor(color)
        elif isinstance(color, list) and len(color) >= 3:
            if len(color) == 3:
                self.text_border_color = QColor(color[0], color[1], color[2])
            else:
                self.text_border_color = QColor(color[0], color[1], color[2], color[3])
        elif isinstance(color, QColor):
            self.text_border_color = color

    def set_text_border_width(self, width: int) -> None:
        """设置文本边框宽度"""
        self.text_border_width = width

    def set_text_padding(self, padding: int) -> None:
        """设置文本内边距"""
        self.text_padding = padding

    def set_text_border_enabled(self, enabled: bool) -> None:
        """设置文本边框是否启用"""
        self.text_border_enabled = enabled

    # 绘图相关属性的 setter 方法
    def set_current_tool(self, tool: str) -> None:
        """设置当前工具"""
        self.current_tool = tool

    def set_current_color(self, color: Union[QColor, str, List[int]]) -> None:
        """设置当前绘图颜色"""
        if isinstance(color, str):
            self.current_color = QColor(color)
        elif isinstance(color, list) and len(color) >= 3:
            if len(color) == 3:
                self.current_color = QColor(color[0], color[1], color[2])
            else:
                self.current_color = QColor(color[0], color[1], color[2], color[3])
        elif isinstance(color, QColor):
            self.current_color = color

    def set_current_thickness(self, thickness: int) -> None:
        """设置当前绘图厚度"""
        self.current_thickness = thickness

    def set_current_opacity(self, opacity: float) -> None:
        """设置当前绘图不透明度"""
        self.current_opacity = opacity

    def set_canvas_color(self, color: Union[QColor, str, List[int]]) -> None:
        """设置画布背景颜色"""
        if isinstance(color, str):
            self.canvas_color = QColor(color)
        elif isinstance(color, list) and len(color) >= 3:
            if len(color) == 3:
                self.canvas_color = QColor(color[0], color[1], color[2])
            else:
                self.canvas_color = QColor(color[0], color[1], color[2], color[3])
        elif isinstance(color, QColor):
            self.canvas_color = color

    def set_canvas_opacity(self, opacity: float) -> None:
        """设置画布不透明度"""
        self.canvas_opacity = opacity
        # 确保canvas_color是QColor对象
        if isinstance(self.canvas_color, list):
            self.canvas_color = QColor(*self.canvas_color)
        
        # 设置画布颜色的透明度，但确保至少有最小透明度来接收鼠标事件
        if opacity == 0.0:
            # 当透明度为0时，设置一个极小的透明度来确保鼠标事件可以被接收
            self.canvas_color.setAlphaF(0.003)  # 几乎完全透明，但仍可接收鼠标事件
        else:
            self.canvas_color.setAlphaF(self.canvas_opacity)
