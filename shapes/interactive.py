"""
交互式形状类 - 文本、激光笔、橡皮擦
"""
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QFontMetrics
from PyQt5.QtCore import QPointF, QRectF, QDateTime, Qt
from .base import Shape


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


class Eraser(Shape):
    """橡皮擦类 - 用圆形表示擦除区域"""
    
    def __init__(self, points, **kwargs):
        # 橡皮擦不需要颜色，只需要大小信息
        super().__init__(**kwargs)
        self.points = points  # 擦除路径上的点
        # 橡皮擦是特殊的形状，用于标记需要删除的区域
        
    def draw(self, painter):
        """绘制橡皮擦预览 - 显示为半透明的圆形"""
        if not self.points:
            return
            
        # 保存当前状态
        old_pen = painter.pen()
        old_brush = painter.brush()
        
        # 设置橡皮擦预览样式 - 半透明的白色圆圈
        preview_color = QColor(255, 255, 255, 100)  # 半透明白色
        preview_pen = QPen(preview_color, 2, Qt.DashLine)
        preview_brush = QBrush(QColor(255, 255, 255, 50))  # 更透明的填充
        
        painter.setPen(preview_pen)
        painter.setBrush(preview_brush)
        
        # 在每个点绘制圆形橡皮擦预览
        radius = self.thickness * 2  # 橡皮擦大小基于粗细设置
        for point in self.points:
            painter.drawEllipse(point, radius, radius)
        
        # 恢复状态
        painter.setPen(old_pen)
        painter.setBrush(old_brush)
    
    def to_dict(self):
        """序列化为字典 - 橡皮擦不需要保存，因为它是删除操作"""
        data = super().to_dict()
        data.update({
            'points': [{'x': p.x(), 'y': p.y()} for p in self.points]
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """从字典反序列化 - 橡皮擦通常不需要从文件恢复"""
        color = QColor(*data["color"])
        points = [QPointF(p['x'], p['y']) for p in data['points']]
        return cls(points, color=color, thickness=data["thickness"], opacity=data["opacity"])
    
    def get_eraser_radius(self):
        """获取橡皮擦半径"""
        return self.thickness * 2
    
    def intersects_with_shape(self, shape):
        """检查橡皮擦是否与指定形状相交"""
        if not self.points:
            return False
            
        eraser_radius = self.get_eraser_radius()
        
        # 对于不同类型的形状，使用不同的相交检测算法
        from .basic import Point, Line, Rectangle, Circle
        from .advanced import Freehand, FilledFreehand, Arrow
        from .ruler import LineRuler, CircleRuler
        from .image import Image
        
        if isinstance(shape, Point):
            return self._intersects_with_point(shape, eraser_radius)
        elif isinstance(shape, (Freehand, FilledFreehand)):
            return self._intersects_with_freehand(shape, eraser_radius)
        elif isinstance(shape, Line):
            return self._intersects_with_line(shape, eraser_radius)
        elif isinstance(shape, Rectangle):
            return self._intersects_with_rectangle(shape, eraser_radius)
        elif isinstance(shape, Circle):
            return self._intersects_with_circle(shape, eraser_radius)
        elif isinstance(shape, Arrow):
            return self._intersects_with_arrow(shape, eraser_radius)
        elif isinstance(shape, Text):
            return self._intersects_with_text(shape, eraser_radius)
        elif isinstance(shape, LineRuler):
            return self._intersects_with_line_ruler(shape, eraser_radius)
        elif isinstance(shape, CircleRuler):
            return self._intersects_with_circle_ruler(shape, eraser_radius)
        elif isinstance(shape, Image):
            return self._intersects_with_image(shape, eraser_radius)
        else:
            return False
    
    def _intersects_with_point(self, point_shape, eraser_radius):
        """检查与点的相交"""
        for eraser_point in self.points:
            distance = ((eraser_point.x() - point_shape.center_point.x())**2 + 
                       (eraser_point.y() - point_shape.center_point.y())**2)**0.5
            if distance <= eraser_radius + point_shape.thickness:
                return True
        return False
    
    def _intersects_with_freehand(self, freehand_shape, eraser_radius):
        """检查与自由绘制的相交"""
        for eraser_point in self.points:
            for shape_point in freehand_shape.points:
                distance = ((eraser_point.x() - shape_point.x())**2 + 
                           (eraser_point.y() - shape_point.y())**2)**0.5
                if distance <= eraser_radius + freehand_shape.thickness:
                    return True
        return False
    
    def _intersects_with_line(self, line_shape, eraser_radius):
        """检查与直线的相交"""
        for eraser_point in self.points:
            # 计算点到线段的距离
            if self._point_to_line_distance(eraser_point, line_shape.start_point, line_shape.end_point) <= eraser_radius + line_shape.thickness:
                return True
        return False
    
    def _intersects_with_rectangle(self, rect_shape, eraser_radius):
        """检查与矩形的相交"""
        rect = rect_shape.rect
        for eraser_point in self.points:
            # 检查点是否在矩形内或距离矩形边缘足够近
            if (rect.contains(eraser_point) or 
                self._point_to_rect_distance(eraser_point, rect) <= eraser_radius + rect_shape.thickness):
                return True
        return False
    
    def _intersects_with_circle(self, circle_shape, eraser_radius):
        """检查与圆形的相交"""
        for eraser_point in self.points:
            center_distance = ((eraser_point.x() - circle_shape.center_point.x())**2 + 
                              (eraser_point.y() - circle_shape.center_point.y())**2)**0.5
            # 检查橡皮擦是否与圆的边缘相交
            if abs(center_distance - circle_shape.radius) <= eraser_radius + circle_shape.thickness:
                return True
        return False
    
    def _intersects_with_arrow(self, arrow_shape, eraser_radius):
        """检查与箭头的相交"""
        # 箭头主要由线段组成，检查与线段的相交
        return self._intersects_with_line(arrow_shape, eraser_radius)
    
    def _intersects_with_text(self, text_shape, eraser_radius):
        """检查与文本的相交"""
        for eraser_point in self.points:
            # 简单的文本边界框检测
            distance = ((eraser_point.x() - text_shape.position.x())**2 + 
                       (eraser_point.y() - text_shape.position.y())**2)**0.5
            if distance <= eraser_radius + 20:  # 给文本一个固定的检测范围
                return True
        return False
    
    def _intersects_with_line_ruler(self, ruler_shape, eraser_radius):
        """检查与直线标尺的相交"""
        # 直线标尺主要由主线和刻度线组成
        # 首先检查与主线的相交
        for eraser_point in self.points:
            # 检查与主线的相交
            if self._point_to_line_distance(eraser_point, ruler_shape.start_point, ruler_shape.end_point) <= eraser_radius + ruler_shape.thickness:
                return True
            
            # 检查与刻度线的相交（如果显示刻度）
            if hasattr(ruler_shape, 'show_ticks') and ruler_shape.show_ticks:
                if self._intersects_with_ruler_ticks(eraser_point, ruler_shape, eraser_radius):
                    return True
        return False
    
    def _intersects_with_circle_ruler(self, ruler_shape, eraser_radius):
        """检查与圆形标尺的相交"""
        for eraser_point in self.points:
            center_distance = ((eraser_point.x() - ruler_shape.center_point.x())**2 + 
                              (eraser_point.y() - ruler_shape.center_point.y())**2)**0.5
            
            # 检查橡皮擦是否与圆的边缘相交
            if abs(center_distance - ruler_shape.radius) <= eraser_radius + ruler_shape.thickness:
                return True
                
            # 检查与直径线的相交（如果显示直径线）
            if hasattr(ruler_shape, 'show_diameter_line') and ruler_shape.show_diameter_line:
                # 水平直径线
                horizontal_start = QPointF(ruler_shape.center_point.x() - ruler_shape.radius, ruler_shape.center_point.y())
                horizontal_end = QPointF(ruler_shape.center_point.x() + ruler_shape.radius, ruler_shape.center_point.y())
                if self._point_to_line_distance(eraser_point, horizontal_start, horizontal_end) <= eraser_radius + ruler_shape.thickness:
                    return True
                    
                # 垂直直径线
                vertical_start = QPointF(ruler_shape.center_point.x(), ruler_shape.center_point.y() - ruler_shape.radius)
                vertical_end = QPointF(ruler_shape.center_point.x(), ruler_shape.center_point.y() + ruler_shape.radius)
                if self._point_to_line_distance(eraser_point, vertical_start, vertical_end) <= eraser_radius + ruler_shape.thickness:
                    return True
        return False
    
    def _intersects_with_ruler_ticks(self, eraser_point, ruler_shape, eraser_radius):
        """检查与标尺刻度线的相交"""
        if not hasattr(ruler_shape, 'show_ticks') or not ruler_shape.show_ticks:
            return False
        
        # 使用新的刻度间隔逻辑
        if hasattr(ruler_shape, 'tick_interval') and ruler_shape.tick_interval > 0:
            return self._intersects_with_interval_ticks(eraser_point, ruler_shape, eraser_radius)
        
        return False
    
    def _intersects_with_interval_ticks(self, eraser_point, ruler_shape, eraser_radius):
        """检查与按间隔绘制的刻度线的相交"""
        import math
        
        # 获取标尺的实际长度和像素长度
        dx = ruler_shape.end_point.x() - ruler_shape.start_point.x()
        dy = ruler_shape.end_point.y() - ruler_shape.start_point.y()
        total_pixel_length = math.sqrt(dx * dx + dy * dy)
        
        if total_pixel_length == 0:
            return False
        
        # 计算单位向量
        unit_x = dx / total_pixel_length
        unit_y = dy / total_pixel_length
        perp_unit_x = -unit_y
        perp_unit_y = unit_x
        
        # 计算刻度间隔对应的像素距离
        scale_factor = ruler_shape.get_scale_factor()
        pixel_interval = ruler_shape.tick_interval / scale_factor
        
        # 检查起点刻度
        if self._check_single_tick_intersection(eraser_point, ruler_shape.start_point, perp_unit_x, perp_unit_y, True, eraser_radius, ruler_shape.thickness):
            return True
        
        # 检查中间刻度
        current_distance = pixel_interval
        tick_index = 1
        
        while current_distance < total_pixel_length:
            tick_x = ruler_shape.start_point.x() + unit_x * current_distance
            tick_y = ruler_shape.start_point.y() + unit_y * current_distance
            tick_pos = QPointF(tick_x, tick_y)
            
            # 判断是否为主刻度
            actual_distance = current_distance * scale_factor
            is_major = (tick_index % 5 == 0) or (abs(actual_distance - round(actual_distance)) < 0.01)
            
            if self._check_single_tick_intersection(eraser_point, tick_pos, perp_unit_x, perp_unit_y, is_major, eraser_radius, ruler_shape.thickness):
                return True
            
            current_distance += pixel_interval
            tick_index += 1
        
        # 检查终点刻度
        if total_pixel_length - (current_distance - pixel_interval) > pixel_interval * 0.1:
            if self._check_single_tick_intersection(eraser_point, ruler_shape.end_point, perp_unit_x, perp_unit_y, True, eraser_radius, ruler_shape.thickness):
                return True
        
        return False
    
    def _check_single_tick_intersection(self, eraser_point, tick_pos, perp_unit_x, perp_unit_y, is_major, eraser_radius, thickness):
        """检查单个刻度线的相交"""
        # 刻度线长度
        tick_length = 8 if is_major else 4
        half_length = tick_length / 2
        
        # 计算刻度线端点
        start_x = tick_pos.x() - perp_unit_x * half_length
        start_y = tick_pos.y() - perp_unit_y * half_length
        end_x = tick_pos.x() + perp_unit_x * half_length
        end_y = tick_pos.y() + perp_unit_y * half_length
        
        tick_start = QPointF(start_x, start_y)
        tick_end = QPointF(end_x, end_y)
        
        # 检查与刻度线的相交
        return self._point_to_line_distance(eraser_point, tick_start, tick_end) <= eraser_radius + thickness
    
    def _point_to_line_distance(self, point, line_start, line_end):
        """计算点到线段的最短距离"""
        # 向量计算
        line_vec = QPointF(line_end.x() - line_start.x(), line_end.y() - line_start.y())
        point_vec = QPointF(point.x() - line_start.x(), point.y() - line_start.y())
        
        line_len_sq = line_vec.x()**2 + line_vec.y()**2
        if line_len_sq == 0:
            # 线段退化为点
            return ((point.x() - line_start.x())**2 + (point.y() - line_start.y())**2)**0.5
        
        # 投影比例
        t = max(0, min(1, (point_vec.x() * line_vec.x() + point_vec.y() * line_vec.y()) / line_len_sq))
        
        # 投影点
        projection = QPointF(line_start.x() + t * line_vec.x(), line_start.y() + t * line_vec.y())
        
        # 距离
        return ((point.x() - projection.x())**2 + (point.y() - projection.y())**2)**0.5
    
    def _point_to_rect_distance(self, point, rect):
        """计算点到矩形的最短距离"""
        # 如果点在矩形内，距离为0
        if rect.contains(point):
            return 0
        
        # 计算到矩形边的最短距离
        dx = max(0, max(rect.left() - point.x(), point.x() - rect.right()))
        dy = max(0, max(rect.top() - point.y(), point.y() - rect.bottom()))
        
        return (dx**2 + dy**2)**0.5
    
    def _intersects_with_image(self, image_shape, eraser_radius):
        """检查与图片的相交"""
        # 获取图片的边界矩形
        image_rect = image_shape.get_bounding_rect()
        
        # 如果图片没有有效的边界矩形，不相交
        if image_rect.isNull() or image_rect.isEmpty():
            return False
        
        # 检查橡皮擦的每个点是否与图片区域相交
        for eraser_point in self.points:
            distance = self._point_to_rect_distance(eraser_point, image_rect)
            if distance <= eraser_radius:
                return True
        
        return False
