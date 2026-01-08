from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QScrollArea, QWidget,
                             QMessageBox, QGroupBox, QGridLayout, QSpinBox)
from PyQt5.QtCore import Qt
from config import save_config
from .hotkey_manager import HotkeyManager

class HotkeySettingsDialog(QDialog):
    def __init__(self, main_window, config):
        super().__init__(main_window)
        self.main_window = main_window
        self.config = config
        self.hotkey_inputs = {}
        self.font_size_spinbox = None
        
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setMinimumSize(500, 700)
        
        self.setup_ui()
        self.load_current_hotkeys()
        self.load_current_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 应用程序控制组
        app_group = QGroupBox("应用程序控制")
        app_layout = QGridLayout(app_group)
        app_hotkeys = [
            ("toggle_visibility", "显示/隐藏窗口"),
            ("toggle_passthrough", "切换鼠标穿透"),
            ("toggle_canvas_visibility", "显示/隐藏画布"),
            ("toggle_toolbar_collapse", "折叠/展开工具栏"),
            ("toggle_complete_hide", "完全隐藏窗口(可自定义)")
        ]
        
        for i, (key, label) in enumerate(app_hotkeys):
            app_layout.addWidget(QLabel(label + ":"), i, 0)
            input_field = QLineEdit()
            input_field.setPlaceholderText("例如: <ctrl>+<alt>+h")
            self.hotkey_inputs[key] = input_field
            app_layout.addWidget(input_field, i, 1)
        
        scroll_layout.addWidget(app_group)
        
        # 特殊功能说明
        special_group = QGroupBox("特殊功能")
        special_layout = QVBoxLayout(special_group)
        
        toolbar_hide_label = QLabel("🔸 工具栏完全隐藏: 请自定义快捷键")
        toolbar_hide_label.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font-weight: bold;
                padding: 8px;
                background-color: #f0f7ff;
                border: 1px solid #b3d7ff;
                border-radius: 4px;
            }
        """)
        special_layout.addWidget(toolbar_hide_label)
        
        note_label = QLabel("注意: 工具栏完全隐藏后可以通过以下方式重新显示：1.上面设置的可自定义快捷键\n2. 点击系统托盘图标")
        note_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 5px;
                background-color: #fff9e6;
                border: 1px solid #ffd700;
                border-radius: 4px;
            }
        """)
        special_layout.addWidget(note_label)
        
        scroll_layout.addWidget(special_group)
        
        # 绘制控制组
        draw_group = QGroupBox("绘制控制")
        draw_layout = QGridLayout(draw_group)
        
        draw_hotkeys = [
            ("clear_canvas", "清空画布"),
            ("undo", "撤销"),
            ("redo", "重做"),
            ("single_draw_mode", "单次绘制模式"),
            ("toggle_fill_mode", "填充开关")
        ]
        
        for i, (key, label) in enumerate(draw_hotkeys):
            draw_layout.addWidget(QLabel(label + ":"), i, 0)
            input_field = QLineEdit()
            input_field.setPlaceholderText("例如: <ctrl>+z")
            self.hotkey_inputs[key] = input_field
            draw_layout.addWidget(input_field, i, 1)
        
        scroll_layout.addWidget(draw_group)
        
        # 属性调整组
        property_group = QGroupBox("属性调整")
        property_layout = QGridLayout(property_group)
        
        property_hotkeys = [
            ("thickness_increase", "增加线条粗细"),
            ("thickness_decrease", "减少线条粗细"),
            ("drawing_opacity_increase", "增加绘制不透明度"),
            ("drawing_opacity_decrease", "减少绘制不透明度"),
            ("canvas_opacity_increase", "增加画布不透明度"),
            ("canvas_opacity_decrease", "减少画布不透明度")
        ]
        
        for i, (key, label) in enumerate(property_hotkeys):
            property_layout.addWidget(QLabel(label + ":"), i, 0)
            input_field = QLineEdit()
            if "thickness" in key:
                input_field.setPlaceholderText("例如: <ctrl>+q")
            elif "drawing_opacity" in key:
                input_field.setPlaceholderText("例如: <ctrl>+<alt>+q")
            elif "canvas_opacity" in key:
                input_field.setPlaceholderText("例如: <ctrl>+<shift>+q")
            self.hotkey_inputs[key] = input_field
            property_layout.addWidget(input_field, i, 1)
        
        scroll_layout.addWidget(property_group)
        
        # 工具选择组
        tool_group = QGroupBox("工具选择")
        tool_layout = QGridLayout(tool_group)
        tool_hotkeys = [
            ("tool_line", "直线工具"),
            ("tool_rectangle", "多边形工具"),
            ("tool_circle", "圆形工具"),
            ("tool_arrow", "箭头工具"),
            ("tool_freehand", "自由绘制"),
            ("tool_point", "点工具"),
            ("tool_laser_pointer", "激光笔"),
            ("tool_text", "文本工具"),
            ("tool_eraser", "橡皮擦工具"),
            ("tool_line_ruler", "直线标尺"),
            ("tool_circle_ruler", "圆形标尺"),
            ("tool_image", "图片工具")
        ]
        
        for i, (key, label) in enumerate(tool_hotkeys):
            tool_layout.addWidget(QLabel(label + ":"), i, 0)
            input_field = QLineEdit()
            input_field.setPlaceholderText("例如: <ctrl>+1")
            self.hotkey_inputs[key] = input_field
            tool_layout.addWidget(input_field, i, 1)
        
        scroll_layout.addWidget(tool_group)
        
        # 标尺功能组
        ruler_group = QGroupBox("标尺功能")
        ruler_layout = QGridLayout(ruler_group)
        ruler_hotkeys = [
            ("ruler_settings", "标尺设置"),
            ("ruler_calibration", "快速标定")
        ]
        
        for i, (key, label) in enumerate(ruler_hotkeys):
            ruler_layout.addWidget(QLabel(label + ":"), i, 0)
            input_field = QLineEdit()
            input_field.setPlaceholderText("例如: f6")
            self.hotkey_inputs[key] = input_field
            ruler_layout.addWidget(input_field, i, 1)
        
        scroll_layout.addWidget(ruler_group)
        
        # 界面设置组
        ui_group = QGroupBox("界面设置")
        ui_layout = QGridLayout(ui_group)
        
        # 字体大小设置
        ui_layout.addWidget(QLabel("工具栏字体大小:"), 0, 0)
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setMinimum(8)
        self.font_size_spinbox.setMaximum(24)
        self.font_size_spinbox.setValue(11)
        self.font_size_spinbox.setSuffix(" px")
        self.font_size_spinbox.setToolTip("设置工具栏按钮和文字的字体大小")
        ui_layout.addWidget(self.font_size_spinbox, 0, 1)
        
        scroll_layout.addWidget(ui_group)
        
        # 说明
        info_label = QLabel("热键格式说明:\n"
                           "- 修饰键: <ctrl>, <alt>, <shift>\n"
                           "- 功能键: <f1>, <f2>, ..., <f12>\n"
                           "- 普通键: a, b, c, ..., 1, 2, 3, ...\n"
                           "- 组合: <ctrl>+<alt>+h, <ctrl>+z, <f1>")
        info_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc; }")
        scroll_layout.addWidget(info_label)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("重置默认")
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def load_current_hotkeys(self):
        """加载当前的热键设置"""
        hotkeys = self.config.get("hotkeys", {})
        for key, input_field in self.hotkey_inputs.items():
            input_field.setText(hotkeys.get(key, ""))
    
    def load_current_settings(self):
        """加载当前的界面设置"""
        if self.font_size_spinbox:
            self.font_size_spinbox.setValue(self.config.get("toolbar_font_size", 11))
    def reset_to_defaults(self):
        """重置为默认热键""" 
        default_hotkeys = {
            "toggle_visibility": "<ctrl>+<alt>+h",
            "toggle_passthrough": "<ctrl>+<alt>+p",
            "toggle_canvas_visibility": "<ctrl>+<alt>+v",
            "toggle_toolbar_collapse": "<ctrl>+<alt>+t",
            "clear_canvas": "<ctrl>+<alt>+c",
            "undo": "<ctrl>+z",
            "redo": "<ctrl>+y",
            "single_draw_mode": "<ctrl>+<alt>+s",
            "toggle_fill_mode": "<ctrl>+<shift>+5",
            "tool_line": "<ctrl>+1",
            "tool_rectangle": "<ctrl>+2",
            "tool_circle": "<ctrl>+3",
            "tool_arrow": "<ctrl>+4",
            "tool_freehand": "<ctrl>+5",
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
        }
        
        for key, hotkey in default_hotkeys.items():
            if key in self.hotkey_inputs:
                self.hotkey_inputs[key].setText(hotkey)
    
    def validate_hotkey(self, hotkey_str):
        """验证热键格式是否正确"""
        if not hotkey_str.strip():
            return True  # 空热键是允许的
        
        # 简单的格式验证
        parts = hotkey_str.split('+')
        valid_modifiers = ['<ctrl>', '<alt>', '<shift>']
        valid_function_keys = [f'<f{i}>' for i in range(1, 13)]
        
        for part in parts:
            part = part.strip().lower()
            if part.startswith('<') and part.endswith('>'):
                if part not in valid_modifiers + valid_function_keys:
                    return False
            elif len(part) != 1 or not (part.isalnum() or part in '`-=[]\\;\',./'):
                return False
        
        return True
    
    def apply_settings(self):
        """应用设置"""
        new_hotkeys = {}
        
        # 验证所有热键
        for key, input_field in self.hotkey_inputs.items():
            hotkey = input_field.text().strip()
            if hotkey and not self.validate_hotkey(hotkey):
                QMessageBox.warning(self, "热键格式错误", 
                                  f"热键 '{hotkey}' 格式不正确。\n请参考格式说明。")
                return
            new_hotkeys[key] = hotkey
        
        # 检查重复热键
        used_hotkeys = {}
        for key, hotkey in new_hotkeys.items():
            if hotkey and hotkey in used_hotkeys:
                QMessageBox.warning(self, "重复热键", 
                                  f"热键 '{hotkey}' 被多个功能使用。\n请修改重复的热键。")
                return
            if hotkey:
                used_hotkeys[hotkey] = key
        
        # 保存配置
        self.config["hotkeys"] = new_hotkeys
        
        # 保存界面设置
        if self.font_size_spinbox:
            self.config["toolbar_font_size"] = self.font_size_spinbox.value()
        
        save_config(self.config)
        
        # 应用字体大小设置到工具栏
        if hasattr(self.main_window, 'toolbar') and self.main_window.toolbar:
            self.main_window.toolbar.update_font_size(self.config["toolbar_font_size"])
        
        # 重新注册热键
        if hasattr(self.main_window, 'hotkey_manager') and self.main_window.hotkey_manager:
            self.main_window.hotkey_manager.stop_listening()
        self.main_window.hotkey_manager = None
        
        # 重新创建热键管理器
        self.main_window.hotkey_manager = HotkeyManager(self.main_window)
        
        # 重新设置热键
        self.main_window.hotkey_handler.setup_hotkeys()
        
        # 确保hotkey_manager已创建后再启动监听
        if hasattr(self.main_window, 'hotkey_manager') and self.main_window.hotkey_manager:
            self.main_window.hotkey_manager.start_listening()
        
        QMessageBox.information(self, "设置已保存", "热键设置和界面设置已成功保存并应用。")
        self.accept()

    def closeEvent(self, event):
        """重写关闭事件以确保工具栏回到最前面"""
        try:
            # 立即确保工具栏回到最前面，并延迟再次确保
            if (hasattr(self, 'main_window') and 
                self.main_window and 
                hasattr(self.main_window, 'window_manager')):
                self.main_window.window_manager.ensure_toolbar_on_top()
                # 延迟再次确保，给对话框更多时间完全关闭
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(300, self.main_window.window_manager.ensure_toolbar_on_top)
            
            super().closeEvent(event)
        except Exception as e:
            print(f"Error in closeEvent: {e}")
            event.accept()
