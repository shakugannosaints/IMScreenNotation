"""
Canvas module - 画布模块

提供绘图画布的完整功能，包括：
- 绘图画布主组件 (DrawingCanvas)
- 画布属性管理 (CanvasProperties)  
- 事件处理 (CanvasEventHandler)
- 状态管理 (CanvasStateManager)
- 绘制管理 (CanvasPainter)
- 类型定义 (ShapeType)

主要接口：
    DrawingCanvas: 主绘图画布组件，提供所有绘图功能
    
使用示例：
    from canvas import DrawingCanvas
    
    canvas = DrawingCanvas()
    canvas.set_current_tool('line')
    canvas.set_current_color(QColor(255, 0, 0))
    canvas.show()
"""

from .drawing_canvas import DrawingCanvas
from .properties import CanvasProperties
from .events import CanvasEventHandler
from .state_manager import CanvasStateManager
from .painter import CanvasPainter
from .types import ShapeType

# 向外暴露的主要接口
__all__ = [
    'DrawingCanvas',
    'CanvasProperties', 
    'CanvasEventHandler',
    'CanvasStateManager',
    'CanvasPainter',
    'ShapeType'
]

# 为了保持向后兼容性，保留原来的导入方式
# 旧的导入 from gui import DrawingCanvas 仍然可以工作
