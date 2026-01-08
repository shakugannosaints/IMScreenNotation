"""
Canvas types and type definitions
"""
from typing import List, Union
from shapes import Line, Rectangle, Circle, Arrow, Freehand, Point, LaserPointer, FilledFreehand, Text, Eraser, Image, Polygon

# 定义Shape类型联合
ShapeType = Union[Line, Rectangle, Polygon, Circle, Arrow, Freehand, Point, LaserPointer, FilledFreehand, Text, Eraser, Image]
