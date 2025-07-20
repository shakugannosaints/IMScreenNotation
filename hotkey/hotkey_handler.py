"""
热键管理模块
处理热键设置和回调函数的注册
"""
from typing import TYPE_CHECKING
from .hotkey_settings import HotkeySettingsDialog
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
        
        # 注册标尺功能热键
        self._register_ruler_hotkeys(hotkeys)
        
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
                # 检查按钮是否存在
                if hasattr(self.main_window.toolbar, 'single_draw_mode_btn') and self.main_window.toolbar.single_draw_mode_btn:
                    self.main_window.toolbar.single_draw_mode_btn.click()
                else:
                    print("警告: single_draw_mode_btn 未初始化")
            self.main_window.hotkey_manager.register_hotkey(hotkeys["single_draw_mode"], toggle_single_draw)
        
        # 注册属性调整热键
        self._register_property_adjustment_hotkeys(hotkeys)
    
    def _register_property_adjustment_hotkeys(self, hotkeys: dict) -> None:
        """注册属性调整热键（粗细、绘制不透明度、画布不透明度）"""
        # 线条粗细调整热键
        if hotkeys.get("thickness_increase"):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["thickness_increase"],
                lambda: self._adjust_thickness(increase=True)
            )
        
        if hotkeys.get("thickness_decrease"):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["thickness_decrease"],
                lambda: self._adjust_thickness(increase=False)
            )
        
        # 绘制不透明度调整热键
        if hotkeys.get("drawing_opacity_increase"):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["drawing_opacity_increase"],
                lambda: self._adjust_drawing_opacity(increase=True)
            )
        
        if hotkeys.get("drawing_opacity_decrease"):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["drawing_opacity_decrease"],
                lambda: self._adjust_drawing_opacity(increase=False)
            )
        
        # 画布不透明度调整热键
        if hotkeys.get("canvas_opacity_increase"):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["canvas_opacity_increase"],
                lambda: self._adjust_canvas_opacity(increase=True)
            )
        
        if hotkeys.get("canvas_opacity_decrease"):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["canvas_opacity_decrease"],
                lambda: self._adjust_canvas_opacity(increase=False)
            )
    
    def _adjust_thickness(self, increase: bool) -> None:
        """调整线条粗细"""
        try:
            current = self.main_window.canvas.properties.current_thickness
            
            if increase:
                new_value = min(current + 1, 20)  # 最大粗细限制为20
            else:
                new_value = max(current - 1, 1)   # 最小粗细限制为1
            
            if new_value != current:
                # 更新画布属性
                self.main_window.canvas.set_current_thickness(new_value)
                
                # 更新工具栏滑块和标签
                if hasattr(self.main_window, 'toolbar') and self.main_window.toolbar:
                    if hasattr(self.main_window.toolbar, 'thickness_slider') and self.main_window.toolbar.thickness_slider:
                        self.main_window.toolbar.thickness_slider.blockSignals(True)
                        self.main_window.toolbar.thickness_slider.setValue(new_value)
                        self.main_window.toolbar.thickness_slider.blockSignals(False)
                    
                    if hasattr(self.main_window.toolbar, 'thickness_label') and self.main_window.toolbar.thickness_label:
                        self.main_window.toolbar.thickness_label.setText(f"粗细: {new_value}")
                
                # 显示状态消息
                self.main_window._status_bar.showMessage(f"线条粗细: {new_value}", STATUS_MESSAGE_TIMEOUT_LONG)
                print(f"线条粗细调整为: {new_value}")
        except Exception as e:
            print(f"调整线条粗细时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _adjust_drawing_opacity(self, increase: bool) -> None:
        """调整绘制不透明度"""
        try:
            current = self.main_window.canvas.properties.current_opacity
            current_percentage = int(current * 100)
            
            if increase:
                new_percentage = min(current_percentage + 5, 100)  # 每次增加5%
            else:
                new_percentage = max(current_percentage - 5, 0)    # 每次减少5%
            
            new_opacity = new_percentage / 100.0
            
            if abs(new_opacity - current) > 0.01:  # 避免浮点数误差
                # 更新画布属性
                self.main_window.canvas.set_current_opacity(new_opacity)
                
                # 更新工具栏滑块和标签
                if hasattr(self.main_window, 'toolbar') and self.main_window.toolbar:
                    if hasattr(self.main_window.toolbar, 'drawing_opacity_slider') and self.main_window.toolbar.drawing_opacity_slider:
                        self.main_window.toolbar.drawing_opacity_slider.blockSignals(True)
                        self.main_window.toolbar.drawing_opacity_slider.setValue(new_percentage)
                        self.main_window.toolbar.drawing_opacity_slider.blockSignals(False)
                    
                    if hasattr(self.main_window.toolbar, 'drawing_opacity_label') and self.main_window.toolbar.drawing_opacity_label:
                        self.main_window.toolbar.drawing_opacity_label.setText(f"绘制不透明度: {new_percentage}%")
                
                # 显示状态消息
                self.main_window._status_bar.showMessage(f"绘制不透明度: {new_percentage}%", STATUS_MESSAGE_TIMEOUT_LONG)
                print(f"绘制不透明度调整为: {new_percentage}%")
        except Exception as e:
            print(f"调整绘制不透明度时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _adjust_canvas_opacity(self, increase: bool) -> None:
        """调整画布不透明度"""
        try:
            current = self.main_window.canvas.properties.canvas_opacity
            current_percentage = int(current * 100)
            
            if increase:
                new_percentage = min(current_percentage + 5, 100)  # 每次增加5%
            else:
                new_percentage = max(current_percentage - 5, 0)    # 每次减少5%
            
            new_opacity = new_percentage / 100.0
            
            if abs(new_opacity - current) > 0.01:  # 避免浮点数误差
                # 更新画布属性
                self.main_window.canvas.set_canvas_opacity(new_opacity)
                
                # 记住当前模式下的用户设置
                if hasattr(self.main_window, 'passthrough_state'):
                    if self.main_window.passthrough_state:
                        self.main_window.user_passthrough_opacity = new_opacity
                    else:
                        self.main_window.user_non_passthrough_opacity = new_opacity
                
                # 更新工具栏滑块和标签
                if hasattr(self.main_window, 'toolbar') and self.main_window.toolbar:
                    if hasattr(self.main_window.toolbar, 'canvas_opacity_slider') and self.main_window.toolbar.canvas_opacity_slider:
                        self.main_window.toolbar.canvas_opacity_slider.blockSignals(True)
                        self.main_window.toolbar.canvas_opacity_slider.setValue(new_percentage)
                        self.main_window.toolbar.canvas_opacity_slider.blockSignals(False)
                    
                    if hasattr(self.main_window.toolbar, 'canvas_opacity_label') and self.main_window.toolbar.canvas_opacity_label:
                        self.main_window.toolbar.canvas_opacity_label.setText(f"画布不透明度: {new_percentage}%")
                
                # 显示状态消息
                self.main_window._status_bar.showMessage(f"画布不透明度: {new_percentage}%", STATUS_MESSAGE_TIMEOUT_LONG)
                print(f"画布不透明度调整为: {new_percentage}%")
        except Exception as e:
            print(f"调整画布不透明度时出错: {e}")
            import traceback
            traceback.print_exc()
    
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
            "tool_text": "text",
            "tool_eraser": "eraser",
            "tool_line_ruler": "line_ruler",
            "tool_circle_ruler": "circle_ruler"
        }
        
        for hotkey_name, tool_name in tool_hotkeys.items():
            if hotkeys.get(hotkey_name) and hasattr(self.main_window, 'tool_manager'):
                self.main_window.tool_manager.add_tool_hotkey(hotkeys[hotkey_name], tool_name)
    
    def _register_ruler_hotkeys(self, hotkeys: dict) -> None:
        """注册标尺功能热键"""
        # 标尺设置
        if hotkeys.get("ruler_settings") and hasattr(self.main_window, 'ruler_manager'):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["ruler_settings"], 
                self.main_window.ruler_manager.open_ruler_settings
            )
        
        # 快速标定
        if hotkeys.get("ruler_calibration") and hasattr(self.main_window, 'ruler_manager'):
            self.main_window.hotkey_manager.register_hotkey(
                hotkeys["ruler_calibration"], 
                self.main_window.ruler_manager.start_quick_calibration
            )
    
    def test_hotkey_function(self) -> None:
        """测试热键功能"""
        print("测试热键被触发!")
        self.main_window._status_bar.showMessage("热键测试成功！", STATUS_MESSAGE_TIMEOUT_LONG)
    
    def open_hotkey_settings(self) -> None:
        """打开热键设置对话框"""
        dialog: HotkeySettingsDialog = HotkeySettingsDialog(self.main_window, self.main_window.config)
        dialog.exec_()
