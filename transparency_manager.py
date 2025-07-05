"""
透明度和穿透模式管理模块
"""
from typing import TYPE_CHECKING
from PyQt5.QtCore import Qt
from constants import STATUS_MESSAGE_TIMEOUT

if TYPE_CHECKING:
    from main import AnnotationTool


class TransparencyManager:
    """透明度管理器"""
    
    def __init__(self, main_window: 'AnnotationTool'):
        self.main_window = main_window
    
    def initialize_transparency_settings(self) -> None:
        """初始化透明度设置"""
        config = self.main_window.config
        
        # 默认透明度设置
        self.main_window.passthrough_opacity = config["passthrough_opacity"]
        self.main_window.non_passthrough_opacity = config["non_passthrough_opacity"]
        self.main_window.passthrough_state = False  # 初始状态为非穿透
        
        # 记住用户在每个模式下的透明度设置
        self.main_window.user_passthrough_opacity = config.get("passthrough_opacity", 0.1)
        self.main_window.user_non_passthrough_opacity = config.get("non_passthrough_opacity", 0.8)

        # 设置初始透明度
        if self.main_window.passthrough_state:
            self.main_window.setWindowFlags(self.main_window.windowFlags() | Qt.WindowTransparentForInput)
            if self.main_window.canvas.canvas_opacity != self.main_window.user_passthrough_opacity:
                self.main_window.canvas.set_canvas_opacity(self.main_window.user_passthrough_opacity)
            self.main_window.toolbar.toggle_passthrough_btn.setChecked(True)
            self.main_window.toolbar.toggle_passthrough_btn.setText("🖱️ 非穿透")
        else:
            if self.main_window.canvas.canvas_opacity == 0.0:
                self.main_window.canvas.set_canvas_opacity(self.main_window.user_non_passthrough_opacity)
            else:
                self.main_window.user_non_passthrough_opacity = self.main_window.canvas.canvas_opacity
            self.main_window.toolbar.toggle_passthrough_btn.setChecked(False)
            self.main_window.toolbar.toggle_passthrough_btn.setText("🖱️ 穿透")
        
        # 更新GUI滑动条以同步画布透明度
        self.main_window.toolbar.update_canvas_opacity_ui()
    
    def toggle_mouse_passthrough(self) -> None:
        """切换鼠标穿透模式"""
        current_flags = self.main_window.windowFlags()
        if self.main_window.passthrough_state:
            # Currently in pass-through mode, switch to non-pass-through
            new_flags = current_flags & ~Qt.WindowTransparentForInput
            self.main_window.setWindowFlags(new_flags)
            self.main_window.passthrough_state = False
            # 使用用户在非穿透模式下设置的透明度
            self.main_window.canvas.set_canvas_opacity(self.main_window.user_non_passthrough_opacity)
            self.main_window.toolbar.toggle_passthrough_btn.setChecked(False)
            self.main_window.toolbar.toggle_passthrough_btn.setText("🖱️ 穿透")
            self.main_window.toolbar.toggle_passthrough_btn.setProperty("class", "action")
            self.main_window._status_bar.showMessage("鼠标非穿透模式", STATUS_MESSAGE_TIMEOUT)
        else:
            # Currently in non-pass-through mode, switch to pass-through
            new_flags = current_flags | Qt.WindowTransparentForInput
            self.main_window.setWindowFlags(new_flags)
            self.main_window.passthrough_state = True
            # 使用用户在穿透模式下设置的透明度
            self.main_window.canvas.set_canvas_opacity(self.main_window.user_passthrough_opacity)
            self.main_window.toolbar.toggle_passthrough_btn.setChecked(True)
            self.main_window.toolbar.toggle_passthrough_btn.setText("🖱️ 非穿透")
            self.main_window.toolbar.toggle_passthrough_btn.setProperty("class", "action active")
            self.main_window._status_bar.showMessage("鼠标穿透模式", STATUS_MESSAGE_TIMEOUT)
        
        # 更新GUI滑动条以同步画布透明度
        self.main_window.toolbar.update_canvas_opacity_ui()
        
        # 刷新按钮样式
        if self.main_window.toolbar.toggle_passthrough_btn.style():
            self.main_window.toolbar.toggle_passthrough_btn.style().polish(
                self.main_window.toolbar.toggle_passthrough_btn
            )
        
        # 必须重新显示窗口以应用新的标志
        self.main_window.show()
        self.main_window.activateWindow()
        self.main_window.raise_()
        
        # 确保工具栏在主窗口之上
        # 直接调用确保工具栏在最前面的逻辑
        if (hasattr(self.main_window, 'toolbar') and 
            self.main_window.toolbar and 
            not self.main_window.toolbar_completely_hidden):
            self.main_window.toolbar.raise_()
            self.main_window.toolbar.activateWindow()
            self.main_window.toolbar.show()
    
    def change_canvas_opacity(self, value: int) -> None:
        """通过工具栏处理画布透明度变化"""
        self.main_window.toolbar.change_canvas_opacity(value)
    
    def update_canvas_opacity_ui(self) -> None:
        """更新GUI上的画布透明度显示，确保与实际画布透明度一致"""
        self.main_window.toolbar.update_canvas_opacity_ui()
