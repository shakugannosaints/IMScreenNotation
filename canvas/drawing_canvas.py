"""
Main drawing canvas widget
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter
from typing import List, Optional

from .types import ShapeType
from .properties import CanvasProperties
from .events import CanvasEventHandler
from .state_manager import CanvasStateManager
from .painter import CanvasPainter


class DrawingCanvas(QWidget):
    """主绘图画布组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)  # Enable mouse tracking even when no button is pressed
        
        # 确保画布没有边距和固定的布局约束
        self.setContentsMargins(0, 0, 0, 0)
        
        # 初始化核心组件
        self.properties = CanvasProperties()
        self.event_handler = CanvasEventHandler(self)
        self.state_manager = CanvasStateManager(self)
        self.painter = CanvasPainter(self)
        
        # 绘图状态
        self.shapes: List[ShapeType] = []  # List to store all drawn shapes
        self.current_shape: Optional[ShapeType] = None
        self.drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()

    # 属性设置方法的代理
    def set_current_tool(self, tool: str) -> None:
        """设置当前工具"""
        self.properties.set_current_tool(tool)

    def set_current_color(self, color) -> None:
        """设置当前绘图颜色"""
        self.properties.set_current_color(color)

    def set_current_thickness(self, thickness: int) -> None:
        """设置当前绘图厚度"""
        self.properties.set_current_thickness(thickness)

    def set_current_opacity(self, opacity: float) -> None:
        """设置当前绘图不透明度"""
        self.properties.set_current_opacity(opacity)

    def set_canvas_color(self, color) -> None:
        """设置画布背景颜色"""
        self.properties.set_canvas_color(color)
        self.update()  # Redraw the canvas

    def set_canvas_opacity(self, opacity: float) -> None:
        """设置画布不透明度"""
        self.properties.set_canvas_opacity(opacity)
        self.update()

    # 文本相关属性设置方法的代理
    def set_text_font_family(self, font_family: str) -> None:
        """设置文本字体族"""
        self.properties.set_text_font_family(font_family)

    def set_text_font_size(self, font_size: int) -> None:
        """设置文本字体大小"""
        self.properties.set_text_font_size(font_size)

    def set_text_font_bold(self, bold: bool) -> None:
        """设置文本是否粗体"""
        self.properties.set_text_font_bold(bold)

    def set_text_font_italic(self, italic: bool) -> None:
        """设置文本是否斜体"""
        self.properties.set_text_font_italic(italic)

    def set_text_color(self, color) -> None:
        """设置文本颜色"""
        self.properties.set_text_color(color)

    def set_text_background_color(self, color) -> None:
        """设置文本背景颜色"""
        self.properties.set_text_background_color(color)

    def set_text_border_color(self, color) -> None:
        """设置文本边框颜色"""
        self.properties.set_text_border_color(color)

    def set_text_border_width(self, width: int) -> None:
        """设置文本边框宽度"""
        self.properties.set_text_border_width(width)

    def set_text_padding(self, padding: int) -> None:
        """设置文本内边距"""
        self.properties.set_text_padding(padding)

    def set_text_border_enabled(self, enabled: bool) -> None:
        """设置文本边框是否启用"""
        self.properties.set_text_border_enabled(enabled)

    # 状态管理方法的代理
    def undo(self):
        """撤销操作"""
        self.state_manager.undo()

    def redo(self):
        """重做操作"""
        self.state_manager.redo()

    def clear_canvas(self):
        """清空画布"""
        self.state_manager.clear_canvas()

    def to_json_data(self):
        """将画布内容导出为JSON数据"""
        return self.state_manager.to_json_data()

    def from_json_data(self, json_data):
        """从JSON数据导入画布内容"""
        self.state_manager.from_json_data(json_data)

    # Qt事件处理
    def paintEvent(self, event):
        """绘制事件处理"""
        painter = QPainter(self)
        self.painter.paint_canvas(painter)

    def mousePressEvent(self, event):
        """鼠标按下事件处理"""
        self.event_handler.handle_mouse_press(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件处理"""
        self.event_handler.handle_mouse_move(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件处理"""
        self.event_handler.handle_mouse_release(event)
