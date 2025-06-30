from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPoint, QRect
import json
from shapes import Line, Rectangle, Circle, Arrow, Freehand, Point, LaserPointer, FilledFreehand

class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True) # Enable mouse tracking even when no button is pressed
        self.shapes = [] # List to store all drawn shapes
        self.undo_stack = [] # For undo functionality
        self.redo_stack = [] # For redo functionality
        self.current_shape = None
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

    def set_canvas_color(self, color):
        # 确保color是QColor对象
        if isinstance(color, list):
            self.canvas_color = QColor(*color)
        else:
            self.canvas_color = color
        self.update() # Redraw the canvas

    def set_canvas_opacity(self, opacity):
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

    def set_current_tool(self, tool):
        print(f"DrawingCanvas.set_current_tool: 将工具从 {self.current_tool} 切换到 {tool}")
        self.current_tool = tool
        # 强制更新UI
        self.update()
        print(f"DrawingCanvas.set_current_tool: 工具已设置为 {self.current_tool}")

    def set_current_color(self, color):
        # 确保color是QColor对象
        if isinstance(color, list):
            self.current_color = QColor(*color)
        else:
            self.current_color = color

    def set_current_thickness(self, thickness):
        self.current_thickness = thickness

    def set_current_opacity(self, opacity):
        self.current_opacity = opacity

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
            if self.current_tool == 'freehand':
                self.current_shape = Freehand([self.start_point], color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
            elif self.current_tool == 'filled_freehand':
                self.current_shape = FilledFreehand([self.start_point], color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
            elif self.current_tool == 'point':
                self.current_shape = Point(self.start_point, color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
                self.shapes.append(self.current_shape)
                self.undo_stack.append(self.current_shape)
                self.redo_stack.clear()
                self.current_shape = None
                self.drawing = False # Point is a single click action
            elif self.current_tool == 'laser_pointer':
                self.current_shape = LaserPointer(event.pos(), color=self.current_color, thickness=self.current_thickness, opacity=self.current_opacity)
                self.update() # 立即更新显示激光笔
                return # 激光笔是临时的，不添加到shapes列表中
            else:
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
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.current_shape and self.current_tool != 'point': # Point is handled in mousePressEvent
                if self.single_draw_mode:
                    self.shapes.clear()
                    self.undo_stack.clear()
                    self.redo_stack.clear()
                self.shapes.append(self.current_shape)
                self.undo_stack.append(self.current_shape)
                self.redo_stack.clear() # Clear redo stack on new action
            self.current_shape = None
            self.update()

    def undo(self):
        if self.undo_stack:
            shape = self.undo_stack.pop()
            self.shapes.remove(shape)
            self.redo_stack.append(shape)
            self.update()

    def redo(self):
        if self.redo_stack:
            shape = self.redo_stack.pop()
            self.shapes.append(shape)
            self.undo_stack.append(shape)
            self.update()

    def clear_canvas(self):
        self.shapes.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update()

    def to_json_data(self):
        """将画布内容导出为JSON数据"""
        serialized_shapes = []
        for shape in self.shapes:
            serialized_shapes.append(shape.to_dict())
        return json.dumps(serialized_shapes, indent=2)

    def from_json_data(self, json_data):
        """从JSON数据导入画布内容"""
        self.clear_canvas() # Clear current canvas before loading
        try:
            data = json.loads(json_data)
            for shape_data in data:
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
                elif shape_type == "LaserPointer":
                    shape = LaserPointer.from_dict(shape_dict)
                else:
                    continue # Skip unknown shape types
                
                self.shapes.append(shape)
                self.undo_stack.append(shape)
            self.update()
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"导入数据时出错: {e}")
            raise

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

