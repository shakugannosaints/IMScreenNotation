from PyQt5.QtWidgets import QWidget, QApplication, QInputDialog, QFontDialog, QColorDialog
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF
import json
from typing import List, Union, Optional
from shapes import Line, Rectangle, Circle, Arrow, Freehand, Point, LaserPointer, FilledFreehand, Text, Eraser

# 定义Shape类型联合
ShapeType = Union[Line, Rectangle, Circle, Arrow, Freehand, Point, LaserPointer, FilledFreehand, Text, Eraser]

class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True) # Enable mouse tracking even when no button is pressed
        
        # 确保画布没有边距和固定的布局约束
        self.setContentsMargins(0, 0, 0, 0)
        
        self.shapes: List[ShapeType] = [] # List to store all drawn shapes
        self.undo_stack = [] # For undo functionality - stores canvas states
        self.redo_stack = [] # For redo functionality - stores canvas states
        self.current_shape: Optional[ShapeType] = None
        self.drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.current_tool = 'line' # Default tool
        self.current_color = QColor(255, 0, 0, 255) # Default drawing color (red)
        self.current_thickness = 3 # Default drawing thickness
        self.current_opacity = 1.0 # Default drawing opacity
        self.canvas_color = QColor(0, 0, 0, 0) # Default transparent background
        self.canvas_opacity = 0.0 # Default fully transparent
        self.single_draw_mode = False # New attribute for single draw mode
        
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
        self.update()  # Redraw the canvas

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
        self.update()

    def save_state_to_undo_stack(self):
        """保存当前画布状态到撤销栈"""
        # 将shapes序列化为字典列表，避免深拷贝PyQt对象
        serialized_shapes = []
        for shape in self.shapes:
            serialized_shapes.append(shape.to_dict())
        
        self.undo_stack.append(serialized_shapes)
        
        # 限制撤销栈的大小，避免内存过度使用
        if len(self.undo_stack) > 50:  # 最多保存50个状态
            self.undo_stack.pop(0)
        
        # 清空重做栈，因为有新的操作
        self.redo_stack.clear()



    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw canvas background with current color and opacity
        # 如果画布完全透明，绘制一个几乎透明的背景来确保鼠标事件可以被接收
        if self.canvas_color.alpha() == 0:
            # 绘制一个几乎透明的背景 (alpha = 1) 来接收鼠标事件
            transparent_bg = QColor(0, 0, 0, 1)  # 几乎透明的黑色
            painter.fillRect(self.rect(), transparent_bg)
        else:
            painter.fillRect(self.rect(), self.canvas_color)

        for shape in self.shapes:
            shape.draw(painter)

        if self.current_shape:
            self.current_shape.draw(painter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point = event.pos()
            self.end_point = event.pos()
            
            if self.current_tool == 'text':
                # 文本工具：弹出输入对话框
                self.create_text_annotation(event.pos())
                return
            elif self.current_tool == 'freehand':
                # 保存状态到撤销栈（在创建新shape前）
                self.save_state_to_undo_stack()
                self.current_shape = Freehand([self.start_point], color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
            elif self.current_tool == 'filled_freehand':
                # 保存状态到撤销栈（在创建新shape前）
                self.save_state_to_undo_stack()
                self.current_shape = FilledFreehand([self.start_point], color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
            elif self.current_tool == 'point':
                # 保存状态到撤销栈（在创建新shape前）
                self.save_state_to_undo_stack()
                self.current_shape = Point(self.start_point, color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
                self.shapes.append(self.current_shape)
                self.current_shape = None
                self.drawing = False # Point is a single click action
            elif self.current_tool == 'laser_pointer':
                # 激光笔不保存状态，因为它是临时的
                self.current_shape = LaserPointer(event.pos(), color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
                self.update() # 立即更新显示激光笔
                return # 激光笔是临时的，不添加到shapes列表中，也不保存状态
            elif self.current_tool == 'eraser':
                # 橡皮擦工具：开始擦除操作
                self.save_state_to_undo_stack()
                self.current_shape = Eraser([self.start_point], color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
            else:
                # 其他工具（line, rectangle, circle, arrow）在释放鼠标时保存状态
                self.current_shape = None # Reset current shape

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = event.pos()
            if self.current_tool == 'line':
                self.current_shape = Line(self.start_point, self.end_point, color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
            elif self.current_tool == 'rectangle':
                rect = QRect(self.start_point, self.end_point).normalized()
                self.current_shape = Rectangle(rect, color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
            elif self.current_tool == 'circle':
                radius = int(((self.end_point.x() - self.start_point.x())**2 + (self.end_point.y() - self.start_point.y())**2)**0.5)
                self.current_shape = Circle(self.start_point, radius, color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
            elif self.current_tool == 'arrow':
                self.current_shape = Arrow(self.start_point, self.end_point, color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
            elif self.current_tool == 'freehand':
                if isinstance(self.current_shape, Freehand):
                    self.current_shape.points.append(self.end_point)
            elif self.current_tool == 'filled_freehand':
                if isinstance(self.current_shape, FilledFreehand):
                    self.current_shape.points.append(self.end_point)
            elif self.current_tool == 'laser_pointer':
                # 更新激光笔位置
                self.current_shape = LaserPointer(event.pos(), color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
                self.update()
                return # 激光笔是临时的，不添加到shapes列表中
            elif self.current_tool == 'eraser':
                # 橡皮擦：添加擦除点
                if isinstance(self.current_shape, Eraser):
                    self.current_shape.points.append(self.end_point)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.current_shape and self.current_tool != 'point' and self.current_tool != 'laser_pointer':
                # 对于需要拖拽的工具（line, rectangle, circle, arrow），在释放时保存状态
                if self.current_tool in ['line', 'rectangle', 'circle', 'arrow']:
                    self.save_state_to_undo_stack()
                
                # 橡皮擦特殊处理：执行擦除操作
                if self.current_tool == 'eraser' and isinstance(self.current_shape, Eraser):
                    self.perform_erase_operation(self.current_shape)
                else:
                    if self.single_draw_mode:
                        self.shapes.clear()
                        # 单次绘制模式下，清空撤销栈并重新开始
                        self.undo_stack.clear()
                        self.redo_stack.clear()
                        # 保存空白状态
                        self.undo_stack.append([])  # 空的序列化状态列表
                    
                    self.shapes.append(self.current_shape)
            self.current_shape = None
            self.update()

    def undo(self):
        """撤销操作 - 恢复到上一个状态"""
        if self.undo_stack:
            # 将当前状态序列化并保存到重做栈
            current_serialized_state = []
            for shape in self.shapes:
                current_serialized_state.append(shape.to_dict())
            self.redo_stack.append(current_serialized_state)
            
            # 限制重做栈的大小
            if len(self.redo_stack) > 50:
                self.redo_stack.pop(0)
            
            # 恢复到上一个状态
            previous_serialized_state = self.undo_stack.pop()
            self.shapes = self._deserialize_shapes(previous_serialized_state)
            self.update()

    def redo(self):
        """重做操作 - 恢复到下一个状态"""
        if self.redo_stack:
            # 将当前状态序列化并保存到撤销栈
            current_serialized_state = []
            for shape in self.shapes:
                current_serialized_state.append(shape.to_dict())
            self.undo_stack.append(current_serialized_state)
            
            # 限制撤销栈的大小
            if len(self.undo_stack) > 50:
                self.undo_stack.pop(0)
            
            # 恢复到下一个状态
            next_serialized_state = self.redo_stack.pop()
            self.shapes = self._deserialize_shapes(next_serialized_state)
            self.update()

    def _deserialize_shapes(self, serialized_shapes):
        """从序列化的形状数据重建形状对象列表"""
        shapes = []
        for shape_data in serialized_shapes:
            # 创建shape_data的副本，避免修改原始数据
            shape_dict = shape_data.copy()
            shape_type = shape_dict.pop("type")
            
            if shape_type == "Line":
                shape = Line.from_dict(shape_dict)
            elif shape_type == "Rectangle":
                shape = Rectangle.from_dict(shape_dict)
            elif shape_type == "Circle":
                shape = Circle.from_dict(shape_dict)
            elif shape_type == "Arrow":
                shape = Arrow.from_dict(shape_dict)
            elif shape_type == "Freehand":
                shape = Freehand.from_dict(shape_dict)
            elif shape_type == "FilledFreehand":
                shape = FilledFreehand.from_dict(shape_dict)
            elif shape_type == "Point":
                shape = Point.from_dict(shape_dict)
            elif shape_type == "Text":
                shape = Text.from_dict(shape_dict)
            elif shape_type == "LaserPointer":
                # 跳过激光笔，因为它不应该被保存/恢复
                continue
            elif shape_type == "Eraser":
                # 跳过橡皮擦，因为它不应该被保存/恢复（它是删除操作）
                continue
            else:
                continue # Skip unknown shape types
            
            shapes.append(shape)
        return shapes

    def clear_canvas(self):
        """清空画布 - 支持撤销/重做"""
        # 先保存当前状态到撤销栈
        self.save_state_to_undo_stack()
        
        # 清空画布
        self.shapes.clear()
        self.update()

    def to_json_data(self):
        """将画布内容导出为JSON数据"""
        serialized_shapes = []
        for shape in self.shapes:
            serialized_shapes.append(shape.to_dict())
        return json.dumps(serialized_shapes, indent=2)

    def from_json_data(self, json_data):
        """从JSON数据导入画布内容"""
        # 保存当前状态到撤销栈
        self.save_state_to_undo_stack()
        
        # 清空当前画布
        self.shapes.clear()
        
        try:
            data = json.loads(json_data)
            self.shapes = self._deserialize_shapes(data)
            self.update()
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"导入数据时出错: {e}")
            raise

    def create_text_annotation(self, position):
        """创建文本标注"""
        try:
            # 确保在主线程中执行
            from PyQt5.QtCore import QTimer
            from PyQt5.QtWidgets import QInputDialog
            
            # 弹出文本输入对话框
            text, ok = QInputDialog.getText(self, '输入文本', '请输入要标注的文本:')
            if ok and text:
                # 保存状态到撤销栈
                self.save_state_to_undo_stack()
                
                # 创建文本对象
                text_shape = Text(
                    position=QPointF(position),
                    text=text,
                    font_family=self.text_font_family,
                    font_size=self.text_font_size,
                    font_bold=self.text_font_bold,
                    font_italic=self.text_font_italic,
                    text_color=self.text_color,
                    background_color=self.text_background_color,
                    border_color=self.text_border_color,
                    border_enabled=self.text_border_enabled,
                    border_width=self.text_border_width,
                    padding=self.text_padding,
                    color=self.current_color,
                    thickness=self.current_thickness,
                    opacity=self.current_opacity
                )
                
                # 添加到形状列表
                self.shapes.append(text_shape)
                
                # 如果是单次绘制模式，清空其他形状
                if self.single_draw_mode:
                    self.shapes = [text_shape]
                    self.undo_stack.clear()
                
                # 更新显示
                self.update()
                
            # 重置绘制状态
            self.drawing = False
            self.current_shape = None
            
        except Exception as e:
            print(f"Error creating text annotation: {e}")
            # 重置绘制状态
            self.drawing = False
            self.current_shape = None
    
    def perform_erase_operation(self, eraser_shape):
        """执行橡皮擦操作 - 删除与橡皮擦相交的形状"""
        if not isinstance(eraser_shape, Eraser):
            return
            
        # 收集需要删除的形状
        shapes_to_remove = []
        
        for shape in self.shapes:
            # 跳过激光笔和橡皮擦本身
            if isinstance(shape, (LaserPointer, Eraser)):
                continue
                
            # 检查形状是否与橡皮擦相交
            if eraser_shape.intersects_with_shape(shape):
                shapes_to_remove.append(shape)
        
        # 删除相交的形状
        for shape in shapes_to_remove:
            if shape in self.shapes:
                self.shapes.remove(shape)
        
        print(f"橡皮擦删除了 {len(shapes_to_remove)} 个形状")

# Example usage (for testing purposes, will be integrated into main app later)
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    canvas = DrawingCanvas()
    canvas.setWindowTitle('Drawing Canvas Test')
    canvas.setGeometry(100, 100, 800, 600)
    canvas.set_canvas_color(QColor(255, 255, 0, 100)) # Semi-transparent yellow
    canvas.show()
    sys.exit(app.exec_())

