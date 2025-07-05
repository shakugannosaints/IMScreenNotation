"""
窗口管理模块
处理主窗口的属性设置、显示隐藏等功能
"""
from typing import TYPE_CHECKING
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QRect
from constants import STATUS_MESSAGE_TIMEOUT

if TYPE_CHECKING:
    from main import AnnotationTool


class WindowManager:
    """窗口管理器"""
    
    def __init__(self, main_window: 'AnnotationTool'):
        self.main_window = main_window
    
    def setup_window_properties(self) -> None:
        """设置窗口属性"""
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
        else:
            # 如果无法获取主屏幕，使用默认值
            screen_geometry = QRect(0, 0, 1920, 1080)
        
        # 设置窗口覆盖整个屏幕，去除所有边距
        self.main_window.setGeometry(screen_geometry)
        self.main_window.setFixedSize(screen_geometry.size())
        
        # 确保画布也覆盖整个窗口
        self.main_window.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_window.main_layout.setSpacing(0)
        
        # 设置窗口属性使其成为透明覆盖层
        self.main_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.main_window.setAttribute(Qt.WA_TranslucentBackground)
    
    def setup_menubar(self) -> None:
        """设置菜单栏 - 在无边框模式下隐藏菜单栏"""
        menu_bar = self.main_window.menuBar()
        if menu_bar:
            menu_bar.setVisible(False)
            menu_bar.setMaximumHeight(0)
    
    def toggle_visibility(self) -> None:
        """切换主窗口显示/隐藏"""
        print("热键 toggle_visibility 被触发!")
        if self.main_window.isVisible():
            self.main_window.hide()
            print("主窗口已隐藏")
        else:
            self.main_window.show()
            print("主窗口已显示")
    
    def toggle_canvas_visibility(self) -> None:
        """切换画布显示/隐藏"""
        if self.main_window.canvas.isVisible():
            self.main_window.canvas.hide()
            self.main_window.toolbar.toggle_visibility_btn.setText("👁️ 显示")
            self.main_window.toolbar.toggle_visibility_btn.setChecked(True)
            self.main_window.toolbar.toggle_visibility_btn.setProperty("class", "action active")
            self.main_window._status_bar.showMessage("画布已隐藏", STATUS_MESSAGE_TIMEOUT)
        else:
            self.main_window.canvas.show()
            self.main_window.toolbar.toggle_visibility_btn.setText("👁️ 隐藏")
            self.main_window.toolbar.toggle_visibility_btn.setChecked(False)
            self.main_window.toolbar.toggle_visibility_btn.setProperty("class", "action")
            self.main_window._status_bar.showMessage("画布已显示", STATUS_MESSAGE_TIMEOUT)
        
        # 刷新按钮样式
        if self.main_window.toolbar.toggle_visibility_btn.style():
            self.main_window.toolbar.toggle_visibility_btn.style().polish(
                self.main_window.toolbar.toggle_visibility_btn
            )
    
    def ensure_toolbar_on_top(self) -> None:
        """确保工具栏始终显示在最前面"""
        if (hasattr(self.main_window, 'toolbar') and 
            self.main_window.toolbar and 
            not self.main_window.toolbar_completely_hidden):
            self.main_window.toolbar.raise_()
            self.main_window.toolbar.activateWindow()
            self.main_window.toolbar.show()
