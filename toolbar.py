"""
工具栏界面模块
包含屏幕标注工具的浮动工具栏界面
"""

from typing import Dict, Any, Optional, Callable
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QColorDialog, QSlider, QLabel, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, QPoint, QEvent


class AnnotationToolbar(QWidget):
    """屏幕标注工具栏"""
    
    def __init__(self, main_window, canvas):
        super().__init__()
        self.main_window = main_window
        self.canvas = canvas
        
        # 拖动相关属性
        self.drag_position: Optional[QPoint] = None
        self.dragging: bool = False
        
        # 工具按钮组
        self.tool_button_group: Dict[str, QPushButton] = {}
        
        # 控件属性
        self.color_btn: QPushButton
        self.thickness_slider: QSlider
        self.thickness_label: QLabel
        self.drawing_opacity_slider: QSlider
        self.drawing_opacity_label: QLabel
        self.canvas_opacity_slider: QSlider
        self.canvas_opacity_label: QLabel
        self.toggle_passthrough_btn: QPushButton
        self.toggle_visibility_btn: QPushButton
        self.single_draw_mode_btn: QPushButton
        self.toggle_collapse_btn: QPushButton
        self.title_container: QWidget
        self.title_label: QLabel
        
        # 操作按钮
        self.undo_btn: QPushButton
        self.redo_btn: QPushButton
        self.clear_btn: QPushButton
        self.import_btn: QPushButton
        self.export_btn: QPushButton
        self.exit_btn: QPushButton
        self.settings_btn: QPushButton
        self.save_config_btn: QPushButton
        self.theme_toggle_btn: QPushButton
        
        # 折叠状态
        self.is_collapsed = False
        
        # 主题状态
        self.is_dark_theme = True
        
        self.setup_toolbar()
        
    def setup_toolbar(self) -> None:
        """设置工具栏界面"""
        self.setWindowTitle("标注工具")
        # 确保工具栏始终在最顶层
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        
        # 启用鼠标追踪
        self.setMouseTracking(True)
        
        # 现代化样式
        self.setStyleSheet(self.get_theme_stylesheet())
        
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
        
        # 标题区域
        self.setup_title_section(toolbar_main_layout)
        
        # 内容区域容器
        self.content_widget = QWidget()
        self.update_content_widget_style()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setSpacing(6)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # 工具选择区域
        self.setup_tools_section(content_layout)
        
        # 颜色和属性控制区域
        self.setup_attributes_section(content_layout)
        
        # 操作按钮区域
        self.setup_actions_section(content_layout)
        
        toolbar_main_layout.addWidget(self.content_widget)
        
        # 设置工具栏窗口大小和位置
        self.setFixedSize(380, 620)
        self.move(50, 50)
        self.show()

    def setup_title_section(self, main_layout: QVBoxLayout) -> None:
        """设置标题区域"""
        self.title_container = QWidget()
        self.title_container.setObjectName("titleContainer")
        self.title_container.setCursor(Qt.SizeAllCursor)
        title_layout = QHBoxLayout(self.title_container)
        title_layout.setContentsMargins(12, 8, 12, 8)
        title_layout.setSpacing(8)
        
        # 标题标签
        self.title_label = QLabel("⚡ 屏幕标注工具")
        self.title_label.setObjectName("titleLabel")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # 主题切换按钮
        self.theme_toggle_btn = QPushButton("☀️")
        self.theme_toggle_btn.setObjectName("themeToggleButton")
        self.theme_toggle_btn.setToolTip("切换到白天模式")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        title_layout.addWidget(self.theme_toggle_btn)
        
        # 折叠按钮
        self.toggle_collapse_btn = QPushButton("🔼")
        self.toggle_collapse_btn.setObjectName("collapseButton")
        self.toggle_collapse_btn.clicked.connect(self.toggle_toolbar_collapse)
        title_layout.addWidget(self.toggle_collapse_btn)
        
        # 安装事件过滤器
        self.title_container.installEventFilter(self)
        
        main_layout.addWidget(self.title_container)
        
    def setup_tools_section(self, main_layout: QVBoxLayout) -> None:
        """设置工具选择区域"""
        tools_card = QFrame()
        tools_card.setFrameStyle(QFrame.NoFrame)
        tools_card.setProperty("class", "card")
        tools_layout = QVBoxLayout(tools_card)
        tools_layout.setContentsMargins(6, 6, 6, 6)
        tools_layout.setSpacing(6)
        
        # 区域标题
        tools_title = QLabel("🎨 绘制工具")
        tools_title.setProperty("class", "section-title")
        tools_layout.addWidget(tools_title)
        
        # 工具按钮网格布局
        tool_buttons = [
            ("直线", "line"),
            ("矩形", "rectangle"), 
            ("圆形", "circle"),
            ("箭头", "arrow"),
            ("自由绘制", "freehand"),
            ("填充绘制", "filled_freehand"),
            ("点", "point"),
            ("激光笔", "laser_pointer")
        ]
        
        self.tool_button_group = {}
        
        # 第一行工具按钮
        tools_row1 = QHBoxLayout()
        tools_row1.setSpacing(4)
        for name, tool in tool_buttons[:4]:
            btn = QPushButton(name)
            btn.setProperty("class", "tool")
            btn.setCheckable(True)
            btn.setMinimumSize(70, 28)
            btn.setMaximumSize(85, 32)
            tool_name = str(tool)
            btn.clicked.connect(lambda checked, tool_name=tool_name: self.main_window.select_tool(tool_name))
            tools_row1.addWidget(btn)
            self.tool_button_group[tool] = btn
        tools_layout.addLayout(tools_row1)
        
        # 第二行工具按钮
        tools_row2 = QHBoxLayout()
        tools_row2.setSpacing(4)
        for name, tool in tool_buttons[4:]:
            btn = QPushButton(name)
            btn.setProperty("class", "tool")
            btn.setCheckable(True)
            btn.setMinimumSize(70, 28)
            btn.setMaximumSize(85, 32)
            tool_name = str(tool)
            btn.clicked.connect(lambda checked, tool_name=tool_name: self.main_window.select_tool(tool_name))
            tools_row2.addWidget(btn)
            self.tool_button_group[tool] = btn
        tools_layout.addLayout(tools_row2)
        
        # 默认选择直线工具
        self.tool_button_group["line"].setChecked(True)
        
        main_layout.addWidget(tools_card)
        
    def setup_attributes_section(self, main_layout: QVBoxLayout) -> None:
        """设置属性控制区域"""
        attrs_card = QFrame()
        attrs_card.setFrameStyle(QFrame.NoFrame)
        attrs_card.setProperty("class", "card")
        attrs_layout = QVBoxLayout(attrs_card)
        attrs_layout.setContentsMargins(6, 6, 6, 6)
        attrs_layout.setSpacing(6)
        
        # 区域标题
        attrs_title = QLabel("⚙️ 绘制属性")
        attrs_title.setProperty("class", "section-title")
        attrs_layout.addWidget(attrs_title)
        
        # 颜色选择
        color_container = QWidget()
        color_layout = QHBoxLayout(color_container)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setSpacing(6)
        
        color_label = QLabel("颜色")
        color_label.setMinimumWidth(40)
        color_label.setMaximumWidth(50)
        self.color_btn = QPushButton("选择颜色")
        self.color_btn.setObjectName("colorButton")
        self.color_btn.clicked.connect(self.pick_color)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_btn)
        attrs_layout.addWidget(color_container)
        
        # 粗细控制
        thickness_container = QWidget()
        thickness_layout = QVBoxLayout(thickness_container)
        thickness_layout.setContentsMargins(0, 0, 0, 0)
        thickness_layout.setSpacing(2)
        
        self.thickness_label = QLabel(f"粗细: {self.canvas.current_thickness}")
        self.thickness_label.setMinimumHeight(16)
        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setMinimum(1)
        self.thickness_slider.setMaximum(20)
        self.thickness_slider.setValue(self.canvas.current_thickness)
        self.thickness_slider.valueChanged.connect(self.change_thickness)
        
        thickness_layout.addWidget(self.thickness_label)
        thickness_layout.addWidget(self.thickness_slider)
        attrs_layout.addWidget(thickness_container)
        
        # 绘制不透明度控制
        draw_opacity_container = QWidget()
        draw_opacity_layout = QVBoxLayout(draw_opacity_container)
        draw_opacity_layout.setContentsMargins(0, 0, 0, 0)
        draw_opacity_layout.setSpacing(2)
        
        self.drawing_opacity_label = QLabel(f"绘制透明度: {int(self.canvas.current_opacity * 100)}%")
        self.drawing_opacity_label.setMinimumHeight(16)
        self.drawing_opacity_slider = QSlider(Qt.Horizontal)
        self.drawing_opacity_slider.setMinimum(0)
        self.drawing_opacity_slider.setMaximum(100)
        self.drawing_opacity_slider.setValue(int(self.canvas.current_opacity * 100))
        self.drawing_opacity_slider.valueChanged.connect(self.change_drawing_opacity)
        
        draw_opacity_layout.addWidget(self.drawing_opacity_label)
        draw_opacity_layout.addWidget(self.drawing_opacity_slider)
        attrs_layout.addWidget(draw_opacity_container)
        
        # 画布不透明度控制
        canvas_opacity_container = QWidget()
        canvas_opacity_layout = QVBoxLayout(canvas_opacity_container)
        canvas_opacity_layout.setContentsMargins(0, 0, 0, 0)
        canvas_opacity_layout.setSpacing(2)
        
        self.canvas_opacity_label = QLabel(f"画布透明度: {int(self.canvas.canvas_opacity * 100)}%")
        self.canvas_opacity_label.setMinimumHeight(16)
        self.canvas_opacity_slider = QSlider(Qt.Horizontal)
        self.canvas_opacity_slider.setMinimum(0)
        self.canvas_opacity_slider.setMaximum(100)
        self.canvas_opacity_slider.setValue(int(self.canvas.canvas_opacity * 100))
        self.canvas_opacity_slider.valueChanged.connect(self.change_canvas_opacity)
        
        canvas_opacity_layout.addWidget(self.canvas_opacity_label)
        canvas_opacity_layout.addWidget(self.canvas_opacity_slider)
        attrs_layout.addWidget(canvas_opacity_container)
        attrs_layout.addStretch()
        
        main_layout.addWidget(attrs_card)

    def setup_actions_section(self, main_layout: QVBoxLayout) -> None:
        """设置操作按钮区域"""
        actions_card = QFrame()
        actions_card.setFrameStyle(QFrame.NoFrame)
        actions_card.setProperty("class", "card")
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(6, 6, 6, 6)
        actions_layout.setSpacing(6)
        
        # 区域标题
        actions_title = QLabel("🎯 操作控制")
        actions_title.setProperty("class", "section-title")
        actions_layout.addWidget(actions_title)
        
        # 编辑操作行
        edit_row = QHBoxLayout()
        edit_row.setSpacing(4)
        
        self.undo_btn = QPushButton("↶ 撤销")
        self.undo_btn.setProperty("class", "action")
        self.undo_btn.clicked.connect(self.canvas.undo)
        edit_row.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton("↷ 重做")
        self.redo_btn.setProperty("class", "action")
        self.redo_btn.clicked.connect(self.canvas.redo)
        edit_row.addWidget(self.redo_btn)
        
        self.clear_btn = QPushButton("🗑 清空")
        self.clear_btn.setProperty("class", "action warning")
        self.clear_btn.clicked.connect(self.canvas.clear_canvas)
        edit_row.addWidget(self.clear_btn)
        
        actions_layout.addLayout(edit_row)
        
        # 添加间距
        actions_layout.addSpacing(4)
        
        # 模式控制行
        mode_row = QHBoxLayout()
        mode_row.setSpacing(4)
        
        self.toggle_passthrough_btn = QPushButton("🖱 穿透")
        self.toggle_passthrough_btn.setProperty("class", "action")
        self.toggle_passthrough_btn.setCheckable(True)
        self.toggle_passthrough_btn.clicked.connect(self.main_window.toggle_mouse_passthrough)
        mode_row.addWidget(self.toggle_passthrough_btn)
        
        self.toggle_visibility_btn = QPushButton("👁 隐藏")
        self.toggle_visibility_btn.setProperty("class", "action")
        self.toggle_visibility_btn.setCheckable(True)
        self.toggle_visibility_btn.clicked.connect(self.main_window.toggle_canvas_visibility)
        mode_row.addWidget(self.toggle_visibility_btn)
        
        self.single_draw_mode_btn = QPushButton("1️⃣ 单次")
        self.single_draw_mode_btn.setProperty("class", "action")
        self.single_draw_mode_btn.setCheckable(True)
        self.single_draw_mode_btn.clicked.connect(self.main_window.toggle_single_draw_mode)
        mode_row.addWidget(self.single_draw_mode_btn)
        
        actions_layout.addLayout(mode_row)
        
        # 添加间距
        actions_layout.addSpacing(4)
        
        # 文件操作行
        file_row = QHBoxLayout()
        file_row.setSpacing(4)
        
        self.import_btn = QPushButton("📥 导入")
        self.import_btn.setProperty("class", "action primary")
        self.import_btn.clicked.connect(self.main_window.import_canvas_content)
        file_row.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.setProperty("class", "action success")
        self.export_btn.clicked.connect(self.main_window.export_canvas_content)
        file_row.addWidget(self.export_btn)
        
        self.save_config_btn = QPushButton("💾 保存")
        self.save_config_btn.setProperty("class", "action")
        self.save_config_btn.clicked.connect(self.main_window.save_current_config)
        file_row.addWidget(self.save_config_btn)
        
        actions_layout.addLayout(file_row)
        
        # 添加间距
        actions_layout.addSpacing(4)
        
        # 系统操作行
        system_row = QHBoxLayout()
        system_row.setSpacing(4)
        
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.setProperty("class", "action")
        self.settings_btn.clicked.connect(self.main_window.open_hotkey_settings)
        system_row.addWidget(self.settings_btn)
        
        self.exit_btn = QPushButton("❌ 退出")
        self.exit_btn.setProperty("class", "action danger")
        self.exit_btn.clicked.connect(self.main_window.close_application)
        system_row.addWidget(self.exit_btn)
        
        # 添加空白填充
        system_row.addStretch()
        
        actions_layout.addLayout(system_row)
        
        main_layout.addWidget(actions_card)
        
    def get_theme_stylesheet(self) -> str:
        """获取当前主题的样式表"""
        if self.is_dark_theme:
            return self.get_dark_theme_stylesheet()
        else:
            return self.get_light_theme_stylesheet()
    
    def get_dark_theme_stylesheet(self) -> str:
        """获取黑夜模式样式表"""
        return """
            /* 主容器样式 */
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 11px;
                border: none;
            }
            
            /* 卡片容器样式 */
            QFrame.card {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 6px;
                margin: 2px;
            }
            
            /* 标题区域样式 */
            QWidget#titleContainer {
                background-color: #0078d4;
                border-radius: 8px 8px 0px 0px;
                padding: 8px;
            }
            
            /* 标题标签样式 */
            QLabel#titleLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 0px;
            }
            
            /* 工具按钮样式 */
            QPushButton.tool {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                color: #ffffff;
                padding: 6px 8px;
                font-size: 9px;
                font-weight: 500;
                min-height: 26px;
                min-width: 65px;
                max-width: 80px;
            }
            QPushButton.tool:hover {
                background-color: #4a4a4a;
                border: 1px solid #0078d4;
                color: #ffffff;
            }
            QPushButton.tool:pressed {
                background-color: #2a2a2a;
                border: 1px solid #0078d4;
            }
            QPushButton.tool:checked {
                background-color: #0078d4;
                border: 1px solid #106ebe;
                color: #ffffff;
                font-weight: 600;
            }
            
            /* 操作按钮样式 */
            QPushButton.action {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                color: #ffffff;
                padding: 5px 8px;
                font-size: 9px;
                min-height: 24px;
                min-width: 60px;
                max-width: 85px;
            }
            QPushButton.action:hover {
                background-color: #3a3a3a;
                border: 1px solid #0078d4;
            }
            QPushButton.action:pressed {
                background-color: #1a1a1a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
            }
            QPushButton.action:checked {
                background-color: #0078d4;
                border: 1px solid #106ebe;
                border-radius: 6px;
                color: #ffffff;
            }
            
            /* 激活状态按钮样式 */
            QPushButton.action.active {
                background-color: #0078d4;
                border: 1px solid #106ebe;
                color: #ffffff;
                font-weight: 600;
            }
            QPushButton.action.active:hover {
                background-color: #106ebe;
                border: 1px solid #005a9e;
            }
            
            /* 特殊按钮样式 */
            QPushButton.primary {
                background-color: #0078d4;
                border: 1px solid #106ebe;
            }
            QPushButton.primary:hover {
                background-color: #106ebe;
            }
            
            QPushButton.success {
                background-color: #28a745;
                border: 1px solid #1e7e34;
            }
            QPushButton.success:hover {
                background-color: #1e7e34;
            }
            
            QPushButton.warning {
                background-color: #fd7e14;
                border: 1px solid #e8590c;
            }
            QPushButton.warning:hover {
                background-color: #e8590c;
            }
            
            QPushButton.danger {
                background-color: #dc3545;
                border: 1px solid #bd2130;
            }
            QPushButton.danger:hover {
                background-color: #bd2130;
            }
            
            /* 颜色按钮特殊样式 */
            QPushButton#colorButton {
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                min-height: 26px;
                min-width: 100px;
                max-width: 120px;
                font-weight: bold;
                font-size: 9px;
            }
            QPushButton#colorButton:hover {
                border: 1px solid #0078d4;
            }
            
            /* 标签样式 */
            QLabel {
                color: #ffffff;
                font-size: 9px;
                font-weight: 500;
                background: transparent;
                border: none;
                padding: 2px;
            }
            
            QLabel.section-title {
                color: #0078d4;
                font-size: 10px;
                font-weight: bold;
                padding: 3px 2px;
                border-bottom: 1px solid #3a3a3a;
                margin-bottom: 4px;
            }
            
            /* 滑块样式 */
            QSlider::groove:horizontal {
                border: 1px solid #3a3a3a;
                height: 4px;
                background: #2a2a2a;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #106ebe;
                width: 14px;
                height: 14px;
                border-radius: 7px;
                margin: -5px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #106ebe;
            }
            QSlider::handle:horizontal:pressed {
                background: #005a9e;
            }
            
            /* 折叠按钮样式 */
            QPushButton#collapseButton {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 12px;
                color: #ffffff;
                font-size: 10px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton#collapseButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #0078d4;
            }
            
            /* 主题切换按钮样式 */
            QPushButton#themeToggleButton {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 12px;
                color: #ffffff;
                font-size: 10px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton#themeToggleButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #0078d4;
            }
        """
    
    def get_light_theme_stylesheet(self) -> str:
        """获取白天模式样式表"""
        return """
            /* 主容器样式 */
            QWidget {
                background-color: #ffffff;
                color: #333333;
                font-family: "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 11px;
                border: none;
            }
            
            /* 卡片容器样式 */
            QFrame.card {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                padding: 6px;
                margin: 2px;
            }
            
            /* 标题区域样式 */
            QWidget#titleContainer {
                background-color: #0078d4;
                border-radius: 8px 8px 0px 0px;
                padding: 8px;
            }
            
            /* 标题标签样式 */
            QLabel#titleLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 0px;
            }
            
            /* 工具按钮样式 */
            QPushButton.tool {
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
                border-radius: 6px;
                color: #333333;
                padding: 6px 8px;
                font-size: 9px;
                font-weight: 500;
                min-height: 26px;
                min-width: 65px;
                max-width: 80px;
            }
            QPushButton.tool:hover {
                background-color: #d8d8d8;
                border: 1px solid #0078d4;
                color: #333333;
            }
            QPushButton.tool:pressed {
                background-color: #c8c8c8;
                border: 1px solid #0078d4;
                color: #333333;
            }
            QPushButton.tool:checked {
                background-color: #0078d4;
                border: 1px solid #106ebe;
                color: #333333;
                font-weight: 600;
            }
            
            /* 操作按钮样式 */
            QPushButton.action {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                color: #333333;
                padding: 5px 8px;
                font-size: 9px;
                min-height: 24px;
                min-width: 60px;
                max-width: 85px;
            }
            QPushButton.action:hover {
                background-color: #e0e0e0;
                border: 1px solid #0078d4;
            }
            QPushButton.action:pressed {
                background-color: #d0d0d0;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
            }
            QPushButton.action:checked {
                background-color: #0078d4;
                border: 1px solid #106ebe;
                border-radius: 6px;
                color: #333333;
            }
            
            /* 激活状态按钮样式 */
            QPushButton.action.active {
                background-color: #0078d4;
                border: 1px solid #106ebe;
                color: #333333;
                font-weight: 600;
            }
            QPushButton.action.active:hover {
                background-color: #106ebe;
                border: 1px solid #005a9e;
            }
            
            /* 特殊按钮样式 */
            QPushButton.primary {
                background-color: #0078d4;
                border: 1px solid #106ebe;
                color: #333333;
            }
            QPushButton.primary:hover {
                background-color: #106ebe;
            }
            
            QPushButton.success {
                background-color: #28a745;
                border: 1px solid #1e7e34;
                color: #333333;
            }
            QPushButton.success:hover {
                background-color: #1e7e34;
            }
            
            QPushButton.warning {
                background-color: #fd7e14;
                border: 1px solid #e8590c;
                color: #333333;
            }
            QPushButton.warning:hover {
                background-color: #e8590c;
            }
            
            QPushButton.danger {
                background-color: #dc3545;
                border: 1px solid #bd2130;
                color: #333333;
            }
            QPushButton.danger:hover {
                background-color: #bd2130;
            }
            
            /* 颜色按钮特殊样式 */
            QPushButton#colorButton {
                border: 2px solid #c0c0c0;
                border-radius: 6px;
                min-height: 26px;
                min-width: 100px;
                max-width: 120px;
                font-weight: bold;
                font-size: 9px;
            }
            QPushButton#colorButton:hover {
                border: 1px solid #0078d4;
            }
            
            /* 标签样式 */
            QLabel {
                color: #333333;
                font-size: 9px;
                font-weight: 500;
                background: transparent;
                border: none;
                padding: 2px;
            }
            
            QLabel.section-title {
                color: #0078d4;
                font-size: 10px;
                font-weight: bold;
                padding: 3px 2px;
                border-bottom: 1px solid #d0d0d0;
                margin-bottom: 4px;
            }
            
            /* 滑块样式 */
            QSlider::groove:horizontal {
                border: 1px solid #d0d0d0;
                height: 4px;
                background: #f0f0f0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #106ebe;
                width: 14px;
                height: 14px;
                border-radius: 7px;
                margin: -5px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #106ebe;
            }
            QSlider::handle:horizontal:pressed {
                background: #005a9e;
            }
            
            /* 折叠按钮样式 */
            QPushButton#collapseButton {
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
                border-radius: 12px;
                color: #333333;
                font-size: 10px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton#collapseButton:hover {
                background-color: #d8d8d8;
                border: 1px solid #0078d4;
            }
            
            /* 主题切换按钮样式 */
            QPushButton#themeToggleButton {
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
                border-radius: 12px;
                color: #333333;
                font-size: 10px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton#themeToggleButton:hover {
                background-color: #d8d8d8;
                border: 1px solid #0078d4;
            }
        """
    
    def toggle_theme(self) -> None:
        """切换主题"""
        self.is_dark_theme = not self.is_dark_theme
        self.setStyleSheet(self.get_theme_stylesheet())
        
        # 更新主题切换按钮图标
        if self.is_dark_theme:
            self.theme_toggle_btn.setText("☀️")
            self.theme_toggle_btn.setToolTip("切换到白天模式")
        else:
            self.theme_toggle_btn.setText("🌙")
            self.theme_toggle_btn.setToolTip("切换到黑夜模式")
        
        # 更新内容区域的样式
        self.update_content_widget_style()
        
        # 重新应用颜色按钮的样式
        self.update_color_button()
        
        # 显示状态信息
        theme_name = "黑夜模式" if self.is_dark_theme else "白天模式"
        self.main_window.statusBar().showMessage(f"已切换到{theme_name}", 1000)

    def update_color_button(self) -> None:
        """更新颜色按钮的显示"""
        color: QColor = self.canvas.current_color
        
        # 根据主题选择边框颜色
        border_color = "#4a4a4a" if self.is_dark_theme else "#c0c0c0"
        
        self.color_btn.setStyleSheet(f"""
            QPushButton#colorButton {{
                background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()});
                border: 2px solid {border_color};
                border-radius: 6px;
                color: {"white" if color.red() + color.green() + color.blue() < 384 else "black"};
                font-weight: bold;
                min-height: 28px;
                min-width: 80px;
            }}
            QPushButton#colorButton:hover {{
                border: 1px solid #0078d4;
            }}
        """)

    def change_thickness(self, value: int) -> None:
        """改变线条粗细"""
        self.canvas.set_current_thickness(value)
        self.thickness_label.setText(f"粗细: {value}")

    def pick_color(self) -> None:
        """选择颜色并应用到画布"""
        # 创建一个独立的颜色选择对话框
        dialog: QColorDialog = QColorDialog(self.canvas.current_color, self)
        
        # 设置对话框选项，确保它总是在最前面
        dialog.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        dialog.setOption(QColorDialog.ShowAlphaChannel, True)
        
        # 临时隐藏主窗口来避免遮挡对话框
        main_visible: bool = self.main_window.isVisible()
        if main_visible and not self.main_window.passthrough_state:
            self.main_window.hide()
        
        # 显示对话框并等待用户选择
        if dialog.exec_() == QColorDialog.Accepted:
            color: QColor = dialog.currentColor()
            if color.isValid():
                self.canvas.set_current_color(color)
                self.update_color_button()
        
        # 恢复主窗口可见性
        if main_visible:
            self.main_window.show()
            self.main_window.activateWindow()
            self.main_window.raise_()
        
        # 确保工具栏在最前面
        self.main_window.ensure_toolbar_on_top()

    def change_drawing_opacity(self, value: int) -> None:
        """改变绘制不透明度"""
        opacity: float = value / 100.0
        self.canvas.set_current_opacity(opacity)
        self.drawing_opacity_label.setText(f"绘制透明度: {value}%")

    def change_canvas_opacity(self, value: int) -> None:
        """改变画布不透明度"""
        opacity: float = value / 100.0
        self.canvas.set_canvas_opacity(opacity)
        
        # 记住当前模式下的用户设置
        if self.main_window.passthrough_state:
            self.main_window.user_passthrough_opacity = opacity
        else:
            self.main_window.user_non_passthrough_opacity = opacity
        
        self.canvas_opacity_label.setText(f"画布透明度: {value}%")

    def update_canvas_opacity_ui(self) -> None:
        """更新GUI上的画布透明度显示，确保与实际画布透明度一致"""
        current_opacity: float = self.canvas.canvas_opacity
        percentage: int = int(current_opacity * 100)
        
        # 更新滑动条值（防止触发信号循环）
        self.canvas_opacity_slider.blockSignals(True)
        self.canvas_opacity_slider.setValue(percentage)
        self.canvas_opacity_slider.blockSignals(False)
        
        # 更新标签显示
        self.canvas_opacity_label.setText(f"画布透明度: {percentage}%")

    def toggle_toolbar_collapse(self) -> None:
        """切换工具栏折叠/展开状态"""
        collapsed_height: int = 50  # 标题栏的高度
        expanded_height: int = 620  # 完全展开的高度
        
        if not self.is_collapsed:
            # 折叠
            self.content_widget.hide()
            self.setFixedSize(380, collapsed_height)
            self.toggle_collapse_btn.setText("🔽")
            self.is_collapsed = True
            self.main_window.statusBar().showMessage("工具栏已折叠", 1000)
        else:
            # 展开
            self.content_widget.show()
            self.setFixedSize(380, expanded_height)
            self.toggle_collapse_btn.setText("🔼")
            self.is_collapsed = False
            self.main_window.statusBar().showMessage("工具栏已展开", 1000)
            
        # 确保工具栏始终在最前面
        self.main_window.ensure_toolbar_on_top()

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        """事件过滤器，用于处理工具栏的拖动"""
        # 处理工具栏拖动
        if obj == self.title_container:
            if event.type() == event.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    # 记录鼠标按下位置和拖动状态
                    self.drag_position = event.globalPos() - self.pos()
                    self.dragging = True
                    return True
            elif event.type() == event.MouseMove:
                if self.dragging and event.buttons() & Qt.LeftButton:
                    # 计算新位置并移动工具栏
                    new_pos: QPoint = event.globalPos() - self.drag_position
                    self.move(new_pos)
                    return True
            elif event.type() == event.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    # 释放拖动状态
                    self.dragging = False
                    return True
        
        # 让其他事件继续正常处理
        return super().eventFilter(obj, event)

    def update_content_widget_style(self) -> None:
        """更新内容区域的样式"""
        bg_color = "#1a1a1a" if self.is_dark_theme else "#ffffff"
        self.content_widget.setStyleSheet(f"background-color: {bg_color}; border-radius: 0px 0px 8px 8px;")
