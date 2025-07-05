"""
配置管理模块
处理应用程序配置的保存和加载
"""
from typing import TYPE_CHECKING, Dict, Any
from config import load_config, save_config
from constants import STATUS_MESSAGE_TIMEOUT

if TYPE_CHECKING:
    from main import AnnotationTool


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, main_window: 'AnnotationTool'):
        self.main_window = main_window
    
    def save_current_config(self) -> None:
        """保存当前配置"""
        config = self.main_window.config
        
        # 保存画布相关配置
        config["current_color"] = self.main_window.canvas.current_color
        config["current_thickness"] = self.main_window.canvas.current_thickness
        config["current_opacity"] = self.main_window.canvas.current_opacity
        config["canvas_color"] = self.main_window.canvas.canvas_color
        config["canvas_opacity"] = self.main_window.canvas.canvas_opacity
        
        # 保存透明度设置
        if hasattr(self.main_window, 'user_passthrough_opacity'):
            config["passthrough_opacity"] = self.main_window.user_passthrough_opacity
        if hasattr(self.main_window, 'user_non_passthrough_opacity'):
            config["non_passthrough_opacity"] = self.main_window.user_non_passthrough_opacity
        
        # 保存工具栏字体大小设置
        if hasattr(self.main_window, 'toolbar') and self.main_window.toolbar:
            config["toolbar_font_size"] = self.main_window.toolbar.font_size
        
        # 保存文本相关配置
        self._save_text_config(config)
        
        save_config(config)
        self.main_window._status_bar.showMessage("配置已保存", STATUS_MESSAGE_TIMEOUT)
    
    def _save_text_config(self, config: Dict[str, Any]) -> None:
        """保存文本相关配置"""
        text_config_keys = [
            "text_font_family", "text_font_size", "text_font_bold", "text_font_italic",
            "text_color", "text_background_color", "text_border_color", 
            "text_border_enabled", "text_border_width", "text_padding"
        ]
        
        for key in text_config_keys:
            if hasattr(self.main_window.canvas, key):
                config[key] = getattr(self.main_window.canvas, key)
    
    def load_and_apply_config(self) -> None:
        """加载并应用配置"""
        config = load_config()
        self.main_window.config = config
        
        # 应用画布配置
        self._apply_canvas_config(config)
        
        # 应用文本配置
        self._apply_text_config(config)
    
    def _apply_canvas_config(self, config: Dict[str, Any]) -> None:
        """应用画布配置"""
        canvas = self.main_window.canvas
        
        canvas.set_current_color(config["current_color"])
        canvas.set_current_thickness(config["current_thickness"])
        canvas.set_current_opacity(config["current_opacity"])
        canvas.set_canvas_color(config["canvas_color"])
        canvas.set_canvas_opacity(config["canvas_opacity"])
    
    def _apply_text_config(self, config: Dict[str, Any]) -> None:
        """应用文本配置"""
        canvas = self.main_window.canvas
        
        try:
            canvas.set_text_font_family(config["text_font_family"])
            canvas.set_text_font_size(config["text_font_size"])
            canvas.set_text_font_bold(config["text_font_bold"])
            canvas.set_text_font_italic(config["text_font_italic"])
            canvas.set_text_color(config["text_color"])
            canvas.set_text_background_color(config["text_background_color"])
            canvas.set_text_border_color(config["text_border_color"])
            canvas.text_border_enabled = config["text_border_enabled"]
            canvas.set_text_border_width(config["text_border_width"])
            canvas.set_text_padding(config["text_padding"])
        except Exception as e:
            print(f"Error applying text config: {e}")
            # 如果应用配置失败，确保画布有基本的默认值
            self._ensure_canvas_text_defaults(canvas)
    
    def _ensure_canvas_text_defaults(self, canvas) -> None:
        """确保画布有基本的文本默认值"""
        from PyQt5.QtGui import QColor
        
        if not hasattr(canvas, 'text_font_family') or canvas.text_font_family is None:
            canvas.text_font_family = 'Arial'
        if not hasattr(canvas, 'text_font_size') or canvas.text_font_size is None:
            canvas.text_font_size = 16
        if not hasattr(canvas, 'text_font_bold') or canvas.text_font_bold is None:
            canvas.text_font_bold = False
        if not hasattr(canvas, 'text_font_italic') or canvas.text_font_italic is None:
            canvas.text_font_italic = False
        if not hasattr(canvas, 'text_color') or canvas.text_color is None:
            canvas.text_color = QColor(255, 0, 0, 255)
        if not hasattr(canvas, 'text_background_color'):
            canvas.text_background_color = None
        if not hasattr(canvas, 'text_border_color'):
            canvas.text_border_color = None
        if not hasattr(canvas, 'text_border_enabled') or canvas.text_border_enabled is None:
            canvas.text_border_enabled = True
        if not hasattr(canvas, 'text_border_width') or canvas.text_border_width is None:
            canvas.text_border_width = 1
        if not hasattr(canvas, 'text_padding') or canvas.text_padding is None:
            canvas.text_padding = 5
