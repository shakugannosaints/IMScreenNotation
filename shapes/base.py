"""
基础形状类 - 定义所有形状的基础接口和属性
"""
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QDateTime


class Shape:
    """所有形状的基类"""
    
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
