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
        # 获取完整屏幕区域（包括任务栏等系统界面）
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()  # 使用完整屏幕几何，包括任务栏
            print(f"主屏幕几何: {screen_geometry}")
        else:
            # 如果无法获取主屏幕，使用默认值
            screen_geometry = QRect(0, 0, 1920, 1080)
        
        # 隐藏状态栏，避免占用空间
        if self.main_window._status_bar:
            self.main_window._status_bar.hide()
            self.main_window._status_bar.setMaximumHeight(0)
        
        # 设置主窗口的内容边距为0
        if hasattr(self.main_window, 'central_widget'):
            self.main_window.central_widget.setContentsMargins(0, 0, 0, 0)
        
        # 设置窗口覆盖整个屏幕，去除所有边距
        self.main_window.setGeometry(screen_geometry)
        self.main_window.setFixedSize(screen_geometry.size())
        
        # 移除布局管理器对画布的约束，直接设置画布为中心控件
        if hasattr(self.main_window, 'canvas') and self.main_window.canvas:
            print(f"画布创建前的窗口几何: {self.main_window.geometry()}")
            
            # 从原来的布局中移除画布
            if self.main_window.main_layout.count() > 0:
                self.main_window.main_layout.removeWidget(self.main_window.canvas)
            
            # 直接将画布设置为中心控件，不使用布局管理器
            self.main_window.setCentralWidget(self.main_window.canvas)
            
            # 确保画布没有边距和spacing
            self.main_window.canvas.setContentsMargins(0, 0, 0, 0)
            
            # 确保画布的几何与窗口匹配
            self.main_window.canvas.setGeometry(0, 0, screen_geometry.width(), screen_geometry.height())
            self.main_window.canvas.setFixedSize(screen_geometry.size())
            
            print(f"设置后的画布几何: {self.main_window.canvas.geometry()}")
            print(f"设置后的画布尺寸: {self.main_window.canvas.size()}")
        
        # 设置窗口属性使其成为透明覆盖层
        self.main_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.main_window.setAttribute(Qt.WA_TranslucentBackground)
    
    def setup_menubar(self) -> None:
        """设置菜单栏 - 在无边框模式下隐藏菜单栏"""
        menu_bar = self.main_window.menuBar()
        if menu_bar:
            menu_bar.setVisible(False)
            menu_bar.setMaximumHeight(0)
            menu_bar.setFixedHeight(0)
            # 确保菜单栏不占用任何空间
            menu_bar.setContentsMargins(0, 0, 0, 0)
    
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
            if self.main_window.toolbar.toggle_visibility_btn:
                self.main_window.toolbar.toggle_visibility_btn.setText("👁️ 显示")
                self.main_window.toolbar.toggle_visibility_btn.setChecked(True)
                self.main_window.toolbar.toggle_visibility_btn.setProperty("class", "action active")
            self.main_window._status_bar.showMessage("画布已隐藏", STATUS_MESSAGE_TIMEOUT)
        else:
            self.main_window.canvas.show()
            if self.main_window.toolbar.toggle_visibility_btn:
                self.main_window.toolbar.toggle_visibility_btn.setText("👁️ 隐藏")
                self.main_window.toolbar.toggle_visibility_btn.setChecked(False)
                self.main_window.toolbar.toggle_visibility_btn.setProperty("class", "action")
            self.main_window._status_bar.showMessage("画布已显示", STATUS_MESSAGE_TIMEOUT)
        
        # 刷新按钮样式
        if (self.main_window.toolbar.toggle_visibility_btn and 
            self.main_window.toolbar.toggle_visibility_btn.style()):
            self.main_window.toolbar.toggle_visibility_btn.style().unpolish(
                self.main_window.toolbar.toggle_visibility_btn
            )
            self.main_window.toolbar.toggle_visibility_btn.style().polish(
                self.main_window.toolbar.toggle_visibility_btn
            )
    
    def ensure_toolbar_on_top(self) -> None:
        """确保工具栏始终显示在最前面"""
        if (hasattr(self.main_window, 'toolbar') and 
            self.main_window.toolbar and 
            not self.main_window.toolbar_completely_hidden):
            
            # 首先确保工具栏可见
            if not self.main_window.toolbar.isVisible():
                self.main_window.toolbar.show()
            
            # 将工具栏置顶
            self.main_window.toolbar.raise_()
            self.main_window.toolbar.repaint()  # 强制重绘
            
            # 只在非穿透模式下才激活窗口，避免在穿透模式下抢夺焦点
            if not getattr(self.main_window, 'passthrough_state', False):
                self.main_window.toolbar.activateWindow()
                self.main_window.toolbar.setFocus()  # 确保获得焦点
