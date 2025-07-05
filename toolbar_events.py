"""
工具栏事件处理模块
负责处理工具栏的各种事件和交互操作
"""

from typing import Dict, Any, Optional
from PyQt5.QtWidgets import QWidget, QColorDialog
from PyQt5.QtGui import QColor, QMouseEvent
from PyQt5.QtCore import Qt, QPoint, QEvent, QCoreApplication, QTimer


class ToolbarEventHandler:
    """工具栏事件处理器"""
    
    def __init__(self, toolbar):
        """初始化事件处理器
        
        Args:
            toolbar: 工具栏实例
        """
        self.toolbar = toolbar
        self.main_window = toolbar.main_window
        self.canvas = toolbar.canvas
    
    def handle_color_selection(self) -> None:
        """处理颜色选择事件"""
        # 创建一个独立的颜色选择对话框
        dialog: QColorDialog = QColorDialog(self.canvas.current_color, self.toolbar)
        
        # 设置对话框选项，确保它总是在最前面
        dialog.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        dialog.setOption(QColorDialog.ShowAlphaChannel, True)
        
        # 临时隐藏主窗口来避免遮挡对话框
        main_visible: bool = self.main_window.isVisible()
        if main_visible and not self.main_window.passthrough_state:
            self.main_window.hide()
        
        # 显示对话框并等待用户选择
        if dialog.exec_() == QColorDialog.Accepted:
            color: QColor = dialog.currentColor()
            if color.isValid():
                self.canvas.set_current_color(color)
                self.toolbar.update_color_button()
        
        # 恢复主窗口可见性
        if main_visible:
            self.main_window.show()
            self.main_window.activateWindow()
            self.main_window.raise_()
        
        # 确保工具栏在最前面
        self.main_window.ensure_toolbar_on_top()
    
    def handle_thickness_change(self, value: int) -> None:
        """处理线条粗细变化事件
        
        Args:
            value: 新的粗细值
        """
        self.canvas.set_current_thickness(value)
        self.toolbar.thickness_label.setText(f"粗细: {value}")
    
    def handle_drawing_opacity_change(self, value: int) -> None:
        """处理绘制不透明度变化事件
        
        Args:
            value: 新的不透明度值（0-100）
        """
        opacity: float = value / 100.0
        self.canvas.set_current_opacity(opacity)
        self.toolbar.drawing_opacity_label.setText(f"绘制不透明度: {value}%")
    
    def handle_canvas_opacity_change(self, value: int) -> None:
        """处理画布不透明度变化事件
        
        Args:
            value: 新的不透明度值（0-100）
        """
        opacity: float = value / 100.0
        self.canvas.set_canvas_opacity(opacity)
        
        # 记住当前模式下的用户设置
        if self.main_window.passthrough_state:
            self.main_window.user_passthrough_opacity = opacity
        else:
            self.main_window.user_non_passthrough_opacity = opacity
        
        self.toolbar.canvas_opacity_label.setText(f"画布不透明度: {value}%")
    
    def handle_toolbar_collapse_toggle(self) -> None:
        """处理工具栏折叠/展开切换事件"""
        # 检查可滚动内容是否存在
        if not hasattr(self.toolbar, 'scrollable_content') or not self.toolbar.scrollable_content:
            self.main_window.statusBar().showMessage("工具栏内容未初始化", 2000)
            return
            
        if not self.toolbar.is_collapsed:
            # 折叠
            self.toolbar.scrollable_content.hide()
            self.toolbar.setFixedSize(self.toolbar.toolbar_width, self.toolbar.collapsed_height)
            self.toolbar.toggle_collapse_btn.setText("🔽")
            self.toolbar.is_collapsed = True
            self.main_window.statusBar().showMessage("工具栏已折叠", 1000)
        else:
            # 展开
            self.toolbar.scrollable_content.show()
            self.toolbar.setFixedSize(self.toolbar.toolbar_width, self.toolbar.toolbar_height)
            self.toolbar.toggle_collapse_btn.setText("🔼")
            self.toolbar.is_collapsed = False
            self.main_window.statusBar().showMessage("工具栏已展开", 1000)
            
        # 确保工具栏始终在最前面
        self.main_window.ensure_toolbar_on_top()
    
    def handle_text_style_dialog(self) -> None:
        """处理文本样式设置对话框事件"""
        # 暂时停止工具栏的定时器，避免焦点冲突
        if hasattr(self.main_window, 'toolbar_timer'):
            self.main_window.toolbar_timer.stop()
        
        try:
            # 确保在主线程中执行
            from text_style_dialog import TextStyleDialog
            
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            # 创建对话框
            dialog = TextStyleDialog(self.canvas, self.toolbar)
            
            # 设置对话框属性以确保正常显示
            dialog.setWindowModality(Qt.ApplicationModal)
            dialog.setAttribute(Qt.WA_DeleteOnClose)
            dialog.raise_()
            dialog.activateWindow()
            
            # 确保对话框在主线程中执行
            result = dialog.exec_()
            
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            if result == TextStyleDialog.Accepted:
                # 对话框已经在accept时应用了设置
                print("Text style dialog accepted")
                
                # 确保配置被保存到文件
                if hasattr(self.main_window, 'save_current_config'):
                    self.main_window.save_current_config()
                    print("Configuration saved after dialog accepted")
                
        except Exception as e:
            print(f"Error opening text style dialog: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 恢复工具栏定时器
            if hasattr(self.main_window, 'toolbar_timer'):
                self.main_window.toolbar_timer.start(1000)
    
    def handle_mouse_events(self, obj: QWidget, event: QEvent) -> bool:
        """处理鼠标事件（主要用于拖动）
        
        Args:
            obj: 事件源对象
            event: 事件对象
            
        Returns:
            bool: 是否处理了事件
        """
        # 处理工具栏拖动
        if obj == self.toolbar.title_container:
            if event.type() == QEvent.MouseButtonPress:
                mouse_event = event
                if isinstance(mouse_event, QMouseEvent) and mouse_event.button() == Qt.LeftButton:
                    # 记录鼠标按下位置和拖动状态
                    self.toolbar.drag_position = mouse_event.globalPos() - self.toolbar.pos()
                    self.toolbar.dragging = True
                    return True
            elif event.type() == QEvent.MouseMove:
                mouse_event = event
                if isinstance(mouse_event, QMouseEvent) and self.toolbar.dragging and (mouse_event.buttons() & Qt.LeftButton) != 0:
                    # 计算新位置并移动工具栏
                    new_pos: QPoint = mouse_event.globalPos() - self.toolbar.drag_position
                    self.toolbar.move(new_pos)
                    return True
            elif event.type() == QEvent.MouseButtonRelease:
                mouse_event = event
                if isinstance(mouse_event, QMouseEvent) and mouse_event.button() == Qt.LeftButton:
                    # 释放拖动状态
                    self.toolbar.dragging = False
                    return True
        
        return False
    
    def update_canvas_opacity_display(self) -> None:
        """更新画布透明度显示，确保与实际画布透明度一致"""
        current_opacity: float = self.canvas.canvas_opacity
        percentage: int = int(current_opacity * 100)
        
        # 更新滑动条值（防止触发信号循环）
        self.toolbar.canvas_opacity_slider.blockSignals(True)
        self.toolbar.canvas_opacity_slider.setValue(percentage)
        self.toolbar.canvas_opacity_slider.blockSignals(False)
        
        # 更新标签显示
        self.toolbar.canvas_opacity_label.setText(f"画布不透明度: {percentage}%")
