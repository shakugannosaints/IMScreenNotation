"""
文本样式配置对话框
用于设置文本标注的字体、颜色、背景、边框等样式
"""

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt

from .ui_builder import TextStyleUIBuilder
from .event_handler import TextStyleEventHandler
from .theme_manager import TextStyleThemeManager
from .settings_manager import TextStyleSettingsManager


class TextStyleDialog(QDialog):
    """文本样式配置对话框"""
    
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.parent_widget = parent  # 保存父窗口引用
        self.setWindowTitle("文本样式设置")
        self.setModal(True)
        self.setFixedSize(450, 720)  # 增加对话框高度
        
        # 设置窗口标志以确保对话框正常显示
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowModality(Qt.ApplicationModal)
        
        # 确保对话框在屏幕中央显示
        self.move_to_center()
        
        try:
            # 初始化各个管理器
            self.ui_builder = TextStyleUIBuilder(self)
            self.event_handler = TextStyleEventHandler(self)
            self.theme_manager = TextStyleThemeManager(self)
            self.settings_manager = TextStyleSettingsManager(self.canvas, self)
            
            # 初始化界面
            self.ui_builder.setup_ui()
            
            # 应用样式表
            self.theme_manager.apply_stylesheet()
            
            # 加载当前设置
            self.settings_manager.load_current_settings()
            
        except Exception as e:
            print(f"Error initializing TextStyleDialog: {e}")
            import traceback
            traceback.print_exc()
            
    def move_to_center(self):
        """将对话框移动到屏幕中央"""
        try:
            from PyQt5.QtWidgets import QApplication
            desktop = QApplication.desktop()
            screen_geometry = desktop.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
        except Exception as e:
            print(f"Error moving dialog to center: {e}")
            
    def refresh_theme(self):
        """刷新对话框主题"""
        self.theme_manager.refresh_theme()
        
    def showEvent(self, event):
        """重写显示事件以确保对话框稳定显示"""
        super().showEvent(event)
        # 确保对话框正常显示
        self.activateWindow()
        
    def closeEvent(self, event):
        """重写关闭事件"""
        self.event_handler.handle_close_event(event)
