import sys
import json
import os
from typing import Dict, Any, Optional, Callable
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QColorDialog, QSlider, 
                             QLabel, QFileDialog, QStatusBar, QMenuBar, QAction, 
                             QSystemTrayIcon, QMenu, QStyle)
from PyQt5.QtGui import QColor, QIcon, QCloseEvent, QPixmap, QPainter
from PyQt5.QtCore import Qt, QTimer, QPoint, QEvent
from gui import DrawingCanvas
from hotkey_manager import HotkeyManager
from config import load_config, save_config
from hotkey_settings import HotkeySettingsDialog
from toolbar import AnnotationToolbar

# 显式导入所有必需的模块确保PyInstaller能正确打包
try:
    import text_style_dialog
    print("Successfully imported text_style_dialog")
except ImportError as e:
    print(f"Warning: text_style_dialog module not found: {e}")

try:
    from PyQt5.QtWidgets import QColorDialog, QInputDialog, QFontDialog
    print("Successfully imported PyQt5 dialog modules")
except ImportError as e:
    print(f"Warning: PyQt5 dialog modules not found: {e}")
    
try:
    from PyQt5.QtCore import QCoreApplication
    print("Successfully imported QCoreApplication")
except ImportError as e:
    print(f"Warning: QCoreApplication not found: {e}")

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

