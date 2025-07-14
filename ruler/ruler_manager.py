"""
标尺管理器 - 管理标尺功能的核心类
"""
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor
from .ruler_settings import RulerSettingsDialog, QuickRulerCalibrationDialog


class RulerManager(QObject):
    """标尺管理器"""
    
    # 信号
    ruler_settings_changed = pyqtSignal(dict)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.canvas = main_window.canvas
        
        # 标尺设置
        self.ruler_settings = {
            'pixel_length': 100,
            'real_length': 10.0,
            'unit': 'cm',
            'show_ticks': True,
            'tick_interval': 1.0,  # 刻度间隔
            'show_diameter_line': True
        }
        
        # 标尺模式状态
        self.ruler_mode = False
        self.ruler_type = 'line'  # 'line' 或 'circle'
        self.calibration_mode = False
        
        # 临时标定数据
        self.temp_calibration_line = None
        
    def open_ruler_settings(self):
        """打开标尺设置对话框"""
        dialog = RulerSettingsDialog(self.main_window, self.ruler_settings)
        if dialog.exec_() == RulerSettingsDialog.Accepted:
            self.ruler_settings = dialog.settings  # 直接从settings属性获取，避免访问已删除的控件
            self.ruler_settings_changed.emit(self.ruler_settings)
            self.main_window._status_bar.showMessage("标尺设置已更新", 2000)
    
    def start_quick_calibration(self):
        """开始快速标定"""
        # 首先弹出对话框让用户输入实际长度
        dialog = QuickRulerCalibrationDialog(self.main_window)
        if dialog.exec_() == QuickRulerCalibrationDialog.Accepted:
            real_length, unit = dialog.calibration_data
            if real_length and real_length > 0:
                # 保存用户输入的数据
                self.pending_calibration_data = (real_length, unit)
                
                # 切换到直线工具
                self.main_window.select_tool('line')
                self.calibration_mode = True
                self.main_window._status_bar.showMessage(
                    f"请在屏幕上画一条长度为 {real_length}{unit} 的直线进行标定", 5000
                )
                
                # 连接画布信号，监听绘制完成
                self.canvas.state_manager.shape_added.connect(self.on_calibration_shape_added)
            else:
                self.main_window._status_bar.showMessage("标定取消", 2000)
        else:
            self.main_window._status_bar.showMessage("标定取消", 2000)
    
    def on_calibration_shape_added(self, shape):
        """标定形状绘制完成"""
        if not self.calibration_mode:
            return
        
        # 断开信号
        try:
            self.canvas.state_manager.shape_added.disconnect(self.on_calibration_shape_added)
        except TypeError:
            # 如果信号未连接，忽略错误
            pass
        
        # 检查是否是直线
        if shape.__class__.__name__ != 'Line':
            self.calibration_mode = False
            QMessageBox.warning(self.main_window, "标定失败", "请绘制一条直线进行标定")
            return
        
        # 保存临时标定线
        self.temp_calibration_line = shape
        
        # 计算像素长度
        import math
        dx = shape.end_point.x() - shape.start_point.x()
        dy = shape.end_point.y() - shape.start_point.y()
        pixel_length = math.sqrt(dx * dx + dy * dy)
        
        # 使用之前保存的标定数据
        if hasattr(self, 'pending_calibration_data') and self.pending_calibration_data:
            real_length, unit = self.pending_calibration_data
            
            # 更新标尺设置
            self.ruler_settings['pixel_length'] = int(pixel_length)
            self.ruler_settings['real_length'] = real_length
            self.ruler_settings['unit'] = unit
            
            # 删除临时标定线
            if self.temp_calibration_line in self.canvas.shapes:
                self.canvas.shapes.remove(self.temp_calibration_line)
                self.canvas.update()
            
            self.ruler_settings_changed.emit(self.ruler_settings)
            self.main_window._status_bar.showMessage(
                f"标定完成: {pixel_length:.0f}px = {real_length}{unit}", 3000
            )
        else:
            # 删除临时标定线
            if self.temp_calibration_line in self.canvas.shapes:
                self.canvas.shapes.remove(self.temp_calibration_line)
                self.canvas.update()
            self.main_window._status_bar.showMessage("标定失败：缺少标定数据", 2000)
        
        self.calibration_mode = False
        self.temp_calibration_line = None
        # 清除待标定数据
        if hasattr(self, 'pending_calibration_data'):
            delattr(self, 'pending_calibration_data')
    
    def toggle_ruler_mode(self):
        """切换标尺模式"""
        self.ruler_mode = not self.ruler_mode
        if self.ruler_mode:
            self.main_window._status_bar.showMessage("标尺模式已开启", 2000)
        else:
            self.main_window._status_bar.showMessage("标尺模式已关闭", 2000)
        
        return self.ruler_mode
    
    def set_ruler_type(self, ruler_type):
        """设置标尺类型"""
        if ruler_type in ['line', 'circle']:
            self.ruler_type = ruler_type
            if ruler_type == 'line':
                self.main_window.select_tool('line_ruler')
            else:
                self.main_window.select_tool('circle_ruler')
            
            self.main_window._status_bar.showMessage(
                f"切换到{'直线' if ruler_type == 'line' else '圆形'}标尺", 2000
            )
    
    def get_ruler_settings(self):
        """获取当前标尺设置"""
        return self.ruler_settings.copy()
    
    def update_ruler_settings(self, settings):
        """更新标尺设置"""
        self.ruler_settings.update(settings)
        self.ruler_settings_changed.emit(self.ruler_settings)
    
    def create_line_ruler(self, start_point, end_point):
        """创建直线标尺"""
        from shapes.ruler import LineRuler
        
        ruler = LineRuler(
            start_point=start_point,
            end_point=end_point,
            pixel_length=self.ruler_settings['pixel_length'],
            real_length=self.ruler_settings['real_length'],
            unit=self.ruler_settings['unit'],
            color=self.canvas.properties.current_color,
            thickness=self.canvas.properties.current_thickness,
            opacity=self.canvas.properties.current_opacity
        )
        
        # 设置刻度相关属性
        ruler.show_ticks = self.ruler_settings.get('show_ticks', True)
        ruler.tick_interval = self.ruler_settings.get('tick_interval', 1.0)
        
        return ruler
    
    def create_circle_ruler(self, center_point, radius):
        """创建圆形标尺"""
        from shapes.ruler import CircleRuler
        
        ruler = CircleRuler(
            center_point=center_point,
            radius=radius,
            pixel_length=self.ruler_settings['pixel_length'],
            real_length=self.ruler_settings['real_length'],
            unit=self.ruler_settings['unit'],
            color=self.canvas.properties.current_color,
            thickness=self.canvas.properties.current_thickness,
            opacity=self.canvas.properties.current_opacity
        )
        
        # 设置显示相关属性
        ruler.show_diameter_line = self.ruler_settings.get('show_diameter_line', True)
        
        return ruler
    
    def get_scale_info(self):
        """获取当前缩放信息"""
        scale_factor = self.ruler_settings['real_length'] / self.ruler_settings['pixel_length']
        return f"当前标尺: {self.ruler_settings['pixel_length']}px = {self.ruler_settings['real_length']}{self.ruler_settings['unit']} (1px = {scale_factor:.4f}{self.ruler_settings['unit']})"
