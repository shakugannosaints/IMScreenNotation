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
from hotkey.hotkey_manager import HotkeyManager
from config import load_config, save_config
from hotkey.hotkey_settings import HotkeySettingsDialog
from toolbar.toolbar import AnnotationToolbar

# 导入新的模块化组件
from manager.window_manager import WindowManager
from manager.transparency_manager import TransparencyManager
from manager.tool_manager import ToolManager
from manager.tray_manager import TrayManager
from file_operations import FileOperations
from hotkey.hotkey_handler import HotkeyHandler
from manager.config_manager import ConfigManager
from constants import TOOLBAR_CHECK_INTERVAL, STATUS_MESSAGE_TIMEOUT

# 显式导入所有必需的模块确保PyInstaller能正确打包
try:
    # 导入打包修复模块
    import packaging_fix
    packaging_fix.init_packaging_fix()
    print("Packaging fix initialized")
except ImportError as e:
    print(f"Warning: packaging_fix module not found: {e}")

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
        
        # 初始化管理器
        self.window_manager = WindowManager(self)
        self.transparency_manager = TransparencyManager(self)
        self.tool_manager = ToolManager(self)
        self.tray_manager = TrayManager(self)
        self.file_operations = FileOperations(self)
        self.hotkey_handler = HotkeyHandler(self)
        self.config_manager = ConfigManager(self)
        
        # 应用配置到画布
        self.config_manager._apply_canvas_config(self.config)
        self.config_manager._apply_text_config(self.config)
        
        # 如果是首次运行（没有配置文件），立即保存一次配置以创建文件
        import os
        if not os.path.exists("config.json"):
            print("首次运行，创建默认配置文件...")
            self.config_manager.save_current_config()
        
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

        self.window_manager.setup_menubar()
        self.setup_toolbar()
        self.window_manager.setup_window_properties()
        self.transparency_manager.initialize_transparency_settings()
        self.hotkey_handler.setup_hotkeys()  # 设置热键
        self.hotkey_manager.start_listening()  # 启动热键监听
        
        # 初始化颜色按钮显示
        self.toolbar.update_color_button()
        
        # 初始化画布透明度GUI显示
        self.toolbar.update_canvas_opacity_ui()
        
        # 确保工具栏在主窗口显示后仍然在最前面
        self.window_manager.ensure_toolbar_on_top()
        
        # 设置定时器定期确保工具栏在最前面
        self.toolbar_timer = QTimer()
        self.toolbar_timer.timeout.connect(self.window_manager.ensure_toolbar_on_top)
        self.toolbar_timer.start(TOOLBAR_CHECK_INTERVAL)  # 每秒检查一次
        
        # 初始化系统托盘
        self.tray_manager.setup_system_tray()
    def setup_toolbar(self) -> None:
        """设置工具栏"""
        # 创建工具栏实例
        self.toolbar = AnnotationToolbar(self, self.canvas)

    def close_application(self) -> None:
        """关闭应用程序"""
        self.close()

    # 委托方法 - 工具管理
    def select_tool(self, tool: str) -> None:
        """选择工具并更新按钮状态"""
        self.tool_manager.select_tool(tool)

    # 委托方法 - 透明度管理  
    def change_canvas_opacity(self, value: int) -> None:
        """通过工具栏处理画布透明度变化"""
        self.transparency_manager.change_canvas_opacity(value)

    def update_canvas_opacity_ui(self) -> None:
        """更新GUI上的画布透明度显示，确保与实际画布透明度一致"""
        self.transparency_manager.update_canvas_opacity_ui()

    def toggle_mouse_passthrough(self) -> None:
        """切换鼠标穿透模式"""
        self.transparency_manager.toggle_mouse_passthrough()

    # 委托方法 - 窗口管理
    def toggle_visibility(self) -> None:
        """切换主窗口显示/隐藏"""
        self.window_manager.toggle_visibility()

    def toggle_canvas_visibility(self) -> None:
        """切换画布显示/隐藏"""
        self.window_manager.toggle_canvas_visibility()

    def ensure_toolbar_on_top(self) -> None:
        """确保工具栏始终显示在最前面"""
        self.window_manager.ensure_toolbar_on_top()

    # 委托方法 - 文件操作
    def import_canvas_content(self) -> None:
        """导入标注内容"""
        self.file_operations.import_canvas_content()

    def export_canvas_content(self) -> None:
        """导出标注内容"""
        self.file_operations.export_canvas_content()

    # 委托方法 - 热键设置
    def open_hotkey_settings(self) -> None:
        """打开热键设置对话框"""
        self.hotkey_handler.open_hotkey_settings()

    # 委托方法 - 托盘管理
    def show_from_tray(self) -> None:
        """从托盘恢复窗口显示"""
        self.tray_manager.show_from_tray()

    def toggle_toolbar_complete_hide(self) -> None:
        """完全隐藏/显示工具栏和主窗口"""
        if self.toolbar_completely_hidden:
            # 当前完全隐藏，需要显示 - 从托盘恢复
            self.tray_manager.show_from_tray()
        else:
            # 当前显示，需要完全隐藏到托盘
            self.tray_manager.hide_to_tray()

    def toggle_single_draw_mode(self, checked: bool) -> None:
        """切换单次绘制模式"""
        self.tool_manager.toggle_single_draw_mode(checked)

    def toggle_toolbar_collapse(self) -> None:
        """切换工具栏折叠/展开状态"""
        self.toolbar.toggle_toolbar_collapse()

    def save_current_config(self) -> None:
        """保存当前配置"""
        self.config_manager.save_current_config()

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
        if hasattr(self, 'tray_manager') and self.tray_manager:
            self.tray_manager.cleanup()
        event.accept()

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        """事件过滤器"""
        # 让事件继续正常处理
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    tool: AnnotationTool = AnnotationTool()
    tool.show()
    sys.exit(app.exec_())


