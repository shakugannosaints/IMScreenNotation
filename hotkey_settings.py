from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QScrollArea, QWidget,
                             QMessageBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt
from config import save_config

class HotkeySettingsDialog(QDialog):
    def __init__(self, main_window, config):
        super().__init__(main_window)
        self.main_window = main_window
        self.config = config
        self.hotkey_inputs = {}
        
        self.setWindowTitle("热键设置")
        self.setModal(True)
        self.setMinimumSize(500, 600)
        
        self.setup_ui()
        self.load_current_hotkeys()
    
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
            ("toggle_toolbar_collapse", "折叠/展开工具栏")
        ]
        
        for i, (key, label) in enumerate(app_hotkeys):
            app_layout.addWidget(QLabel(label + ":"), i, 0)
            input_field = QLineEdit()
            input_field.setPlaceholderText("例如: <ctrl>+<alt>+h")
            self.hotkey_inputs[key] = input_field
            app_layout.addWidget(input_field, i, 1)
        
        scroll_layout.addWidget(app_group)
        
        # 绘制控制组
        draw_group = QGroupBox("绘制控制")
        draw_layout = QGridLayout(draw_group)
        
        draw_hotkeys = [
            ("clear_canvas", "清空画布"),
            ("undo", "撤销"),
            ("redo", "重做"),
            ("single_draw_mode", "单次绘制模式")
        ]
        
        for i, (key, label) in enumerate(draw_hotkeys):
            draw_layout.addWidget(QLabel(label + ":"), i, 0)
            input_field = QLineEdit()
            input_field.setPlaceholderText("例如: <ctrl>+z")
            self.hotkey_inputs[key] = input_field
            draw_layout.addWidget(input_field, i, 1)
        
        scroll_layout.addWidget(draw_group)
        
        # 工具选择组
        tool_group = QGroupBox("工具选择")
        tool_layout = QGridLayout(tool_group)
        tool_hotkeys = [
            ("tool_line", "直线工具"),
            ("tool_rectangle", "矩形工具"),
            ("tool_circle", "圆形工具"),
            ("tool_arrow", "箭头工具"),
            ("tool_freehand", "自由绘制"),
            ("tool_filled_freehand", "填充绘制"),
            ("tool_point", "点工具"),
            ("tool_laser_pointer", "激光笔")
        ]
        
        for i, (key, label) in enumerate(tool_hotkeys):
            tool_layout.addWidget(QLabel(label + ":"), i, 0)
            input_field = QLineEdit()
            input_field.setPlaceholderText("例如: <ctrl>+1")
            self.hotkey_inputs[key] = input_field
            tool_layout.addWidget(input_field, i, 1)
        
        scroll_layout.addWidget(tool_group)
        
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
    def reset_to_defaults(self):
        """重置为默认热键"""
        default_hotkeys = {
            "toggle_visibility": "<ctrl>+<alt>+h",
            "toggle_passthrough": "<ctrl>+<alt>+p",
            "toggle_canvas_visibility": "<ctrl>+<alt>+v",
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
            "tool_laser_pointer": "<ctrl>+7"
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
        save_config(self.config)
        
        # 重新注册热键
        self.main_window.hotkey_manager.stop_listening()
        self.main_window.hotkey_manager = None
        self.main_window.setup_hotkeys()
        self.main_window.hotkey_manager.start_listening()
        
        QMessageBox.information(self, "设置已保存", "热键设置已成功保存并应用。")
        self.accept()
