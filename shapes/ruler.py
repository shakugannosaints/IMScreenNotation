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
    
    def __init__(self, start_point, end_point, pixel_length=100, real_length=10.0, unit="cm", **kwargs):
        super().__init__(pixel_length=pixel_length, real_length=real_length, unit=unit, **kwargs)
        self.start_point = start_point
        self.end_point = end_point
        self.show_ticks = True  # 是否显示刻度
        self.tick_interval = 1.0  # 刻度间隔（实际单位）
        
    def get_length(self):
        """获取直线的像素长度"""
        dx = self.end_point.x() - self.start_point.x()
        dy = self.end_point.y() - self.start_point.y()
        return math.sqrt(dx * dx + dy * dy)
    
    def get_actual_length(self):
        """获取实际长度"""
        pixel_len = self.get_length()
        # 使用当前标尺的实际长度比例来计算
        # 如果pixel_length为0，则按1:1的比例计算
        if self.pixel_length == 0:
            return pixel_len
        return pixel_len * (self.real_length / self.pixel_length)
    
    def set_tick_interval(self, interval):
        """设置刻度间隔（实际单位）"""
        if interval > 0:
            self.tick_interval = interval
    
    def get_tick_interval(self):
        """获取当前刻度间隔"""
        return self.tick_interval
    
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
        if not self.show_ticks:
            return
            
        # 获取标尺的当前像素长度
        current_pixel_length = self.get_length()
        
        # 如果长度太短，不绘制刻度
        if current_pixel_length <= 0:
            return
        
        # 获取基准缩放因子（实际单位/像素）
        # 这个缩放因子基于构造时设定的参考长度关系
        if self.pixel_length == 0:
            scale_factor = 1.0  # 默认1像素=1单位
        else:
            scale_factor = self.real_length / self.pixel_length
        
        # 计算刻度间隔对应的像素距离
        # tick_interval是实际单位的间隔，需要转换为像素距离
        pixel_interval = self.tick_interval / scale_factor
        
        # 如果刻度间隔太小（小于1像素），不绘制刻度
        if pixel_interval < 1:
            return
        
        # 获取标尺的总像素长度
        total_pixel_length = current_pixel_length
        
        # 计算标尺方向的单位向量
        dx = self.end_point.x() - self.start_point.x()
        dy = self.end_point.y() - self.start_point.y()
        length = math.sqrt(dx * dx + dy * dy)
        
        if length == 0:
            return
            
        unit_x = dx / length
        unit_y = dy / length
        
        # 垂直方向单位向量（用于绘制刻度线）
        perp_unit_x = -unit_y
        perp_unit_y = unit_x
        
        # 绘制起点刻度（总是绘制）
        self._draw_single_tick(painter, self.start_point, perp_unit_x, perp_unit_y, True)
        
        # 绘制中间刻度
        current_distance = pixel_interval
        tick_index = 1
        
        while current_distance < total_pixel_length:
            # 计算当前刻度位置
            tick_x = self.start_point.x() + unit_x * current_distance
            tick_y = self.start_point.y() + unit_y * current_distance
            tick_pos = QPointF(tick_x, tick_y)
            
            # 判断是否为主刻度（每5个刻度或整数单位）
            actual_distance = current_distance * scale_factor
            is_major = (tick_index % 5 == 0) or (abs(actual_distance - round(actual_distance)) < 0.01)
            
            self._draw_single_tick(painter, tick_pos, perp_unit_x, perp_unit_y, is_major)
            
            current_distance += pixel_interval
            tick_index += 1
        
        # 绘制终点刻度（总是绘制，除非与最后一个刻度重合）
        if total_pixel_length - (current_distance - pixel_interval) > pixel_interval * 0.1:
            self._draw_single_tick(painter, self.end_point, perp_unit_x, perp_unit_y, True)
    
    def _draw_single_tick(self, painter, position, perp_unit_x, perp_unit_y, is_major):
        """绘制单个刻度线"""
        # 刻度线长度
        tick_length = 8 if is_major else 4  # 主刻度8像素，次刻度4像素
        
        # 计算刻度线端点
        half_length = tick_length / 2
        start_x = position.x() - perp_unit_x * half_length
        start_y = position.y() - perp_unit_y * half_length
        end_x = position.x() + perp_unit_x * half_length
        end_y = position.y() + perp_unit_y * half_length
        
        # 绘制刻度线
        painter.drawLine(
            QPointF(start_x, start_y),
            QPointF(end_x, end_y)
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
            'tick_interval': self.tick_interval,
        })
        return data

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        start_point = QPointF(data["start_point_x"], data["start_point_y"])
        end_point = QPointF(data["end_point_x"], data["end_point_y"])
        ruler = cls(
            start_point, end_point,
            pixel_length=data.get("pixel_length", 100),
            real_length=data.get("real_length", 10.0),
            unit=data.get("unit", "cm"),
            color=color,
            thickness=data["thickness"],
            opacity=data["opacity"]
        )
        # 设置刻度间隔，使用新的tick_interval
        ruler.tick_interval = data.get("tick_interval", 1.0)
        ruler.show_ticks = data.get("show_ticks", True)
        return ruler


class CircleRuler(RulerBase):
    """圆形标尺"""
    
    def __init__(self, center_point, radius, pixel_length=100, real_length=10.0, unit="cm", **kwargs):
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
        ruler = cls(
            center_point, radius,
            pixel_length=data.get("pixel_length", 100),
            real_length=data.get("real_length", 10.0),
            unit=data.get("unit", "cm"),
            color=color,
            thickness=data["thickness"],
            opacity=data["opacity"]
        )
        # 设置显示直径线属性
        ruler.show_diameter_line = data.get("show_diameter_line", True)
        return ruler
