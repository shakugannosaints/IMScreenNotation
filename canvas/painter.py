"""
Canvas painting and rendering functionality
"""
from PyQt5.QtGui import QPainter, QColor


class CanvasPainter:
    """处理画布的绘制和渲染"""
    
    def __init__(self, canvas):
        self.canvas = canvas

    def paint_canvas(self, painter: QPainter):
        """绘制整个画布"""
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw canvas background with current color and opacity
        # 如果画布完全透明，绘制一个几乎透明的背景来确保鼠标事件可以被接收
        if self.canvas.properties.canvas_color.alpha() == 0:
            # 绘制一个几乎透明的背景 (alpha = 1) 来接收鼠标事件
            transparent_bg = QColor(0, 0, 0, 1)  # 几乎透明的黑色
            painter.fillRect(self.canvas.rect(), transparent_bg)
        else:
            painter.fillRect(self.canvas.rect(), self.canvas.properties.canvas_color)

        # Draw all shapes
        for shape in self.canvas.shapes:
            shape.draw(painter)

        # Draw current shape being drawn
        if self.canvas.current_shape:
            self.canvas.current_shape.draw(painter)
