"""
常量定义模块
定义项目中使用的所有常量
"""

# 工具名称映射
TOOL_NAMES = {
    "line": "直线",
    "rectangle": "矩形", 
    "circle": "圆形",
    "arrow": "箭头",
    "freehand": "自由绘制",
    "filled_freehand": "填充绘制",
    "point": "点",
    "laser_pointer": "激光笔",
    "text": "文本"
}

# 默认配置值
DEFAULT_CONFIG = {
    "toolbar_font_size": 11,
    "text_font_family": "Arial",
    "text_font_size": 16,
    "text_font_bold": False,
    "text_font_italic": False,
    "text_border_enabled": True,
    "text_border_width": 1,
    "text_padding": 5
}

# 系统托盘相关常量
TRAY_TOOLTIP = "屏幕标注工具 - 点击恢复窗口"
TRAY_NOTIFICATION_TITLE = "屏幕标注工具"
TRAY_NOTIFICATION_MESSAGE = "程序已最小化到系统托盘\n点击托盘图标恢复窗口"
TRAY_NOTIFICATION_TIMEOUT = 3000

# 文件过滤器
JSON_FILE_FILTER = "JSON Files (*.json)"

# 状态栏消息超时时间（毫秒）
STATUS_MESSAGE_TIMEOUT = 2000
STATUS_MESSAGE_TIMEOUT_LONG = 3000

# 定时器间隔
TOOLBAR_CHECK_INTERVAL = 3000
