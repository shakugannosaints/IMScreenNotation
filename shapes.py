from PyQt5.QtGui import QColor, QPen, QPainterPath
from PyQt5.QtCore import QPointF, QRectF, QDateTime
import math

class Shape:
    def __init__(self, color=QColor(255, 0, 0, 255), thickness=3, opacity=1.0):
        self.base_color = color  # 保存原始颜色，不包含透明度
        self.thickness = thickness
        self.opacity = opacity
        self._update_pen()

    def _update_pen(self):
        """更新画笔，应用当前的透明度设置"""
        # 创建一个新的颜色对象，应用透明度
        drawing_color = QColor(self.base_color)
        drawing_color.setAlphaF(self.opacity)
        self.pen = QPen(drawing_color)
        self.pen.setWidth(self.thickness)

    @property 
    def color(self):
        """获取当前绘制颜色（包含透明度）"""
        drawing_color = QColor(self.base_color)
        drawing_color.setAlphaF(self.opacity)
        return drawing_color

    def set_color(self, color):
        self.base_color = QColor(color)  # 复制颜色以避免意外修改
        self._update_pen()

    def set_thickness(self, thickness):
        self.thickness = thickness
        self._update_pen()

    def set_opacity(self, opacity):
        self.opacity = opacity
        self._update_pen()

    def draw(self, painter):
        raise NotImplementedError

    def to_dict(self):
        return {
            'type': self.__class__.__name__,
            'color': self.base_color.getRgb(),
            'thickness': self.thickness,
            'opacity': self.opacity
        }

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        return cls(color=color, thickness=data["thickness"], opacity=data["opacity"])

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

class Arrow(Shape):
    def __init__(self, start_point, end_point, **kwargs):
        super().__init__(**kwargs)
        self.start_point = start_point
        self.end_point = end_point

    def draw(self, painter):
        painter.setPen(self.pen)
        painter.drawLine(self.start_point, self.end_point)
        
        # Draw arrowhead
        # Calculate angle of the line from start to end
        dx = self.end_point.x() - self.start_point.x()
        dy = self.end_point.y() - self.start_point.y()
        
        # Avoid division by zero for very short lines
        if abs(dx) < 0.1 and abs(dy) < 0.1:
            return
        
        # Calculate angle in radians first, then convert to degrees
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        arrow_size = 15
        arrow_angle = 30

        # Calculate the two arrow wing endpoints
        # First wing - rotate backwards by (180 - arrow_angle) degrees
        wing1_angle = angle_rad + math.radians(180 - arrow_angle)
        wing1_end = QPointF(
            self.end_point.x() + arrow_size * math.cos(wing1_angle),
            self.end_point.y() + arrow_size * math.sin(wing1_angle)
        )

        # Second wing - rotate backwards by (180 + arrow_angle) degrees  
        wing2_angle = angle_rad + math.radians(180 + arrow_angle)
        wing2_end = QPointF(
            self.end_point.x() + arrow_size * math.cos(wing2_angle),
            self.end_point.y() + arrow_size * math.sin(wing2_angle)
        )

        # Draw the arrow wings
        painter.drawLine(self.end_point, wing1_end)
        painter.drawLine(self.end_point, wing2_end)

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

class LaserPointer(Shape):
    def __init__(self, center_point, radius=10, duration=500, **kwargs):
        super().__init__(**kwargs)
        self.center_point = center_point
        self.radius = radius
        self.start_time = QDateTime.currentMSecsSinceEpoch() # Set start time when created
        self.duration = duration # in milliseconds

    def draw(self, painter):
        elapsed_time = QDateTime.currentMSecsSinceEpoch() - self.start_time
        if elapsed_time > self.duration:
            return # Laser pointer disappears after duration

        # Simple pulsating effect (optional)
        pulse_factor = (self.duration - elapsed_time) / self.duration
        current_alpha = self.opacity * pulse_factor
        
        # 创建脉冲效果的颜色
        current_color = QColor(self.base_color)
        current_color.setAlphaF(current_alpha)

        painter.setPen(QPen(current_color, self.thickness))
        painter.setBrush(current_color)
        painter.drawEllipse(self.center_point, self.radius, self.radius)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'center_point_x': self.center_point.x(),
            'center_point_y': self.center_point.y(),
            'radius': self.radius,
            'duration': self.duration,
            'start_time': self.start_time # Include start_time for accurate reconstruction
        })
        return data

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        center_point = QPointF(data["center_point_x"], data["center_point_y"])
        radius = data["radius"]
        duration = data["duration"]
        start_time = data["start_time"]
        # When loading, we need to adjust the start_time to make the laser pointer visible again
        # This is a simplified approach; a more robust solution might involve re-triggering the animation
        instance = cls(center_point, radius, duration=duration, color=color, thickness=data["thickness"], opacity=data["opacity"])
        instance.start_time = start_time # Restore original start time
        return instance


