"""
工具管理模块
处理绘图工具的选择和切换
"""
from typing import TYPE_CHECKING
from constants import TOOL_NAMES, STATUS_MESSAGE_TIMEOUT

if TYPE_CHECKING:
    from main import AnnotationTool


class ToolManager:
    """工具管理器"""
    
    def __init__(self, main_window: 'AnnotationTool'):
        self.main_window = main_window
    
    def select_tool(self, tool: str) -> None:
        """选择工具并更新按钮状态"""
        
        # 检查工具名称是否有效
        if not tool:
            print("错误: 工具名称为空")
            return
        
        # 取消所有工具按钮的选中状态
        for btn in self.main_window.toolbar.tool_button_group.values():
            btn.setChecked(False)
        
        # 选中当前工具按钮
        if tool in self.main_window.toolbar.tool_button_group:
            self.main_window.toolbar.tool_button_group[tool].setChecked(True)
            
            # 设置画布工具
            self.main_window.canvas.set_current_tool(tool)
            
            # 状态栏显示工具切换信息
            tool_name = TOOL_NAMES.get(tool, tool)
            self.main_window._status_bar.showMessage(f"已切换到{tool_name}工具", STATUS_MESSAGE_TIMEOUT)
            
            # 强制更新画布
            self.main_window.canvas.update()
        else:
            print(f"错误: 找不到工具 '{tool}' 对应的按钮")
    
    def toggle_single_draw_mode(self, checked: bool) -> None:
        """切换单次绘制模式"""
        self.main_window.canvas.single_draw_mode = checked
        
        # 检查按钮是否存在
        if not self.main_window.toolbar.single_draw_mode_btn:
            print("警告: single_draw_mode_btn 未初始化")
            return
            
        if checked:
            self.main_window.toolbar.single_draw_mode_btn.setProperty("class", "action active")
            self.main_window._status_bar.showMessage("已开启单次绘制模式", STATUS_MESSAGE_TIMEOUT)
        else:
            self.main_window.toolbar.single_draw_mode_btn.setProperty("class", "action")
            self.main_window._status_bar.showMessage("已关闭单次绘制模式", STATUS_MESSAGE_TIMEOUT)
        
        # 刷新按钮样式
        button_style = self.main_window.toolbar.single_draw_mode_btn.style()
        if button_style:
            button_style.unpolish(self.main_window.toolbar.single_draw_mode_btn)
            button_style.polish(self.main_window.toolbar.single_draw_mode_btn)
    
    def add_tool_hotkey(self, hotkey_str: str, tool_name: str) -> None:
        """添加工具切换热键"""
        # 为了避免闭包问题，创建一个副本
        tool_name_copy: str = str(tool_name)
        
        def tool_callback() -> None:
            # 确保工具名称正确传递
            print(f"触发工具热键：{hotkey_str} -> {tool_name_copy}")
            
            # 直接在回调中调用select_tool，而不是使用QTimer
            try:
                print(f"工具热键回调正在执行，切换到工具: {tool_name_copy}")
                self.select_tool(tool_name_copy)
                print(f"工具热键回调执行完毕")
            except Exception as e:
                print(f"工具热键回调执行出错: {e}")
                import traceback
                traceback.print_exc()
        
        self.main_window.hotkey_manager.register_hotkey(hotkey_str, tool_callback)