class AnnotationTool(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("屏幕标注工具")
        self.setGeometry(100, 100, 1000, 800)

        #类型注解
        self._status_bar: QStatusBar = self.statusBar()
        
        # 设置状态栏
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
        
        # 初始化文本相关属性
        self.canvas.set_text_font_family(self.config["text_font_family"])
        self.canvas.set_text_font_size(self.config["text_font_size"])
        self.canvas.set_text_font_bold(self.config["text_font_bold"])
        self.canvas.set_text_font_italic(self.config["text_font_italic"])
        self.canvas.set_text_color(self.config["text_color"])
        self.canvas.set_text_background_color(self.config["text_background_color"])
        self.canvas.set_text_border_color(self.config["text_border_color"])
        self.canvas.set_text_border_width(self.config["text_border_width"])
        self.canvas.set_text_padding(self.config["text_padding"])
        
        self.main_layout.addWidget(self.canvas)
          # 初始化热键管理器
        self.hotkey_manager: HotkeyManager = HotkeyManager(self)

        # 工具栏完全隐藏状态（不保存到配置文件）
        self.toolbar_completely_hidden: bool = False

        # 工具栏相关属性
        self.toolbar: AnnotationToolbar
        self.toolbar_timer: QTimer
        
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
        self.toolbar.update_color_button()
        
        # 初始化画布透明度GUI显示
        self.toolbar.update_canvas_opacity_ui()
        
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
        """设置工具栏"""
        # 创建工具栏实例
        self.toolbar = AnnotationToolbar(self, self.canvas)


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
        for btn in self.toolbar.tool_button_group.values():
            btn.setChecked(False)
        
        # 选中当前工具按钮
        if tool in self.toolbar.tool_button_group:
            self.toolbar.tool_button_group[tool].setChecked(True)
            
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
                "laser_pointer": "激光笔",
                "text": "文本"
            }
            tool_name = tool_names.get(tool, tool)
            self._status_bar.showMessage(f"已切换到{tool_name}工具", 2000)
            print(f"工具已切换到: {tool}")
            
            # 强制更新画布
            self.canvas.update()
        else:
            print(f"错误: 找不到工具 '{tool}' 对应的按钮")



    def change_canvas_opacity(self, value: int) -> None:
        """通过工具栏处理画布透明度变化"""
        self.toolbar.change_canvas_opacity(value)

    def update_canvas_opacity_ui(self) -> None:
        """更新GUI上的画布透明度显示，确保与实际画布透明度一致"""
        self.toolbar.update_canvas_opacity_ui()

    def toggle_mouse_passthrough(self) -> None:
        current_flags = self.windowFlags()
        if self.passthrough_state:
            # Currently in pass-through mode, switch to non-pass-through
            new_flags = current_flags & ~Qt.WindowTransparentForInput  # type: ignore
            self.setWindowFlags(new_flags)
            self.passthrough_state = False
            # 使用用户在非穿透模式下设置的透明度
            self.canvas.set_canvas_opacity(self.user_non_passthrough_opacity)
            # 不设置整个窗口透明度，只设置画布背景透明度
            # self.setWindowOpacity(self.user_non_passthrough_opacity)
            self.toolbar.toggle_passthrough_btn.setChecked(False)
            self.toolbar.toggle_passthrough_btn.setText("🖱️ 穿透")
            self.toolbar.toggle_passthrough_btn.setProperty("class", "action")
            self._status_bar.showMessage("鼠标非穿透模式", 2000)
        else:
            # Currently in non-pass-through mode, switch to pass-through
            new_flags = current_flags | Qt.WindowTransparentForInput  # type: ignore
            self.setWindowFlags(new_flags)
            self.passthrough_state = True
            # 使用用户在穿透模式下设置的透明度
            self.canvas.set_canvas_opacity(self.user_passthrough_opacity)
            # 不设置整个窗口透明度，只设置画布背景透明度
            # self.setWindowOpacity(self.user_passthrough_opacity)
            self.toolbar.toggle_passthrough_btn.setChecked(True)
            self.toolbar.toggle_passthrough_btn.setText("🖱️ 非穿透")
            self.toolbar.toggle_passthrough_btn.setProperty("class", "action active")
            self._status_bar.showMessage("鼠标穿透模式", 2000)
        
        # 更新GUI滑动条以同步画布透明度
        self.update_canvas_opacity_ui()
        
        # 刷新按钮样式
        if self.toolbar.toggle_passthrough_btn.style():  # type: ignore
            self.toolbar.toggle_passthrough_btn.style().polish(self.toolbar.toggle_passthrough_btn)  # type: ignore
        
        # 必须重新显示窗口以应用新的标志
        self.show()
        self.activateWindow()
        self.raise_()
        
        # 确保工具栏在主窗口之上
        self.ensure_toolbar_on_top()

    def toggle_canvas_visibility(self) -> None:
        if self.canvas.isVisible():
            self.canvas.hide()
            self.toolbar.toggle_visibility_btn.setText("👁️ 显示")
            self.toolbar.toggle_visibility_btn.setChecked(True)
            self.toolbar.toggle_visibility_btn.setProperty("class", "action active")
            self._status_bar.showMessage("画布已隐藏", 2000)
        else:
            self.canvas.show()
            self.toolbar.toggle_visibility_btn.setText("👁️ 隐藏")
            self.toolbar.toggle_visibility_btn.setChecked(False)
            self.toolbar.toggle_visibility_btn.setProperty("class", "action")
            self._status_bar.showMessage("画布已显示", 2000)
        
        # 刷新按钮样式
        if self.toolbar.toggle_visibility_btn.style():  # type: ignore
            self.toolbar.toggle_visibility_btn.style().polish(self.toolbar.toggle_visibility_btn)  # type: ignore

    def toggle_single_draw_mode(self, checked: bool) -> None:
        self.canvas.single_draw_mode = checked
        if checked:
            self.toolbar.single_draw_mode_btn.setProperty("class", "action active")
            self._status_bar.showMessage("已开启单次绘制模式", 2000)
        else:
            self.toolbar.single_draw_mode_btn.setProperty("class", "action")
            self._status_bar.showMessage("已关闭单次绘制模式", 2000)
        
        # 刷新按钮样式
        if self.toolbar.single_draw_mode_btn.style():  # type: ignore
            self.toolbar.single_draw_mode_btn.style().polish(self.toolbar.single_draw_mode_btn)  # type: ignore

    def import_canvas_content(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "导入标注", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, "r") as f:
                    json_data: str = f.read()
                self.canvas.from_json_data(json_data)
                self._status_bar.showMessage("标注导入成功", 2000)
            except Exception as e:
                self._status_bar.showMessage(f"导入失败: {e}", 2000)

    def export_canvas_content(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(self, "导出标注", "", "JSON Files (*.json)")
        if file_name:
            try:
                json_data: str = self.canvas.to_json_data()
                with open(file_name, "w") as f:
                    f.write(json_data)
                self._status_bar.showMessage("标注导出成功", 2000)
            except Exception as e:
                self._status_bar.showMessage(f"导出失败: {e}", 2000)

    def setup_window_properties(self) -> None:
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        if screen:  # type: ignore
            screen_geometry = screen.geometry()  # type: ignore
        else:
            # 如果无法获取主屏幕，使用默认值
            from PyQt5.QtCore import QRect
            screen_geometry = QRect(0, 0, 1920, 1080)
        
        # 设置窗口覆盖整个屏幕，去除所有边距
        self.setGeometry(screen_geometry)
        self.setFixedSize(screen_geometry.size())  # 固定窗口大小为屏幕大小
        
        # 确保画布也覆盖整个窗口
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 去除布局边距
        self.main_layout.setSpacing(0)  # 去除组件间距
        
        # 设置窗口属性使其成为透明覆盖层
        # 移除 Qt.Tool 标志，以确保工具栏可以显示在主窗口之上
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # type: ignore
        self.setAttribute(Qt.WA_TranslucentBackground)  # type: ignore

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
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)  # type: ignore
            # 如果是穿透模式，使用穿透透明度
            if self.canvas.canvas_opacity != self.user_passthrough_opacity:
                self.canvas.set_canvas_opacity(self.user_passthrough_opacity)
            self.toolbar.toggle_passthrough_btn.setChecked(True)
            self.toolbar.toggle_passthrough_btn.setText("🖱️ 非穿透")
        else:
            # 如果是非穿透模式，保持配置文件中的透明度设置
            # 只有当前透明度与配置不符时才需要调整
            if self.canvas.canvas_opacity == 0.0:
                # 如果配置文件中是0透明度，使用非穿透默认透明度
                self.canvas.set_canvas_opacity(self.user_non_passthrough_opacity)
            else:
                # 使用当前画布透明度作为非穿透模式的用户设置
                self.user_non_passthrough_opacity = self.canvas.canvas_opacity
            self.toolbar.toggle_passthrough_btn.setChecked(False)
            self.toolbar.toggle_passthrough_btn.setText("🖱️ 穿透")
        
        # 更新GUI滑动条以同步画布透明度
        self.update_canvas_opacity_ui()
            
        # 添加状态栏
        self._status_bar

    def setup_menubar(self) -> None:
        """设置菜单栏 - 在无边框模式下隐藏菜单栏"""
        # 隐藏菜单栏以确保真正的无边框体验
        menu_bar = self.menuBar()
        if menu_bar:  # type: ignore
            menu_bar.setVisible(False)  # type: ignore
            menu_bar.setMaximumHeight(0)  # type: ignore

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
        # 保存字体大小设置
        if hasattr(self, 'toolbar') and self.toolbar:
            self.config["toolbar_font_size"] = self.toolbar.font_size
        
        # 保存文本相关配置
        self.config["text_font_family"] = self.canvas.text_font_family
        self.config["text_font_size"] = self.canvas.text_font_size
        self.config["text_font_bold"] = self.canvas.text_font_bold
        self.config["text_font_italic"] = self.canvas.text_font_italic
        self.config["text_color"] = self.canvas.text_color
        self.config["text_background_color"] = self.canvas.text_background_color
        self.config["text_border_color"] = self.canvas.text_border_color
        self.config["text_border_width"] = self.canvas.text_border_width
        self.config["text_padding"] = self.canvas.text_padding
        
        save_config(self.config)
        self._status_bar.showMessage("配置已保存", 2000)
        
    def toggle_toolbar_collapse(self) -> None:
        """切换工具栏折叠/展开状态"""
        self.toolbar.toggle_toolbar_collapse()

    def setup_system_tray(self) -> None:
        """设置系统托盘"""
        # 检查系统是否支持系统托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("系统托盘不可用")
            return
        
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 断言确保 tray_icon 不为 None
        assert self.tray_icon is not None
        
        # 设置托盘图标（使用现有的ico文件）
        icon = None
        try:
            # 尝试使用绝对路径加载图标文件
            icon_path = get_resource_path("1.ico")
            print(f"尝试加载图标文件: {icon_path}")
            
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                print(f"图标文件存在，加载结果: isNull={icon.isNull()}")
                if not icon.isNull():
                    print(f"图标可用尺寸: {icon.availableSizes()}")
            else:
                print(f"图标文件不存在: {icon_path}")
                # 尝试查找当前目录和几个可能的位置
                possible_paths = [
                    "1.ico",  # 相对路径
                    os.path.join(os.getcwd(), "1.ico"),  # 当前工作目录
                    os.path.join(os.path.dirname(sys.argv[0]), "1.ico"),  # exe所在目录
                ]
                
                for path in possible_paths:
                    print(f"尝试路径: {path}")
                    if os.path.exists(path):
                        icon = QIcon(path)
                        if not icon.isNull():
                            print(f"在路径 {path} 找到有效图标")
                            break
                        
            # 检查图标是否有效
            if icon is None or icon.isNull():
                print("图标文件无效或不存在，创建默认图标")
                icon = create_default_icon()
                
        except Exception as e:
            print(f"加载图标文件失败: {e}")
            # 如果创建默认图标也失败，使用系统标准图标
            try:
                icon = create_default_icon()
                print("使用自定义默认图标")
            except Exception as e2:
                print(f"创建默认图标失败: {e2}，使用系统图标")
                style = self.style()
                if style:  # type: ignore
                    icon = style.standardIcon(QStyle.SP_ComputerIcon)  # type: ignore
                else:
                    icon = create_default_icon()
        
        # 最后检查，确保有可用的图标
        if icon is None or icon.isNull():
            print("使用系统默认图标作为最后备选")
            style = self.style()
            if style:  # type: ignore
                icon = style.standardIcon(QStyle.SP_ComputerIcon)  # type: ignore
            else:
                icon = create_default_icon()
            
        self.tray_icon.setIcon(icon)
        print(f"托盘图标设置完成，图标有效性: {not icon.isNull()}")
        
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
        if hasattr(self, 'toolbar'):
            self.toolbar.show()
            self.toolbar_completely_hidden = False
            self.ensure_toolbar_on_top()
        
        # 隐藏托盘图标
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            self.tray_icon.hide()
            self.tray_icon_visible = False
        
        self._status_bar.showMessage("窗口已从托盘恢复", 2000)
        print("窗口已从托盘恢复")

    def tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """托盘图标被点击"""
        if reason == QSystemTrayIcon.Trigger:  # type: ignore  # 左键单击
            self.show_from_tray()
        elif reason == QSystemTrayIcon.DoubleClick:  # type: ignore  # 双击
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
            if hasattr(self, 'toolbar'):
                self.toolbar.hide()
            
            self.toolbar_completely_hidden = True
            
            # 显示托盘图标
            if hasattr(self, 'tray_icon') and self.tray_icon is not None and QSystemTrayIcon.isSystemTrayAvailable():
                self.tray_icon.show()
                self.tray_icon_visible = True
                # 显示托盘通知
                self.tray_icon.showMessage(
                    "屏幕标注工具",
                    "程序已最小化到系统托盘\n点击托盘图标恢复窗口",
                    QSystemTrayIcon.Information,  # type: ignore
                    3000
                )
            
            print("程序已隐藏到系统托盘")

    def ensure_toolbar_on_top(self) -> None:
        """确保工具栏始终显示在最前面"""
        if hasattr(self, 'toolbar') and self.toolbar and not self.toolbar_completely_hidden:
            self.toolbar.raise_()
            self.toolbar.activateWindow()
            self.toolbar.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        """关闭事件处理"""
        # 在退出前自动保存当前配置
        self.save_current_config()
        
        if hasattr(self, 'toolbar_timer'):
            self.toolbar_timer.stop()
        if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
            self.hotkey_manager.stop_listening()
        if hasattr(self, 'toolbar'):
            self.toolbar.close()
        # 清理托盘图标
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
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
                self.toolbar.single_draw_mode_btn.click()
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
        if hotkeys.get("tool_text"):
            self.add_tool_hotkey(hotkeys["tool_text"], "text")
            
        # 添加测试热键 F9
        self.hotkey_manager.register_hotkey("f9", self.test_hotkey_function)
        
        print(f"热键设置完成，共注册 {len(self.hotkey_manager.hotkeys)} 个热键")

    def test_hotkey_function(self) -> None:
        """测试热键功能"""
        print("测试热键被触发!")
        self._status_bar.showMessage("热键测试成功！", 3000)
        
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
        """事件过滤器"""
        # 让事件继续正常处理
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    tool: AnnotationTool = AnnotationTool()
    tool.show()
    sys.exit(app.exec_())


