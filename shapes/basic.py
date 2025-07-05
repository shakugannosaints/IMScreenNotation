"""
基本几何形状类 - 直线、矩形、圆形、点
"""
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPointF, QRectF
from .base import Shape


class Line(Shape):
    def __init__(self, start_point, end_point, **kwargs):
        super().__init__(**kwargs)
        self.start_point = start_point
        self.end_point = end_point

    def draw(self, painter):
        painter.setPen(self.pen)
        painter.drawLine(self.start_point, self.end_point)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'start_point_x': self.start_point.x(),
            'start_point_y': self.start_point.y(),
            'end_point_x': self.end_point.x(),
            'end_point_y': self.end_point.y()
        })
        return data

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        start_point = QPointF(data["start_point_x"], data["start_point_y"])
        end_point = QPointF(data["end_point_x"], data["end_point_y"])
        return cls(start_point, end_point, color=color, thickness=data["thickness"], opacity=data["opacity"])


class Rectangle(Shape):
    def __init__(self, rect, **kwargs):
        super().__init__(**kwargs)
        self.rect = rect

    def draw(self, painter):
        painter.setPen(self.pen)
        painter.drawRect(self.rect)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'rect_x': self.rect.x(),
            'rect_y': self.rect.y(),
            'rect_width': self.rect.width(),
            'rect_height': self.rect.height()
        })
        return data

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        rect = QRectF(data["rect_x"], data["rect_y"], data["rect_width"], data["rect_height"])
        return cls(rect, color=color, thickness=data["thickness"], opacity=data["opacity"])


class Circle(Shape):
    def __init__(self, center_point, radius, **kwargs):
        super().__init__(**kwargs)
        self.center_point = center_point
        self.radius = radius

    def draw(self, painter):
        painter.setPen(self.pen)
        painter.drawEllipse(self.center_point, self.radius, self.radius)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'center_point_x': self.center_point.x(),
            'center_point_y': self.center_point.y(),
            'radius': self.radius
        })
        return data

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        center_point = QPointF(data["center_point_x"], data["center_point_y"])
        radius = data["radius"]
        return cls(center_point, radius, color=color, thickness=data["thickness"], opacity=data["opacity"])


class Point(Shape):
    def __init__(self, center_point, radius=3, **kwargs):
        super().__init__(**kwargs)
        self.center_point = center_point
        self.radius = radius

    def draw(self, painter):
        # 保存当前画笔状态
        old_pen = painter.pen()
        old_brush = painter.brush()
        
        painter.setPen(self.pen)
        painter.setBrush(self.color)  # 使用包含透明度的颜色
        painter.drawEllipse(self.center_point, self.radius, self.radius)
        
        # 恢复原始画笔状态
        painter.setPen(old_pen)
        painter.setBrush(old_brush)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'center_point_x': self.center_point.x(),
            'center_point_y': self.center_point.y(),
            'radius': self.radius
        })
        return data

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        center_point = QPointF(data["center_point_x"], data["center_point_y"])
        radius = data["radius"]
        return cls(center_point, radius, color=color, thickness=data["thickness"], opacity=data["opacity"])
