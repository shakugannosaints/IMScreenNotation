"""
工具栏主题管理模块
负责管理工具栏的样式和主题切换
"""

from typing import Dict, Any
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor


class ToolbarThemeManager:
    """工具栏主题管理器"""
    
    def __init__(self, toolbar_widget):
        """初始化主题管理器
        
        Args:
            toolbar_widget: 工具栏组件实例
        """
        self.toolbar = toolbar_widget
        self.is_dark_theme = True
        self.font_size = 11
    
    def get_theme_stylesheet(self) -> str:
        """获取当前主题的样式表"""
        base_styles = self.get_dark_theme_stylesheet() if self.is_dark_theme else self.get_light_theme_stylesheet()
        scrollable_styles = self.get_scrollable_components_stylesheet()
        return base_styles + "\n" + scrollable_styles
    
    def get_dark_theme_stylesheet(self) -> str:
        """获取黑夜模式样式表"""
        return f"""
            /* 主容器样式 */
            QWidget {{
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: {self.font_size}px;
                border: none;
            }}
            
            /* 卡片容器样式 */
            QFrame.card {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 6px;
                margin: 2px;
            }}
            
            /* 标题区域样式 */
            QWidget#titleContainer {{
                background-color: #0078d4;
                border-radius: 8px 8px 0px 0px;
                padding: 8px;
            }}
            
            /* 标题标签样式 */
            QLabel#titleLabel {{
                color: #ffffff;
                font-size: {self.font_size + 1}px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 0px;
            }}
            
            /* 工具按钮样式 */
            QPushButton.tool {{
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                color: #ffffff;
                padding: 6px 8px;
                font-size: {max(self.font_size - 2, 8)}px;
                font-weight: 500;
                min-height: 26px;
                min-width: 65px;
                max-width: 80px;
            }}
            QPushButton.tool:hover {{
                background-color: #4a4a4a;
                border: 1px solid #0078d4;
                color: #ffffff;
            }}
            QPushButton.tool:pressed {{
                background-color: #2a2a2a;
                border: 1px solid #0078d4;
            }}
            QPushButton.tool:checked {{
                background-color: #0078d4;
                border: 1px solid #106ebe;
                color: #ffffff;
                font-weight: 600;
            }}
            
            /* 操作按钮样式 */
            QPushButton.action {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                color: #ffffff;
                padding: 6px 8px;
                font-size: {max(self.font_size - 2, 8)}px;
                min-height: 28px;
                min-width: 60px;
                max-width: 85px;
            }}
            QPushButton.action:hover {{
                background-color: #3a3a3a;
                border: 1px solid #0078d4;
            }}
            QPushButton.action:pressed {{
                background-color: #1a1a1a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
            }}
            QPushButton.action:checked {{
                background-color: #0078d4;
                border: 1px solid #106ebe;
                border-radius: 6px;
                color: #ffffff;
            }}
            
            /* 激活状态按钮样式 */
            QPushButton.action.active {{
                background-color: #0078d4;
                border: 1px solid #106ebe;
                color: #ffffff;
                font-weight: 600;
            }}
            QPushButton.action.active:hover {{
                background-color: #106ebe;
                border: 1px solid #005a9e;
            }}
            
            /* 特殊按钮样式 */
            QPushButton.primary {{
                background-color: #0078d4;
                border: 1px solid #106ebe;
            }}
            QPushButton.primary:hover {{
                background-color: #106ebe;
            }}
            
            QPushButton.success {{
                background-color: #28a745;
                border: 1px solid #1e7e34;
            }}
            QPushButton.success:hover {{
                background-color: #1e7e34;
            }}
            
            QPushButton.warning {{
                background-color: #fd7e14;
                border: 1px solid #e8590c;
            }}
            QPushButton.warning:hover {{
                background-color: #e8590c;
            }}
            
            QPushButton.danger {{
                background-color: #dc3545;
                border: 1px solid #bd2130;
            }}
            QPushButton.danger:hover {{
                background-color: #bd2130;
            }}
            
            /* 颜色按钮特殊样式 */
            QPushButton#colorButton {{
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                min-height: 26px;
                min-width: 100px;
                max-width: 120px;
                font-weight: bold;
                font-size: {max(self.font_size - 2, 8)}px;
            }}
            QPushButton#colorButton:hover {{
                border: 1px solid #0078d4;
            }}
            
            /* 标签样式 */
            QLabel {{
                color: #ffffff;
                font-size: {max(self.font_size - 2, 8)}px;
                font-weight: 500;
                background: transparent;
                border: none;
                padding: 2px;
            }}
            
            QLabel.section-title {{
                color: #0078d4;
                font-size: {max(self.font_size - 1, 9)}px;
                font-weight: bold;
                padding: 3px 2px;
                border-bottom: 1px solid #3a3a3a;
                margin-bottom: 4px;
            }}
            
            /* 滑块样式 */
            QSlider::groove:horizontal {{
                border: 1px solid #3a3a3a;
                height: 4px;
                background: #2a2a2a;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: #0078d4;
                border: 1px solid #106ebe;
                width: 14px;
                height: 14px;
                border-radius: 7px;
                margin: -5px 0;
            }}
            QSlider::handle:horizontal:hover {{
                background: #106ebe;
            }}
            QSlider::handle:horizontal:pressed {{
                background: #005a9e;
            }}
            
            /* 折叠按钮样式 */
            QPushButton#collapseButton {{
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 12px;
                color: #ffffff;
                font-size: {max(self.font_size - 1, 9)}px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }}
            QPushButton#collapseButton:hover {{
                background-color: #4a4a4a;
                border: 1px solid #0078d4;
            }}
            
            /* 主题切换按钮样式 */
            QPushButton#themeToggleButton {{
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 12px;
                color: #ffffff;
                font-size: {max(self.font_size - 1, 9)}px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }}
            QPushButton#themeToggleButton:hover {{
                background-color: #4a4a4a;
                border: 1px solid #0078d4;
            }}
        """
    
    def get_light_theme_stylesheet(self) -> str:
        """获取白天模式样式表"""
        return f"""
            /* 主容器样式 */
            QWidget {{
                background-color: #ffffff;
                color: #333333;
                font-family: "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: {self.font_size}px;
                border: none;
            }}
            
            /* 卡片容器样式 */
            QFrame.card {{
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                padding: 6px;
                margin: 2px;
            }}
            
            /* 标题区域样式 */
            QWidget#titleContainer {{
                background-color: #0078d4;
                border-radius: 8px 8px 0px 0px;
                padding: 8px;
            }}
            
            /* 标题标签样式 */
            QLabel#titleLabel {{
                color: #ffffff;
                font-size: {self.font_size + 1}px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 0px;
            }}
            
            /* 工具按钮样式 */
            QPushButton.tool {{
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
                border-radius: 6px;
                color: #333333;
                padding: 6px 8px;
                font-size: {max(self.font_size - 2, 8)}px;
                font-weight: 500;
                min-height: 26px;
                min-width: 65px;
                max-width: 80px;
            }}
            QPushButton.tool:hover {{
                background-color: #d8d8d8;
                border: 1px solid #0078d4;
                color: #333333;
            }}
            QPushButton.tool:pressed {{
                background-color: #c8c8c8;
                border: 1px solid #0078d4;
                color: #333333;
            }}
            QPushButton.tool:checked {{
                background-color: #0078d4;
                border: 1px solid #106ebe;
                color: #333333;
                font-weight: 600;
            }}
            
            /* 操作按钮样式 */
            QPushButton.action {{
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                color: #333333;
                padding: 6px 8px;
                font-size: {max(self.font_size - 2, 8)}px;
                min-height: 28px;
                min-width: 60px;
                max-width: 85px;
            }}
            QPushButton.action:hover {{
                background-color: #e0e0e0;
                border: 1px solid #0078d4;
            }}
            QPushButton.action:pressed {{
                background-color: #d0d0d0;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
            }}
            QPushButton.action:checked {{
                background-color: #0078d4;
                border: 1px solid #106ebe;
                border-radius: 6px;
                color: #333333;
            }}
            
            /* 激活状态按钮样式 */
            QPushButton.action.active {{
                background-color: #0078d4;
                border: 1px solid #106ebe;
                color: #333333;
                font-weight: 600;
            }}
            QPushButton.action.active:hover {{
                background-color: #106ebe;
                border: 1px solid #005a9e;
            }}
            
            /* 特殊按钮样式 */
            QPushButton.primary {{
                background-color: #0078d4;
                border: 1px solid #106ebe;
                color: #333333;
            }}
            QPushButton.primary:hover {{
                background-color: #106ebe;
            }}
            
            QPushButton.success {{
                background-color: #28a745;
                border: 1px solid #1e7e34;
                color: #333333;
            }}
            QPushButton.success:hover {{
                background-color: #1e7e34;
            }}
            
            QPushButton.warning {{
                background-color: #fd7e14;
                border: 1px solid #e8590c;
                color: #333333;
            }}
            QPushButton.warning:hover {{
                background-color: #e8590c;
            }}
            
            QPushButton.danger {{
                background-color: #dc3545;
                border: 1px solid #bd2130;
                color: #333333;
            }}
            QPushButton.danger:hover {{
                background-color: #bd2130;
            }}
            
            /* 颜色按钮特殊样式 */
            QPushButton#colorButton {{
                border: 2px solid #c0c0c0;
                border-radius: 6px;
                min-height: 26px;
                min-width: 100px;
                max-width: 120px;
                font-weight: bold;
                font-size: {max(self.font_size - 2, 8)}px;
            }}
            QPushButton#colorButton:hover {{
                border: 1px solid #0078d4;
            }}
            
            /* 标签样式 */
            QLabel {{
                color: #333333;
                font-size: {max(self.font_size - 2, 8)}px;
                font-weight: 500;
                background: transparent;
                border: none;
                padding: 2px;
            }}
            
            QLabel.section-title {{
                color: #0078d4;
                font-size: {max(self.font_size - 1, 9)}px;
                font-weight: bold;
                padding: 3px 2px;
                border-bottom: 1px solid #d0d0d0;
                margin-bottom: 4px;
            }}
            
            /* 滑块样式 */
            QSlider::groove:horizontal {{
                border: 1px solid #d0d0d0;
                height: 4px;
                background: #f0f0f0;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: #0078d4;
                border: 1px solid #106ebe;
                width: 14px;
                height: 14px;
                border-radius: 7px;
                margin: -5px 0;
            }}
            QSlider::handle:horizontal:hover {{
                background: #106ebe;
            }}
            QSlider::handle:horizontal:pressed {{
                background: #005a9e;
            }}
            
            /* 折叠按钮样式 */
            QPushButton#collapseButton {{
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
                border-radius: 12px;
                color: #333333;
                font-size: {max(self.font_size - 1, 9)}px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }}
            QPushButton#collapseButton:hover {{
                background-color: #d8d8d8;
                border: 1px solid #0078d4;
            }}
            
            /* 主题切换按钮样式 */
            QPushButton#themeToggleButton {{
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
                border-radius: 12px;
                color: #333333;
                font-size: {max(self.font_size - 1, 9)}px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }}
            QPushButton#themeToggleButton:hover {{
                background-color: #d8d8d8;
                border: 1px solid #0078d4;
            }}
        """
    
    def get_scrollable_components_stylesheet(self) -> str:
        """获取可滚动组件的样式表"""
        if self.is_dark_theme:
            return """
            /* 可折叠区域样式 */
            QWidget#collapsibleSection {
                background-color: transparent;
                border: none;
                margin: 2px 0px;
            }
            
            QWidget#sectionHeader {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 4px;
            }
            
            QWidget#sectionHeader:hover {
                background-color: #4a4a4a;
                border-color: #0078d4;
            }
            
            QLabel#collapseIndicator {
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
            }
            
            QLabel#sectionTitle {
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
            }
            
            QWidget#sectionContent {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                border-top: none;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                margin-top: 0px;
            }
            
            /* 滚动区域样式 */
            QScrollArea#scrollableContent {
                border: none;
                background: transparent;
            }
            
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.5);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                border: none;
                background: none;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            """
        else:
            return """
            /* 可折叠区域样式 - 白天模式 */
            QWidget#collapsibleSection {
                background-color: transparent;
                border: none;
                margin: 2px 0px;
            }
            
            QWidget#sectionHeader {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
                border-radius: 6px;
                padding: 4px;
            }
            
            QWidget#sectionHeader:hover {
                background-color: #e0e0e0;
                border-color: #0078d4;
            }
            
            QLabel#collapseIndicator {
                color: #333333;
                font-weight: bold;
                font-size: 12px;
            }
            
            QLabel#sectionTitle {
                color: #333333;
                font-weight: bold;
                font-size: 12px;
            }
            
            QWidget#sectionContent {
                background-color: #fafafa;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                border-top: none;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                margin-top: 0px;
            }
            
            /* 滚动区域样式 - 白天模式 */
            QScrollArea#scrollableContent {
                border: none;
                background: transparent;
            }
            
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.1);
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.5);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                border: none;
                background: none;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            """
    
    def toggle_theme(self) -> None:
        """切换主题"""
        self.is_dark_theme = not self.is_dark_theme
        self.toolbar.setStyleSheet(self.get_theme_stylesheet())
        
        # 更新主题切换按钮图标
        if self.is_dark_theme:
            self.toolbar.theme_toggle_btn.setText("☀️")
            self.toolbar.theme_toggle_btn.setToolTip("切换到白天模式")
        else:
            self.toolbar.theme_toggle_btn.setText("🌙")
            self.toolbar.theme_toggle_btn.setToolTip("切换到黑夜模式")
        
        # 更新内容区域的样式
        self.update_content_widget_style()
        
        # 重新应用颜色按钮的样式
        self.toolbar.update_color_button()
        
        # 显示状态信息
        theme_name = "黑夜模式" if self.is_dark_theme else "白天模式"
        self.toolbar.main_window.statusBar().showMessage(f"已切换到{theme_name}", 1000)
    
    def update_content_widget_style(self) -> None:
        """更新内容区域的样式"""
        if hasattr(self.toolbar, 'content_widget') and self.toolbar.content_widget:
            # 传统内容区域样式
            bg_color = "#1a1a1a" if self.is_dark_theme else "#ffffff"
            self.toolbar.content_widget.setStyleSheet(f"background-color: {bg_color}; border-radius: 0px 0px 8px 8px;")
        
        if hasattr(self.toolbar, 'scrollable_content') and self.toolbar.scrollable_content:
            # 可滚动内容区域样式
            scrollable_styles = self.get_scrollable_components_stylesheet()
            self.toolbar.scrollable_content.setStyleSheet(scrollable_styles)
    
    def update_color_button_style(self, color: QColor) -> None:
        """更新颜色按钮的显示样式
        
        Args:
            color: 要显示的颜色
        """
        # 根据主题选择边框颜色
        border_color = "#4a4a4a" if self.is_dark_theme else "#c0c0c0"
        
        self.toolbar.color_btn.setStyleSheet(f"""
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
    
    def update_font_size(self, size: int) -> None:
        """更新字体大小
        
        Args:
            size: 新的字体大小
        """
        self.font_size = size
        self.toolbar.setStyleSheet(self.get_theme_stylesheet())
