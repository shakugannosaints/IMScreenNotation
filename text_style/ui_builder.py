"""
文本样式UI构建器
负责构建对话框的用户界面
"""

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QSpinBox, QCheckBox, QComboBox, QGroupBox, 
                             QFormLayout, QFrame)
from PyQt5.QtCore import Qt


class TextStyleUIBuilder:
    """文本样式UI构建器"""
    
    def __init__(self, dialog):
        self.dialog = dialog
        
    def setup_ui(self):
        """设置界面布局"""
        main_layout = QVBoxLayout(self.dialog)
        main_layout.setSpacing(15)  # 增加间距
        main_layout.setContentsMargins(20, 20, 20, 20)  # 增加边距
        
        # 字体设置组
        self._create_font_group(main_layout)
        
        # 颜色设置组
        self._create_color_group(main_layout)
        
        # 边框设置组
        self._create_border_group(main_layout)
        
        # 其他设置组
        self._create_other_group(main_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 按钮区域
        self._create_button_area(main_layout)

        # 注意：不在这里调用 toggle_border_enable，等到加载设置后再调用
        
    def _create_font_group(self, main_layout):
        """创建字体设置组"""
        font_group = QGroupBox("🔤 字体设置")
        font_group.setMinimumHeight(160)  # 设置最小高度
        font_layout = QFormLayout(font_group)
        font_layout.setSpacing(12)  # 增加间距
        font_layout.setContentsMargins(15, 25, 15, 15)  # 增加顶部边距
        
        # 字体族
        self.dialog.font_family_combo = QComboBox()
        self.dialog.font_family_combo.addItems([
            "Arial", "Times New Roman", "Courier New", "Helvetica", 
            "Georgia", "Verdana", "Comic Sans MS", "Impact", "Lucida Console",
            "Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "FangSong"
        ])
        self.dialog.font_family_combo.setMinimumHeight(32)  # 增加高度
        # 设置下拉菜单的样式以确保显示稳定
        self.dialog.font_family_combo.setFocusPolicy(Qt.StrongFocus)
        self.dialog.font_family_combo.setAttribute(Qt.WA_MacShowFocusRect, False)
        font_layout.addRow("字体族:", self.dialog.font_family_combo)
        
        # 字体大小
        self.dialog.font_size_spin = QSpinBox()
        self.dialog.font_size_spin.setRange(8, 72)
        self.dialog.font_size_spin.setValue(16)
        self.dialog.font_size_spin.setMinimumHeight(32)  # 增加高度
        font_layout.addRow("字体大小:", self.dialog.font_size_spin)
        
        # 字体样式
        style_layout = QHBoxLayout()
        style_layout.setSpacing(20)  # 增加间距
        self.dialog.font_bold_check = QCheckBox("粗体")
        self.dialog.font_bold_check.setMinimumHeight(28)  # 增加高度
        self.dialog.font_italic_check = QCheckBox("斜体")
        self.dialog.font_italic_check.setMinimumHeight(28)  # 增加高度
        style_layout.addWidget(self.dialog.font_bold_check)
        style_layout.addWidget(self.dialog.font_italic_check)
        style_layout.addStretch()
        font_layout.addRow("字体样式:", style_layout)
        
        main_layout.addWidget(font_group)
        
    def _create_color_group(self, main_layout):
        """创建颜色设置组"""
        color_group = QGroupBox("🎨 颜色设置")
        color_group.setMinimumHeight(120)  # 设置最小高度
        color_layout = QFormLayout(color_group)
        color_layout.setSpacing(12)  # 增加间距
        color_layout.setContentsMargins(15, 25, 15, 15)  # 增加顶部边距
        
        # 文本颜色
        self.dialog.text_color_btn = QPushButton("选择文本颜色")
        self.dialog.text_color_btn.setMinimumHeight(36)  # 增加按钮高度
        self.dialog.text_color_btn.clicked.connect(self.dialog.event_handler.choose_text_color)
        color_layout.addRow("文本颜色:", self.dialog.text_color_btn)
        
        # 背景颜色
        bg_color_layout = QHBoxLayout()
        bg_color_layout.setSpacing(10)  # 增加间距
        self.dialog.bg_color_btn = QPushButton("选择背景颜色")
        self.dialog.bg_color_btn.setMinimumHeight(36)  # 增加按钮高度
        self.dialog.bg_color_btn.clicked.connect(self.dialog.event_handler.choose_background_color)
        self.dialog.bg_transparent_check = QCheckBox("透明背景")
        self.dialog.bg_transparent_check.setMinimumHeight(28)  # 增加高度
        self.dialog.bg_transparent_check.toggled.connect(self.dialog.event_handler.toggle_background_transparency)
        bg_color_layout.addWidget(self.dialog.bg_color_btn)
        bg_color_layout.addWidget(self.dialog.bg_transparent_check)
        color_layout.addRow("背景颜色:", bg_color_layout)
        
        main_layout.addWidget(color_group)
        
    def _create_border_group(self, main_layout):
        """创建边框设置组"""
        border_group = QGroupBox("🔲 边框设置")
        border_group.setMinimumHeight(150)  # 设置最小高度
        border_layout = QFormLayout(border_group)
        border_layout.setSpacing(12)  # 增加间距
        border_layout.setContentsMargins(15, 25, 15, 15)  # 增加顶部边距
        
        # 边框开关
        self.dialog.border_enable_check = QCheckBox("启用边框")
        self.dialog.border_enable_check.setMinimumHeight(28)  # 增加高度
        self.dialog.border_enable_check.toggled.connect(self.dialog.event_handler.toggle_border_enable)
        border_layout.addRow("", self.dialog.border_enable_check)
        
        # 边框颜色
        self.dialog.border_color_btn = QPushButton("选择边框颜色")
        self.dialog.border_color_btn.setMinimumHeight(36)  # 增加按钮高度
        self.dialog.border_color_btn.clicked.connect(self.dialog.event_handler.choose_border_color)
        border_layout.addRow("边框颜色:", self.dialog.border_color_btn)
        
        # 边框宽度
        self.dialog.border_width_spin = QSpinBox()
        self.dialog.border_width_spin.setRange(1, 10)
        self.dialog.border_width_spin.setValue(1)
        self.dialog.border_width_spin.setMinimumHeight(32)  # 增加高度
        border_layout.addRow("边框宽度:", self.dialog.border_width_spin)
        
        main_layout.addWidget(border_group)
        
    def _create_other_group(self, main_layout):
        """创建其他设置组"""
        other_group = QGroupBox("⚙️ 其他设置")
        other_group.setMinimumHeight(80)  # 设置最小高度
        other_layout = QFormLayout(other_group)
        other_layout.setSpacing(12)  # 增加间距
        other_layout.setContentsMargins(15, 25, 15, 15)  # 增加顶部边距
        
        # 内边距
        self.dialog.padding_spin = QSpinBox()
        self.dialog.padding_spin.setRange(0, 20)
        self.dialog.padding_spin.setValue(5)
        self.dialog.padding_spin.setMinimumHeight(32)  # 增加高度
        other_layout.addRow("内边距:", self.dialog.padding_spin)
        
        main_layout.addWidget(other_group)
        
    def _create_button_area(self, main_layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)  # 增加间距
        button_layout.setContentsMargins(0, 10, 0, 0)  # 增加顶部边距

        # 确定和取消按钮
        self.dialog.ok_btn = QPushButton("✅ 确定")
        self.dialog.ok_btn.setMinimumHeight(40)  # 增加按钮高度
        self.dialog.ok_btn.setMinimumWidth(100)  # 增加按钮宽度
        self.dialog.ok_btn.clicked.connect(self.dialog.event_handler.accept_settings)
        
        self.dialog.cancel_btn = QPushButton("❌ 取消")
        self.dialog.cancel_btn.setMinimumHeight(40)  # 增加按钮高度
        self.dialog.cancel_btn.setMinimumWidth(100)  # 增加按钮宽度
        self.dialog.cancel_btn.clicked.connect(self.dialog.close)
        button_layout.addStretch()
        button_layout.addWidget(self.dialog.ok_btn)
        button_layout.addWidget(self.dialog.cancel_btn)

        main_layout.addLayout(button_layout)
