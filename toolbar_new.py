"""
工具栏界面模块（重构版）
包含屏幕标注工具的浮动工具栏界面
"""

from typing import Dict, Any, Optional, Callable
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QColorDialog, QSlider, QLabel, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QColor, QFont, QMouseEvent
from PyQt5.QtCore import Qt, QPoint, QEvent
from PyQt5 import QtCore

# 导入拆分的模块
from toolbar_theme import ToolbarThemeManager
from toolbar_widgets import ToolbarWidgetBuilder
from toolbar_events import ToolbarEventHandler


class AnnotationToolbar(QWidget):
    """屏幕标注工具栏（重构版）"""
    
    def __init__(self, main_window, canvas):
        super().__init__()
        self.main_window = main_window
        self.canvas = canvas
        
        # 初始化模块化组件
        self.theme_manager = ToolbarThemeManager(self)
        self.widget_builder = ToolbarWidgetBuilder(self)
        self.event_handler = ToolbarEventHandler(self)
        
        # 拖动相关属性
        self.drag_position: QPoint = QPoint(0, 0)
        self.dragging: bool = False
        
        # 工具按钮组
        self.tool_button_group: Dict[str, QPushButton] = {}
        
        # 初始化控件属性（将在widget_builder中创建）
        self._init_widget_attributes()
        
        # 状态属性
        self.is_collapsed = False
        
        # 工具栏尺寸
        self.toolbar_width = 380
        self.toolbar_height = 680
        self.collapsed_height = 50
        
        self.setup_toolbar()
    
    def _init_widget_attributes(self) -> None:
        """初始化控件属性（占位符，实际在widget_builder中创建）"""
        # 基本控件
        self.color_btn: Optional[QPushButton] = None
        self.thickness_slider: Optional[QSlider] = None
        self.thickness_label: Optional[QLabel] = None
        self.drawing_opacity_slider: Optional[QSlider] = None
        self.drawing_opacity_label: Optional[QLabel] = None
        self.canvas_opacity_slider: Optional[QSlider] = None
        self.canvas_opacity_label: Optional[QLabel] = None
        
        # 标题区域控件
        self.title_container: Optional[QWidget] = None
        self.title_label: Optional[QLabel] = None
        self.theme_toggle_btn: Optional[QPushButton] = None
        self.toggle_collapse_btn: Optional[QPushButton] = None
        
        # 模式控制按钮
        self.toggle_passthrough_btn: Optional[QPushButton] = None
        self.toggle_visibility_btn: Optional[QPushButton] = None
        self.single_draw_mode_btn: Optional[QPushButton] = None
        
        # 操作按钮
        self.undo_btn: Optional[QPushButton] = None
        self.redo_btn: Optional[QPushButton] = None
        self.clear_btn: Optional[QPushButton] = None
        self.import_btn: Optional[QPushButton] = None
        self.export_btn: Optional[QPushButton] = None
        self.exit_btn: Optional[QPushButton] = None
        self.settings_btn: Optional[QPushButton] = None
        self.save_config_btn: Optional[QPushButton] = None
        self.text_style_btn: Optional[QPushButton] = None
        
        # 内容区域
        self.content_widget: Optional[QWidget] = None
        
    def setup_toolbar(self) -> None:
        """设置工具栏界面"""
        # 从主窗口配置中获取字体大小
        if hasattr(self.main_window, 'config') and 'toolbar_font_size' in self.main_window.config:
            self.theme_manager.font_size = self.main_window.config['toolbar_font_size']
        
        self.setWindowTitle("标注工具")
        # 确保工具栏始终在最顶层
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        
        # 启用鼠标追踪
        self.setMouseTracking(True)
        
        # 应用主题样式
        self.setStyleSheet(self.theme_manager.get_theme_stylesheet())
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # 主工具栏布局
        toolbar_main_layout = QVBoxLayout(self)
        toolbar_main_layout.setSpacing(0)
        toolbar_main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 使用widget_builder创建界面组件
        self.widget_builder.setup_title_section(toolbar_main_layout)
        
        # 内容区域容器
        self.content_widget = QWidget()
        self.theme_manager.update_content_widget_style()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setSpacing(8)
        content_layout.setContentsMargins(12, 12, 12, 12)
        
        # 使用widget_builder创建各个区域
        self.widget_builder.setup_tools_section(content_layout)
        self.widget_builder.setup_attributes_section(content_layout)
        self.widget_builder.setup_actions_section(content_layout)
        
        toolbar_main_layout.addWidget(self.content_widget)
        
        # 计算并设置自适应尺寸
        self.calculate_and_set_size()
        self.move(50, 50)
        self.show()

    # 事件处理方法（委托给event_handler）
    def pick_color(self) -> None:
        """选择颜色并应用到画布"""
        self.event_handler.handle_color_selection()

    def change_thickness(self, value: int) -> None:
        """改变线条粗细"""
        self.event_handler.handle_thickness_change(value)

    def change_drawing_opacity(self, value: int) -> None:
        """改变绘制不透明度"""
        self.event_handler.handle_drawing_opacity_change(value)

    def change_canvas_opacity(self, value: int) -> None:
        """改变画布不透明度"""
        self.event_handler.handle_canvas_opacity_change(value)

    def toggle_toolbar_collapse(self) -> None:
        """切换工具栏折叠/展开状态"""
        self.event_handler.handle_toolbar_collapse_toggle()

    def open_text_style_dialog(self) -> None:
        """打开文本样式设置对话框"""
        self.event_handler.handle_text_style_dialog()

    def update_canvas_opacity_ui(self) -> None:
        """更新GUI上的画布透明度显示，确保与实际画布透明度一致"""
        self.event_handler.update_canvas_opacity_display()

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        """事件过滤器，用于处理工具栏的拖动"""
        if self.event_handler.handle_mouse_events(obj, event):
            return True
        
        # 让其他事件继续正常处理
        return super().eventFilter(obj, event)

    # 主题和样式相关方法（委托给theme_manager）
    def update_color_button(self) -> None:
        """更新颜色按钮的显示"""
        color: QColor = self.canvas.current_color
        self.theme_manager.update_color_button_style(color)

    def update_font_size(self, size: int) -> None:
        """更新字体大小"""
        self.theme_manager.update_font_size(size)
        
        # 重新计算和设置尺寸
        self.calculate_and_set_size()
        
        # 强制重绘界面
        self.repaint()

    # 尺寸计算方法
    def calculate_and_set_size(self) -> None:
        """计算并设置工具栏的最佳尺寸"""
        # 确保内容已完全布局
        if self.content_widget:
            self.content_widget.adjustSize()
        
        # 获取标题区域高度
        title_height = self.title_container.sizeHint().height() if self.title_container else 50
        
        # 获取内容区域高度
        content_height = self.content_widget.sizeHint().height() if self.content_widget else 600
        
        # 计算总高度（标题 + 内容 + 额外边距）
        total_height = title_height + content_height + 20  # 20px额外边距
        
        # 确保最小高度
        min_height = 650
        self.toolbar_height = max(total_height, min_height)
        
        # 设置工具栏尺寸
        self.setFixedSize(self.toolbar_width, self.toolbar_height)
        
        # 更新折叠高度
        self.collapsed_height = title_height + 10  # 10px边距

    def get_recommended_size(self) -> tuple:
        """获取推荐的工具栏尺寸"""
        # 基于字体大小计算推荐尺寸
        base_width = 380
        base_height = 680
        
        # 根据字体大小调整
        font_scale = self.theme_manager.font_size / 11.0
        adjusted_width = int(base_width * font_scale)
        adjusted_height = int(base_height * font_scale)
        
        return adjusted_width, adjusted_height
    
    # 属性访问器，用于兼容性
    @property
    def font_size(self) -> int:
        """获取字体大小"""
        return self.theme_manager.font_size
    
    @property
    def is_dark_theme(self) -> bool:
        """获取是否为黑夜主题"""
        return self.theme_manager.is_dark_theme
