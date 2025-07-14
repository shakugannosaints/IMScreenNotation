"""
标尺设置对话框 - 用于设置标尺的标定参数
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QComboBox, QPushButton, QDoubleSpinBox,
                            QSpinBox, QCheckBox, QGroupBox, QFormLayout,
                            QDialogButtonBox, QTabWidget, QWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QDoubleValidator, QIntValidator


class RulerSettingsDialog(QDialog):
    """标尺设置对话框"""
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("标尺设置")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        # 设置窗口标志以确保对话框正常显示并保持焦点
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowModality(Qt.ApplicationModal)
        
        # 初始化焦点保护定时器
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self.ensure_focus)
        self.focus_timer.setSingleShot(False)
        
        # 默认设置
        self.settings = {
            'pixel_length': 100,
            'real_length': 10.0,
            'unit': 'cm',
            'show_ticks': True,
            'tick_interval': 1.0,  # 改为刻度间隔
            'show_diameter_line': True
        }
        
        # 应用当前设置
        if current_settings:
            self.settings.update(current_settings)
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 标定设置选项卡
        calibration_tab = QWidget()
        self.setup_calibration_tab(calibration_tab)
        tab_widget.addTab(calibration_tab, "标定设置")
        
        # 显示设置选项卡
        display_tab = QWidget()
        self.setup_display_tab(display_tab)
        tab_widget.addTab(display_tab, "显示设置")
        
        layout.addWidget(tab_widget)
        
        # 按钮组
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Reset
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Reset).clicked.connect(self.reset_settings)
        
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def setup_calibration_tab(self, tab):
        """设置标定选项卡"""
        layout = QVBoxLayout()
        
        # 标定说明
        info_label = QLabel("请设置一个已知长度的参考标准，用于标定标尺。")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 12px; padding: 10px;")
        layout.addWidget(info_label)
        
        # 标定参数组
        calibration_group = QGroupBox("标定参数")
        calibration_layout = QFormLayout()
        
        # 像素长度
        self.pixel_length_spin = QSpinBox()
        self.pixel_length_spin.setRange(1, 9999)
        self.pixel_length_spin.setSuffix(" px")
        self.pixel_length_spin.setToolTip("参考标准在屏幕上的像素长度")
        calibration_layout.addRow("像素长度:", self.pixel_length_spin)
        
        # 实际长度
        self.real_length_spin = QDoubleSpinBox()
        self.real_length_spin.setRange(0.01, 9999.99)
        self.real_length_spin.setDecimals(2)
        self.real_length_spin.setSingleStep(0.1)
        self.real_length_spin.setToolTip("参考标准的实际长度")
        calibration_layout.addRow("实际长度:", self.real_length_spin)
        
        # 单位
        self.unit_edit = QLineEdit()
        self.unit_edit.setPlaceholderText("例如: cm, mm, m, in, ft 等")
        self.unit_edit.setToolTip("长度单位（可自定义输入）")
        calibration_layout.addRow("单位:", self.unit_edit)
        
        calibration_group.setLayout(calibration_layout)
        layout.addWidget(calibration_group)
        
        # 使用说明
        usage_label = QLabel(
            "使用方法:\n"
            "1. 在屏幕上找到一个已知实际长度的物体\n"
            "2. 测量该物体在屏幕上的像素长度\n"
            "3. 在上方输入对应的像素长度和实际长度\n"
            "4. 选择合适的单位\n"
            "5. 点击确定完成标定"
        )
        usage_label.setWordWrap(True)
        usage_label.setStyleSheet("color: #666; font-size: 11px; padding: 10px; background: #f5f5f5; border-radius: 5px;")
        layout.addWidget(usage_label)
        
        tab.setLayout(layout)
    
    def setup_display_tab(self, tab):
        """设置显示选项卡"""
        layout = QVBoxLayout()
        
        # 直线标尺显示设置
        line_group = QGroupBox("直线标尺显示")
        line_layout = QFormLayout()
        
        # 显示刻度
        self.show_ticks_check = QCheckBox("显示刻度线")
        self.show_ticks_check.setToolTip("是否在直线标尺上显示刻度线")
        line_layout.addRow(self.show_ticks_check)
        
        # 刻度间隔
        self.tick_interval_spin = QDoubleSpinBox()
        self.tick_interval_spin.setRange(0.01, 1000.0)
        self.tick_interval_spin.setDecimals(2)
        self.tick_interval_spin.setSingleStep(0.1)
        self.tick_interval_spin.setToolTip("刻度间隔（实际长度单位）")
        line_layout.addRow("刻度间隔:", self.tick_interval_spin)
        
        line_group.setLayout(line_layout)
        layout.addWidget(line_group)
        
        # 圆形标尺显示设置
        circle_group = QGroupBox("圆形标尺显示")
        circle_layout = QFormLayout()
        
        # 显示直径线
        self.show_diameter_line_check = QCheckBox("显示直径线")
        self.show_diameter_line_check.setToolTip("是否在圆形标尺上显示直径线")
        circle_layout.addRow(self.show_diameter_line_check)
        
        circle_group.setLayout(circle_layout)
        layout.addWidget(circle_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        tab.setLayout(layout)
    
    def load_settings(self):
        """加载当前设置到界面"""
        self.pixel_length_spin.setValue(int(self.settings['pixel_length']))
        self.real_length_spin.setValue(float(self.settings['real_length']))
        self.unit_edit.setText(self.settings['unit'])
        self.show_ticks_check.setChecked(self.settings['show_ticks'])
        self.tick_interval_spin.setValue(float(self.settings.get('tick_interval', 1.0)))
        self.show_diameter_line_check.setChecked(self.settings['show_diameter_line'])
    
    def get_settings(self):
        """获取当前设置"""
        return {
            'pixel_length': self.pixel_length_spin.value(),
            'real_length': self.real_length_spin.value(),
            'unit': self.unit_edit.text().strip() or 'cm',
            'show_ticks': self.show_ticks_check.isChecked(),
            'tick_interval': self.tick_interval_spin.value(),
            'show_diameter_line': self.show_diameter_line_check.isChecked()
        }
    
    def reset_settings(self):
        """重置为默认设置"""
        self.pixel_length_spin.setValue(100)
        self.real_length_spin.setValue(10.0)
        self.unit_edit.setText('cm')
        self.show_ticks_check.setChecked(True)
        self.tick_interval_spin.setValue(1.0)
        self.show_diameter_line_check.setChecked(True)
    
    def accept(self):
        """确认设置"""
        # 验证输入
        if self.pixel_length_spin.value() <= 0:
            return
        if self.real_length_spin.value() <= 0:
            return
        
        # 更新设置 - 在对话框关闭前保存设置
        self.settings = self.get_settings()
        super().accept()
    
    def ensure_focus(self):
        """确保对话框保持焦点"""
        if self.isVisible() and not self.isActiveWindow():
            self.raise_()
            self.activateWindow()
    
    def showEvent(self, event):
        """重写显示事件以确保对话框保持焦点"""
        super().showEvent(event)
        # 确保对话框获得焦点
        self.raise_()
        self.activateWindow()
        
        # 暂停主窗口的工具栏定时器，避免焦点冲突
        parent_window = self.parent()
        if parent_window:
            toolbar_timer = getattr(parent_window, 'toolbar_timer', None)
            if toolbar_timer and toolbar_timer.isActive():
                self.toolbar_timer_was_active = True
                toolbar_timer.stop()
            else:
                self.toolbar_timer_was_active = False
        else:
            self.toolbar_timer_was_active = False
        
        # 启动焦点保护定时器
        self.focus_timer.start(500)  # 每500毫秒检查一次焦点
    
    def closeEvent(self, event):
        """重写关闭事件以恢复工具栏定时器"""
        # 停止焦点保护定时器
        self.focus_timer.stop()
        
        # 恢复工具栏定时器（如果之前是活动的）
        parent_window = self.parent()
        if (hasattr(self, 'toolbar_timer_was_active') and 
            self.toolbar_timer_was_active and
            parent_window):
            toolbar_timer = getattr(parent_window, 'toolbar_timer', None)
            passthrough_state = getattr(parent_window, 'passthrough_state', False)
            if toolbar_timer and not passthrough_state:
                toolbar_timer.start(1000)  # 减少延迟到1秒重新启动定时器
        
        # 立即确保工具栏回到最前面，并延迟再次确保
        if parent_window and hasattr(parent_window, 'window_manager'):
            parent_window.window_manager.ensure_toolbar_on_top()  # type: ignore
            # 延迟再次确保，给对话框更多时间完全关闭
            QTimer.singleShot(100, parent_window.window_manager.ensure_toolbar_on_top)  # type: ignore
            QTimer.singleShot(500, parent_window.window_manager.ensure_toolbar_on_top)  # type: ignore
        
        super().closeEvent(event)


class QuickRulerCalibrationDialog(QDialog):
    """快速标尺标定对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("快速标定")
        self.setFixedSize(350, 200)
        self.setModal(True)
        
        # 设置窗口标志以确保对话框正常显示并保持焦点
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowModality(Qt.ApplicationModal)
        
        # 初始化焦点保护定时器
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self.ensure_focus)
        self.focus_timer.setSingleShot(False)
        
        # 初始化标定数据
        self.calibration_data = (None, None)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout()
        
        # 说明
        info_label = QLabel("快速标定流程：\n1. 输入已知物体的实际长度和单位\n2. 点击确定后，在屏幕上绘制该物体的直线\n3. 系统将自动计算像素与实际长度的比例")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 12px; padding: 10px; background: #f0f7ff; border: 1px solid #b3d7ff; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # 输入区域
        input_layout = QFormLayout()
        
        # 实际长度
        self.real_length_edit = QLineEdit()
        self.real_length_edit.setPlaceholderText("例如: 10.5")
        input_layout.addRow("实际长度:", self.real_length_edit)
        
        # 单位
        self.unit_edit = QLineEdit()
        self.unit_edit.setText("cm")
        self.unit_edit.setPlaceholderText("例如: cm, mm, m, in, ft 等")
        input_layout.addRow("单位:", self.unit_edit)
        
        layout.addLayout(input_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_calibration_data(self):
        """获取标定数据"""
        try:
            real_length = float(self.real_length_edit.text())
            unit = self.unit_edit.text().strip() or 'cm'
            return real_length, unit
        except ValueError:
            return None, None
    
    def accept(self):
        """确认标定"""
        real_length, unit = self.get_calibration_data()
        if real_length is None or real_length <= 0:
            return
        
        # 保存标定数据
        self.calibration_data = (real_length, unit)
        super().accept()
    
    def ensure_focus(self):
        """确保对话框保持焦点"""
        if self.isVisible() and not self.isActiveWindow():
            self.raise_()
            self.activateWindow()
    
    def showEvent(self, event):
        """重写显示事件以确保对话框保持焦点"""
        super().showEvent(event)
        # 确保对话框获得焦点
        self.raise_()
        self.activateWindow()
        
        # 暂停主窗口的工具栏定时器，避免焦点冲突
        parent_window = self.parent()
        if parent_window:
            toolbar_timer = getattr(parent_window, 'toolbar_timer', None)
            if toolbar_timer and toolbar_timer.isActive():
                self.toolbar_timer_was_active = True
                toolbar_timer.stop()
            else:
                self.toolbar_timer_was_active = False
        else:
            self.toolbar_timer_was_active = False
        
        # 启动焦点保护定时器
        self.focus_timer.start(500)  # 每500毫秒检查一次焦点
    
    def closeEvent(self, event):
        """重写关闭事件以恢复工具栏定时器"""
        # 停止焦点保护定时器
        self.focus_timer.stop()
        
        # 恢复工具栏定时器（如果之前是活动的）
        parent_window = self.parent()
        if (hasattr(self, 'toolbar_timer_was_active') and 
            self.toolbar_timer_was_active and
            parent_window):
            toolbar_timer = getattr(parent_window, 'toolbar_timer', None)
            passthrough_state = getattr(parent_window, 'passthrough_state', False)
            if toolbar_timer and not passthrough_state:
                toolbar_timer.start(1000)  # 减少延迟到1秒重新启动定时器
        
        # 立即确保工具栏回到最前面，并延迟再次确保
        if parent_window and hasattr(parent_window, 'window_manager'):
            parent_window.window_manager.ensure_toolbar_on_top()  # type: ignore
            # 延迟再次确保，给对话框更多时间完全关闭
            QTimer.singleShot(100, parent_window.window_manager.ensure_toolbar_on_top)  # type: ignore
            QTimer.singleShot(500, parent_window.window_manager.ensure_toolbar_on_top)  # type: ignore
        
        super().closeEvent(event)
