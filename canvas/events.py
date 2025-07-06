"""
Canvas event handling (mouse events, etc.)
"""
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF
from PyQt5.QtWidgets import QInputDialog
from shapes import Line, Rectangle, Circle, Arrow, Freehand, Point, LaserPointer, FilledFreehand, Text, Eraser
from .types import ShapeType


class CanvasEventHandler:
    """处理画布的鼠标事件"""
    
    def __init__(self, canvas):
        self.canvas = canvas
    
    def handle_mouse_press(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.canvas.drawing = True
            self.canvas.start_point = event.pos()
            self.canvas.end_point = event.pos()
            
            if self.canvas.properties.current_tool == 'text':
                # 文本工具：弹出输入对话框
                self._create_text_annotation(event.pos())
                return
            elif self.canvas.properties.current_tool == 'freehand':
                # 保存状态到撤销栈（在创建新shape前）
                self.canvas.state_manager.save_state_to_undo_stack()
                self.canvas.current_shape = Freehand(
                    [self.canvas.start_point], 
                    color=self.canvas.properties.current_color, 
                    thickness=self.canvas.properties.current_thickness, 
                    opacity=self.canvas.properties.current_opacity
                )
            elif self.canvas.properties.current_tool == 'filled_freehand':
                # 保存状态到撤销栈（在创建新shape前）
                self.canvas.state_manager.save_state_to_undo_stack()
                self.canvas.current_shape = FilledFreehand(
                    [self.canvas.start_point], 
                    color=self.canvas.properties.current_color, 
                    thickness=self.canvas.properties.current_thickness, 
                    opacity=self.canvas.properties.current_opacity
                )
            elif self.canvas.properties.current_tool == 'point':
                # 保存状态到撤销栈（在创建新shape前）
                self.canvas.state_manager.save_state_to_undo_stack()
                self.canvas.current_shape = Point(
                    self.canvas.start_point, 
                    color=self.canvas.properties.current_color, 
                    thickness=self.canvas.properties.current_thickness, 
                    opacity=self.canvas.properties.current_opacity
                )
                self.canvas.shapes.append(self.canvas.current_shape)
                self.canvas.current_shape = None
                self.canvas.drawing = False  # Point is a single click action
            elif self.canvas.properties.current_tool == 'laser_pointer':
                # 激光笔不保存状态，因为它是临时的
                self.canvas.current_shape = LaserPointer(
                    event.pos(), 
                    color=self.canvas.properties.current_color, 
                    thickness=self.canvas.properties.current_thickness, 
                    opacity=self.canvas.properties.current_opacity
                )
                self.canvas.update()  # 立即更新显示激光笔
                return  # 激光笔是临时的，不添加到shapes列表中，也不保存状态
            elif self.canvas.properties.current_tool == 'eraser':
                # 橡皮擦工具：开始擦除操作
                self.canvas.state_manager.save_state_to_undo_stack()
                self.canvas.current_shape = Eraser(
                    [self.canvas.start_point], 
                    color=self.canvas.properties.current_color, 
                    thickness=self.canvas.properties.current_thickness, 
                    opacity=self.canvas.properties.current_opacity
                )
            else:
                # 其他工具（line, rectangle, circle, arrow）在释放鼠标时保存状态
                self.canvas.current_shape = None  # Reset current shape

    def handle_mouse_move(self, event):
        """处理鼠标移动事件"""
        if self.canvas.drawing:
            self.canvas.end_point = event.pos()
            
            if self.canvas.properties.current_tool == 'line':
                self.canvas.current_shape = Line(
                    self.canvas.start_point, self.canvas.end_point, 
                    color=self.canvas.properties.current_color, 
                    thickness=self.canvas.properties.current_thickness, 
                    opacity=self.canvas.properties.current_opacity
                )
            elif self.canvas.properties.current_tool == 'rectangle':
                rect = QRect(self.canvas.start_point, self.canvas.end_point).normalized()
                self.canvas.current_shape = Rectangle(
                    rect, 
                    color=self.canvas.properties.current_color, 
                    thickness=self.canvas.properties.current_thickness, 
                    opacity=self.canvas.properties.current_opacity
                )
            elif self.canvas.properties.current_tool == 'circle':
                radius = int(((self.canvas.end_point.x() - self.canvas.start_point.x())**2 + 
                             (self.canvas.end_point.y() - self.canvas.start_point.y())**2)**0.5)
                self.canvas.current_shape = Circle(
                    self.canvas.start_point, radius, 
                    color=self.canvas.properties.current_color, 
                    thickness=self.canvas.properties.current_thickness, 
                    opacity=self.canvas.properties.current_opacity
                )
            elif self.canvas.properties.current_tool == 'arrow':
                self.canvas.current_shape = Arrow(
                    self.canvas.start_point, self.canvas.end_point, 
                    color=self.canvas.properties.current_color, 
                    thickness=self.canvas.properties.current_thickness, 
                    opacity=self.canvas.properties.current_opacity
                )
            elif self.canvas.properties.current_tool == 'freehand':
                if isinstance(self.canvas.current_shape, Freehand):
                    self.canvas.current_shape.points.append(self.canvas.end_point)
            elif self.canvas.properties.current_tool == 'filled_freehand':
                if isinstance(self.canvas.current_shape, FilledFreehand):
                    self.canvas.current_shape.points.append(self.canvas.end_point)
            elif self.canvas.properties.current_tool == 'laser_pointer':
                # 更新激光笔位置
                self.canvas.current_shape = LaserPointer(
                    event.pos(), 
                    color=self.canvas.properties.current_color, 
                    thickness=self.canvas.properties.current_thickness, 
                    opacity=self.canvas.properties.current_opacity
                )
                self.canvas.update()
                return  # 激光笔是临时的，不添加到shapes列表中
            elif self.canvas.properties.current_tool == 'eraser':
                # 橡皮擦：添加擦除点
                if isinstance(self.canvas.current_shape, Eraser):
                    self.canvas.current_shape.points.append(self.canvas.end_point)
            
            self.canvas.update()

    def handle_mouse_release(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.canvas.drawing:
            self.canvas.drawing = False
            if (self.canvas.current_shape and 
                self.canvas.properties.current_tool != 'point' and 
                self.canvas.properties.current_tool != 'laser_pointer'):
                
                # 对于需要拖拽的工具（line, rectangle, circle, arrow），在释放时保存状态
                if self.canvas.properties.current_tool in ['line', 'rectangle', 'circle', 'arrow']:
                    self.canvas.state_manager.save_state_to_undo_stack()
                
                # 橡皮擦特殊处理：执行擦除操作
                if (self.canvas.properties.current_tool == 'eraser' and 
                    isinstance(self.canvas.current_shape, Eraser)):
                    self._perform_erase_operation(self.canvas.current_shape)
                else:
                    if self.canvas.properties.single_draw_mode:
                        self.canvas.shapes.clear()
                        # 单次绘制模式下，清空撤销栈并重新开始
                        self.canvas.state_manager.undo_stack.clear()
                        self.canvas.state_manager.redo_stack.clear()
                        # 保存空白状态
                        self.canvas.state_manager.undo_stack.append([])  # 空的序列化状态列表
                    
                    self.canvas.shapes.append(self.canvas.current_shape)
            
            self.canvas.current_shape = None
            self.canvas.update()

    def _create_text_annotation(self, position):
        """创建文本标注"""
        try:
            # 弹出文本输入对话框
            text, ok = QInputDialog.getText(self.canvas, '输入文本', '请输入要标注的文本:')
            if ok and text:
                # 保存状态到撤销栈
                self.canvas.state_manager.save_state_to_undo_stack()
                
                # 创建文本对象
                text_shape = Text(
                    position=QPointF(position),
                    text=text,
                    font_family=self.canvas.properties.text_font_family,
                    font_size=self.canvas.properties.text_font_size,
                    font_bold=self.canvas.properties.text_font_bold,
                    font_italic=self.canvas.properties.text_font_italic,
                    text_color=self.canvas.properties.text_color,
                    background_color=self.canvas.properties.text_background_color,
                    border_color=self.canvas.properties.text_border_color,
                    border_enabled=self.canvas.properties.text_border_enabled,
                    border_width=self.canvas.properties.text_border_width,
                    padding=self.canvas.properties.text_padding,
                    color=self.canvas.properties.current_color,
                    thickness=self.canvas.properties.current_thickness,
                    opacity=self.canvas.properties.current_opacity
                )
                
                # 添加到形状列表
                self.canvas.shapes.append(text_shape)
                
                # 如果是单次绘制模式，清空其他形状
                if self.canvas.properties.single_draw_mode:
                    self.canvas.shapes = [text_shape]
                    self.canvas.state_manager.undo_stack.clear()
                
                # 更新显示
                self.canvas.update()
                
            # 重置绘制状态
            self.canvas.drawing = False
            self.canvas.current_shape = None
            
        except Exception as e:
            print(f"Error creating text annotation: {e}")
            # 重置绘制状态
            self.canvas.drawing = False
            self.canvas.current_shape = None

    def _perform_erase_operation(self, eraser_shape):
        """执行橡皮擦操作 - 删除与橡皮擦相交的形状"""
        if not isinstance(eraser_shape, Eraser):
            return
            
        # 收集需要删除的形状
        shapes_to_remove = []
        
        for shape in self.canvas.shapes:
            # 跳过激光笔和橡皮擦本身
            if isinstance(shape, (LaserPointer, Eraser)):
                continue
                
            # 检查形状是否与橡皮擦相交
            if eraser_shape.intersects_with_shape(shape):
                shapes_to_remove.append(shape)
        
        # 删除相交的形状
        for shape in shapes_to_remove:
            if shape in self.canvas.shapes:
                self.canvas.shapes.remove(shape)
        
        print(f"橡皮擦删除了 {len(shapes_to_remove)} 个形状")
