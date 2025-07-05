"""
工具栏组件创建模块
负责创建和设置工具栏的各种界面组件
"""

from typing import Dict, List, Tuple
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QSlider, QLabel, QFrame)
from PyQt5.QtCore import Qt


class ToolbarWidgetBuilder:
    """工具栏组件构建器"""
    
    def __init__(self, toolbar):
        """初始化组件构建器
        
        Args:
            toolbar: 工具栏实例
        """
        self.toolbar = toolbar
        self.main_window = toolbar.main_window
        self.canvas = toolbar.canvas
    
    def setup_title_section(self, main_layout: QVBoxLayout) -> None:
        """设置标题区域"""
        self.toolbar.title_container = QWidget()
        self.toolbar.title_container.setObjectName("titleContainer")
        self.toolbar.title_container.setCursor(Qt.SizeAllCursor)
        title_layout = QHBoxLayout(self.toolbar.title_container)
        title_layout.setContentsMargins(12, 8, 12, 8)
        title_layout.setSpacing(8)
        
        # 标题标签
        self.toolbar.title_label = QLabel("⚡ 屏幕标注工具")
        self.toolbar.title_label.setObjectName("titleLabel")
        title_layout.addWidget(self.toolbar.title_label)
        
        title_layout.addStretch()
        
        # 主题切换按钮
        self.toolbar.theme_toggle_btn = QPushButton("☀️")
        self.toolbar.theme_toggle_btn.setObjectName("themeToggleButton")
        self.toolbar.theme_toggle_btn.setToolTip("切换到白天模式")
        self.toolbar.theme_toggle_btn.clicked.connect(self.toolbar.theme_manager.toggle_theme)
        title_layout.addWidget(self.toolbar.theme_toggle_btn)
        
        # 折叠按钮
        self.toolbar.toggle_collapse_btn = QPushButton("🔼")
        self.toolbar.toggle_collapse_btn.setObjectName("collapseButton")
        self.toolbar.toggle_collapse_btn.clicked.connect(self.toolbar.toggle_toolbar_collapse)
        title_layout.addWidget(self.toolbar.toggle_collapse_btn)
        
        # 安装事件过滤器
        self.toolbar.title_container.installEventFilter(self.toolbar)
        
        main_layout.addWidget(self.toolbar.title_container)
        
    def setup_tools_section(self, main_layout: QVBoxLayout) -> None:
        """设置工具选择区域"""
        tools_card = QFrame()
        tools_card.setFrameStyle(QFrame.NoFrame)
        tools_card.setProperty("class", "card")
        tools_layout = QVBoxLayout(tools_card)
        tools_layout.setContentsMargins(6, 6, 6, 6)
        tools_layout.setSpacing(6)
        
        # 区域标题
        tools_title = QLabel("🎨 绘制工具")
        tools_title.setProperty("class", "section-title")
        tools_layout.addWidget(tools_title)
        
        # 工具按钮定义
        tool_buttons = self._get_tool_button_definitions()
        
        self.toolbar.tool_button_group = {}
        
        # 创建工具按钮行
        self._create_tool_button_rows(tools_layout, tool_buttons)
        
        # 默认选择直线工具
        self.toolbar.tool_button_group["line"].setChecked(True)
        
        main_layout.addWidget(tools_card)
        
    def _get_tool_button_definitions(self) -> List[Tuple[str, str]]:
        """获取工具按钮定义列表"""
        return [
            ("直线", "line"),
            ("矩形", "rectangle"), 
            ("圆形", "circle"),
            ("箭头", "arrow"),
            ("自由绘制", "freehand"),
            ("填充绘制", "filled_freehand"),
            ("点", "point"),
            ("激光笔", "laser_pointer"),
            ("文本", "text")
        ]
    
    def _create_tool_button_rows(self, layout: QVBoxLayout, tool_buttons: List[Tuple[str, str]]) -> None:
        """创建工具按钮行"""
        # 第一行工具按钮（4个）
        tools_row1 = QHBoxLayout()
        tools_row1.setSpacing(4)
        for name, tool in tool_buttons[:4]:
            btn = self._create_tool_button(name, tool)
            tools_row1.addWidget(btn)
        layout.addLayout(tools_row1)
        
        # 第二行工具按钮（4个）
        tools_row2 = QHBoxLayout()
        tools_row2.setSpacing(4)
        for name, tool in tool_buttons[4:8]:
            btn = self._create_tool_button(name, tool)
            tools_row2.addWidget(btn)
        layout.addLayout(tools_row2)
        
        # 第三行工具按钮（文本工具）
        tools_row3 = QHBoxLayout()
        tools_row3.setSpacing(4)
        for name, tool in tool_buttons[8:]:
            btn = self._create_tool_button(name, tool)
            tools_row3.addWidget(btn)
        # 添加空白占位符使文本按钮居中
        tools_row3.addStretch()
        layout.addLayout(tools_row3)
    
    def _create_tool_button(self, name: str, tool: str) -> QPushButton:
        """创建单个工具按钮"""
        btn = QPushButton(name)
        btn.setProperty("class", "tool")
        btn.setCheckable(True)
        btn.setMinimumSize(70, 28)
        btn.setMaximumSize(85, 32)
        tool_name = str(tool)
        btn.clicked.connect(lambda checked, tool_name=tool_name: self.main_window.select_tool(tool_name))
        self.toolbar.tool_button_group[tool] = btn
        return btn
        
    def setup_attributes_section(self, main_layout: QVBoxLayout) -> None:
        """设置属性控制区域"""
        attrs_card = QFrame()
        attrs_card.setFrameStyle(QFrame.NoFrame)
        attrs_card.setProperty("class", "card")
        attrs_layout = QVBoxLayout(attrs_card)
        attrs_layout.setContentsMargins(8, 8, 8, 8)
        attrs_layout.setSpacing(10)
        
        # 区域标题
        attrs_title = QLabel("⚙️ 绘制属性")
        attrs_title.setProperty("class", "section-title")
        attrs_layout.addWidget(attrs_title)
        
        # 创建各种属性控件
        self._create_color_selection(attrs_layout)
        self._create_thickness_control(attrs_layout)
        self._create_drawing_opacity_control(attrs_layout)
        self._create_canvas_opacity_control(attrs_layout)
        self._create_text_style_control(attrs_layout)
        
        main_layout.addWidget(attrs_card)
    
    def _create_color_selection(self, layout: QVBoxLayout) -> None:
        """创建颜色选择控件"""
        color_container = QWidget()
        color_layout = QHBoxLayout(color_container)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setSpacing(8)
        
        color_label = QLabel("颜色")
        color_label.setMinimumWidth(50)
        color_label.setMaximumWidth(60)
        
        self.toolbar.color_btn = QPushButton("选择颜色")
        self.toolbar.color_btn.setObjectName("colorButton")
        self.toolbar.color_btn.setMinimumHeight(32)
        self.toolbar.color_btn.clicked.connect(self.toolbar.pick_color)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.toolbar.color_btn)
        layout.addWidget(color_container)
    
    def _create_thickness_control(self, layout: QVBoxLayout) -> None:
        """创建粗细控制控件"""
        thickness_container = QWidget()
        thickness_layout = QVBoxLayout(thickness_container)
        thickness_layout.setContentsMargins(0, 0, 0, 0)
        thickness_layout.setSpacing(6)
        
        self.toolbar.thickness_label = QLabel(f"粗细: {self.canvas.current_thickness}")
        self.toolbar.thickness_label.setMinimumHeight(20)
        
        self.toolbar.thickness_slider = QSlider(Qt.Horizontal)
        self.toolbar.thickness_slider.setMinimum(1)
        self.toolbar.thickness_slider.setMaximum(20)
        self.toolbar.thickness_slider.setValue(self.canvas.current_thickness)
        self.toolbar.thickness_slider.setMinimumHeight(24)
        self.toolbar.thickness_slider.valueChanged.connect(self.toolbar.change_thickness)
        
        thickness_layout.addWidget(self.toolbar.thickness_label)
        thickness_layout.addWidget(self.toolbar.thickness_slider)
        layout.addWidget(thickness_container)
    
    def _create_drawing_opacity_control(self, layout: QVBoxLayout) -> None:
        """创建绘制不透明度控制控件"""
        draw_opacity_container = QWidget()
        draw_opacity_layout = QVBoxLayout(draw_opacity_container)
        draw_opacity_layout.setContentsMargins(0, 0, 0, 0)
        draw_opacity_layout.setSpacing(6)
        
        self.toolbar.drawing_opacity_label = QLabel(f"绘制不透明度: {int(self.canvas.current_opacity * 100)}%")
        self.toolbar.drawing_opacity_label.setMinimumHeight(20)
        
        self.toolbar.drawing_opacity_slider = QSlider(Qt.Horizontal)
        self.toolbar.drawing_opacity_slider.setMinimum(0)
        self.toolbar.drawing_opacity_slider.setMaximum(100)
        self.toolbar.drawing_opacity_slider.setValue(int(self.canvas.current_opacity * 100))
        self.toolbar.drawing_opacity_slider.setMinimumHeight(24)
        self.toolbar.drawing_opacity_slider.valueChanged.connect(self.toolbar.change_drawing_opacity)
        
        draw_opacity_layout.addWidget(self.toolbar.drawing_opacity_label)
        draw_opacity_layout.addWidget(self.toolbar.drawing_opacity_slider)
        layout.addWidget(draw_opacity_container)
    
    def _create_canvas_opacity_control(self, layout: QVBoxLayout) -> None:
        """创建画布不透明度控制控件"""
        canvas_opacity_container = QWidget()
        canvas_opacity_layout = QVBoxLayout(canvas_opacity_container)
        canvas_opacity_layout.setContentsMargins(0, 0, 0, 0)
        canvas_opacity_layout.setSpacing(6)
        
        self.toolbar.canvas_opacity_label = QLabel(f"画布不透明度: {int(self.canvas.canvas_opacity * 100)}%")
        self.toolbar.canvas_opacity_label.setMinimumHeight(20)
        
        self.toolbar.canvas_opacity_slider = QSlider(Qt.Horizontal)
        self.toolbar.canvas_opacity_slider.setMinimum(0)
        self.toolbar.canvas_opacity_slider.setMaximum(100)
        self.toolbar.canvas_opacity_slider.setValue(int(self.canvas.canvas_opacity * 100))
        self.toolbar.canvas_opacity_slider.setMinimumHeight(24)
        self.toolbar.canvas_opacity_slider.valueChanged.connect(self.toolbar.change_canvas_opacity)
        
        canvas_opacity_layout.addWidget(self.toolbar.canvas_opacity_label)
        canvas_opacity_layout.addWidget(self.toolbar.canvas_opacity_slider)
        layout.addWidget(canvas_opacity_container)
    
    def _create_text_style_control(self, layout: QVBoxLayout) -> None:
        """创建文本样式控件"""
        text_style_container = QWidget()
        text_style_layout = QHBoxLayout(text_style_container)
        text_style_layout.setContentsMargins(0, 0, 0, 0)
        text_style_layout.setSpacing(8)
        
        text_style_label = QLabel("文本样式")
        text_style_label.setMinimumWidth(50)
        text_style_label.setMaximumWidth(60)
        
        self.toolbar.text_style_btn = QPushButton("🎨 文本样式")
        self.toolbar.text_style_btn.setProperty("class", "action")
        self.toolbar.text_style_btn.setMinimumHeight(32)
        self.toolbar.text_style_btn.clicked.connect(self.toolbar.open_text_style_dialog)
        
        text_style_layout.addWidget(text_style_label)
        text_style_layout.addWidget(self.toolbar.text_style_btn)
        layout.addWidget(text_style_container)

    def setup_actions_section(self, main_layout: QVBoxLayout) -> None:
        """设置操作按钮区域"""
        actions_card = QFrame()
        actions_card.setFrameStyle(QFrame.NoFrame)
        actions_card.setProperty("class", "card")
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(8, 8, 8, 8)
        actions_layout.setSpacing(10)
        
        # 区域标题
        actions_title = QLabel("🎯 操作控制")
        actions_title.setProperty("class", "section-title")
        actions_layout.addWidget(actions_title)
        
        # 创建各种操作按钮行
        self._create_edit_actions_row(actions_layout)
        actions_layout.addSpacing(8)
        
        self._create_mode_control_row(actions_layout)
        actions_layout.addSpacing(8)
        
        self._create_file_operations_row(actions_layout)
        actions_layout.addSpacing(8)
        
        self._create_system_operations_row(actions_layout)
        
        main_layout.addWidget(actions_card)
    
    def _create_edit_actions_row(self, layout: QVBoxLayout) -> None:
        """创建编辑操作行"""
        edit_row = QHBoxLayout()
        edit_row.setSpacing(6)
        
        self.toolbar.undo_btn = QPushButton("↶ 撤销")
        self.toolbar.undo_btn.setProperty("class", "action")
        self.toolbar.undo_btn.setMinimumHeight(32)
        self.toolbar.undo_btn.clicked.connect(self.canvas.undo)
        edit_row.addWidget(self.toolbar.undo_btn)
        
        self.toolbar.redo_btn = QPushButton("↷ 重做")
        self.toolbar.redo_btn.setProperty("class", "action")
        self.toolbar.redo_btn.setMinimumHeight(32)
        self.toolbar.redo_btn.clicked.connect(self.canvas.redo)
        edit_row.addWidget(self.toolbar.redo_btn)
        
        self.toolbar.clear_btn = QPushButton("🗑 清空")
        self.toolbar.clear_btn.setProperty("class", "action warning")
        self.toolbar.clear_btn.setMinimumHeight(32)
        self.toolbar.clear_btn.clicked.connect(self.canvas.clear_canvas)
        edit_row.addWidget(self.toolbar.clear_btn)
        
        layout.addLayout(edit_row)
    
    def _create_mode_control_row(self, layout: QVBoxLayout) -> None:
        """创建模式控制行"""
        mode_row = QHBoxLayout()
        mode_row.setSpacing(6)
        
        self.toolbar.toggle_passthrough_btn = QPushButton("🖱 穿透")
        self.toolbar.toggle_passthrough_btn.setProperty("class", "action")
        self.toolbar.toggle_passthrough_btn.setMinimumHeight(32)
        self.toolbar.toggle_passthrough_btn.setCheckable(True)
        self.toolbar.toggle_passthrough_btn.clicked.connect(self.main_window.toggle_mouse_passthrough)
        mode_row.addWidget(self.toolbar.toggle_passthrough_btn)
        
        self.toolbar.toggle_visibility_btn = QPushButton("👁 隐藏")
        self.toolbar.toggle_visibility_btn.setProperty("class", "action")
        self.toolbar.toggle_visibility_btn.setMinimumHeight(32)
        self.toolbar.toggle_visibility_btn.setCheckable(True)
        self.toolbar.toggle_visibility_btn.clicked.connect(self.main_window.toggle_canvas_visibility)
        mode_row.addWidget(self.toolbar.toggle_visibility_btn)
        
        self.toolbar.single_draw_mode_btn = QPushButton("1️⃣ 单次")
        self.toolbar.single_draw_mode_btn.setProperty("class", "action")
        self.toolbar.single_draw_mode_btn.setMinimumHeight(32)
        self.toolbar.single_draw_mode_btn.setCheckable(True)
        self.toolbar.single_draw_mode_btn.clicked.connect(self.main_window.toggle_single_draw_mode)
        mode_row.addWidget(self.toolbar.single_draw_mode_btn)
        
        layout.addLayout(mode_row)
    
    def _create_file_operations_row(self, layout: QVBoxLayout) -> None:
        """创建文件操作行"""
        file_row = QHBoxLayout()
        file_row.setSpacing(6)
        
        self.toolbar.import_btn = QPushButton("📥 导入")
        self.toolbar.import_btn.setProperty("class", "action primary")
        self.toolbar.import_btn.setMinimumHeight(32)
        self.toolbar.import_btn.clicked.connect(self.main_window.import_canvas_content)
        file_row.addWidget(self.toolbar.import_btn)
        
        self.toolbar.export_btn = QPushButton("📤 导出")
        self.toolbar.export_btn.setProperty("class", "action success")
        self.toolbar.export_btn.setMinimumHeight(32)
        self.toolbar.export_btn.clicked.connect(self.main_window.export_canvas_content)
        file_row.addWidget(self.toolbar.export_btn)
        
        self.toolbar.save_config_btn = QPushButton("💾 保存")
        self.toolbar.save_config_btn.setProperty("class", "action")
        self.toolbar.save_config_btn.setMinimumHeight(32)
        self.toolbar.save_config_btn.clicked.connect(self.main_window.save_current_config)
        file_row.addWidget(self.toolbar.save_config_btn)
        
        layout.addLayout(file_row)
    
    def _create_system_operations_row(self, layout: QVBoxLayout) -> None:
        """创建系统操作行"""
        system_row = QHBoxLayout()
        system_row.setSpacing(6)
        
        self.toolbar.settings_btn = QPushButton("⚙️ 设置")
        self.toolbar.settings_btn.setProperty("class", "action")
        self.toolbar.settings_btn.setMinimumHeight(32)
        self.toolbar.settings_btn.clicked.connect(self.main_window.open_hotkey_settings)
        system_row.addWidget(self.toolbar.settings_btn)
        
        self.toolbar.exit_btn = QPushButton("❌ 退出")
        self.toolbar.exit_btn.setProperty("class", "action danger")
        self.toolbar.exit_btn.setMinimumHeight(32)
        self.toolbar.exit_btn.clicked.connect(self.main_window.close_application)
        system_row.addWidget(self.toolbar.exit_btn)
        
        # 添加空白填充
        system_row.addStretch()
        
        layout.addLayout(system_row)
