"""
高级形状类 - 箭头、自由绘制、填充自由绘制
"""
import math
from PyQt5.QtGui import QColor, QPen, QPainterPath, QPolygonF
from PyQt5.QtCore import QPointF
from .base import Shape


class Arrow(Shape):
    def __init__(self, start_point, end_point, **kwargs):
        super().__init__(**kwargs)
        self.start_point = start_point
        self.end_point = end_point

    def draw(self, painter):
        # Calculate angle of the line from start to end
        dx = self.end_point.x() - self.start_point.x()
        dy = self.end_point.y() - self.start_point.y()
        
        # Avoid division by zero for very short lines
        if abs(dx) < 0.1 and abs(dy) < 0.1:
            return
        
        # Calculate angle in radians
        angle_rad = math.atan2(dy, dx)
        
        # Arrow parameters
        arrow_size = max(15, self.thickness * 2)  # 根据线条粗细调整箭头大小
        arrow_angle = 30
        
        # Calculate the shortened end point for the main line
        # This prevents the main line from overlapping with the arrowhead
        shortened_end = QPointF(
            self.end_point.x() - arrow_size * 0.7 * math.cos(angle_rad),
            self.end_point.y() - arrow_size * 0.7 * math.sin(angle_rad)
        )
        
        # Calculate the arrowhead triangle points
        wing1_angle = angle_rad + math.radians(180 - arrow_angle)
        wing1_end = QPointF(
            self.end_point.x() + arrow_size * math.cos(wing1_angle),
            self.end_point.y() + arrow_size * math.sin(wing1_angle)
        )
        
        wing2_angle = angle_rad + math.radians(180 + arrow_angle)
        wing2_end = QPointF(
            self.end_point.x() + arrow_size * math.cos(wing2_angle),
            self.end_point.y() + arrow_size * math.sin(wing2_angle)
        )
        
        # Save current brush and pen state
        old_brush = painter.brush()
        old_pen = painter.pen()
        
        # Calculate the exact point where the line should end
        # We need to find where the arrow base intersects with the line
        # The arrow base is the line connecting wing1_end and wing2_end
        
        # Calculate the midpoint of the arrow base
        arrow_base_mid = QPointF(
            (wing1_end.x() + wing2_end.x()) / 2,
            (wing1_end.y() + wing2_end.y()) / 2
        )
        
        # The line should end at this base midpoint, accounting for line thickness
        # Move back slightly more to ensure no overlap even with thick lines
        line_end = QPointF(
            arrow_base_mid.x() - (self.thickness / 2 + 2) * math.cos(angle_rad),
            arrow_base_mid.y() - (self.thickness / 2 + 2) * math.sin(angle_rad)
        )
        
        # Draw the main line
        painter.setPen(self.pen)
        painter.drawLine(self.start_point, line_end)
        
        # Draw the arrowhead with thin outline for sharpness
        arrowhead = QPolygonF([self.end_point, wing1_end, wing2_end])
        
        # Use a thin pen for sharp edges
        arrow_pen = QPen(self.color, max(1, int(self.thickness * 0.2)))  # Even thinner for very sharp edges
        painter.setPen(arrow_pen)
        painter.setBrush(self.color)
        painter.drawPolygon(arrowhead)
        
        # Restore original brush and pen state
        painter.setBrush(old_brush)
        painter.setPen(old_pen)

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


class Freehand(Shape):
    def __init__(self, points, **kwargs):
        super().__init__(**kwargs)
        self.points = points # List of QPointF

    def draw(self, painter):
        painter.setPen(self.pen)
        if len(self.points) > 1:
            path = QPainterPath()
            path.moveTo(self.points[0])
            for i in range(1, len(self.points)):
                path.lineTo(self.points[i])
            painter.drawPath(path)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'points': [{'x': p.x(), 'y': p.y()} for p in self.points]
        })
        return data

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        points = [QPointF(p['x'], p['y']) for p in data['points']]
        return cls(points, color=color, thickness=data["thickness"], opacity=data["opacity"])


class FilledFreehand(Shape):
    def __init__(self, points, **kwargs):
        super().__init__(**kwargs)
        self.points = points # List of QPointF

    def draw(self, painter):
        # 保存当前画笔状态
        old_pen = painter.pen()
        old_brush = painter.brush()
        
        painter.setPen(self.pen)
        painter.setBrush(self.color)  # 设置填充颜色
        
        if len(self.points) > 2:  # 至少需要3个点才能形成一个封闭区域
            path = QPainterPath()
            path.moveTo(self.points[0])
            for i in range(1, len(self.points)):
                path.lineTo(self.points[i])
            path.closeSubpath()  # 封闭路径以便填充
            painter.drawPath(path)
        elif len(self.points) > 1:
            # 如果点数不足，只绘制线条
            path = QPainterPath()
            path.moveTo(self.points[0])
            for i in range(1, len(self.points)):
                path.lineTo(self.points[i])
            painter.drawPath(path)
        
        # 恢复原始画笔状态
        painter.setPen(old_pen)
        painter.setBrush(old_brush)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'points': [{'x': p.x(), 'y': p.y()} for p in self.points]
        })
        return data

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        points = [QPointF(p['x'], p['y']) for p in data['points']]
        return cls(points, color=color, thickness=data["thickness"], opacity=data["opacity"])
