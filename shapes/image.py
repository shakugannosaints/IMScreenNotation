"""
图片形状类 - 处理图片标注
"""
import os
from PyQt5.QtGui import QColor, QPen, QPixmap, QPainter
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtWidgets import QFileDialog
from .base import Shape


class Image(Shape):
    """图片标注形状"""
    
    def __init__(self, position, image_path="", scale_factor=1.0, rotation=0, **kwargs):
        super().__init__(**kwargs)
        self.position = position  # 图片左上角位置
        self.image_path = image_path  # 图片文件路径
        self.scale_factor = scale_factor  # 缩放比例
        self.rotation = rotation  # 旋转角度（度）
        self.pixmap = None  # 缓存的QPixmap对象
        self.original_size = None  # 原始尺寸
        self.scaled_size = None  # 缩放后尺寸
        self.selection_threshold = 20  # 点击检测阈值（像素）
        
        # 加载图片
        if image_path:
            self.load_image()
    
    def load_image(self):
        """加载图片文件"""
        if os.path.exists(self.image_path):
            self.pixmap = QPixmap(self.image_path)
            if not self.pixmap.isNull():
                self.original_size = self.pixmap.size()
                self.update_scaled_size()
                return True
        return False
    
    def update_scaled_size(self):
        """更新缩放后的尺寸"""
        if self.original_size is not None:
            self.scaled_size = self.original_size * self.scale_factor
    
    def set_scale_factor(self, scale_factor):
        """设置缩放比例"""
        self.scale_factor = max(0.1, min(5.0, scale_factor))  # 限制在0.1到5.0之间
        self.update_scaled_size()
    
    def set_rotation(self, rotation):
        """设置旋转角度"""
        self.rotation = rotation % 360  # 限制在0-359度之间
    
    def contains_point(self, point):
        """检查点是否在图片区域内（用于编辑检测）"""
        if self.scaled_size is None:
            return False
        
        # 检查点击是否在图片左上角附近的选择区域
        left_top_rect = QRectF(
            self.position.x() - self.selection_threshold,
            self.position.y() - self.selection_threshold,
            self.selection_threshold * 2,
            self.selection_threshold * 2
        )
        
        return left_top_rect.contains(point)
    
    def get_bounding_rect(self):
        """获取图片的边界矩形"""
        if self.scaled_size is None:
            return QRectF()
        
        return QRectF(
            self.position.x(),
            self.position.y(),
            self.scaled_size.width(),
            self.scaled_size.height()
        )
    
    def draw(self, painter):
        """绘制图片"""
        if not self.pixmap or self.pixmap.isNull() or self.scaled_size is None:
            # 如果图片加载失败，绘制一个占位符
            self._draw_placeholder(painter)
            return
        
        # 保存当前状态
        old_opacity = painter.opacity()
        old_transform = painter.transform()
        
        # 设置不透明度（使用基类的opacity属性）
        painter.setOpacity(self.opacity)
        
        # 计算绘制矩形的中心点（旋转中心）
        draw_rect = QRectF(
            self.position.x(),
            self.position.y(),
            self.scaled_size.width(),
            self.scaled_size.height()
        )
        center = draw_rect.center()
        
        # 应用旋转变换
        if self.rotation != 0:
            painter.translate(center)
            painter.rotate(self.rotation)
            painter.translate(-center)
        
        # 绘制图片
        painter.drawPixmap(draw_rect.toRect(), self.pixmap)
        
        # 恢复状态
        painter.setTransform(old_transform)
        painter.setOpacity(old_opacity)
    
    def _draw_placeholder(self, painter):
        """绘制占位符（当图片加载失败时）"""
        # 绘制一个简单的矩形占位符
        placeholder_size = 100
        placeholder_rect = QRectF(
            self.position.x(),
            self.position.y(),
            placeholder_size,
            placeholder_size
        )
        
        # 设置占位符样式
        placeholder_color = QColor(200, 200, 200, 100)
        painter.fillRect(placeholder_rect, placeholder_color)
        
        # 绘制边框
        border_color = QColor(150, 150, 150)
        border_pen = QPen(border_color, 2, Qt.DashLine)
        painter.setPen(border_pen)
        painter.drawRect(placeholder_rect)
        
        # 绘制文字说明
        painter.setPen(QPen(QColor(100, 100, 100)))
        painter.drawText(placeholder_rect, Qt.AlignCenter, "图片\n加载失败")
    
    def _draw_selection_indicator(self, painter):
        """绘制选择指示器"""
        # 绘制左上角的选择区域指示器
        indicator_rect = QRectF(
            self.position.x() - self.selection_threshold,
            self.position.y() - self.selection_threshold,
            self.selection_threshold * 2,
            self.selection_threshold * 2
        )
        
        # 半透明蓝色填充
        indicator_color = QColor(0, 120, 255, 100)
        painter.fillRect(indicator_rect, indicator_color)
        
        # 蓝色边框
        border_pen = QPen(QColor(0, 120, 255), 2)
        painter.setPen(border_pen)
        painter.drawRect(indicator_rect)
    
    def to_dict(self):
        """序列化为字典"""
        data = super().to_dict()
        data.update({
            'position': [self.position.x(), self.position.y()],
            'image_path': self.image_path,
            'scale_factor': self.scale_factor,
            'rotation': self.rotation
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """从字典反序列化"""
        position = QPointF(data['position'][0], data['position'][1])
        image_path = data.get('image_path', '')
        scale_factor = data.get('scale_factor', 1.0)
        rotation = data.get('rotation', 0)
        
        # 创建基础属性
        color = QColor(*data["color"])
        thickness = data["thickness"]
        opacity = data["opacity"]
        
        image_shape = cls(
            position=position,
            image_path=image_path,
            scale_factor=scale_factor,
            rotation=rotation,
            color=color,
            thickness=thickness,
            opacity=opacity
        )
        
        return image_shape
    
    @staticmethod
    def select_image_file(parent=None):
        """选择图片文件的静态方法"""
        file_dialog = QFileDialog(parent)
        file_dialog.setWindowTitle("选择图片文件")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        # 设置图片文件过滤器
        filters = [
            "所有支持的图片 (*.png *.jpg *.jpeg *.bmp *.gif *.svg *.tiff *.webp)",
            "PNG 文件 (*.png)",
            "JPEG 文件 (*.jpg *.jpeg)",
            "BMP 文件 (*.bmp)",
            "GIF 文件 (*.gif)",
            "SVG 文件 (*.svg)",
            "TIFF 文件 (*.tiff)",
            "WebP 文件 (*.webp)",
            "所有文件 (*.*)"
        ]
        file_dialog.setNameFilters(filters)
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                return selected_files[0]
        
        return None
