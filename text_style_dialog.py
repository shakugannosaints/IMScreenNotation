"""
文本样式配置对话框
用于设置文本标注的字体、颜色、背景、边框等样式
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QCheckBox, QComboBox,
                             QColorDialog, QGroupBox, QFormLayout, QFrame)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt


class TextStyleDialog(QDialog):
    """文本样式配置对话框"""
    
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.parent_widget = parent  # 保存父窗口引用
        self.setWindowTitle("文本样式设置")
        self.setModal(True)
        self.setFixedSize(450, 720)  # 增加对话框高度
        
        # 设置窗口标志以确保对话框正常显示
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowModality(Qt.ApplicationModal)
        
        # 确保对话框在屏幕中央显示
        self.move_to_center()
        
        try:
            # 初始化界面
            self.setup_ui()
            
            # 应用样式表
            self.apply_stylesheet()
            
            # 加载当前设置
            self.load_current_settings()
            
        except Exception as e:
            print(f"Error initializing TextStyleDialog: {e}")
            import traceback
            traceback.print_exc()
            
    def move_to_center(self):
        """将对话框移动到屏幕中央"""
        try:
            from PyQt5.QtWidgets import QApplication
            desktop = QApplication.desktop()
            screen_geometry = desktop.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
        except Exception as e:
            print(f"Error moving dialog to center: {e}")
        
    def setup_ui(self):
        """设置界面布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)  # 增加间距
        main_layout.setContentsMargins(20, 20, 20, 20)  # 增加边距
        
        # 字体设置组
        font_group = QGroupBox("🔤 字体设置")
        font_group.setMinimumHeight(160)  # 设置最小高度
        font_layout = QFormLayout(font_group)
        font_layout.setSpacing(12)  # 增加间距
        font_layout.setContentsMargins(15, 25, 15, 15)  # 增加顶部边距
        
        # 字体族
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Arial", "Times New Roman", "Courier New", "Helvetica", 
            "Georgia", "Verdana", "Comic Sans MS", "Impact", "Lucida Console",
            "Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "FangSong"
        ])
        self.font_family_combo.setMinimumHeight(32)  # 增加高度
        # 设置下拉菜单的样式以确保显示稳定
        self.font_family_combo.setFocusPolicy(Qt.StrongFocus)
        self.font_family_combo.setAttribute(Qt.WA_MacShowFocusRect, False)
        font_layout.addRow("字体族:", self.font_family_combo)
        
        # 字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(16)
        self.font_size_spin.setMinimumHeight(32)  # 增加高度
        font_layout.addRow("字体大小:", self.font_size_spin)
        
        # 字体样式
        style_layout = QHBoxLayout()
        style_layout.setSpacing(20)  # 增加间距
        self.font_bold_check = QCheckBox("粗体")
        self.font_bold_check.setMinimumHeight(28)  # 增加高度
        self.font_italic_check = QCheckBox("斜体")
        self.font_italic_check.setMinimumHeight(28)  # 增加高度
        style_layout.addWidget(self.font_bold_check)
        style_layout.addWidget(self.font_italic_check)
        style_layout.addStretch()
        font_layout.addRow("字体样式:", style_layout)
        
        main_layout.addWidget(font_group)
        
        # 颜色设置组
        color_group = QGroupBox("🎨 颜色设置")
        color_group.setMinimumHeight(120)  # 设置最小高度
        color_layout = QFormLayout(color_group)
        color_layout.setSpacing(12)  # 增加间距
        color_layout.setContentsMargins(15, 25, 15, 15)  # 增加顶部边距
        
        # 文本颜色
        self.text_color_btn = QPushButton("选择文本颜色")
        self.text_color_btn.setMinimumHeight(36)  # 增加按钮高度
        self.text_color_btn.clicked.connect(self.choose_text_color)
        color_layout.addRow("文本颜色:", self.text_color_btn)
        
        # 背景颜色
        bg_color_layout = QHBoxLayout()
        bg_color_layout.setSpacing(10)  # 增加间距
        self.bg_color_btn = QPushButton("选择背景颜色")
        self.bg_color_btn.setMinimumHeight(36)  # 增加按钮高度
        self.bg_color_btn.clicked.connect(self.choose_background_color)
        self.bg_transparent_check = QCheckBox("透明背景")
        self.bg_transparent_check.setMinimumHeight(28)  # 增加高度
        self.bg_transparent_check.toggled.connect(self.toggle_background_transparency)
        bg_color_layout.addWidget(self.bg_color_btn)
        bg_color_layout.addWidget(self.bg_transparent_check)
        color_layout.addRow("背景颜色:", bg_color_layout)
        
        main_layout.addWidget(color_group)
        
        # 边框设置组
        border_group = QGroupBox("🔲 边框设置")
        border_group.setMinimumHeight(150)  # 设置最小高度
        border_layout = QFormLayout(border_group)
        border_layout.setSpacing(12)  # 增加间距
        border_layout.setContentsMargins(15, 25, 15, 15)  # 增加顶部边距
        
        # 边框开关
        self.border_enable_check = QCheckBox("启用边框")
        self.border_enable_check.setMinimumHeight(28)  # 增加高度
        self.border_enable_check.toggled.connect(self.toggle_border_enable)
        border_layout.addRow("", self.border_enable_check)
        
        # 边框颜色
        self.border_color_btn = QPushButton("选择边框颜色")
        self.border_color_btn.setMinimumHeight(36)  # 增加按钮高度
        self.border_color_btn.clicked.connect(self.choose_border_color)
        border_layout.addRow("边框颜色:", self.border_color_btn)
        
        # 边框宽度
        self.border_width_spin = QSpinBox()
        self.border_width_spin.setRange(1, 10)
        self.border_width_spin.setValue(1)
        self.border_width_spin.setMinimumHeight(32)  # 增加高度
        border_layout.addRow("边框宽度:", self.border_width_spin)
        
        main_layout.addWidget(border_group)
        
        # 其他设置组
        other_group = QGroupBox("⚙️ 其他设置")
        other_group.setMinimumHeight(80)  # 设置最小高度
        other_layout = QFormLayout(other_group)
        other_layout.setSpacing(12)  # 增加间距
        other_layout.setContentsMargins(15, 25, 15, 15)  # 增加顶部边距
        
        # 内边距
        self.padding_spin = QSpinBox()
        self.padding_spin.setRange(0, 20)
        self.padding_spin.setValue(5)
        self.padding_spin.setMinimumHeight(32)  # 增加高度
        other_layout.addRow("内边距:", self.padding_spin)
        
        main_layout.addWidget(other_group)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)  # 增加间距
        button_layout.setContentsMargins(0, 10, 0, 0)  # 增加顶部边距

        # 确定和取消按钮
        self.ok_btn = QPushButton("✅ 确定")
        self.ok_btn.setMinimumHeight(40)  # 增加按钮高度
        self.ok_btn.setMinimumWidth(100)  # 增加按钮宽度
        self.ok_btn.clicked.connect(self.accept_settings)
        
        self.cancel_btn = QPushButton("❌ 取消")
        self.cancel_btn.setMinimumHeight(40)  # 增加按钮高度
        self.cancel_btn.setMinimumWidth(100)  # 增加按钮宽度
        self.cancel_btn.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

        # 注意：不在这里调用 toggle_border_enable，等到加载设置后再调用
        
    def load_current_settings(self):
        """加载当前画布的文本设置"""
        try:
            # 字体设置 - 使用 getattr 提供默认值
            font_family = getattr(self.canvas, 'text_font_family', 'Arial')
            font_family_index = self.font_family_combo.findText(font_family)
            if font_family_index >= 0:
                self.font_family_combo.setCurrentIndex(font_family_index)
            
            font_size = getattr(self.canvas, 'text_font_size', 12)
            self.font_size_spin.setValue(font_size)
            
            font_bold = getattr(self.canvas, 'text_font_bold', False)
            self.font_bold_check.setChecked(font_bold)
            
            font_italic = getattr(self.canvas, 'text_font_italic', False)
            self.font_italic_check.setChecked(font_italic)
            
            # 颜色设置
            text_color = getattr(self.canvas, 'text_color', QColor(0, 0, 0))
            self.update_color_button(self.text_color_btn, text_color)
            
            # 背景色设置
            bg_color = getattr(self.canvas, 'text_background_color', None)
            if bg_color:
                self.update_color_button(self.bg_color_btn, bg_color)
                self.bg_transparent_check.setChecked(False)
            else:
                self.bg_transparent_check.setChecked(True)
            
            # 边框设置 - 暂时断开信号连接以避免在加载设置时触发toggle方法
            border_enabled = getattr(self.canvas, 'text_border_enabled', True)
            
            # 断开信号连接
            self.border_enable_check.toggled.disconnect(self.toggle_border_enable)
            self.border_enable_check.setChecked(border_enabled)
            # 重新连接信号
            self.border_enable_check.toggled.connect(self.toggle_border_enable)
            
            border_color = getattr(self.canvas, 'text_border_color', None)
            if border_color:
                self.update_color_button(self.border_color_btn, border_color)
            else:
                # 如果没有边框颜色但启用了边框，使用默认黑色
                if border_enabled:
                    default_border_color = QColor(0, 0, 0)
                    setattr(self.canvas, 'text_border_color', default_border_color)
                    self.update_color_button(self.border_color_btn, default_border_color)
                    
            border_width = getattr(self.canvas, 'text_border_width', 1)
            self.border_width_spin.setValue(border_width)
            
            # 其他设置
            padding = getattr(self.canvas, 'text_padding', 5)
            self.padding_spin.setValue(padding)
            
            # 在最后调用 toggle_border_enable 来正确设置UI状态（但不修改画布状态）
            self.toggle_border_enable()
            
        except Exception as e:
            print(f"Error loading current settings: {e}")
            # 如果加载失败，使用默认值
            self.font_family_combo.setCurrentIndex(0)
            self.font_size_spin.setValue(12)
            self.font_bold_check.setChecked(False)
            self.font_italic_check.setChecked(False)
            self.bg_transparent_check.setChecked(True)
            self.border_enable_check.setChecked(False)
            self.border_width_spin.setValue(1)
            self.padding_spin.setValue(5)
            
            # 在异常情况下也调用 toggle_border_enable
            self.toggle_border_enable()
        
    def update_color_button(self, button, color):
        """更新颜色按钮的样式"""
        if color:
            # 根据颜色亮度决定文字颜色
            brightness = (color.red() * 299 + color.green() * 587 + color.blue() * 114) / 1000
            text_color = "white" if brightness < 128 else "black"
            
            # 根据主题选择边框颜色
            is_dark = self.get_parent_theme()
            border_color = "#4a4a4a" if is_dark else "#d0d0d0"
            
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                    color: {text_color} !important;
                    border: 2px solid {border_color};
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 8px 12px;
                    min-height: 28px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    border: 2px solid #0078d4;
                    color: {text_color} !important;
                }}
                QPushButton:pressed {{
                    border: 2px solid #0078d4;
                    background-color: {color.darker().name()};
                    color: {text_color} !important;
                }}
            """)
        else:
            # 恢复默认样式，确保文本颜色正确
            is_dark = self.get_parent_theme()
            text_color = "#ffffff" if is_dark else "#333333"
            button.setStyleSheet(f"""
                QPushButton {{
                    color: {text_color} !important;
                }}
            """)
            
    def choose_text_color(self):
        """选择文本颜色"""
        try:
            from PyQt5.QtCore import QCoreApplication
            
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            color = QColorDialog.getColor(self.canvas.text_color, self, "选择文本颜色")
            if color.isValid():
                self.canvas.text_color = color
                self.update_color_button(self.text_color_btn, color)
                
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
        except Exception as e:
            print(f"Error choosing text color: {e}")
            
    def choose_background_color(self):
        """选择背景颜色"""
        try:
            from PyQt5.QtCore import QCoreApplication
            
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            current_color = self.canvas.text_background_color or QColor(255, 255, 255)
            color = QColorDialog.getColor(current_color, self, "选择背景颜色")
            if color.isValid():
                self.canvas.text_background_color = color
                self.update_color_button(self.bg_color_btn, color)
                self.bg_transparent_check.setChecked(False)
                
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
        except Exception as e:
            print(f"Error choosing background color: {e}")
            
    def choose_border_color(self):
        """选择边框颜色"""
        try:
            from PyQt5.QtCore import QCoreApplication
            
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            current_color = self.canvas.text_border_color or QColor(0, 0, 0)
            color = QColorDialog.getColor(current_color, self, "选择边框颜色")
            if color.isValid():
                self.canvas.text_border_color = color
                self.update_color_button(self.border_color_btn, color)
                
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
        except Exception as e:
            print(f"Error choosing border color: {e}")
            
    def toggle_background_transparency(self):
        """切换背景透明度"""
        if self.bg_transparent_check.isChecked():
            self.canvas.text_background_color = None
            self.bg_color_btn.setStyleSheet("")
        else:
            # 如果没有背景颜色，设置默认白色
            if not self.canvas.text_background_color:
                self.canvas.text_background_color = QColor(255, 255, 255)
                self.update_color_button(self.bg_color_btn, self.canvas.text_background_color)
                
    def toggle_border_enable(self):
        """切换边框启用状态"""
        enabled = self.border_enable_check.isChecked()
        self.border_color_btn.setEnabled(enabled)
        self.border_width_spin.setEnabled(enabled)
        
        # 立即更新canvas的边框启用状态
        setattr(self.canvas, 'text_border_enabled', enabled)
        
        if enabled:
            current_border_color = getattr(self.canvas, 'text_border_color', None)
            if not current_border_color:
                border_color = QColor(0, 0, 0)
                setattr(self.canvas, 'text_border_color', border_color)
                self.update_color_button(self.border_color_btn, border_color)
        else:
            setattr(self.canvas, 'text_border_color', None)
            self.border_color_btn.setStyleSheet("")
            
        
    def apply_settings(self):
        """应用设置到画布"""
        try:
            # 字体设置 - 使用 setattr 安全设置属性
            setattr(self.canvas, 'text_font_family', self.font_family_combo.currentText())
            setattr(self.canvas, 'text_font_size', self.font_size_spin.value())
            setattr(self.canvas, 'text_font_bold', self.font_bold_check.isChecked())
            setattr(self.canvas, 'text_font_italic', self.font_italic_check.isChecked())
            
            # 边框设置
            setattr(self.canvas, 'text_border_enabled', self.border_enable_check.isChecked())
            if self.border_enable_check.isChecked():
                setattr(self.canvas, 'text_border_width', self.border_width_spin.value())
            else:
                setattr(self.canvas, 'text_border_color', None)
                
            # 其他设置
            setattr(self.canvas, 'text_padding', self.padding_spin.value())
            
        except Exception as e:
            print(f"Error applying settings: {e}")
            import traceback
            traceback.print_exc()
        
    def accept_settings(self):
        """接受设置并关闭对话框"""
        try:
            from PyQt5.QtCore import QCoreApplication
            
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            self.apply_settings()
            
            # 触发配置保存
            self.trigger_config_save()
            
            # 强制处理所有待处理的事件
            QCoreApplication.processEvents()
            
            # 使用 accept() 而不是 close()，这样对话框会返回 Accepted 状态
            self.accept()
            
        except Exception as e:
            print(f"Error accepting settings: {e}")
            import traceback
            traceback.print_exc()
            self.close()
    
    def trigger_config_save(self):
        """触发配置保存"""
        try:
            # 查找主窗口并触发配置保存
            if self.parent_widget:
                # 如果父窗口有save_current_config方法，直接调用
                if hasattr(self.parent_widget, 'save_current_config'):
                    self.parent_widget.save_current_config()
                    print("Configuration saved via parent widget")
                # 如果父窗口是toolbar，通过main_window保存
                elif hasattr(self.parent_widget, 'main_window') and hasattr(self.parent_widget.main_window, 'save_current_config'):
                    self.parent_widget.main_window.save_current_config()
                    print("Configuration saved via main window")
                else:
                    print("Warning: Unable to find save_current_config method")
            else:
                print("Warning: No parent widget found for config save")
        except Exception as e:
            print(f"Error triggering config save: {e}")
            import traceback
            traceback.print_exc()
        
    def get_parent_theme(self):
        """获取父窗口的主题状态"""
        try:
            # 尝试从父窗口获取主题信息
            if self.parent_widget:
                # 如果父窗口有is_dark_theme属性，直接使用
                if hasattr(self.parent_widget, 'is_dark_theme'):
                    return self.parent_widget.is_dark_theme
                # 如果父窗口是主窗口，尝试获取toolbar的主题
                elif hasattr(self.parent_widget, 'toolbar') and hasattr(self.parent_widget.toolbar, 'is_dark_theme'):
                    return self.parent_widget.toolbar.is_dark_theme
            
            # 如果无法获取主题信息，默认使用浅色主题
            return False
        except Exception as e:
            print(f"Error getting parent theme: {e}")
            return False
    
    def refresh_theme(self):
        """刷新对话框主题"""
        try:
            # 重新应用样式表
            self.apply_stylesheet()
            
            # 更新所有颜色按钮
            if hasattr(self, 'text_color_btn'):
                self.update_color_button(self.text_color_btn, self.canvas.text_color)
            
            if hasattr(self, 'bg_color_btn') and self.canvas.text_background_color:
                self.update_color_button(self.bg_color_btn, self.canvas.text_background_color)
                
            if hasattr(self, 'border_color_btn') and self.canvas.text_border_color:
                self.update_color_button(self.border_color_btn, self.canvas.text_border_color)
                
        except Exception as e:
            print(f"Error refreshing theme: {e}")
    
    def apply_stylesheet(self):
        """应用现代化样式表"""
        # 根据父窗口的主题状态选择样式
        is_dark = self.get_parent_theme()
        if is_dark:
            self.setStyleSheet(self.get_dark_theme_stylesheet())
        else:
            self.setStyleSheet(self.get_light_theme_stylesheet())
    
    def get_dark_theme_stylesheet(self):
        """获取深色主题样式表"""
        return """
            QDialog {
                background-color: #2a2a2a;
                color: #ffffff;
                font-family: "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 11px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #0078d4;
                font-size: 12px;
            }
            
            QLabel {
                color: #ffffff;
                font-size: 11px;
                min-height: 20px;
            }
            
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                color: #ffffff;
                padding: 8px 12px;
                font-size: 11px;
                min-height: 28px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #0078d4;
            }
            
            QPushButton:pressed {
                background-color: #2a2a2a;
                border: 1px solid #0078d4;
            }
            
            QSpinBox {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                color: #ffffff;
                padding: 6px;
                font-size: 11px;
                min-height: 24px;
            }
            
            QSpinBox:focus {
                border: 1px solid #0078d4;
            }
            
            QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                color: #ffffff;
                padding: 6px;
                font-size: 11px;
                min-height: 24px;
            }
            
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #4a4a4a;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #4a4a4a;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ffffff;
            }
            
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                outline: none;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 6px;
                border: none;
                min-height: 20px;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #106ebe;
                color: #ffffff;
            }
            
            QCheckBox {
                color: #ffffff;
                font-size: 11px;
                spacing: 8px;
                min-height: 24px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #4a4a4a;
                border-radius: 3px;
                background-color: #3a3a3a;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #106ebe;
            }
            
            QCheckBox::indicator:checked:hover {
                background-color: #106ebe;
            }
            
            QFrame[frameShape="4"] {
                color: #4a4a4a;
                max-height: 1px;
            }
        """
    
    def get_light_theme_stylesheet(self):
        """获取浅色主题样式表"""
        return """
            QDialog {
                background-color: #ffffff;
                color: #333333;
                font-family: "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 11px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                color: #333333;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #0078d4;
                font-size: 12px;
            }
            
            QLabel {
                color: #333333;
                font-size: 11px;
                min-height: 20px;
            }
            
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                color: #333333;
                padding: 8px 12px;
                font-size: 11px;
                min-height: 28px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #0078d4;
            }
            
            QPushButton:pressed {
                background-color: #d0d0d0;
                border: 1px solid #0078d4;
            }
            
            QSpinBox {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                color: #333333;
                padding: 6px;
                font-size: 11px;
                min-height: 24px;
            }
            
            QSpinBox:focus {
                border: 1px solid #0078d4;
            }
            
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                color: #333333;
                padding: 6px;
                font-size: 11px;
                min-height: 24px;
            }
            
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #d0d0d0;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #e0e0e0;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #333333;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                outline: none;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 6px;
                border: none;
                min-height: 20px;
                color: #333333;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #106ebe;
                color: #ffffff;
            }
            
            QCheckBox {
                color: #333333;
                font-size: 11px;
                spacing: 8px;
                min-height: 24px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: #ffffff;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #106ebe;
            }
            
            QCheckBox::indicator:checked:hover {
                background-color: #106ebe;
            }
            
            QFrame[frameShape="4"] {
                color: #d0d0d0;
                max-height: 1px;
            }
        """
    
    def showEvent(self, event):
        """重写显示事件以确保对话框稳定显示"""
        super().showEvent(event)
        # 确保对话框正常显示
        self.activateWindow()
        
    def closeEvent(self, event):
        """重写关闭事件"""
        try:
            from PyQt5.QtCore import QCoreApplication
            
            # 在关闭前应用设置并保存配置
            self.apply_settings()
            self.trigger_config_save()
            
            # 确保所有事件都被处理
            QCoreApplication.processEvents()
            super().closeEvent(event)
            # 强制清理资源
            self.deleteLater()
        except Exception as e:
            print(f"Error in closeEvent: {e}")
            super().closeEvent(event)
