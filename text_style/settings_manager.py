"""
文本样式设置管理器
负责管理文本样式的加载、保存和应用
"""

from PyQt5.QtGui import QColor
from typing import Any


class TextStyleSettingsManager:
    """文本样式设置管理器"""
    
    def __init__(self, canvas, dialog):
        self.canvas = canvas
        self.dialog = dialog
        
    def ensure_canvas_text_attributes(self):
        """确保画布有必要的文本属性"""
        if not hasattr(self.canvas, 'text_font_family'):
            self.canvas.text_font_family = 'Arial'
        if not hasattr(self.canvas, 'text_font_size'):
            self.canvas.text_font_size = 16
        if not hasattr(self.canvas, 'text_font_bold'):
            self.canvas.text_font_bold = False
        if not hasattr(self.canvas, 'text_font_italic'):
            self.canvas.text_font_italic = False
        if not hasattr(self.canvas, 'text_color'):
            self.canvas.text_color = QColor(255, 0, 0, 255)
        if not hasattr(self.canvas, 'text_background_color'):
            self.canvas.text_background_color = None
        if not hasattr(self.canvas, 'text_border_color'):
            self.canvas.text_border_color = None
        if not hasattr(self.canvas, 'text_border_enabled'):
            self.canvas.text_border_enabled = True
        if not hasattr(self.canvas, 'text_border_width'):
            self.canvas.text_border_width = 1
        if not hasattr(self.canvas, 'text_padding'):
            self.canvas.text_padding = 5
        
    def load_current_settings(self):
        """加载当前画布的文本设置"""
        try:
            # 字体设置 - 使用 getattr 提供默认值
            font_family = getattr(self.canvas, 'text_font_family', 'Arial')
            font_family_index = self.dialog.font_family_combo.findText(font_family)
            if font_family_index >= 0:
                self.dialog.font_family_combo.setCurrentIndex(font_family_index)
            
            font_size = getattr(self.canvas, 'text_font_size', 16)
            self.dialog.font_size_spin.setValue(font_size)
            
            font_bold = getattr(self.canvas, 'text_font_bold', False)
            self.dialog.font_bold_check.setChecked(font_bold)
            
            font_italic = getattr(self.canvas, 'text_font_italic', False)
            self.dialog.font_italic_check.setChecked(font_italic)
            
            # 颜色设置
            text_color = getattr(self.canvas, 'text_color', QColor(255, 0, 0, 255))
            self.dialog.theme_manager.update_color_button(self.dialog.text_color_btn, text_color)
            
            # 背景色设置
            bg_color = getattr(self.canvas, 'text_background_color', None)
            if bg_color:
                self.dialog.theme_manager.update_color_button(self.dialog.bg_color_btn, bg_color)
                self.dialog.bg_transparent_check.setChecked(False)
            else:
                self.dialog.bg_transparent_check.setChecked(True)
            
            # 边框设置 - 暂时断开信号连接以避免在加载设置时触发toggle方法
            border_enabled = getattr(self.canvas, 'text_border_enabled', True)
            
            # 断开信号连接
            self.dialog.border_enable_check.toggled.disconnect(self.dialog.event_handler.toggle_border_enable)
            self.dialog.border_enable_check.setChecked(border_enabled)
            # 重新连接信号
            self.dialog.border_enable_check.toggled.connect(self.dialog.event_handler.toggle_border_enable)
            
            border_color = getattr(self.canvas, 'text_border_color', None)
            if border_color:
                self.dialog.theme_manager.update_color_button(self.dialog.border_color_btn, border_color)
            else:
                # 如果没有边框颜色但启用了边框，使用默认黑色
                if border_enabled:
                    default_border_color = QColor(0, 0, 0)
                    setattr(self.canvas, 'text_border_color', default_border_color)
                    self.dialog.theme_manager.update_color_button(self.dialog.border_color_btn, default_border_color)
                    
            border_width = getattr(self.canvas, 'text_border_width', 1)
            self.dialog.border_width_spin.setValue(border_width)
            
            # 其他设置
            padding = getattr(self.canvas, 'text_padding', 5)
            self.dialog.padding_spin.setValue(padding)
            
            # 在最后调用 toggle_border_enable 来正确设置UI状态（但不修改画布状态）
            self.dialog.event_handler.toggle_border_enable()
            
        except Exception as e:
            print(f"Error loading current settings: {e}")
            # 如果加载失败，确保画布有基本的文本属性
            self.ensure_canvas_text_attributes()
            # 设置默认UI值
            self.dialog.font_family_combo.setCurrentIndex(0)
            self.dialog.font_size_spin.setValue(16)
            self.dialog.font_bold_check.setChecked(False)
            self.dialog.font_italic_check.setChecked(False)
            self.dialog.bg_transparent_check.setChecked(True)
            self.dialog.border_enable_check.setChecked(True)
            self.dialog.border_width_spin.setValue(1)
            self.dialog.padding_spin.setValue(5)
            
            # 在异常情况下也调用 toggle_border_enable
            self.dialog.event_handler.toggle_border_enable()
    
    def apply_settings(self):
        """应用设置到画布"""
        try:
            # 字体设置 - 使用 setattr 安全设置属性
            setattr(self.canvas, 'text_font_family', self.dialog.font_family_combo.currentText())
            setattr(self.canvas, 'text_font_size', self.dialog.font_size_spin.value())
            setattr(self.canvas, 'text_font_bold', self.dialog.font_bold_check.isChecked())
            setattr(self.canvas, 'text_font_italic', self.dialog.font_italic_check.isChecked())
            
            # 边框设置
            setattr(self.canvas, 'text_border_enabled', self.dialog.border_enable_check.isChecked())
            if self.dialog.border_enable_check.isChecked():
                setattr(self.canvas, 'text_border_width', self.dialog.border_width_spin.value())
            else:
                setattr(self.canvas, 'text_border_color', None)
                
            # 其他设置
            setattr(self.canvas, 'text_padding', self.dialog.padding_spin.value())
            
        except Exception as e:
            print(f"Error applying settings: {e}")
            import traceback
            traceback.print_exc()
    
    def trigger_config_save(self):
        """触发配置保存"""
        try:
            # 查找主窗口并触发配置保存
            if self.dialog.parent_widget:
                # 如果父窗口有save_current_config方法，直接调用
                if hasattr(self.dialog.parent_widget, 'save_current_config'):
                    self.dialog.parent_widget.save_current_config()
                    print("Configuration saved via parent widget")
                # 如果父窗口是toolbar，通过main_window保存
                elif hasattr(self.dialog.parent_widget, 'main_window') and hasattr(self.dialog.parent_widget.main_window, 'save_current_config'):
                    self.dialog.parent_widget.main_window.save_current_config()
                    print("Configuration saved via main window")
                else:
                    print("Warning: Unable to find save_current_config method")
            else:
                print("Warning: No parent widget found for config save")
        except Exception as e:
            print(f"Error triggering config save: {e}")
            import traceback
            traceback.print_exc()
