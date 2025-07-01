import sys
import json
from typing import Dict, Any, Optional, Callable
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QColorDialog, QSlider, QLabel, QFileDialog, QStatusBar, QMenuBar, QAction, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QColor, QIcon, QCloseEvent
from PyQt5.QtCore import Qt, QTimer, QPoint, QEvent
from gui import DrawingCanvas
from hotkey_manager import HotkeyManager
from config import load_config, save_config
from hotkey_settings import HotkeySettingsDialog

class AnnotationTool(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("屏幕标注工具")
        self.setGeometry(100, 100, 1000, 800)

        self.central_widget: QWidget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout: QVBoxLayout = QVBoxLayout(self.central_widget)

        self.config: Dict[str, Any] = load_config()

        self.canvas: DrawingCanvas = DrawingCanvas()
        self.canvas.set_current_color(self.config["current_color"])
        self.canvas.set_current_thickness(self.config["current_thickness"])
        self.canvas.set_current_opacity(self.config["current_opacity"])
        self.canvas.set_canvas_color(self.config["canvas_color"])
        self.canvas.set_canvas_opacity(self.config["canvas_opacity"])
        self.main_layout.addWidget(self.canvas)
          # 初始化热键管理器
        self.hotkey_manager: HotkeyManager = HotkeyManager(self)

        # 工具栏完全隐藏状态（不保存到配置文件）
        self.toolbar_completely_hidden: bool = False

        # 工具栏相关属性类型定义（将在setup方法中初始化）
        self.toolbar_window: QWidget
        self.toolbar_drag_position: Optional[QPoint] = None
        self.toolbar_dragging: bool = False
        self.toolbar_timer: QTimer
        
        # 按钮相关属性类型定义（将在setup方法中初始化）
        self.tool_button_group: Dict[str, QPushButton] = {}
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
        
        # 透明度相关属性
        self.passthrough_opacity: float
        self.non_passthrough_opacity: float
        self.passthrough_state: bool
        self.user_passthrough_opacity: float
        self.user_non_passthrough_opacity: float
        
        # 系统托盘相关属性
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.tray_icon_visible: bool = False

        self.setup_menubar()
        self.setup_toolbar()
        self.setup_window_properties()
        self.setup_hotkeys()  # 设置热键
        self.hotkey_manager.start_listening()  # 启动热键监听
        
        # 初始化颜色按钮显示
        self.update_color_button()
        
        # 初始化画布透明度GUI显示
        self.update_canvas_opacity_ui()
        
        # 确保工具栏在主窗口显示后仍然在最前面
        self.ensure_toolbar_on_top()
        
        # 设置定时器定期确保工具栏在最前面
        self.toolbar_timer = QTimer()
        self.toolbar_timer.timeout.connect(self.ensure_toolbar_on_top)
        self.toolbar_timer.start(1000)  # 每秒检查一次
        
        # 初始化系统托盘
        self.setup_system_tray()
    def toggle_visibility(self) -> None:
        """切换主窗口显示/隐藏"""
        print("热键 toggle_visibility 被触发!")
        if self.isVisible():
            self.hide()
            print("主窗口已隐藏")
        else:
            self.show()
            print("主窗口已显示")
            
    def setup_toolbar(self) -> None:
        # 创建浮动工具栏窗口
        self.toolbar_window = QWidget()
        self.toolbar_window.setWindowTitle("标注工具")
        # 确保工具栏始终在最顶层，优先级高于主窗口
        self.toolbar_window.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.toolbar_window.setAttribute(Qt.WA_DeleteOnClose, False)
        # 设置工具栏窗口的层级更高
        self.toolbar_window.setAttribute(Qt.WA_AlwaysShowToolTips)
        
        # 启用鼠标追踪以便实现拖动功能
        self.toolbar_window.setMouseTracking(True)
        
        # 记录拖动状态和位置
        self.toolbar_drag_position = None
        self.toolbar_dragging = False
        
        # 设置工具栏样式，优化外观并支持按钮状态变色
        self.toolbar_window.setStyleSheet("""
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
        toolbar_main_layout = QVBoxLayout(self.toolbar_window)
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
            btn.clicked.connect(lambda checked, tool_name=tool_name: self.select_tool(tool_name))
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
            btn.clicked.connect(lambda checked, tool_name=tool_name: self.select_tool(tool_name))
            tools_row2.addWidget(btn)
            self.tool_button_group[tool] = btn
        # 添加空白填充
        tools_row2.addStretch()
        tools_layout.addLayout(tools_row2)
        
        # 默认选择直线工具
        self.tool_button_group["line"].setChecked(True)
        
        toolbar_main_layout.addWidget(tools_group)
        
        # 颜色和属性控制区域
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
        # 显示当前颜色
        self.update_color_button()
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
        
        toolbar_main_layout.addWidget(attrs_group)
        
        # 操作按钮区域
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
        self.toggle_passthrough_btn.clicked.connect(self.toggle_mouse_passthrough)
        action_row2.addWidget(self.toggle_passthrough_btn)
        
        self.toggle_visibility_btn = QPushButton("👁️ 隐藏")
        self.toggle_visibility_btn.setCheckable(True)
        self.toggle_visibility_btn.setMinimumSize(70, 32)
        self.toggle_visibility_btn.clicked.connect(self.toggle_canvas_visibility)
        action_row2.addWidget(self.toggle_visibility_btn)
        
        self.single_draw_mode_btn = QPushButton("1️⃣ 单次")
        self.single_draw_mode_btn.setCheckable(True)
        self.single_draw_mode_btn.setMinimumSize(70, 32)
        self.single_draw_mode_btn.clicked.connect(self.toggle_single_draw_mode)
        action_row2.addWidget(self.single_draw_mode_btn)
        
        actions_layout.addLayout(action_row2)
        
        # 第三行操作按钮 - 文件操作
        action_row3 = QHBoxLayout()
        action_row3.setSpacing(6)
        
        self.import_btn = QPushButton("📥 导入")
        self.import_btn.setMinimumSize(70, 32)
        self.import_btn.clicked.connect(self.import_canvas_content)
        action_row3.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.setMinimumSize(70, 32)
        self.export_btn.clicked.connect(self.export_canvas_content)
        action_row3.addWidget(self.export_btn)
        
        # 添加退出按钮
        self.exit_btn = QPushButton("❌ 退出")
        self.exit_btn.setMinimumSize(70, 32)
        self.exit_btn.clicked.connect(self.close_application)
        self.exit_btn.setProperty("class", "danger")
        action_row3.addWidget(self.exit_btn)
        
        actions_layout.addLayout(action_row3)
        
        # 第四行操作按钮 - 设置功能
        action_row4 = QHBoxLayout()
        action_row4.setSpacing(6)
        
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.setMinimumSize(70, 32)
        self.settings_btn.clicked.connect(self.open_hotkey_settings)
        action_row4.addWidget(self.settings_btn)
        
        self.save_config_btn = QPushButton("💾 保存")
        self.save_config_btn.setMinimumSize(70, 32)
        self.save_config_btn.clicked.connect(self.save_current_config)
        action_row4.addWidget(self.save_config_btn)
        
        # 添加空白填充
        action_row4.addStretch()
        
        actions_layout.addLayout(action_row4)
        
        toolbar_main_layout.addWidget(actions_group)
        
        # 设置工具栏窗口大小和位置 - 优化尺寸，增加高度以容纳新按钮
        self.toolbar_window.setFixedSize(320, 520)  # 展开状态的初始大小
        self.toolbar_window.move(50, 50)
        self.toolbar_window.show()
        
        # 确保工具栏始终在最前面
        self.ensure_toolbar_on_top()

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

    def close_application(self) -> None:
        """关闭应用程序"""
        self.close()

    def select_tool(self, tool: str) -> None:
        """选择工具并更新按钮状态"""
        print(f"select_tool 被调用，工具名称: {tool}")
        
        # 检查工具名称是否有效
        if not tool:
            print("错误: 工具名称为空")
            return
        
        # 取消所有工具按钮的选中状态
        for btn in self.tool_button_group.values():
            btn.setChecked(False)
        
        # 选中当前工具按钮
        if tool in self.tool_button_group:
            self.tool_button_group[tool].setChecked(True)
            
            # 设置画布工具
            print(f"当前画布工具: {self.canvas.current_tool}, 准备切换到: {tool}")
            self.canvas.set_current_tool(tool)
            print(f"画布工具已切换: {self.canvas.current_tool}")
            
            # 状态栏显示工具切换信息
            tool_names = {
                "line": "直线",
                "rectangle": "矩形",
                "circle": "圆形",
                "arrow": "箭头",
                "freehand": "自由绘制",
                "filled_freehand": "填充绘制",
                "point": "点",
                "laser_pointer": "激光笔"
            }
            tool_name = tool_names.get(tool, tool)
            self.statusBar().showMessage(f"已切换到{tool_name}工具", 2000)
            print(f"工具已切换到: {tool}")
            
            # 强制更新画布
            self.canvas.update()
        else:
            print(f"错误: 找不到工具 '{tool}' 对应的按钮")

    def change_thickness(self, value: int) -> None:
        """改变线条粗细"""
        self.canvas.set_current_thickness(value)
        self.thickness_label.setText(f"粗细: {value}")

    def pick_color(self) -> None:
        """选择颜色并应用到画布"""
        # 创建一个独立的颜色选择对话框
        dialog: QColorDialog = QColorDialog(self.canvas.current_color, self.toolbar_window)
        
        # 设置对话框选项，确保它总是在最前面
        dialog.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        dialog.setOption(QColorDialog.ShowAlphaChannel, True)
        
        # 临时隐藏主窗口来避免遮挡对话框
        main_visible: bool = self.isVisible()
        if main_visible and not self.passthrough_state:
            self.hide()
        
        # 显示对话框并等待用户选择
        if dialog.exec_() == QColorDialog.Accepted:
            color: QColor = dialog.currentColor()
            if color.isValid():
                self.canvas.set_current_color(color)
                self.update_color_button()
        
        # 恢复主窗口可见性
        if main_visible:
            self.show()
            self.activateWindow()
            self.raise_()
        
        # 确保工具栏在最前面
        self.ensure_toolbar_on_top()

    def change_drawing_opacity(self, value: int) -> None:
        opacity: float = value / 100.0
        self.canvas.set_current_opacity(opacity)
        self.drawing_opacity_label.setText(f"绘制: {value}%")

    def change_canvas_opacity(self, value: int) -> None:
        opacity: float = value / 100.0
        self.canvas.set_canvas_opacity(opacity)
        
        # 记住当前模式下的用户设置
        if self.passthrough_state:
            self.user_passthrough_opacity = opacity
        else:
            self.user_non_passthrough_opacity = opacity
        
        # 不要设置整个窗口的透明度，只设置画布背景的透明度
        # self.setWindowOpacity(opacity)  # 注释掉这一行
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

    def toggle_mouse_passthrough(self) -> None:
        current_flags = self.windowFlags()
        if self.passthrough_state:
            # Currently in pass-through mode, switch to non-pass-through
            new_flags = current_flags & ~Qt.WindowTransparentForInput
            self.setWindowFlags(new_flags)
            self.passthrough_state = False
            # 使用用户在非穿透模式下设置的透明度
            self.canvas.set_canvas_opacity(self.user_non_passthrough_opacity)
            # 不设置整个窗口透明度，只设置画布背景透明度
            # self.setWindowOpacity(self.user_non_passthrough_opacity)
            self.toggle_passthrough_btn.setChecked(False)
            self.toggle_passthrough_btn.setText("🖱️ 穿透")
            self.toggle_passthrough_btn.setProperty("class", "")
            self.statusBar().showMessage("鼠标非穿透模式", 2000)
        else:
            # Currently in non-pass-through mode, switch to pass-through
            new_flags = current_flags | Qt.WindowTransparentForInput
            self.setWindowFlags(new_flags)
            self.passthrough_state = True
            # 使用用户在穿透模式下设置的透明度
            self.canvas.set_canvas_opacity(self.user_passthrough_opacity)
            # 不设置整个窗口透明度，只设置画布背景透明度
            # self.setWindowOpacity(self.user_passthrough_opacity)
            self.toggle_passthrough_btn.setChecked(True)
            self.toggle_passthrough_btn.setText("🖱️ 非穿透")
            self.toggle_passthrough_btn.setProperty("class", "active")
            self.statusBar().showMessage("鼠标穿透模式", 2000)
        
        # 更新GUI滑动条以同步画布透明度
        self.update_canvas_opacity_ui()
        
        # 刷新按钮样式
        self.toggle_passthrough_btn.style().polish(self.toggle_passthrough_btn)
        
        # 必须重新显示窗口以应用新的标志
        self.show()
        self.activateWindow()
        self.raise_()
        
        # 确保工具栏在主窗口之上
        self.ensure_toolbar_on_top()

    def toggle_canvas_visibility(self) -> None:
        if self.canvas.isVisible():
            self.canvas.hide()
            self.toggle_visibility_btn.setText("👁️ 显示")
            self.toggle_visibility_btn.setChecked(True)
            self.toggle_visibility_btn.setProperty("class", "active")
            self.statusBar().showMessage("画布已隐藏", 2000)
        else:
            self.canvas.show()
            self.toggle_visibility_btn.setText("👁️ 隐藏")
            self.toggle_visibility_btn.setChecked(False)
            self.toggle_visibility_btn.setProperty("class", "")
            self.statusBar().showMessage("画布已显示", 2000)
        
        # 刷新按钮样式
        self.toggle_visibility_btn.style().polish(self.toggle_visibility_btn)

    def toggle_single_draw_mode(self, checked: bool) -> None:
        self.canvas.single_draw_mode = checked
        if checked:
            self.single_draw_mode_btn.setProperty("class", "active")
            self.statusBar().showMessage("已开启单次绘制模式", 2000)
        else:
            self.single_draw_mode_btn.setProperty("class", "")
            self.statusBar().showMessage("已关闭单次绘制模式", 2000)
        
        # 刷新按钮样式
        self.single_draw_mode_btn.style().polish(self.single_draw_mode_btn)

    def import_canvas_content(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "导入标注", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, "r") as f:
                    json_data: str = f.read()
                self.canvas.from_json_data(json_data)
                self.statusBar().showMessage("标注导入成功", 2000)
            except Exception as e:
                self.statusBar().showMessage(f"导入失败: {e}", 2000)

    def export_canvas_content(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(self, "导出标注", "", "JSON Files (*.json)")
        if file_name:
            try:
                json_data: str = self.canvas.to_json_data()
                with open(file_name, "w") as f:
                    f.write(json_data)
                self.statusBar().showMessage("标注导出成功", 2000)
            except Exception as e:
                self.statusBar().showMessage(f"导出失败: {e}", 2000)

    def setup_window_properties(self) -> None:
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        
        # 设置窗口覆盖整个屏幕，去除所有边距
        self.setGeometry(screen)
        self.setFixedSize(screen.size())  # 固定窗口大小为屏幕大小
        
        # 确保画布也覆盖整个窗口
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 去除布局边距
        self.main_layout.setSpacing(0)  # 去除组件间距
        
        # 设置窗口属性使其成为透明覆盖层
        # 移除 Qt.Tool 标志，以确保工具栏可以显示在主窗口之上
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 默认透明度设置
        self.passthrough_opacity = self.config["passthrough_opacity"]
        self.non_passthrough_opacity = self.config["non_passthrough_opacity"]
        self.passthrough_state = False  # 初始状态为非穿透
        
        # 记住用户在每个模式下的透明度设置
        # 优先使用配置文件中保存的用户设置，如果没有则使用默认值
        self.user_passthrough_opacity = self.config.get("passthrough_opacity", 0.1)
        self.user_non_passthrough_opacity = self.config.get("non_passthrough_opacity", 0.8)

        # 设置初始透明度 - 使用配置文件中的透明度，而不是重新设置
        if self.passthrough_state:
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
            # 如果是穿透模式，使用穿透透明度
            if self.canvas.canvas_opacity != self.user_passthrough_opacity:
                self.canvas.set_canvas_opacity(self.user_passthrough_opacity)
            self.toggle_passthrough_btn.setChecked(True)
            self.toggle_passthrough_btn.setText("🖱️ 非穿透")
        else:
            # 如果是非穿透模式，保持配置文件中的透明度设置
            # 只有当前透明度与配置不符时才需要调整
            if self.canvas.canvas_opacity == 0.0:
                # 如果配置文件中是0透明度，使用非穿透默认透明度
                self.canvas.set_canvas_opacity(self.user_non_passthrough_opacity)
            else:
                # 使用当前画布透明度作为非穿透模式的用户设置
                self.user_non_passthrough_opacity = self.canvas.canvas_opacity
            self.toggle_passthrough_btn.setChecked(False)
            self.toggle_passthrough_btn.setText("🖱️ 穿透")
        
        # 更新GUI滑动条以同步画布透明度
        self.update_canvas_opacity_ui()
            
        # 添加状态栏
        self.statusBar()

    def setup_menubar(self) -> None:
        """设置菜单栏 - 在无边框模式下隐藏菜单栏"""
        # 隐藏菜单栏以确保真正的无边框体验
        self.menuBar().setVisible(False)
        self.menuBar().setMaximumHeight(0)

    def open_hotkey_settings(self) -> None:
        """打开热键设置对话框"""
        dialog: HotkeySettingsDialog = HotkeySettingsDialog(self, self.config)
        dialog.exec_()

    def save_current_config(self) -> None:
        """保存当前配置"""
        self.config["current_color"] = self.canvas.current_color
        self.config["current_thickness"] = self.canvas.current_thickness
        self.config["current_opacity"] = self.canvas.current_opacity
        self.config["canvas_color"] = self.canvas.canvas_color
        self.config["canvas_opacity"] = self.canvas.canvas_opacity
        # 同时保存穿透模式的透明度设置 - 保存用户实际设置的值
        self.config["passthrough_opacity"] = self.user_passthrough_opacity
        self.config["non_passthrough_opacity"] = self.user_non_passthrough_opacity
        save_config(self.config)
        self.statusBar().showMessage("配置已保存", 2000)
        
    def toggle_toolbar_collapse(self) -> None:
        """切换工具栏折叠/展开状态"""
        # 定义工具栏的折叠高度和展开高度
        collapsed_height: int = 36  # 标题栏的高度
        expanded_height: int = 520  # 完全展开的高度
        
        # 获取当前高度
        current_height: int = self.toolbar_window.height()
        
        if current_height > collapsed_height:
            # 当前是展开状态，需要折叠
            self.toolbar_window.setFixedSize(320, collapsed_height)
            self.toggle_collapse_btn.setText("🔽")
            # 隐藏除标题容器外的所有组件
            for i in range(1, self.toolbar_window.layout().count()):
                widget = self.toolbar_window.layout().itemAt(i).widget()
                if widget:
                    widget.hide()
            self.statusBar().showMessage("工具栏已折叠", 1000)
        else:
            # 当前是折叠状态，需要展开
            self.toolbar_window.setFixedSize(320, expanded_height)
            self.toggle_collapse_btn.setText("🔼")
            # 显示所有组件
            for i in range(1, self.toolbar_window.layout().count()):
                widget = self.toolbar_window.layout().itemAt(i).widget()
                if widget:
                    widget.show()
            self.statusBar().showMessage("工具栏已展开", 1000)
              # 确保工具栏始终在最前面
        self.ensure_toolbar_on_top()

    def setup_system_tray(self) -> None:
        """设置系统托盘"""
        # 检查系统是否支持系统托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("系统托盘不可用")
            return
        
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置托盘图标（使用现有的ico文件）
        try:
            icon: QIcon = QIcon("1.ico")
            if icon.isNull():
                # 如果图标文件不存在，创建一个简单的图标
                icon = self.style().standardIcon(self.style().SP_ComputerIcon)
            self.tray_icon.setIcon(icon)
        except:
            # 如果加载图标失败，使用默认图标
            icon = self.style().standardIcon(self.style().SP_ComputerIcon)
            self.tray_icon.setIcon(icon)
        
        # 设置托盘提示
        self.tray_icon.setToolTip("屏幕标注工具 - 点击恢复窗口")
        
        # 创建托盘菜单
        tray_menu: QMenu = QMenu()
        
        # 显示主窗口动作
        show_action: QAction = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)
        
        # 分隔符
        tray_menu.addSeparator()
        
        # 退出动作
        quit_action: QAction = QAction("退出程序", self)
        quit_action.triggered.connect(self.close_application)
        tray_menu.addAction(quit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)
        
        # 托盘图标单击事件
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # 默认不显示托盘图标
        self.tray_icon_visible = False

    def show_from_tray(self) -> None:
        """从托盘恢复窗口显示"""
        # 显示主窗口和工具栏
        self.show()
        self.activateWindow()
        self.raise_()
        
        # 显示工具栏
        if hasattr(self, 'toolbar_window'):
            self.toolbar_window.show()
            self.toolbar_completely_hidden = False
            self.ensure_toolbar_on_top()
        
        # 隐藏托盘图标
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
            self.tray_icon_visible = False
        
        self.statusBar().showMessage("窗口已从托盘恢复", 2000)
        print("窗口已从托盘恢复")

    def tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """托盘图标被点击"""
        if reason == QSystemTrayIcon.Trigger:  # 左键单击
            self.show_from_tray()
        elif reason == QSystemTrayIcon.DoubleClick:  # 双击
            self.show_from_tray()

    def toggle_toolbar_complete_hide(self) -> None:
        """完全隐藏/显示工具栏和主窗口"""
        if self.toolbar_completely_hidden:
            # 当前完全隐藏，需要显示 - 从托盘恢复
            self.show_from_tray()
        else:
            # 当前显示，需要完全隐藏到托盘
            # 隐藏主窗口
            self.hide()
            
            # 隐藏工具栏
            if hasattr(self, 'toolbar_window'):
                self.toolbar_window.hide()
            
            self.toolbar_completely_hidden = True
            
            # 显示托盘图标
            if hasattr(self, 'tray_icon') and QSystemTrayIcon.isSystemTrayAvailable():
                self.tray_icon.show()
                self.tray_icon_visible = True
                # 显示托盘通知
                self.tray_icon.showMessage(
                    "屏幕标注工具",
                    "程序已最小化到系统托盘\n点击托盘图标恢复窗口",
                    QSystemTrayIcon.Information,
                    3000
                )
            
            print("程序已隐藏到系统托盘")

    def ensure_toolbar_on_top(self) -> None:
        """确保工具栏始终显示在最前面"""
        if hasattr(self, 'toolbar_window') and self.toolbar_window and not self.toolbar_completely_hidden:
            self.toolbar_window.raise_()
            self.toolbar_window.activateWindow()
            self.toolbar_window.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        """关闭事件处理"""
        # 在退出前自动保存当前配置
        self.save_current_config()
        
        if hasattr(self, 'toolbar_timer'):
            self.toolbar_timer.stop()
        if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
            self.hotkey_manager.stop_listening()
        if hasattr(self, 'toolbar_window'):
            self.toolbar_window.close()
        # 清理托盘图标
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        event.accept()

    def setup_hotkeys(self) -> None:
        """设置热键"""
        # 清空现有热键
        if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
            self.hotkey_manager.hotkeys.clear()
        else:
            self.hotkey_manager = HotkeyManager(self)
        
        hotkeys = self.config["hotkeys"]
        print(f"设置热键配置: {hotkeys}")
          # 注册所有热键
        if hotkeys.get("toggle_visibility"):
            self.hotkey_manager.register_hotkey(hotkeys["toggle_visibility"], self.toggle_visibility)
        if hotkeys.get("toggle_passthrough"):
            self.hotkey_manager.register_hotkey(hotkeys["toggle_passthrough"], self.toggle_mouse_passthrough)
        if hotkeys.get("toggle_canvas_visibility"):
            self.hotkey_manager.register_hotkey(hotkeys["toggle_canvas_visibility"], self.toggle_canvas_visibility)
        if hotkeys.get("toggle_toolbar_collapse"):
            self.hotkey_manager.register_hotkey(hotkeys["toggle_toolbar_collapse"], self.toggle_toolbar_collapse)
        # 添加工具栏完全隐藏热键（固定为 F12，不保存到配置文件）
        self.hotkey_manager.register_hotkey("f12", self.toggle_toolbar_complete_hide)
        # 添加可自定义的完全隐藏热键
        if hotkeys.get("toggle_complete_hide"):
            self.hotkey_manager.register_hotkey(hotkeys["toggle_complete_hide"], self.toggle_toolbar_complete_hide)
        if hotkeys.get("clear_canvas"):
            self.hotkey_manager.register_hotkey(hotkeys["clear_canvas"], self.canvas.clear_canvas)
        if hotkeys.get("undo"):
            self.hotkey_manager.register_hotkey(hotkeys["undo"], self.canvas.undo)
        if hotkeys.get("redo"):
            self.hotkey_manager.register_hotkey(hotkeys["redo"], self.canvas.redo)
        if hotkeys.get("single_draw_mode"):
            def toggle_single_draw():
                self.single_draw_mode_btn.click()
            self.hotkey_manager.register_hotkey(hotkeys["single_draw_mode"], toggle_single_draw)

        # Tool hotkeys
        if hotkeys.get("tool_line"):
            self.add_tool_hotkey(hotkeys["tool_line"], "line")
        if hotkeys.get("tool_rectangle"):
            self.add_tool_hotkey(hotkeys["tool_rectangle"], "rectangle")
        if hotkeys.get("tool_circle"):
            self.add_tool_hotkey(hotkeys["tool_circle"], "circle")
        if hotkeys.get("tool_arrow"):
            self.add_tool_hotkey(hotkeys["tool_arrow"], "arrow")
        if hotkeys.get("tool_freehand"):
            self.add_tool_hotkey(hotkeys["tool_freehand"], "freehand")
        if hotkeys.get("tool_filled_freehand"):
            self.add_tool_hotkey(hotkeys["tool_filled_freehand"], "filled_freehand")
        if hotkeys.get("tool_point"):
            self.add_tool_hotkey(hotkeys["tool_point"], "point")
        if hotkeys.get("tool_laser_pointer"):
            self.add_tool_hotkey(hotkeys["tool_laser_pointer"], "laser_pointer")
            
        # 添加测试热键 F9
        self.hotkey_manager.register_hotkey("f9", self.test_hotkey_function)
        
        print(f"热键设置完成，共注册 {len(self.hotkey_manager.hotkeys)} 个热键")

    def test_hotkey_function(self) -> None:
        """测试热键功能"""
        print("测试热键被触发!")
        self.statusBar().showMessage("热键测试成功！", 3000)
        
    def add_tool_hotkey(self, hotkey_str: str, tool_name: str) -> None:
        """添加工具切换热键"""
        # 为了避免闭包问题，创建一个副本
        tool_name_copy: str = str(tool_name)
        
        def tool_callback() -> None:
            # 确保工具名称正确传递
            print(f"触发工具热键：{hotkey_str} -> {tool_name_copy}")
            
            # 直接在回调中调用select_tool，而不是使用QTimer
            try:
                print(f"工具热键回调正在执行，切换到工具: {tool_name_copy}")
                self.select_tool(tool_name_copy)
                print(f"工具热键回调执行完毕")
            except Exception as e:
                print(f"工具热键回调执行出错: {e}")
                import traceback
                traceback.print_exc()
        
        self.hotkey_manager.register_hotkey(hotkey_str, tool_callback)

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        """事件过滤器，用于处理工具栏的拖动"""
        # 处理工具栏拖动
        if hasattr(self, 'toolbar_window') and hasattr(self, 'title_container') and obj == self.title_container:
            if event.type() == event.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    # 记录鼠标按下位置和拖动状态
                    self.toolbar_drag_position = event.globalPos() - self.toolbar_window.pos()
                    self.toolbar_dragging = True
                    return True
            elif event.type() == event.MouseMove:
                if hasattr(self, 'toolbar_dragging') and self.toolbar_dragging and event.buttons() & Qt.LeftButton:
                    # 计算新位置并移动工具栏
                    new_pos: QPoint = event.globalPos() - self.toolbar_drag_position
                    self.toolbar_window.move(new_pos)
                    return True
            elif event.type() == event.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    # 释放拖动状态
                    self.toolbar_dragging = False
                    return True
        
        # 让其他事件继续正常处理
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    tool: AnnotationTool = AnnotationTool()
    tool.show()
    sys.exit(app.exec_())


