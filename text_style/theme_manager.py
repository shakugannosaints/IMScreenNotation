"""
文本样式主题管理器
负责管理对话框的主题和样式
"""

from PyQt5.QtGui import QColor


class TextStyleThemeManager:
    """文本样式主题管理器"""
    
    def __init__(self, dialog):
        self.dialog = dialog
        
    def get_parent_theme(self):
        """获取父窗口的主题状态"""
        try:
            # 尝试从父窗口获取主题信息
            if self.dialog.parent_widget:
                # 如果父窗口有is_dark_theme属性，直接使用
                if hasattr(self.dialog.parent_widget, 'is_dark_theme'):
                    return self.dialog.parent_widget.is_dark_theme
                # 如果父窗口是主窗口，尝试获取toolbar的主题
                elif hasattr(self.dialog.parent_widget, 'toolbar') and hasattr(self.dialog.parent_widget.toolbar, 'is_dark_theme'):
                    return self.dialog.parent_widget.toolbar.is_dark_theme
            
            # 如果无法获取主题信息，默认使用浅色主题
            return False
        except Exception as e:
            print(f"Error getting parent theme: {e}")
            return False
    
    def update_color_button(self, button, color):
        """更新颜色按钮的样式"""
        if color:
            # 根据颜色亮度决定文字颜色
            brightness = (color.red() * 299 + color.green() * 587 + color.blue() * 114) / 1000
            text_color = "white" if brightness < 128 else "black"
            
            # 根据主题选择边框颜色
            is_dark = self.get_parent_theme()
            border_color = "#4a4a4a" if is_dark else "#d0d0d0"
            
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                    color: {text_color} !important;
                    border: 2px solid {border_color};
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 8px 12px;
                    min-height: 28px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    border: 2px solid #0078d4;
                    color: {text_color} !important;
                }}
                QPushButton:pressed {{
                    border: 2px solid #0078d4;
                    background-color: {color.darker().name()};
                    color: {text_color} !important;
                }}
            """)
        else:
            # 恢复默认样式，确保文本颜色正确
            is_dark = self.get_parent_theme()
            text_color = "#ffffff" if is_dark else "#333333"
            button.setStyleSheet(f"""
                QPushButton {{
                    color: {text_color} !important;
                }}
            """)
    
    def apply_stylesheet(self):
        """应用现代化样式表"""
        # 根据父窗口的主题状态选择样式
        is_dark = self.get_parent_theme()
        if is_dark:
            self.dialog.setStyleSheet(self.get_dark_theme_stylesheet())
        else:
            self.dialog.setStyleSheet(self.get_light_theme_stylesheet())
    
    def refresh_theme(self):
        """刷新对话框主题"""
        try:
            # 重新应用样式表
            self.apply_stylesheet()
            
            # 更新所有颜色按钮
            if hasattr(self.dialog, 'text_color_btn'):
                self.update_color_button(self.dialog.text_color_btn, self.dialog.canvas.text_color)
            
            if hasattr(self.dialog, 'bg_color_btn') and self.dialog.canvas.text_background_color:
                self.update_color_button(self.dialog.bg_color_btn, self.dialog.canvas.text_background_color)
                
            if hasattr(self.dialog, 'border_color_btn') and self.dialog.canvas.text_border_color:
                self.update_color_button(self.dialog.border_color_btn, self.dialog.canvas.text_border_color)
                
        except Exception as e:
            print(f"Error refreshing theme: {e}")
    
    def get_dark_theme_stylesheet(self):
        """获取深色主题样式表"""
        return """
            QDialog {
                background-color: #2a2a2a;
                color: #ffffff;
                font-family: "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 11px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #0078d4;
                font-size: 12px;
            }
            
            QLabel {
                color: #ffffff;
                font-size: 11px;
                min-height: 20px;
            }
            
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                color: #ffffff;
                padding: 8px 12px;
                font-size: 11px;
                min-height: 28px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #0078d4;
            }
            
            QPushButton:pressed {
                background-color: #2a2a2a;
                border: 1px solid #0078d4;
            }
            
            QSpinBox {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                color: #ffffff;
                padding: 6px;
                font-size: 11px;
                min-height: 24px;
            }
            
            QSpinBox:focus {
                border: 1px solid #0078d4;
            }
            
            QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                color: #ffffff;
                padding: 6px;
                font-size: 11px;
                min-height: 24px;
            }
            
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #4a4a4a;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #4a4a4a;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ffffff;
            }
            
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                outline: none;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 6px;
                border: none;
                min-height: 20px;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #106ebe;
                color: #ffffff;
            }
            
            QCheckBox {
                color: #ffffff;
                font-size: 11px;
                spacing: 8px;
                min-height: 24px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #4a4a4a;
                border-radius: 3px;
                background-color: #3a3a3a;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #106ebe;
            }
            
            QCheckBox::indicator:checked:hover {
                background-color: #106ebe;
            }
            
            QFrame[frameShape="4"] {
                color: #4a4a4a;
                max-height: 1px;
            }
        """
    
    def get_light_theme_stylesheet(self):
        """获取浅色主题样式表"""
        return """
            QDialog {
                background-color: #ffffff;
                color: #333333;
                font-family: "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 11px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                color: #333333;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #0078d4;
                font-size: 12px;
            }
            
            QLabel {
                color: #333333;
                font-size: 11px;
                min-height: 20px;
            }
            
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                color: #333333;
                padding: 8px 12px;
                font-size: 11px;
                min-height: 28px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #0078d4;
            }
            
            QPushButton:pressed {
                background-color: #d0d0d0;
                border: 1px solid #0078d4;
            }
            
            QSpinBox {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                color: #333333;
                padding: 6px;
                font-size: 11px;
                min-height: 24px;
            }
            
            QSpinBox:focus {
                border: 1px solid #0078d4;
            }
            
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                color: #333333;
                padding: 6px;
                font-size: 11px;
                min-height: 24px;
            }
            
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #d0d0d0;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #e0e0e0;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #333333;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                outline: none;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 6px;
                border: none;
                min-height: 20px;
                color: #333333;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #106ebe;
                color: #ffffff;
            }
            
            QCheckBox {
                color: #333333;
                font-size: 11px;
                spacing: 8px;
                min-height: 24px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: #ffffff;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #106ebe;
            }
            
            QCheckBox::indicator:checked:hover {
                background-color: #106ebe;
            }
            
            QFrame[frameShape="4"] {
                color: #d0d0d0;
                max-height: 1px;
            }
        """
