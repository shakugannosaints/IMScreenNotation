"""
文本样式事件处理器
负责处理对话框中的各种事件和交互操作
"""

from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QCoreApplication


class TextStyleEventHandler:
    """文本样式事件处理器"""
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.canvas = dialog.canvas
        
    def choose_text_color(self):
        """选择文本颜色"""
        try:
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            color = QColorDialog.getColor(self.canvas.properties.text_color, self.dialog, "选择文本颜色")
            if color.isValid():
                self.canvas.set_text_color(color)
                self.dialog.theme_manager.update_color_button(self.dialog.text_color_btn, color)
                
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
        except Exception as e:
            print(f"Error choosing text color: {e}")
            
    def choose_background_color(self):
        """选择背景颜色"""
        try:
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            current_color = self.canvas.properties.text_background_color or QColor(255, 255, 255)
            color = QColorDialog.getColor(current_color, self.dialog, "选择背景颜色")
            if color.isValid():
                self.canvas.set_text_background_color(color)
                self.dialog.theme_manager.update_color_button(self.dialog.bg_color_btn, color)
                self.dialog.bg_transparent_check.setChecked(False)
                
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
        except Exception as e:
            print(f"Error choosing background color: {e}")
            
    def choose_border_color(self):
        """选择边框颜色"""
        try:
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            current_color = self.canvas.properties.text_border_color or QColor(0, 0, 0)
            color = QColorDialog.getColor(current_color, self.dialog, "选择边框颜色")
            if color.isValid():
                self.canvas.set_text_border_color(color)
                self.dialog.theme_manager.update_color_button(self.dialog.border_color_btn, color)
                
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
        except Exception as e:
            print(f"Error choosing border color: {e}")
            
    def toggle_background_transparency(self):
        """切换背景透明度"""
        if self.dialog.bg_transparent_check.isChecked():
            self.canvas.set_text_background_color(None)
            self.dialog.bg_color_btn.setStyleSheet("")
        else:
            # 如果没有背景颜色，设置默认白色
            if not self.canvas.properties.text_background_color:
                self.canvas.set_text_background_color(QColor(255, 255, 255))
                self.dialog.theme_manager.update_color_button(
                    self.dialog.bg_color_btn, 
                    self.canvas.properties.text_background_color
                )
                
    def toggle_border_enable(self):
        """切换边框启用状态"""
        enabled = self.dialog.border_enable_check.isChecked()
        self.dialog.border_color_btn.setEnabled(enabled)
        self.dialog.border_width_spin.setEnabled(enabled)
        
        # 立即更新canvas的边框启用状态
        self.canvas.set_text_border_enabled(enabled)
        
        if enabled:
            current_border_color = getattr(self.canvas.properties, 'text_border_color', None)
            if not current_border_color:
                border_color = QColor(0, 0, 0)
                self.canvas.set_text_border_color(border_color)
                self.dialog.theme_manager.update_color_button(self.dialog.border_color_btn, border_color)
        else:
            self.canvas.set_text_border_color(None)
            self.dialog.border_color_btn.setStyleSheet("")
            
    def accept_settings(self):
        """接受设置并关闭对话框"""
        try:
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            self.dialog.settings_manager.apply_settings()
            
            # 触发配置保存
            self.dialog.settings_manager.trigger_config_save()
            
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            # 使用 accept() 而不是 close()，这样对话框会返回 Accepted 状态
            self.dialog.accept()
            
        except Exception as e:
            print(f"Error accepting settings: {e}")
            import traceback
            traceback.print_exc()
            self.dialog.close()
            
    def handle_close_event(self, event):
        """处理关闭事件"""
        try:
            # 在关闭前应用设置并保存配置
            self.dialog.settings_manager.apply_settings()
            self.dialog.settings_manager.trigger_config_save()
            
            # 确保所有事件都被处理
            QCoreApplication.processEvents()
            
            # 立即确保工具栏回到最前面，并延迟再次确保
            if (hasattr(self.dialog, 'parent_widget') and 
                self.dialog.parent_widget and 
                hasattr(self.dialog.parent_widget, 'window_manager')):
                self.dialog.parent_widget.window_manager.ensure_toolbar_on_top()  # type: ignore
                # 延迟再次确保，给对话框更多时间完全关闭
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(300, self.dialog.parent_widget.window_manager.ensure_toolbar_on_top)  # type: ignore
            
            event.accept()
            # 强制清理资源
            self.dialog.deleteLater()
        except Exception as e:
            print(f"Error in closeEvent: {e}")
            event.accept()
