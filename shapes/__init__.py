"""
shapes 包 - 统一导入接口
保持向后兼容性，所有原来从 shapes.py 导入的类都可以直接从这里导入
"""

# 从各个子模块导入所有形状类
from .base import Shape
from .basic import Line, Rectangle, Circle, Point
from .advanced import Arrow, Freehand, FilledFreehand
from .interactive import Text, LaserPointer, Eraser
from .ruler import LineRuler, CircleRuler

# 导出所有类，保持向后兼容
__all__ = [
    'Shape',
    'Line', 
    'Rectangle', 
    'Circle', 
    'Point',
    'Arrow', 
    'Freehand', 
    'FilledFreehand',
    'Text', 
    'LaserPointer', 
    'Eraser',
    'LineRuler',
    'CircleRuler'
]
