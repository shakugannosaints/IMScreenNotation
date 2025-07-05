"""
热键管理模块
处理热键设置和回调函数的注册
"""
from typing import TYPE_CHECKING
from hotkey_settings import HotkeySettingsDialog
from constants import STATUS_MESSAGE_TIMEOUT_LONG

if TYPE_CHECKING:
    from main import AnnotationTool


class HotkeyHandler:
    """热键处理器"""
    
    def __init__(self, main_window: 'AnnotationTool'):
        self.main_window = main_window
    
    def setup_hotkeys(self) -> None:
        """设置热键"""
        # 清空现有热键
        if hasattr(self.main_window, 'hotkey_manager') and self.main_window.hotkey_manager:
            self.main_window.hotkey_manager.hotkeys.clear()
        
        hotkeys = self.main_window.config["hotkeys"]
        print(f"设置热键配置: {hotkeys}")
        
        # 注册基本功能热键
        self._register_basic_hotkeys(hotkeys)
        
        # 注册工具切换热键
        self._register_tool_hotkeys(hotkeys)
        
        # 添加测试热键 F9
        self.main_window.hotkey_manager.register_hotkey("f9", self.test_hotkey_function)
        
        print(f"热键设置完成，共注册 {len(self.main_window.hotkey_manager.hotkeys)} 个热键")
    
    def _register_basic_hotkeys(self, hotkeys: dict) -> None:
        """注册基本功能热键"""
        # 注册每个热键时检查对应的管理器是否存在
        if hotkeys.get("toggle_visibility") and hasattr(self.main_window, 'window_manager'):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["toggle_visibility"], 
                self.main_window.window_manager.toggle_visibility
            )
        
        if hotkeys.get("toggle_passthrough") and hasattr(self.main_window, 'transparency_manager'):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["toggle_passthrough"], 
                self.main_window.transparency_manager.toggle_mouse_passthrough
            )
        
        if hotkeys.get("toggle_canvas_visibility") and hasattr(self.main_window, 'window_manager'):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["toggle_canvas_visibility"], 
                self.main_window.window_manager.toggle_canvas_visibility
            )
        
        if hotkeys.get("toggle_toolbar_collapse"):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["toggle_toolbar_collapse"], 
                self.main_window.toggle_toolbar_collapse
            )
        
        if hotkeys.get("toggle_complete_hide"):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["toggle_complete_hide"], 
                self.main_window.toggle_toolbar_complete_hide
            )
        
        if hotkeys.get("clear_canvas"):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["clear_canvas"], 
                self.main_window.canvas.clear_canvas
            )
        
        if hotkeys.get("undo"):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["undo"], 
                self.main_window.canvas.undo
            )
        
        if hotkeys.get("redo"):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["redo"], 
                self.main_window.canvas.redo
            )
        
        # 单次绘制模式热键需要特殊处理
        if hotkeys.get("single_draw_mode"):
            def toggle_single_draw():
                self.main_window.toolbar.single_draw_mode_btn.click()
            self.main_window.hotkey_manager.register_hotkey(hotkeys["single_draw_mode"], toggle_single_draw)
    
    def _register_tool_hotkeys(self, hotkeys: dict) -> None:
        """注册工具切换热键"""
        tool_hotkeys = {
            "tool_line": "line",
            "tool_rectangle": "rectangle",
            "tool_circle": "circle", 
            "tool_arrow": "arrow",
            "tool_freehand": "freehand",
            "tool_filled_freehand": "filled_freehand",
            "tool_point": "point",
            "tool_laser_pointer": "laser_pointer",
            "tool_text": "text"
        }
        
        for hotkey_name, tool_name in tool_hotkeys.items():
            if hotkeys.get(hotkey_name) and hasattr(self.main_window, 'tool_manager'):
                self.main_window.tool_manager.add_tool_hotkey(hotkeys[hotkey_name], tool_name)
    
    def test_hotkey_function(self) -> None:
        """测试热键功能"""
        print("测试热键被触发!")
        self.main_window._status_bar.showMessage("热键测试成功！", STATUS_MESSAGE_TIMEOUT_LONG)
    
    def open_hotkey_settings(self) -> None:
        """打开热键设置对话框"""
        dialog: HotkeySettingsDialog = HotkeySettingsDialog(self.main_window, self.main_window.config)
        dialog.exec_()
