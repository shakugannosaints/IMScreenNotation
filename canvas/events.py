"""
Canvas event handling (mouse events, etc.)
"""
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF
from PyQt5.QtWidgets import QInputDialog
import math
import time
from shapes import Line, Rectangle, Circle, Arrow, Freehand, Point, LaserPointer, FilledFreehand, Text, Eraser, LineRuler, CircleRuler, Image, Polygon
from .types import ShapeType

# 导入文本编辑对话框
try:
    from text_edit import TextEditDialog
except ImportError:
    # 如果导入失败，使用 None 作为标记
    TextEditDialog = None

# 导入图片设置对话框
try:
    from image_settings_dialog import ImageSettingsDialog
except ImportError:
    ImageSettingsDialog = None


class CanvasEventHandler:
    """处理画布的鼠标事件"""
    
    def __init__(self, canvas):
        self.canvas = canvas

        # Polygon tool interaction state
        self._polygon_active = False
        self._polygon_vertices = []  # list[QPointF]
        self._polygon_preview_point = None  # QPointF | None
        self._polygon_press_time = 0.0
        self._polygon_press_pos = None  # QPointF | None
        self._polygon_dragging = False

    def _cancel_polygon(self) -> None:
        self._polygon_active = False
        self._polygon_vertices = []
        self._polygon_preview_point = None
        self._polygon_press_time = 0.0
        self._polygon_press_pos = None
        self._polygon_dragging = False
        if isinstance(self.canvas.current_shape, Polygon):
            self.canvas.current_shape = None
            self.canvas.update()

    def _polygon_vertex_index_near(self, pos: QPointF, tol: float) -> int:
        for i, v in enumerate(self._polygon_vertices):
            if math.hypot(pos.x() - v.x(), pos.y() - v.y()) <= tol:
                return i
        return -1

    def _update_polygon_preview(self) -> None:
        if not self._polygon_active:
            return
        fill_enabled = bool(getattr(self.canvas.properties, 'fill_mode_enabled', False))
        self.canvas.current_shape = Polygon(
            list(self._polygon_vertices),
            fill=fill_enabled,
            closed=False,
            preview_point=self._polygon_preview_point,
            color=self.canvas.properties.current_color,
            thickness=self.canvas.properties.current_thickness,
            opacity=self.canvas.properties.current_opacity,
        )
        self.canvas.update()

    def _finish_polygon(self, close_to_index=None) -> None:
        if not self._polygon_active:
            return

        pts = list(self._polygon_vertices)
        if len(pts) < 3:
            self._cancel_polygon()
            return

        if close_to_index is not None and 0 <= int(close_to_index) < len(pts):
            idx = int(close_to_index)
            pts = pts[idx:] + pts[:idx]

        fill_enabled = bool(getattr(self.canvas.properties, 'fill_mode_enabled', False))
        polygon = Polygon(
            pts,
            fill=fill_enabled,
            closed=True,
            color=self.canvas.properties.current_color,
            thickness=self.canvas.properties.current_thickness,
            opacity=self.canvas.properties.current_opacity,
        )

        if self.canvas.properties.single_draw_mode:
            self.canvas.shapes.clear()
            self.canvas.state_manager.undo_stack.clear()
            self.canvas.state_manager.redo_stack.clear()
            self.canvas.state_manager.undo_stack.append([])

        self.canvas.shapes.append(polygon)
        self.canvas.state_manager.shape_added.emit(polygon)
        self._cancel_polygon()
    
    def handle_mouse_press(self, event):
        """处理鼠标按下事件"""
        # 兼容旧工具名：rectangle 视为 polygon
        if self.canvas.properties.current_tool == 'rectangle':
            self.canvas.properties.current_tool = 'polygon'

        # Tool switched away from polygon: cancel any in-progress polygon.
        if self._polygon_active and self.canvas.properties.current_tool != 'polygon':
            self._cancel_polygon()

        if self.canvas.properties.current_tool == 'polygon':
            if event.button() == Qt.RightButton:
                # 右键：结束绘制（默认闭合到起点）
                if self._polygon_vertices:
                    self._finish_polygon(close_to_index=0)
                else:
                    self._cancel_polygon()
                return

            if event.button() != Qt.LeftButton:
                return

            pos = QPointF(event.pos())
            tol = max(10.0, float(self.canvas.properties.current_thickness) * 3.0)

            # 单击已有顶点：结束绘制（闭合到该顶点）
            if self._polygon_active and len(self._polygon_vertices) >= 3:
                idx = self._polygon_vertex_index_near(pos, tol)
                if idx != -1:
                    self._finish_polygon(close_to_index=idx)
                    return

            # 开始（或继续）多边形：按下时先记录，抬起时决定“点击”还是“长按拖动”
            if not self._polygon_active:
                self.canvas.state_manager.save_state_to_undo_stack()
                self._polygon_active = True
                self._polygon_vertices = []

            self._polygon_press_time = time.time()
            self._polygon_press_pos = pos
            self._polygon_dragging = False
            self._polygon_preview_point = pos
            self._update_polygon_preview()
            return

        if event.button() == Qt.LeftButton:
            # 兼容旧工具名：filled_freehand 视为 freehand + 填充开启
            if self.canvas.properties.current_tool == 'filled_freehand':
                self.canvas.properties.current_tool = 'freehand'
                if hasattr(self.canvas, 'set_fill_mode_enabled'):
                    self.canvas.set_fill_mode_enabled(True)

            # 检查是否是文本工具且点击了现有文本
            if self.canvas.properties.current_tool == 'text':
                clicked_text = self._find_text_at_position(event.pos())
                if clicked_text:
                    # 编辑现有文本
                    self._edit_existing_text(clicked_text)
                    return
                else:
                    # 创建新文本
                    self._create_text_annotation(event.pos())
                    return
            
            # 检查是否是图片工具
            if self.canvas.properties.current_tool == 'image':
                clicked_image = self._find_image_at_position(event.pos())
                if clicked_image:
                    # 编辑现有图片
                    self._edit_existing_image(clicked_image)
                    return
                else:
                    # 创建新图片
                    self._create_image_annotation(event.pos())
                    return
            
            self.canvas.drawing = True
            self.canvas.start_point = event.pos()
            self.canvas.end_point = event.pos()
            
            if self.canvas.properties.current_tool == 'freehand':
                # 保存状态到撤销栈（在创建新shape前）
                self.canvas.state_manager.save_state_to_undo_stack()
                fill_enabled = bool(getattr(self.canvas.properties, 'fill_mode_enabled', False))
                shape_cls = FilledFreehand if fill_enabled else Freehand
                self.canvas.current_shape = shape_cls(
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
        if self._polygon_active and self.canvas.properties.current_tool != 'polygon':
            self._cancel_polygon()

        if self.canvas.properties.current_tool == 'polygon' and self._polygon_active:
            pos = QPointF(event.pos())
            self._polygon_preview_point = pos

            # 长按拖动判定：按下超过阈值且位移超过阈值
            if event.buttons() & Qt.LeftButton and self._polygon_press_pos is not None:
                long_press_s = 0.25
                drag_threshold = 4.0
                elapsed = time.time() - self._polygon_press_time
                moved = math.hypot(pos.x() - self._polygon_press_pos.x(), pos.y() - self._polygon_press_pos.y())
                if elapsed >= long_press_s and moved >= drag_threshold:
                    self._polygon_dragging = True

            self._update_polygon_preview()
            return

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
                fill_enabled = bool(getattr(self.canvas.properties, 'fill_mode_enabled', False))
                self.canvas.current_shape = Rectangle(
                    rect, 
                    fill=fill_enabled,
                    color=self.canvas.properties.current_color, 
                    thickness=self.canvas.properties.current_thickness, 
                    opacity=self.canvas.properties.current_opacity
                )
            elif self.canvas.properties.current_tool == 'circle':
                radius = int(((self.canvas.end_point.x() - self.canvas.start_point.x())**2 + 
                             (self.canvas.end_point.y() - self.canvas.start_point.y())**2)**0.5)
                fill_enabled = bool(getattr(self.canvas.properties, 'fill_mode_enabled', False))
                self.canvas.current_shape = Circle(
                    self.canvas.start_point, radius, 
                    fill=fill_enabled,
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
                # freehand / filled_freehand（通过 fill_mode_enabled 决定）
                if isinstance(self.canvas.current_shape, (Freehand, FilledFreehand)):
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
            elif self.canvas.properties.current_tool == 'line_ruler':
                # 直线标尺 - 使用 RulerManager 创建
                if hasattr(self.canvas, 'parent') and hasattr(self.canvas.parent(), 'ruler_manager'):
                    # 通过 RulerManager 创建，会应用所有当前设置
                    self.canvas.current_shape = self.canvas.parent().ruler_manager.create_line_ruler(
                        self.canvas.start_point, self.canvas.end_point
                    )
                else:
                    # 备用方案：直接创建
                    self.canvas.current_shape = LineRuler(
                        self.canvas.start_point, self.canvas.end_point,
                        pixel_length=getattr(self.canvas, 'ruler_pixel_length', 100),
                        real_length=getattr(self.canvas, 'ruler_real_length', 10.0),
                        unit=getattr(self.canvas, 'ruler_unit', 'cm'),
                        color=self.canvas.properties.current_color,
                        thickness=self.canvas.properties.current_thickness,
                        opacity=self.canvas.properties.current_opacity
                    )
            elif self.canvas.properties.current_tool == 'circle_ruler':
                # 圆形标尺 - 使用 RulerManager 创建
                radius = int(((self.canvas.end_point.x() - self.canvas.start_point.x())**2 + 
                             (self.canvas.end_point.y() - self.canvas.start_point.y())**2)**0.5)
                if hasattr(self.canvas, 'parent') and hasattr(self.canvas.parent(), 'ruler_manager'):
                    # 通过 RulerManager 创建，会应用所有当前设置
                    self.canvas.current_shape = self.canvas.parent().ruler_manager.create_circle_ruler(
                        self.canvas.start_point, radius
                    )
                else:
                    # 备用方案：直接创建
                    self.canvas.current_shape = CircleRuler(
                        self.canvas.start_point, radius,
                        pixel_length=getattr(self.canvas, 'ruler_pixel_length', 100),
                        real_length=getattr(self.canvas, 'ruler_real_length', 10.0),
                        unit=getattr(self.canvas, 'ruler_unit', 'cm'),
                        color=self.canvas.properties.current_color,
                        thickness=self.canvas.properties.current_thickness,
                        opacity=self.canvas.properties.current_opacity
                    )
            
            self.canvas.update()

    def handle_mouse_release(self, event):
        """处理鼠标释放事件"""
        if self._polygon_active and self.canvas.properties.current_tool != 'polygon':
            self._cancel_polygon()

        if self.canvas.properties.current_tool == 'polygon' and self._polygon_active:
            if event.button() == Qt.RightButton:
                self._finish_polygon(close_to_index=0)
                return

            if event.button() != Qt.LeftButton:
                return

            pos = QPointF(event.pos())
            tol = max(6.0, float(self.canvas.properties.current_thickness) * 2.0)

            if not self._polygon_vertices:
                # 首次交互：点击=首点；长按拖动=首边（两点）
                if self._polygon_dragging and self._polygon_press_pos is not None:
                    start = QPointF(self._polygon_press_pos)
                    self._polygon_vertices.append(start)
                    if math.hypot(pos.x() - start.x(), pos.y() - start.y()) > tol:
                        self._polygon_vertices.append(pos)
                else:
                    self._polygon_vertices.append(pos)
            else:
                last = self._polygon_vertices[-1]
                if math.hypot(pos.x() - last.x(), pos.y() - last.y()) > tol:
                    self._polygon_vertices.append(pos)

            self._polygon_press_pos = None
            self._polygon_dragging = False
            self._polygon_preview_point = pos
            self._update_polygon_preview()
            return

        if event.button() == Qt.LeftButton and self.canvas.drawing:
            self.canvas.drawing = False
            if (self.canvas.current_shape and 
                self.canvas.properties.current_tool != 'point' and 
                self.canvas.properties.current_tool != 'laser_pointer'):
                
                # 对于需要拖拽的工具（line, rectangle, circle, arrow, ruler），在释放时保存状态
                if self.canvas.properties.current_tool in ['line', 'rectangle', 'circle', 'arrow', 'line_ruler', 'circle_ruler']:
                    self.canvas.state_manager.save_state_to_undo_stack()
                
                # 橡皮擦特殊处理：执行擦除操作
                if (self.canvas.properties.current_tool == 'eraser' and 
                    isinstance(self.canvas.current_shape, Eraser)):
                    self._perform_erase_operation(self.canvas.current_shape)
                else:
                    # 自由绘制 / 填充绘制：可选线条纠正（收笔时进行，避免影响实时绘制手感）
                    if (self.canvas.properties.current_tool in ['freehand', 'filled_freehand'] and
                        bool(getattr(self.canvas.properties, 'auto_correct_freehand', False)) and
                        hasattr(self.canvas.current_shape, 'points')):
                        try:
                            corrected_points = self._auto_correct_freehand_points(
                                list(getattr(self.canvas.current_shape, 'points', [])),
                                thickness=self.canvas.properties.current_thickness,
                                prefer_closed=bool(getattr(self.canvas.properties, 'fill_mode_enabled', False)) or (self.canvas.properties.current_tool == 'filled_freehand'),
                            )
                            if corrected_points and len(corrected_points) >= 2:
                                self.canvas.current_shape.points = corrected_points
                        except Exception as e:
                            # 纠正失败时回退到原始轨迹，避免影响绘制
                            print(f"自由绘制线条纠正失败，已回退: {e}")

                    if self.canvas.properties.single_draw_mode:
                        self.canvas.shapes.clear()
                        # 单次绘制模式下，清空撤销栈并重新开始
                        self.canvas.state_manager.undo_stack.clear()
                        self.canvas.state_manager.redo_stack.clear()
                        # 保存空白状态
                        self.canvas.state_manager.undo_stack.append([])  # 空的序列化状态列表
                    
                    self.canvas.shapes.append(self.canvas.current_shape)
                    
                    # 发出形状添加信号
                    self.canvas.state_manager.shape_added.emit(self.canvas.current_shape)
            
            self.canvas.current_shape = None
            self.canvas.update()

    def _auto_correct_freehand_points(self, points, thickness: int, prefer_closed: bool = False):
        """将自由绘制点序列纠正为更直的折线段。

        策略（最小可用且稳定）：
        - 先做去抖/去重（移除很近的点）
        - RDP 简化得到关键点（抖动直线→2点，多边形→少量顶点）
        - 合并近共线段、合并过短边
        - 可选闭合：填充绘制优先闭合；普通自由绘制在接近闭合时闭合
        """

        if not points or len(points) < 2:
            return points

        # 统一为 QPointF
        pts = [QPointF(p) for p in points]

        def dist(a: QPointF, b: QPointF) -> float:
            dx = a.x() - b.x()
            dy = a.y() - b.y()
            return math.hypot(dx, dy)

        # 1) 去重/去抖：移除距离过近的连续点
        min_step = max(1.0, thickness * 0.3)
        filtered = [pts[0]]
        for p in pts[1:]:
            if dist(p, filtered[-1]) >= min_step:
                filtered.append(p)
        if len(filtered) < 2:
            return [pts[0], pts[-1]]

        # 2) RDP 简化（先识别角点，把轨迹分段，避免多边形角被过度简化）
        epsilon = max(2.0, thickness * 0.8)

        def point_line_distance(p: QPointF, a: QPointF, b: QPointF) -> float:
            # 线段 AB 到点 P 的最短距离
            ax, ay = a.x(), a.y()
            bx, by = b.x(), b.y()
            px, py = p.x(), p.y()
            abx, aby = bx - ax, by - ay
            apx, apy = px - ax, py - ay
            ab_len2 = abx * abx + aby * aby
            if ab_len2 <= 1e-9:
                return math.hypot(apx, apy)
            t = (apx * abx + apy * aby) / ab_len2
            t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
            cx = ax + t * abx
            cy = ay + t * aby
            return math.hypot(px - cx, py - cy)

        def rdp(seq, eps: float):
            if len(seq) <= 2:
                return seq
            a, b = seq[0], seq[-1]
            max_d = -1.0
            idx = -1
            for i in range(1, len(seq) - 1):
                d = point_line_distance(seq[i], a, b)
                if d > max_d:
                    max_d = d
                    idx = i
            if max_d > eps and idx != -1:
                left = rdp(seq[: idx + 1], eps)
                right = rdp(seq[idx:], eps)
                return left[:-1] + right
            return [a, b]

        def angle(a: QPointF, b: QPointF, c: QPointF) -> float:
            bax = a.x() - b.x()
            bay = a.y() - b.y()
            bcx = c.x() - b.x()
            bcy = c.y() - b.y()
            ba = math.hypot(bax, bay)
            bc = math.hypot(bcx, bcy)
            if ba <= 1e-9 or bc <= 1e-9:
                return 0.0
            cosv = (bax * bcx + bay * bcy) / (ba * bc)
            cosv = max(-1.0, min(1.0, cosv))
            return math.degrees(math.acos(cosv))

        # 角点检测：角度越小越尖锐；不固定角度，只用于保留“拐点”
        corner_angle_threshold = 125.0
        min_corner_separation = max(10.0, thickness * 2.0)
        corner_indices = [0]
        last_corner_pt = filtered[0]
        for idx in range(1, len(filtered) - 1):
            a, b, c = filtered[idx - 1], filtered[idx], filtered[idx + 1]
            ang = angle(a, b, c)
            if ang <= corner_angle_threshold and dist(b, last_corner_pt) >= min_corner_separation:
                corner_indices.append(idx)
                last_corner_pt = b
        corner_indices.append(len(filtered) - 1)

        # 分段 RDP：每段端点固定，能更稳地保留多边形的边/角
        simplified = []
        for i in range(len(corner_indices) - 1):
            s = corner_indices[i]
            e = corner_indices[i + 1]
            segment = filtered[s : e + 1]
            if len(segment) <= 2:
                seg_simplified = segment
            else:
                # 段内可用更小 epsilon，让边更“直”但不吞掉角点
                seg_simplified = rdp(segment, max(1.5, epsilon * 0.75))
            if not simplified:
                simplified.extend(seg_simplified)
            else:
                simplified.extend(seg_simplified[1:])

        # 3) 合并过短边（避免抖动导致的微小折点）
        min_edge = max(6.0, thickness * 1.5)
        merged = [simplified[0]]
        for p in simplified[1:]:
            if dist(p, merged[-1]) >= min_edge:
                merged.append(p)
            else:
                merged[-1] = p
        if len(merged) < 2:
            merged = [simplified[0], simplified[-1]]

        # 4) 合并近共线段（角度接近 180°）
        collinear_threshold = 170.0
        i = 1
        while i < len(merged) - 1:
            a, b, c = merged[i - 1], merged[i], merged[i + 1]
            if angle(a, b, c) >= collinear_threshold:
                merged.pop(i)
            else:
                i += 1

        # 5) 闭合判断
        close_threshold = max(10.0, thickness * 3.0)
        should_close = prefer_closed or (dist(merged[0], merged[-1]) <= close_threshold and len(merged) >= 3)
        if should_close:
            # 移除尾部过近点后闭合
            if dist(merged[0], merged[-1]) <= close_threshold:
                merged[-1] = merged[0]
            else:
                merged.append(merged[0])

        return merged

    def _create_text_annotation(self, position):
        """创建文本标注"""
        try:
            # 使用多行文本编辑对话框
            if TextEditDialog:
                text, ok = TextEditDialog.get_text_input(
                    self.canvas, 
                    "创建文本标注", 
                    "请输入要标注的文本:", 
                    ""
                )
            else:
                # 回退到原始的单行输入对话框
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
    
    def _find_text_at_position(self, position):
        """查找指定位置的文本标注
        
        Args:
            position: 点击位置 (QPoint)
            
        Returns:
            Text 对象或 None
        """
        # 从后往前遍历（最新绘制的在前面）
        for shape in reversed(self.canvas.shapes):
            if isinstance(shape, Text):
                # 检查点击位置是否在文本区域内
                if hasattr(shape, 'contains_point') and shape.contains_point(QPointF(position)):
                    return shape
                # 如果没有 contains_point 方法，使用简单的距离检测
                elif hasattr(shape, 'position'):
                    distance = ((position.x() - shape.position.x())**2 + 
                               (position.y() - shape.position.y())**2)**0.5
                    # 使用一个合理的点击范围（考虑文本大小）
                    click_range = max(50, shape.font_size * 2) if hasattr(shape, 'font_size') else 50
                    if distance <= click_range:
                        return shape
        return None
    
    def _edit_existing_text(self, text_shape):
        """编辑现有的文本标注
        
        Args:
            text_shape: 要编辑的文本对象
        """
        try:
            # 保存状态到撤销栈（在修改前）
            self.canvas.state_manager.save_state_to_undo_stack()
            
            # 获取当前文本内容
            current_text = text_shape.text if hasattr(text_shape, 'text') else ""
            
            # 使用多行文本编辑对话框
            if TextEditDialog:
                new_text, ok = TextEditDialog.get_text_input(
                    self.canvas, 
                    "编辑文本标注", 
                    "请编辑文本内容:", 
                    current_text
                )
            else:
                # 回退到原始的单行输入对话框
                new_text, ok = QInputDialog.getText(
                    self.canvas, 
                    '编辑文本', 
                    '请编辑文本内容:', 
                    text=current_text
                )
            
            if ok:
                if new_text == "":
                    # 如果文本为空，删除该文本标注
                    if text_shape in self.canvas.shapes:
                        self.canvas.shapes.remove(text_shape)
                        print("文本标注已删除")
                else:
                    # 更新文本内容
                    if hasattr(text_shape, 'set_text'):
                        text_shape.set_text(new_text)
                    else:
                        text_shape.text = new_text
                        # 如果有边界计算方法，重新计算
                        if hasattr(text_shape, '_calculate_bounds'):
                            text_shape._calculate_bounds()
                    
                    print(f"文本标注已更新: {new_text}")
                
                # 更新显示
                self.canvas.update()
            
        except Exception as e:
            print(f"Error editing text annotation: {e}")

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

    def _find_image_at_position(self, position):
        """查找指定位置的图片标注
        
        Args:
            position: 点击位置 (QPoint)
            
        Returns:
            Image 对象或 None
        """
        # 从后往前遍历（最新绘制的在前面）
        for shape in reversed(self.canvas.shapes):
            if isinstance(shape, Image):
                # 检查点击位置是否在图片的选择区域内
                if hasattr(shape, 'contains_point') and shape.contains_point(QPointF(position)):
                    return shape
        return None
    
    def _create_image_annotation(self, position):
        """创建图片标注"""
        try:
            # 打开图片设置对话框
            if ImageSettingsDialog:
                settings = ImageSettingsDialog.get_image_settings(self.canvas)
                if settings:
                    # 保存状态到撤销栈
                    self.canvas.state_manager.save_state_to_undo_stack()
                    
                    # 创建图片对象
                    image_shape = Image(
                        position=QPointF(position),
                        image_path=settings['image_path'],
                        scale_factor=settings['scale_factor'],
                        rotation=settings['rotation'],
                        color=self.canvas.properties.current_color,
                        thickness=self.canvas.properties.current_thickness,
                        opacity=self.canvas.properties.current_opacity
                    )
                    
                    # 添加到形状列表
                    self.canvas.shapes.append(image_shape)
                    
                    # 如果是单次绘制模式，清空其他形状
                    if self.canvas.properties.single_draw_mode:
                        self.canvas.shapes = [image_shape]
                        self.canvas.state_manager.undo_stack.clear()
                    
                    # 更新显示
                    self.canvas.update()
                    print(f"图片标注已创建: {settings['image_path']}")
            else:
                # 回退到简单的文件选择
                image_path = Image.select_image_file(self.canvas)
                if image_path:
                    # 保存状态到撤销栈
                    self.canvas.state_manager.save_state_to_undo_stack()
                    
                    # 创建图片对象（使用默认设置）
                    image_shape = Image(
                        position=QPointF(position),
                        image_path=image_path,
                        scale_factor=1.0,
                        color=self.canvas.properties.current_color,
                        thickness=self.canvas.properties.current_thickness,
                        opacity=self.canvas.properties.current_opacity
                    )
                    
                    # 添加到形状列表
                    self.canvas.shapes.append(image_shape)
                    
                    # 如果是单次绘制模式，清空其他形状
                    if self.canvas.properties.single_draw_mode:
                        self.canvas.shapes = [image_shape]
                        self.canvas.state_manager.undo_stack.clear()
                    
                    # 更新显示
                    self.canvas.update()
                    print(f"图片标注已创建: {image_path}")
            
            # 重置绘制状态
            self.canvas.drawing = False
            self.canvas.current_shape = None
            
        except Exception as e:
            print(f"Error creating image annotation: {e}")
            # 重置绘制状态
            self.canvas.drawing = False
            self.canvas.current_shape = None
    
    def _edit_existing_image(self, image_shape):
        """编辑现有图片标注"""
        try:
            # 打开图片设置对话框，传入现有图片进行编辑
            if ImageSettingsDialog:
                settings = ImageSettingsDialog.get_image_settings(self.canvas, image_shape)
                if settings:
                    # 保存状态到撤销栈（用于撤销编辑操作）
                    self.canvas.state_manager.save_state_to_undo_stack()
                    
                    # 更新图片属性
                    image_shape.image_path = settings['image_path']
                    image_shape.scale_factor = settings['scale_factor']
                    image_shape.rotation = settings['rotation']
                    
                    # 重新加载图片（如果路径改变了）
                    image_shape.load_image()
                    
                    # 更新显示
                    self.canvas.update()
                    print(f"图片标注已更新: {settings['image_path']}")
            else:
                print("图片设置对话框不可用，无法编辑图片")
            
        except Exception as e:
            print(f"Error editing image annotation: {e}")
