"""
标尺相关形状类 - 直线标尺和圆形标尺
"""
import math
from PyQt5.QtGui import QColor, QPen, QFont, QFontMetrics
from PyQt5.QtCore import QPointF, QRectF
from .base import Shape


class RulerBase(Shape):
    """标尺基类，处理标尺的公共功能"""
    
    def __init__(self, pixel_length=100, real_length=10.0, unit="cm", **kwargs):
        super().__init__(**kwargs)
        self.pixel_length = pixel_length  # 像素长度
        self.real_length = real_length    # 实际长度（浮点数）
        self.unit = unit                  # 单位
        self.show_label = True            # 是否显示标签
        self.label_font = QFont("Arial", 10)  # 标签字体
        
    def get_scale_factor(self):
        """获取缩放因子（实际长度/像素长度）"""
        if self.pixel_length == 0:
            return 1.0
        return self.real_length / self.pixel_length
    
    def calculate_actual_length(self, pixel_length):
        """根据像素长度计算实际长度"""
        return pixel_length * self.get_scale_factor()
    
    def format_length(self, length):
        """格式化长度显示"""
        if length < 1:
            return f"{length:.2f} {self.unit}"
        elif length < 10:
            return f"{length:.1f} {self.unit}"
        else:
            return f"{length:.0f} {self.unit}"
    
    def draw_label(self, painter, text, position):
        """绘制标签"""
        if not self.show_label:
            return
            
        # 保存当前状态
        old_pen = painter.pen()
        old_font = painter.font()
        
        # 设置标签样式
        label_color = QColor(self.base_color)
        label_color.setAlphaF(self.opacity)
        painter.setPen(QPen(label_color))
        painter.setFont(self.label_font)
        
        # 计算文本尺寸
        metrics = QFontMetrics(self.label_font)
        text_rect = metrics.boundingRect(text)
        
        # 绘制背景
        bg_color = QColor(255, 255, 255, 200)  # 半透明白色背景
        painter.fillRect(
            int(position.x() - text_rect.width() // 2 - 2),
            int(position.y() - text_rect.height() // 2 - 2),
            text_rect.width() + 4,
            text_rect.height() + 4,
            bg_color
        )
        
        # 绘制文本
        painter.drawText(
            int(position.x() - text_rect.width() // 2),
            int(position.y() + text_rect.height() // 2),
            text
        )
        
        # 恢复状态
        painter.setPen(old_pen)
        painter.setFont(old_font)


class LineRuler(RulerBase):
    """直线标尺"""
    
    def __init__(self, start_point, end_point, pixel_length=100, real_length=10, unit="cm", **kwargs):
        super().__init__(pixel_length=pixel_length, real_length=real_length, unit=unit, **kwargs)
        self.start_point = start_point
        self.end_point = end_point
        self.show_ticks = True  # 是否显示刻度
        self.tick_count = 10    # 刻度数量
        
    def get_length(self):
        """获取直线的像素长度"""
        dx = self.end_point.x() - self.start_point.x()
        dy = self.end_point.y() - self.start_point.y()
        return math.sqrt(dx * dx + dy * dy)
    
    def get_actual_length(self):
        """获取实际长度"""
        pixel_len = self.get_length()
        return self.calculate_actual_length(pixel_len)
    
    def draw(self, painter):
        painter.setPen(self.pen)
        
        # 绘制主线
        painter.drawLine(self.start_point, self.end_point)
        
        # 绘制刻度
        if self.show_ticks:
            self.draw_ticks(painter)
        
        # 绘制长度标签
        if self.show_label:
            actual_length = self.get_actual_length()
            label_text = self.format_length(actual_length)
            
            # 标签位置在直线中点
            mid_x = (self.start_point.x() + self.end_point.x()) / 2
            mid_y = (self.start_point.y() + self.end_point.y()) / 2
            
            # 偏移标签位置避免与直线重叠
            dx = self.end_point.x() - self.start_point.x()
            dy = self.end_point.y() - self.start_point.y()
            length = math.sqrt(dx * dx + dy * dy)
            
            if length > 0:
                # 垂直方向偏移
                offset_x = -dy / length * 15  # 垂直偏移15像素
                offset_y = dx / length * 15
                
                label_pos = QPointF(mid_x + offset_x, mid_y + offset_y)
                self.draw_label(painter, label_text, label_pos)
    
    def draw_ticks(self, painter):
        """绘制刻度"""
        if self.tick_count <= 0:
            return
            
        # 计算刻度位置
        for i in range(self.tick_count + 1):
            t = i / self.tick_count
            tick_x = self.start_point.x() + t * (self.end_point.x() - self.start_point.x())
            tick_y = self.start_point.y() + t * (self.end_point.y() - self.start_point.y())
            
            # 计算刻度线的垂直方向
            dx = self.end_point.x() - self.start_point.x()
            dy = self.end_point.y() - self.start_point.y()
            length = math.sqrt(dx * dx + dy * dy)
            
            if length > 0:
                # 刻度线长度
                tick_length = 5 if i % 5 == 0 else 3  # 每5个刻度一个长刻度
                
                # 垂直方向单位向量
                perp_x = -dy / length * tick_length
                perp_y = dx / length * tick_length
                
                # 绘制刻度线
                painter.drawLine(
                    QPointF(tick_x - perp_x, tick_y - perp_y),
                    QPointF(tick_x + perp_x, tick_y + perp_y)
                )
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'start_point_x': self.start_point.x(),
            'start_point_y': self.start_point.y(),
            'end_point_x': self.end_point.x(),
            'end_point_y': self.end_point.y(),
            'pixel_length': self.pixel_length,
            'real_length': self.real_length,
            'unit': self.unit,
            'show_ticks': self.show_ticks,
            'tick_count': self.tick_count
        })
        return data

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        start_point = QPointF(data["start_point_x"], data["start_point_y"])
        end_point = QPointF(data["end_point_x"], data["end_point_y"])
        return cls(
            start_point, end_point,
            pixel_length=data.get("pixel_length", 100),
            real_length=data.get("real_length", 10),
            unit=data.get("unit", "cm"),
            color=color,
            thickness=data["thickness"],
            opacity=data["opacity"]
        )


class CircleRuler(RulerBase):
    """圆形标尺"""
    
    def __init__(self, center_point, radius, pixel_length=100, real_length=10, unit="cm", **kwargs):
        super().__init__(pixel_length=pixel_length, real_length=real_length, unit=unit, **kwargs)
        self.center_point = center_point
        self.radius = radius
        self.show_diameter_line = True  # 是否显示直径线
        
    def get_diameter(self):
        """获取直径的像素长度"""
        return self.radius * 2
    
    def get_actual_diameter(self):
        """获取实际直径"""
        pixel_diameter = self.get_diameter()
        return self.calculate_actual_length(pixel_diameter)
    
    def draw(self, painter):
        painter.setPen(self.pen)
        
        # 绘制圆形
        painter.drawEllipse(self.center_point, self.radius, self.radius)
        
        # 绘制直径线
        if self.show_diameter_line:
            painter.drawLine(
                QPointF(self.center_point.x() - self.radius, self.center_point.y()),
                QPointF(self.center_point.x() + self.radius, self.center_point.y())
            )
            painter.drawLine(
                QPointF(self.center_point.x(), self.center_point.y() - self.radius),
                QPointF(self.center_point.x(), self.center_point.y() + self.radius)
            )
        
        # 绘制直径标签
        if self.show_label:
            actual_diameter = self.get_actual_diameter()
            label_text = f"⌀{self.format_length(actual_diameter)}"
            
            # 标签位置在圆心上方
            label_pos = QPointF(self.center_point.x(), self.center_point.y() - self.radius - 20)
            self.draw_label(painter, label_text, label_pos)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'center_point_x': self.center_point.x(),
            'center_point_y': self.center_point.y(),
            'radius': self.radius,
            'pixel_length': self.pixel_length,
            'real_length': self.real_length,
            'unit': self.unit,
            'show_diameter_line': self.show_diameter_line
        })
        return data

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        center_point = QPointF(data["center_point_x"], data["center_point_y"])
        radius = data["radius"]
        return cls(
            center_point, radius,
            pixel_length=data.get("pixel_length", 100),
            real_length=data.get("real_length", 10),
            unit=data.get("unit", "cm"),
            color=color,
            thickness=data["thickness"],
            opacity=data["opacity"]
        )
