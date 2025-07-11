"""
Canvas state management (undo/redo functionality)
"""
import json
from PyQt5.QtCore import QObject, pyqtSignal
from shapes import Line, Rectangle, Circle, Arrow, Freehand, Point, LaserPointer, FilledFreehand, Text, Eraser, LineRuler, CircleRuler
from .types import ShapeType


class CanvasStateManager(QObject):
    """管理画布状态，包括撤销/重做功能"""
    
    # 信号
    shape_added = pyqtSignal(object)  # 当添加新形状时发出
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.undo_stack = []  # For undo functionality - stores canvas states
        self.redo_stack = []  # For redo functionality - stores canvas states

    def save_state_to_undo_stack(self):
        """保存当前画布状态到撤销栈"""
        # 将shapes序列化为字典列表，避免深拷贝PyQt对象
        serialized_shapes = []
        for shape in self.canvas.shapes:
            serialized_shapes.append(shape.to_dict())
        
        self.undo_stack.append(serialized_shapes)
        
        # 限制撤销栈的大小，避免内存过度使用
        if len(self.undo_stack) > 50:  # 最多保存50个状态
            self.undo_stack.pop(0)
        
        # 清空重做栈，因为有新的操作
        self.redo_stack.clear()

    def undo(self):
        """撤销操作 - 恢复到上一个状态"""
        if self.undo_stack:
            # 将当前状态序列化并保存到重做栈
            current_serialized_state = []
            for shape in self.canvas.shapes:
                current_serialized_state.append(shape.to_dict())
            self.redo_stack.append(current_serialized_state)
            
            # 限制重做栈的大小
            if len(self.redo_stack) > 50:
                self.redo_stack.pop(0)
            
            # 恢复到上一个状态
            previous_serialized_state = self.undo_stack.pop()
            self.canvas.shapes = self._deserialize_shapes(previous_serialized_state)
            self.canvas.update()

    def redo(self):
        """重做操作 - 恢复到下一个状态"""
        if self.redo_stack:
            # 将当前状态序列化并保存到撤销栈
            current_serialized_state = []
            for shape in self.canvas.shapes:
                current_serialized_state.append(shape.to_dict())
            self.undo_stack.append(current_serialized_state)
            
            # 限制撤销栈的大小
            if len(self.undo_stack) > 50:
                self.undo_stack.pop(0)
            
            # 恢复到下一个状态
            next_serialized_state = self.redo_stack.pop()
            self.canvas.shapes = self._deserialize_shapes(next_serialized_state)
            self.canvas.update()

    def _deserialize_shapes(self, serialized_shapes):
        """从序列化的形状数据重建形状对象列表"""
        shapes = []
        for shape_data in serialized_shapes:
            # 创建shape_data的副本，避免修改原始数据
            shape_dict = shape_data.copy()
            shape_type = shape_dict.pop("type")
            
            if shape_type == "Line":
                shape = Line.from_dict(shape_dict)
            elif shape_type == "Rectangle":
                shape = Rectangle.from_dict(shape_dict)
            elif shape_type == "Circle":
                shape = Circle.from_dict(shape_dict)
            elif shape_type == "Arrow":
                shape = Arrow.from_dict(shape_dict)
            elif shape_type == "Freehand":
                shape = Freehand.from_dict(shape_dict)
            elif shape_type == "FilledFreehand":
                shape = FilledFreehand.from_dict(shape_dict)
            elif shape_type == "Point":
                shape = Point.from_dict(shape_dict)
            elif shape_type == "Text":
                shape = Text.from_dict(shape_dict)
            elif shape_type == "LineRuler":
                shape = LineRuler.from_dict(shape_dict)
            elif shape_type == "CircleRuler":
                shape = CircleRuler.from_dict(shape_dict)
            elif shape_type == "LaserPointer":
                # 跳过激光笔，因为它不应该被保存/恢复
                continue
            elif shape_type == "Eraser":
                # 跳过橡皮擦，因为它不应该被保存/恢复（它是删除操作）
                continue
            else:
                continue  # Skip unknown shape types
            
            shapes.append(shape)
        return shapes

    def clear_canvas(self):
        """清空画布 - 支持撤销/重做"""
        # 先保存当前状态到撤销栈
        self.save_state_to_undo_stack()
        
        # 清空画布
        self.canvas.shapes.clear()
        self.canvas.update()

    def to_json_data(self):
        """将画布内容导出为JSON数据"""
        serialized_shapes = []
        for shape in self.canvas.shapes:
            serialized_shapes.append(shape.to_dict())
        return json.dumps(serialized_shapes, indent=2)

    def from_json_data(self, json_data):
        """从JSON数据导入画布内容"""
        # 保存当前状态到撤销栈
        self.save_state_to_undo_stack()
        
        # 清空当前画布
        self.canvas.shapes.clear()
        
        try:
            data = json.loads(json_data)
            self.canvas.shapes = self._deserialize_shapes(data)
            self.canvas.update()
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"导入数据时出错: {e}")
            raise
