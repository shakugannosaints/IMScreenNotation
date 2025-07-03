from PyQt5.QtGui import QColor, QPen, QPainterPath, QPolygonF, QFont, QFontMetrics
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

class Text(Shape):
    def __init__(self, position, text="", font_family="Arial", font_size=16, 
                 font_bold=False, font_italic=False, text_color=None,
                 background_color=None, border_color=None, border_enabled=True,
                 border_width=1, padding=5, **kwargs):
        super().__init__(**kwargs)
        self.position = position
        self.text = text
        self.font_family = font_family
        self.font_size = font_size
        self.font_bold = font_bold
        self.font_italic = font_italic
        
        # 文本颜色，如果未指定则使用基础颜色
        if text_color:
            if isinstance(text_color, list):
                self.text_color = QColor(*text_color)
            else:
                self.text_color = QColor(text_color)
        else:
            self.text_color = self.base_color
        
        # 背景和边框样式
        if background_color:
            if isinstance(background_color, list):
                self.background_color = QColor(*background_color)
            else:
                self.background_color = QColor(background_color)
        else:
            self.background_color = None
            
        if border_color:
            if isinstance(border_color, list):
                self.border_color = QColor(*border_color)
            else:
                self.border_color = QColor(border_color)
        else:
            self.border_color = None
        self.border_enabled = border_enabled
        self.border_width = border_width
        self.padding = padding
        
        # 计算文本边界
        self._calculate_bounds()
    
    def _calculate_bounds(self):
        """计算文本的边界矩形"""
        font = QFont(self.font_family, self.font_size)
        font.setBold(self.font_bold)
        font.setItalic(self.font_italic)
        
        # 使用QFontMetrics计算文本尺寸
        metrics = QFontMetrics(font)
        
        # 支持多行文本
        lines = self.text.split('\n')
        max_width = 0
        total_height = 0
        
        for line in lines:
            line_rect = metrics.boundingRect(line)
            max_width = max(max_width, line_rect.width())
            total_height += metrics.height()
        
        # 添加内边距
        self.text_rect = QRectF(
            self.position.x() - self.padding,
            self.position.y() - self.padding,
            max_width + 2 * self.padding,
            total_height + 2 * self.padding
        )

    def draw(self, painter):
        # 创建字体
        font = QFont(self.font_family, self.font_size)
        font.setBold(self.font_bold)
        font.setItalic(self.font_italic)
        painter.setFont(font)
        
        # 重新计算边界（以防文本发生变化）
        self._calculate_bounds()
        
        # 绘制背景
        if self.background_color:
            if isinstance(self.background_color, list):
                bg_color = QColor(*self.background_color)
            else:
                bg_color = QColor(self.background_color)
            bg_color.setAlphaF(self.opacity)
            painter.fillRect(self.text_rect, bg_color)
        
        # 绘制边框
        if self.border_enabled and self.border_color and self.border_width > 0:
            if isinstance(self.border_color, list):
                border_color = QColor(*self.border_color)
            else:
                border_color = QColor(self.border_color)
            border_color.setAlphaF(self.opacity)
            border_pen = QPen(border_color, self.border_width)
            painter.setPen(border_pen)
            painter.drawRect(self.text_rect)
        
        # 绘制文本
        if isinstance(self.text_color, list):
            text_color = QColor(*self.text_color)
        else:
            text_color = QColor(self.text_color)
        text_color.setAlphaF(self.opacity)
        painter.setPen(QPen(text_color))
        
        # 计算文本绘制位置
        text_x = int(self.position.x())
        text_y = int(self.position.y())
        
        # 支持多行文本
        lines = self.text.split('\n')
        font_metrics = QFontMetrics(font)
        
        for i, line in enumerate(lines):
            line_y = text_y + i * font_metrics.height() + font_metrics.ascent()
            painter.drawText(text_x, int(line_y), line)

    def set_text(self, text):
        """设置文本内容"""
        self.text = text
        self._calculate_bounds()

    def set_font_family(self, font_family):
        """设置字体族"""
        self.font_family = font_family
        self._calculate_bounds()

    def set_font_size(self, font_size):
        """设置字体大小"""
        self.font_size = font_size
        self._calculate_bounds()

    def set_font_bold(self, bold):
        """设置字体粗体"""
        self.font_bold = bold
        self._calculate_bounds()

    def set_font_italic(self, italic):
        """设置字体斜体"""
        self.font_italic = italic
        self._calculate_bounds()

    def set_text_color(self, color):
        """设置文本颜色"""
        if isinstance(color, list):
            self.text_color = QColor(*color)
        else:
            self.text_color = QColor(color)

    def set_background_color(self, color):
        """设置背景颜色"""
        if color:
            if isinstance(color, list):
                self.background_color = QColor(*color)
            else:
                self.background_color = QColor(color)
        else:
            self.background_color = None
        
    def set_border_color(self, color):
        """设置边框颜色"""
        if color:
            if isinstance(color, list):
                self.border_color = QColor(*color)
            else:
                self.border_color = QColor(color)
        else:
            self.border_color = None

    def set_border_width(self, width):
        """设置边框宽度"""
        self.border_width = width

    def set_padding(self, padding):
        """设置内边距"""
        self.padding = padding
        self._calculate_bounds()

    def contains_point(self, point):
        """检查点是否在文本区域内"""
        return self.text_rect.contains(point)

    def move_to(self, new_position):
        """移动文本到新位置"""
        self.position = new_position
        self._calculate_bounds()

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'position_x': self.position.x(),
            'position_y': self.position.y(),
            'text': self.text,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'font_bold': self.font_bold,
            'font_italic': self.font_italic,
            'text_color': self.text_color.getRgb() if self.text_color else None,
            'background_color': self.background_color.getRgb() if self.background_color else None,
            'border_color': self.border_color.getRgb() if self.border_color else None,
            'border_enabled': self.border_enabled,
            'border_width': self.border_width,
            'padding': self.padding
        })
        return data

    @classmethod
    def from_dict(cls, data):
        position = QPointF(data["position_x"], data["position_y"])
        text_color = QColor(*data["text_color"]) if data["text_color"] else None
        background_color = QColor(*data["background_color"]) if data["background_color"] else None
        border_color = QColor(*data["border_color"]) if data["border_color"] else None
        
        return cls(
            position=position,
            text=data["text"],
            font_family=data["font_family"],
            font_size=data["font_size"],
            font_bold=data["font_bold"],
            font_italic=data["font_italic"],
            text_color=text_color,
            background_color=background_color,
            border_color=border_color,
            border_enabled=data.get("border_enabled", True),  # 默认为True以保持向后兼容
            border_width=data["border_width"],
            padding=data["padding"],
            color=QColor(*data["color"]),
            thickness=data["thickness"],
            opacity=data["opacity"]
        )


