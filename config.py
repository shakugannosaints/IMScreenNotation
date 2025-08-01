import json
from PyQt5.QtGui import QColor

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        # Convert color from list to QColor object
        if "current_color" in config:
            config["current_color"] = QColor(*config["current_color"])
        if "canvas_color" in config:
            config["canvas_color"] = QColor(*config["canvas_color"])
        if "text_color" in config:
            config["text_color"] = QColor(*config["text_color"])
        if "text_background_color" in config and config["text_background_color"]:
            config["text_background_color"] = QColor(*config["text_background_color"])
        if "text_border_color" in config and config["text_border_color"]:
            config["text_border_color"] = QColor(*config["text_border_color"])
        
        # 确保字体大小配置存在
        if "toolbar_font_size" not in config:
            config["toolbar_font_size"] = 11
        
        # 确保文本相关配置存在
        text_defaults = {
            "text_font_family": "Arial",
            "text_font_size": 16,
            "text_font_bold": False,
            "text_font_italic": False,
            "text_color": QColor(255, 0, 0, 255),
            "text_background_color": None,
            "text_border_color": None,
            "text_border_enabled": True,
            "text_border_width": 1,
            "text_padding": 5
        }
        
        for key, default_value in text_defaults.items():
            if key not in config:
                config[key] = default_value
            
        return config
    except FileNotFoundError:
        # 首次运行时创建默认配置，并确保颜色格式一致
        default_config = {
            "hotkeys": {
                "toggle_visibility": "<ctrl>+<alt>+h",
                "toggle_passthrough": "<ctrl>+<alt>+p",
                "toggle_canvas_visibility": "<ctrl>+<alt>+v",
                "toggle_toolbar_collapse": "<ctrl>+<alt>+t",
                "toggle_complete_hide": "",
                "clear_canvas": "<ctrl>+<alt>+c",
                "undo": "<ctrl>+z",
                "redo": "<ctrl>+y",
                "single_draw_mode": "<ctrl>+<alt>+s",
                "tool_line": "<ctrl>+1",
                "tool_rectangle": "<ctrl>+2",
                "tool_circle": "<ctrl>+3",
                "tool_arrow": "<ctrl>+4",
                "tool_freehand": "<ctrl>+5",
                "tool_filled_freehand": "<ctrl>+<shift>+5",
                "tool_point": "<ctrl>+6",
                "tool_laser_pointer": "<ctrl>+7",
                "tool_text": "<ctrl>+8",
                "tool_eraser": "<ctrl>+9",
                "tool_line_ruler": "<ctrl>+<shift>+1",
                "tool_circle_ruler": "<ctrl>+<shift>+2",
                "ruler_settings": "<f6>",
                "ruler_calibration": "<f7>",
                # 属性调整热键
                "thickness_increase": "<ctrl>+q",
                "thickness_decrease": "<ctrl>+w",
                "drawing_opacity_increase": "<ctrl>+<alt>+q",
                "drawing_opacity_decrease": "<ctrl>+<alt>+w",
                "canvas_opacity_increase": "<ctrl>+<shift>+q",
                "canvas_opacity_decrease": "<ctrl>+<shift>+w"
            },
            "current_color": QColor(255, 0, 0, 255),  # RGBA for red
            "current_thickness": 3,
            "current_opacity": 1.0,
            "canvas_color": QColor(0, 0, 0, 0),  # RGBA for transparent
            "canvas_opacity": 0.0,
            "passthrough_opacity": 0.1,
            "non_passthrough_opacity": 0.8,
            "toolbar_font_size": 11,  # 默认字体大小
            # 文本相关配置
            "text_font_family": "Arial",
            "text_font_size": 16,
            "text_font_bold": False,
            "text_font_italic": False,
            "text_color": QColor(255, 0, 0, 255),  # 红色
            "text_background_color": None,  # 透明背景
            "text_border_color": None,  # 无边框
            "text_border_enabled": True,  # 边框默认启用
            "text_border_width": 1,
            "text_padding": 5
        }
        return default_config
    except json.JSONDecodeError:
        print("Error decoding config.json. Using default configuration.")
        # JSON解码错误时也使用默认配置，确保颜色格式一致
        default_config = {
            "hotkeys": {
                "toggle_visibility": "<ctrl>+<alt>+h",
                "toggle_passthrough": "<ctrl>+<alt>+p",
                "toggle_canvas_visibility": "<ctrl>+<alt>+v",
                "toggle_toolbar_collapse": "<ctrl>+<alt>+t",
                "toggle_complete_hide": "",
                "clear_canvas": "<ctrl>+<alt>+c",
                "undo": "<ctrl>+z",
                "redo": "<ctrl>+y",
                "single_draw_mode": "<ctrl>+<alt>+s",
                "tool_line": "<ctrl>+1",
                "tool_rectangle": "<ctrl>+2",
                "tool_circle": "<ctrl>+3",
                "tool_arrow": "<ctrl>+4",
                "tool_freehand": "<ctrl>+5",
                "tool_filled_freehand": "<ctrl>+<shift>+5",
                "tool_point": "<ctrl>+6",
                "tool_laser_pointer": "<ctrl>+7",
                "tool_text": "<ctrl>+8",
                "tool_eraser": "<ctrl>+9",
                "tool_line_ruler": "<ctrl>+<shift>+1",
                "tool_circle_ruler": "<ctrl>+<shift>+2",
                "ruler_settings": "<f6>",
                "ruler_calibration": "<f7>",
                # 属性调整热键
                "thickness_increase": "<ctrl>+=",
                "thickness_decrease": "<ctrl>+-",
                "drawing_opacity_increase": "<ctrl>+<alt>+=",
                "drawing_opacity_decrease": "<ctrl>+<alt>+-",
                "canvas_opacity_increase": "<ctrl>+<shift>+=",
                "canvas_opacity_decrease": "<ctrl>+<shift>+-"
            },
            "current_color": QColor(255, 0, 0, 255),  # RGBA for red
            "current_thickness": 3,
            "current_opacity": 1.0,
            "canvas_color": QColor(0, 0, 0, 0),  # RGBA for transparent
            "canvas_opacity": 0.0,
            "passthrough_opacity": 0.1,
            "non_passthrough_opacity": 0.8,
            "toolbar_font_size": 11,  # 默认字体大小
            # 文本相关配置
            "text_font_family": "Arial",
            "text_font_size": 16,
            "text_font_bold": False,
            "text_font_italic": False,
            "text_color": QColor(255, 0, 0, 255),  # 红色
            "text_background_color": None,  # 透明背景
            "text_border_color": None,  # 无边框
            "text_border_enabled": True,  # 边框默认启用
            "text_border_width": 1,
            "text_padding": 5
        }
        return default_config

def save_config(config):
    # Convert QColor objects to list for JSON serialization
    if isinstance(config["current_color"], QColor):
        config["current_color"] = config["current_color"].getRgb()
    if isinstance(config["canvas_color"], QColor):
        config["canvas_color"] = config["canvas_color"].getRgb()
    if isinstance(config.get("text_color"), QColor):
        config["text_color"] = config["text_color"].getRgb()
    if isinstance(config.get("text_background_color"), QColor):
        config["text_background_color"] = config["text_background_color"].getRgb()
    if isinstance(config.get("text_border_color"), QColor):
        config["text_border_color"] = config["text_border_color"].getRgb()
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


