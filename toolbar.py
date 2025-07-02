"""
工具栏界面模块
包含屏幕标注工具的浮动工具栏界面
"""

from typing import Dict, Any, Optional, Callable
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QColorDialog, QSlider, QLabel)
from PyQt5.QtGui import QColor
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
        
        self.setup_toolbar()
        
    def setup_toolbar(self) -> None:
        """设置工具栏界面"""
        self.setWindowTitle("标注工具")
        # 确保工具栏始终在最顶层，优先级高于主窗口
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        # 设置工具栏窗口的层级更高
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        
        # 启用鼠标追踪以便实现拖动功能
        self.setMouseTracking(True)
        
        # 设置工具栏样式，优化外观并支持按钮状态变色
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(250, 250, 250, 245);
                border: 2px solid #d0d0d0;
                border-radius: 8px;
                font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px 10px;
                min-height: 24px;
                color: #333333;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f0f7ff;
                border-color: #4a9eff;
            }
            QPushButton:pressed {
                background-color: #e1f0ff;
            }
            QPushButton:checked {
                background-color: #0078d4;
                color: white;
                border-color: #106ebe;
                font-weight: 600;
            }
            QPushButton.active {
                background-color: #28a745;
                color: white;
                border-color: #1e7e34;
            }
            QPushButton.warning {
                background-color: #fd7e14;
                color: white;
                border-color: #e8590c;
            }
            QPushButton.danger {
                background-color: #dc3545;
                color: white;
                border-color: #bd2130;
            }
            QLabel {
                color: #333333;
                font-weight: 500;
                margin: 2px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                height: 6px;
                background: #f0f0f0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #005a9e;
                width: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #106ebe;
            }
        """)
        
        # 主工具栏布局 - 优化间距和分组
        toolbar_main_layout = QVBoxLayout(self)
        toolbar_main_layout.setSpacing(8)
        toolbar_main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题区域 - 作为拖动区域
        self.title_container = QWidget()
        self.title_container.setCursor(Qt.SizeAllCursor)  # 显示拖动光标
        title_layout = QHBoxLayout(self.title_container)
        title_layout.setContentsMargins(5, 5, 5, 5)
        
        # 添加标题
        self.title_label = QLabel("🎨 屏幕标注工具")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #0078d4;
                padding: 5px;
                border-bottom: 2px solid #e0e0e0;
                margin-bottom: 5px;
            }
        """)
        title_layout.addWidget(self.title_label)
        
        # 添加缩小/展开按钮
        self.toggle_collapse_btn = QPushButton("🔼")
        self.toggle_collapse_btn.setFixedSize(24, 24)
        self.toggle_collapse_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                border: 1px solid #cccccc;
                border-radius: 12px;
                background-color: #f8f8f8;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.toggle_collapse_btn.clicked.connect(self.toggle_toolbar_collapse)
        title_layout.addWidget(self.toggle_collapse_btn)
        
        # 安装事件过滤器到标题容器，处理拖动
        self.title_container.installEventFilter(self)
        
        toolbar_main_layout.addWidget(self.title_container)
        
        # 工具选择区域
        self.setup_tools_section(toolbar_main_layout)
        
        # 颜色和属性控制区域
        self.setup_attributes_section(toolbar_main_layout)
        
        # 操作按钮区域
        self.setup_actions_section(toolbar_main_layout)
        
        # 设置工具栏窗口大小和位置 - 优化尺寸，增加高度以容纳新按钮
        self.setFixedSize(320, 520)  # 展开状态的初始大小
        self.move(50, 50)
        self.show()
        
    def setup_tools_section(self, main_layout: QVBoxLayout) -> None:
        """设置工具选择区域"""
        tools_group = QWidget()
        tools_layout = QVBoxLayout(tools_group)
        tools_layout.setContentsMargins(0, 0, 0, 0)
        tools_layout.setSpacing(6)
        
        # 工具区域标题
        tools_title = QLabel("📐 绘制工具")
        tools_title.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 3px;")
        tools_layout.addWidget(tools_title)
        
        # 工具按钮 - 分两行布局
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
            btn.setCheckable(True)
            btn.setMinimumSize(65, 32)
            # 创建闭包时正确绑定参数，确保值被正确捕获
            tool_name = str(tool)  # 创建工具名称的副本
            btn.clicked.connect(lambda checked, tool_name=tool_name: self.main_window.select_tool(tool_name))
            tools_row1.addWidget(btn)
            self.tool_button_group[tool] = btn
        tools_layout.addLayout(tools_row1)
        
        # 第二行工具按钮
        tools_row2 = QHBoxLayout()
        tools_row2.setSpacing(4)
        for name, tool in tool_buttons[4:]:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setMinimumSize(65, 32)
            # 创建闭包时正确绑定参数，确保值被正确捕获
            tool_name = str(tool)  # 创建工具名称的副本
            btn.clicked.connect(lambda checked, tool_name=tool_name: self.main_window.select_tool(tool_name))
            tools_row2.addWidget(btn)
            self.tool_button_group[tool] = btn
        # 添加空白填充
        tools_row2.addStretch()
        tools_layout.addLayout(tools_row2)
        
        # 默认选择直线工具
        self.tool_button_group["line"].setChecked(True)
        
        main_layout.addWidget(tools_group)
        
    def setup_attributes_section(self, main_layout: QVBoxLayout) -> None:
        """设置属性控制区域"""
        attrs_group = QWidget()
        attrs_layout = QVBoxLayout(attrs_group)
        attrs_layout.setContentsMargins(0, 0, 0, 0)
        attrs_layout.setSpacing(8)
        
        # 属性区域标题
        attrs_title = QLabel("🎨 绘制属性")
        attrs_title.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 3px;")
        attrs_layout.addWidget(attrs_title)
        
        # 颜色选择行
        color_row = QHBoxLayout()
        color_row.setSpacing(8)
        color_label = QLabel("颜色:")
        color_label.setMinimumWidth(50)
        self.color_btn = QPushButton("选择颜色")
        self.color_btn.setMinimumSize(90, 32)
        self.color_btn.clicked.connect(self.pick_color)
        color_row.addWidget(color_label)
        color_row.addWidget(self.color_btn)
        color_row.addStretch()
        attrs_layout.addLayout(color_row)
        
        # 粗细控制行
        thickness_row = QHBoxLayout()
        thickness_row.setSpacing(8)
        self.thickness_label = QLabel(f"粗细: {self.canvas.current_thickness}")
        self.thickness_label.setMinimumWidth(70)
        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setMinimum(1)
        self.thickness_slider.setMaximum(20)
        self.thickness_slider.setValue(self.canvas.current_thickness)
        self.thickness_slider.valueChanged.connect(self.change_thickness)
        thickness_row.addWidget(self.thickness_label)
        thickness_row.addWidget(self.thickness_slider)
        attrs_layout.addLayout(thickness_row)
        
        # 绘制不透明度控制行
        draw_opacity_row = QHBoxLayout()
        draw_opacity_row.setSpacing(8)
        self.drawing_opacity_label = QLabel(f"绘制: {int(self.canvas.current_opacity * 100)}%")
        self.drawing_opacity_label.setMinimumWidth(70)
        self.drawing_opacity_slider = QSlider(Qt.Horizontal)
        self.drawing_opacity_slider.setMinimum(0)
        self.drawing_opacity_slider.setMaximum(100)
        self.drawing_opacity_slider.setValue(int(self.canvas.current_opacity * 100))
        self.drawing_opacity_slider.valueChanged.connect(self.change_drawing_opacity)
        draw_opacity_row.addWidget(self.drawing_opacity_label)
        draw_opacity_row.addWidget(self.drawing_opacity_slider)
        attrs_layout.addLayout(draw_opacity_row)
        
        # 画布不透明度控制行
        canvas_opacity_row = QHBoxLayout()
        canvas_opacity_row.setSpacing(8)
        self.canvas_opacity_label = QLabel(f"画布: {int(self.canvas.canvas_opacity * 100)}%")
        self.canvas_opacity_label.setMinimumWidth(70)
        self.canvas_opacity_slider = QSlider(Qt.Horizontal)
        self.canvas_opacity_slider.setMinimum(0)
        self.canvas_opacity_slider.setMaximum(100)
        self.canvas_opacity_slider.setValue(int(self.canvas.canvas_opacity * 100))
        self.canvas_opacity_slider.valueChanged.connect(self.change_canvas_opacity)
        canvas_opacity_row.addWidget(self.canvas_opacity_label)
        canvas_opacity_row.addWidget(self.canvas_opacity_slider)
        attrs_layout.addLayout(canvas_opacity_row)
        
        main_layout.addWidget(attrs_group)
        
    def setup_actions_section(self, main_layout: QVBoxLayout) -> None:
        """设置操作按钮区域"""
        actions_group = QWidget()
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)
        
        # 操作区域标题
        actions_title = QLabel("⚙️ 操作控制")
        actions_title.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 3px;")
        actions_layout.addWidget(actions_title)
        
        # 第一行操作按钮 - 编辑操作
        action_row1 = QHBoxLayout()
        action_row1.setSpacing(6)
        
        self.undo_btn = QPushButton("↶ 撤销")
        self.undo_btn.setMinimumSize(70, 32)
        self.undo_btn.clicked.connect(self.canvas.undo)
        action_row1.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton("↷ 重做")
        self.redo_btn.setMinimumSize(70, 32)
        self.redo_btn.clicked.connect(self.canvas.redo)
        action_row1.addWidget(self.redo_btn)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.setMinimumSize(70, 32)
        self.clear_btn.clicked.connect(self.canvas.clear_canvas)
        self.clear_btn.setProperty("class", "warning")
        action_row1.addWidget(self.clear_btn)
        
        actions_layout.addLayout(action_row1)
        
        # 第二行操作按钮 - 模式控制
        action_row2 = QHBoxLayout()
        action_row2.setSpacing(6)
        
        self.toggle_passthrough_btn = QPushButton("🖱️ 穿透")
        self.toggle_passthrough_btn.setCheckable(True)
        self.toggle_passthrough_btn.setMinimumSize(70, 32)
        self.toggle_passthrough_btn.clicked.connect(self.main_window.toggle_mouse_passthrough)
        action_row2.addWidget(self.toggle_passthrough_btn)
        
        self.toggle_visibility_btn = QPushButton("👁️ 隐藏")
        self.toggle_visibility_btn.setCheckable(True)
        self.toggle_visibility_btn.setMinimumSize(70, 32)
        self.toggle_visibility_btn.clicked.connect(self.main_window.toggle_canvas_visibility)
        action_row2.addWidget(self.toggle_visibility_btn)
        
        self.single_draw_mode_btn = QPushButton("1️⃣ 单次")
        self.single_draw_mode_btn.setCheckable(True)
        self.single_draw_mode_btn.setMinimumSize(70, 32)
        self.single_draw_mode_btn.clicked.connect(self.main_window.toggle_single_draw_mode)
        action_row2.addWidget(self.single_draw_mode_btn)
        
        actions_layout.addLayout(action_row2)
        
        # 第三行操作按钮 - 文件操作
        action_row3 = QHBoxLayout()
        action_row3.setSpacing(6)
        
        self.import_btn = QPushButton("📥 导入")
        self.import_btn.setMinimumSize(70, 32)
        self.import_btn.clicked.connect(self.main_window.import_canvas_content)
        action_row3.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.setMinimumSize(70, 32)
        self.export_btn.clicked.connect(self.main_window.export_canvas_content)
        action_row3.addWidget(self.export_btn)
        
        # 添加退出按钮
        self.exit_btn = QPushButton("❌ 退出")
        self.exit_btn.setMinimumSize(70, 32)
        self.exit_btn.clicked.connect(self.main_window.close_application)
        self.exit_btn.setProperty("class", "danger")
        action_row3.addWidget(self.exit_btn)
        
        actions_layout.addLayout(action_row3)
        
        # 第四行操作按钮 - 设置功能
        action_row4 = QHBoxLayout()
        action_row4.setSpacing(6)
        
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.setMinimumSize(70, 32)
        self.settings_btn.clicked.connect(self.main_window.open_hotkey_settings)
        action_row4.addWidget(self.settings_btn)
        
        self.save_config_btn = QPushButton("💾 保存")
        self.save_config_btn.setMinimumSize(70, 32)
        self.save_config_btn.clicked.connect(self.main_window.save_current_config)
        action_row4.addWidget(self.save_config_btn)
        
        # 添加空白填充
        action_row4.addStretch()
        
        actions_layout.addLayout(action_row4)
        
        main_layout.addWidget(actions_group)
        
    def update_color_button(self) -> None:
        """更新颜色按钮的显示"""
        color: QColor = self.canvas.current_color
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()});
                border: 2px solid #666;
                border-radius: 4px;
                color: {"white" if color.red() + color.green() + color.blue() < 384 else "black"};
                font-weight: bold;
            }}
            QPushButton:hover {{
                border-color: #4a9eff;
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
        self.drawing_opacity_label.setText(f"绘制: {value}%")

    def change_canvas_opacity(self, value: int) -> None:
        """改变画布不透明度"""
        opacity: float = value / 100.0
        self.canvas.set_canvas_opacity(opacity)
        
        # 记住当前模式下的用户设置
        if self.main_window.passthrough_state:
            self.main_window.user_passthrough_opacity = opacity
        else:
            self.main_window.user_non_passthrough_opacity = opacity
        
        self.canvas_opacity_label.setText(f"画布: {value}%")

    def update_canvas_opacity_ui(self) -> None:
        """更新GUI上的画布透明度显示，确保与实际画布透明度一致"""
        current_opacity: float = self.canvas.canvas_opacity
        percentage: int = int(current_opacity * 100)
        
        # 更新滑动条值（防止触发信号循环）
        self.canvas_opacity_slider.blockSignals(True)
        self.canvas_opacity_slider.setValue(percentage)
        self.canvas_opacity_slider.blockSignals(False)
        
        # 更新标签显示
        self.canvas_opacity_label.setText(f"画布: {percentage}%")

    def toggle_toolbar_collapse(self) -> None:
        """切换工具栏折叠/展开状态"""
        # 定义工具栏的折叠高度和展开高度
        collapsed_height: int = 36  # 标题栏的高度
        expanded_height: int = 520  # 完全展开的高度
        
        # 获取当前高度
        current_height: int = self.height()
        
        if current_height > collapsed_height:
            # 当前是展开状态，需要折叠
            self.setFixedSize(320, collapsed_height)
            self.toggle_collapse_btn.setText("🔽")
            # 隐藏除标题容器外的所有组件
            for i in range(1, self.layout().count()):
                widget = self.layout().itemAt(i).widget()
                if widget:
                    widget.hide()
            self.main_window.statusBar().showMessage("工具栏已折叠", 1000)
        else:
            # 当前是折叠状态，需要展开
            self.setFixedSize(320, expanded_height)
            self.toggle_collapse_btn.setText("🔼")
            # 显示所有组件
            for i in range(1, self.layout().count()):
                widget = self.layout().itemAt(i).widget()
                if widget:
                    widget.show()
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
