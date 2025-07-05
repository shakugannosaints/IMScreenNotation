"""
工具函数模块
包含资源路径获取、图标创建等通用工具函数
"""
import sys
import os
from typing import Optional
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt


def get_resource_path(relative_path: str) -> str:
    """获取资源文件的绝对路径，支持打包后的exe运行"""
    try:
        # PyInstaller创建临时文件夹并将路径存储在_MEIPASS中
        base_path = getattr(sys, "_MEIPASS", None)
        if base_path is None:
            # 如果不是打包的exe，使用脚本所在目录
            base_path = os.path.dirname(os.path.abspath(__file__))
    except AttributeError:
        # 如果不是打包的exe，使用脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


def create_default_icon() -> QIcon:
    """创建一个默认的托盘图标"""
    # 创建一个16x16的像素图
    pixmap = QPixmap(16, 16)
    pixmap.fill(QColor(0, 0, 0, 0))  # 使用完全透明的QColor替代Qt.transparent
    
    # 在像素图上绘制一个简单的图标
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 绘制一个蓝色圆形作为图标
    painter.setBrush(QColor(0, 120, 212))  # Windows蓝色
    painter.setPen(QColor(0, 90, 158))
    painter.drawEllipse(2, 2, 12, 12)
    
    # 在圆形中间绘制一个白色的"A"字母
    painter.setPen(QColor(255, 255, 255))
    painter.setFont(painter.font())
    painter.drawText(6, 11, "A")
    
    painter.end()
    
    return QIcon(pixmap)


def load_icon_with_fallback(icon_path: str) -> QIcon:
    """加载图标文件，失败时返回默认图标"""
    try:
        # 尝试使用绝对路径加载图标文件
        full_icon_path = get_resource_path(icon_path)
        print(f"尝试加载图标文件: {full_icon_path}")
        
        if os.path.exists(full_icon_path):
            icon = QIcon(full_icon_path)
            print(f"图标文件存在，加载结果: isNull={icon.isNull()}")
            if not icon.isNull():
                print(f"图标可用尺寸: {icon.availableSizes()}")
                return icon
        else:
            print(f"图标文件不存在: {full_icon_path}")
            # 尝试查找当前目录和几个可能的位置
            possible_paths = [
                icon_path,  # 相对路径
                os.path.join(os.getcwd(), icon_path),  # 当前工作目录
                os.path.join(os.path.dirname(sys.argv[0]), icon_path),  # exe所在目录
            ]
            
            for path in possible_paths:
                print(f"尝试路径: {path}")
                if os.path.exists(path):
                    icon = QIcon(path)
                    if not icon.isNull():
                        print(f"在路径 {path} 找到有效图标")
                        return icon
    except Exception as e:
        print(f"加载图标文件失败: {e}")
    
    # 如果加载失败，返回默认图标
    print("使用默认图标")
    return create_default_icon()
