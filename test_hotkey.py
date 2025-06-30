#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试热键管理器的简单脚本
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from hotkey_manager import HotkeyManager

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("热键测试")
        self.setGeometry(300, 300, 400, 200)
        
        # 创建界面
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.status_label = QLabel("按下热键进行测试...")
        self.info_label = QLabel("注册的热键:\nCtrl+1: 测试1\nCtrl+2: 测试2\nAlt+A: 测试A")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.info_label)
        
        # 创建热键管理器
        self.hotkey_manager = HotkeyManager(self)
        
        # 注册测试热键
        self.hotkey_manager.register_hotkey("ctrl+1", self.on_hotkey_1)
        self.hotkey_manager.register_hotkey("ctrl+2", self.on_hotkey_2) 
        self.hotkey_manager.register_hotkey("alt+a", self.on_hotkey_a)
        
        # 启动热键监听
        self.hotkey_manager.start_listening()
        
        # 定时更新状态信息
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(100)  # 每100ms更新一次
    
    def on_hotkey_1(self):
        """Ctrl+1 热键回调"""
        self.status_label.setText("触发了 Ctrl+1 热键！")
        print("Ctrl+1 被触发")
    
    def on_hotkey_2(self):
        """Ctrl+2 热键回调"""
        self.status_label.setText("触发了 Ctrl+2 热键！")
        print("Ctrl+2 被触发")
        
    def on_hotkey_a(self):
        """Alt+A 热键回调"""
        self.status_label.setText("触发了 Alt+A 热键！")
        print("Alt+A 被触发")
    
    def update_status(self):
        """更新状态信息"""
        try:
            info = self.hotkey_manager.get_pressed_keys_info()
            if info['pressed_keys'] or info['modifiers']:
                status_text = f"当前按键: {info['pressed_keys']}\n修饰键: {info['modifiers']}"
                if info['last_triggered']:
                    status_text += f"\n最后触发: {info['last_triggered']}"
                self.info_label.setText(status_text)
        except Exception as e:
            print(f"更新状态失败: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.hotkey_manager.stop_listening()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("热键测试程序已启动")
    print("尝试按下以下热键:")
    print("  Ctrl+1")
    print("  Ctrl+2") 
    print("  Alt+A")
    print("关闭窗口可退出程序")
    
    sys.exit(app.exec_())
