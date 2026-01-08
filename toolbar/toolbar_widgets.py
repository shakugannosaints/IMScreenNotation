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
        
        # GitHub仓库按钮
        self.toolbar.github_btn = QPushButton("❗")
        self.toolbar.github_btn.setObjectName("themeToggleButton")  # 使用相同样式
        self.toolbar.github_btn.setToolTip("访问GitHub仓库")
        self.toolbar.github_btn.clicked.connect(self._open_github_repo)
        title_layout.addWidget(self.toolbar.github_btn)
        
        # 主题切换按钮
        self.toolbar.theme_toggle_btn = QPushButton("☀️")
        self.toolbar.theme_toggle_btn.setObjectName("themeToggleButton")
        self.toolbar.theme_toggle_btn.setToolTip("切换到白天模式")
        self.toolbar.theme_toggle_btn.clicked.connect(self.toolbar.theme_manager.toggle_theme)
        title_layout.addWidget(self.toolbar.theme_toggle_btn)
        
        # 区域管理按钮
        self.toolbar.section_manage_btn = QPushButton("📋")
        self.toolbar.section_manage_btn.setObjectName("themeToggleButton")  # 使用相同样式
        self.toolbar.section_manage_btn.setToolTip("区域管理：点击展开所有，右键折叠所有")
        self.toolbar.section_manage_btn.clicked.connect(self.toolbar.expand_all_sections)
        # 添加右键菜单支持
        self.toolbar.section_manage_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.toolbar.section_manage_btn.customContextMenuRequested.connect(
            lambda: self.toolbar.collapse_all_sections()
        )
        title_layout.addWidget(self.toolbar.section_manage_btn)
        
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
            ("多边形", "polygon"), 
            ("圆形", "circle"),
            ("箭头", "arrow"),
            ("自由绘制", "freehand"),
            ("点", "point"),
            ("激光笔", "laser_pointer"),
            ("文本", "text"),
            ("橡皮擦", "eraser"),
            ("直线标尺", "line_ruler"),
            ("圆形标尺", "circle_ruler"),
            ("图片", "image")
        ]
    
    def _create_tool_button_rows(self, layout: QVBoxLayout, tool_buttons: List[Tuple[str, str]]) -> None:
        """创建工具按钮行（自动排列，每行3个工具，布局更均匀）"""
        buttons_per_row = 3  # 改为每行3个，10个工具可以分成4行（3+3+3+1）
        
        # 计算需要的行数
        total_buttons = len(tool_buttons)
        rows_needed = (total_buttons + buttons_per_row - 1) // buttons_per_row
        
        # 逐行创建工具按钮
        for row_index in range(rows_needed):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(4)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            # 计算当前行的按钮范围
            start_index = row_index * buttons_per_row
            end_index = min(start_index + buttons_per_row, total_buttons)
            
            # 添加当前行的按钮
            for name, tool in tool_buttons[start_index:end_index]:
                btn = self._create_tool_button(name, tool)
                row_layout.addWidget(btn)
            
            # 为了保持布局一致性，即使最后一行按钮不足也要保持固定尺寸
            buttons_in_row = end_index - start_index
            if buttons_in_row < buttons_per_row:
                # 添加空白占位，确保按钮左对齐且保持一致的布局
                for _ in range(buttons_per_row - buttons_in_row):
                    spacer = QWidget()
                    # 使用与按钮相同的最小尺寸
                    spacer.setMinimumSize(70, 28)
                    spacer.setMaximumSize(100, 32)  # 稍微宽一点以适应不同按钮宽度
                    spacer.setSizePolicy(spacer.sizePolicy().Fixed, spacer.sizePolicy().Fixed)
                    row_layout.addWidget(spacer)
            
            layout.addLayout(row_layout)
    
    def _create_tool_button(self, name: str, tool: str) -> QPushButton:
        """创建单个工具按钮"""
        btn = QPushButton(name)
        btn.setProperty("class", "tool")
        btn.setCheckable(True)
        # 根据文本长度动态调整按钮宽度，确保文本能完整显示
        text_width = btn.fontMetrics().boundingRect(name).width()
        min_width = max(70, text_width + 20)  # 至少70像素，或文本宽度+20像素边距
        max_width = max(85, text_width + 25)  # 至少85像素，或文本宽度+25像素边距
        
        btn.setMinimumSize(min_width, 28)
        btn.setMaximumSize(max_width, 32)
        # 设置固定尺寸策略，确保按钮大小一致
        btn.setSizePolicy(btn.sizePolicy().Fixed, btn.sizePolicy().Fixed)
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
        self._create_fill_mode_control(attrs_layout)
        self._create_freehand_auto_correct_control(attrs_layout)
        
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
        
        self.toolbar.thickness_label = QLabel(f"粗细: {self.canvas.properties.current_thickness}")
        self.toolbar.thickness_label.setMinimumHeight(20)
        
        self.toolbar.thickness_slider = QSlider(Qt.Horizontal)
        self.toolbar.thickness_slider.setMinimum(1)
        self.toolbar.thickness_slider.setMaximum(20)
        self.toolbar.thickness_slider.setValue(self.canvas.properties.current_thickness)
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
        
        self.toolbar.drawing_opacity_label = QLabel(f"绘制不透明度: {int(self.canvas.properties.current_opacity * 100)}%")
        self.toolbar.drawing_opacity_label.setMinimumHeight(20)
        
        self.toolbar.drawing_opacity_slider = QSlider(Qt.Horizontal)
        self.toolbar.drawing_opacity_slider.setMinimum(0)
        self.toolbar.drawing_opacity_slider.setMaximum(100)
        self.toolbar.drawing_opacity_slider.setValue(int(self.canvas.properties.current_opacity * 100))
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
        
        self.toolbar.canvas_opacity_label = QLabel(f"画布不透明度: {int(self.canvas.properties.canvas_opacity * 100)}%")
        self.toolbar.canvas_opacity_label.setMinimumHeight(20)
        
        self.toolbar.canvas_opacity_slider = QSlider(Qt.Horizontal)
        self.toolbar.canvas_opacity_slider.setMinimum(0)
        self.toolbar.canvas_opacity_slider.setMaximum(100)
        self.toolbar.canvas_opacity_slider.setValue(int(self.canvas.properties.canvas_opacity * 100))
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

    def _create_freehand_auto_correct_control(self, layout: QVBoxLayout) -> None:
        """创建自由绘制线条纠正开关（仅影响 freehand / filled_freehand）"""
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        label = QLabel("线条纠正")
        label.setMinimumWidth(50)
        label.setMaximumWidth(60)

        self.toolbar.auto_correct_freehand_btn = QPushButton("🧲 开启")
        self.toolbar.auto_correct_freehand_btn.setProperty("class", "action")
        self.toolbar.auto_correct_freehand_btn.setMinimumHeight(32)
        self.toolbar.auto_correct_freehand_btn.setCheckable(True)
        self.toolbar.auto_correct_freehand_btn.setToolTip(
            "仅对【自由绘制/填充绘制】生效：\n"
            "- 抖动直线会被简化为笔直线段\n"
            "- 多边形会被简化为直线边"
        )

        # 初始化状态
        enabled = bool(getattr(self.canvas.properties, 'auto_correct_freehand', False))
        self.toolbar.auto_correct_freehand_btn.setChecked(enabled)
        if enabled:
            self.toolbar.auto_correct_freehand_btn.setText("🧲 已开启")
            self.toolbar.auto_correct_freehand_btn.setProperty("class", "action active")

        def _toggle(checked: bool) -> None:
            self.canvas.set_auto_correct_freehand(checked)
            if checked:
                self.toolbar.auto_correct_freehand_btn.setText("🧲 已开启")
                self.toolbar.auto_correct_freehand_btn.setProperty("class", "action active")
            else:
                self.toolbar.auto_correct_freehand_btn.setText("🧲 开启")
                self.toolbar.auto_correct_freehand_btn.setProperty("class", "action")
            # 刷新按钮样式
            style = self.toolbar.auto_correct_freehand_btn.style()
            if style:
                style.unpolish(self.toolbar.auto_correct_freehand_btn)
                style.polish(self.toolbar.auto_correct_freehand_btn)

        self.toolbar.auto_correct_freehand_btn.toggled.connect(_toggle)

        row.addWidget(label)
        row.addWidget(self.toolbar.auto_correct_freehand_btn)
        layout.addWidget(container)

    def _create_fill_mode_control(self, layout: QVBoxLayout) -> None:
        """创建全局填充模式开关"""
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        label = QLabel("填充")
        label.setMinimumWidth(50)
        label.setMaximumWidth(60)

        self.toolbar.fill_mode_btn = QPushButton("🪣 关闭")
        self.toolbar.fill_mode_btn.setProperty("class", "action")
        self.toolbar.fill_mode_btn.setMinimumHeight(32)
        self.toolbar.fill_mode_btn.setCheckable(True)
        self.toolbar.fill_mode_btn.setToolTip(
            "开启后：\n"
            "- 自由绘制：自动变为填充绘制\n"
            "- 多边形/圆形：自动绘制填充形状\n"
            "关闭后恢复为原来的描边效果。"
        )

        enabled = bool(getattr(self.canvas.properties, 'fill_mode_enabled', False))
        self.toolbar.fill_mode_btn.setChecked(enabled)
        if enabled:
            self.toolbar.fill_mode_btn.setText("🪣 已开启")
            self.toolbar.fill_mode_btn.setProperty("class", "action active")

        def _toggle(checked: bool) -> None:
            self.canvas.set_fill_mode_enabled(checked)
            if checked:
                self.toolbar.fill_mode_btn.setText("🪣 已开启")
                self.toolbar.fill_mode_btn.setProperty("class", "action active")
            else:
                self.toolbar.fill_mode_btn.setText("🪣 关闭")
                self.toolbar.fill_mode_btn.setProperty("class", "action")
            style = self.toolbar.fill_mode_btn.style()
            if style:
                style.unpolish(self.toolbar.fill_mode_btn)
                style.polish(self.toolbar.fill_mode_btn)

        self.toolbar.fill_mode_btn.toggled.connect(_toggle)

        row.addWidget(label)
        row.addWidget(self.toolbar.fill_mode_btn)
        layout.addWidget(container)

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
        
        # 创建所有操作按钮
        self._create_all_action_buttons(actions_layout)
        
        main_layout.addWidget(actions_card)
    
    def _create_all_action_buttons(self, layout: QVBoxLayout) -> None:
        """创建所有操作按钮（自动排列）"""
        # 创建所有按钮
        buttons = []
        
        # 编辑操作按钮
        self.toolbar.undo_btn = QPushButton("↶ 撤销")
        self.toolbar.undo_btn.setProperty("class", "action")
        self.toolbar.undo_btn.setMinimumHeight(32)
        self.toolbar.undo_btn.clicked.connect(self.canvas.undo)
        buttons.append(self.toolbar.undo_btn)
        
        self.toolbar.redo_btn = QPushButton("↷ 重做")
        self.toolbar.redo_btn.setProperty("class", "action")
        self.toolbar.redo_btn.setMinimumHeight(32)
        self.toolbar.redo_btn.clicked.connect(self.canvas.redo)
        buttons.append(self.toolbar.redo_btn)
        
        self.toolbar.clear_btn = QPushButton("🗑 清空")
        self.toolbar.clear_btn.setProperty("class", "action warning")
        self.toolbar.clear_btn.setMinimumHeight(32)
        self.toolbar.clear_btn.clicked.connect(self.canvas.clear_canvas)
        buttons.append(self.toolbar.clear_btn)
        
        # 模式控制按钮
        self.toolbar.toggle_passthrough_btn = QPushButton("🖱 穿透")
        self.toolbar.toggle_passthrough_btn.setProperty("class", "action")
        self.toolbar.toggle_passthrough_btn.setMinimumHeight(32)
        self.toolbar.toggle_passthrough_btn.setCheckable(True)
        self.toolbar.toggle_passthrough_btn.clicked.connect(self.main_window.toggle_mouse_passthrough)
        buttons.append(self.toolbar.toggle_passthrough_btn)
        
        self.toolbar.toggle_visibility_btn = QPushButton("👁 隐藏")
        self.toolbar.toggle_visibility_btn.setProperty("class", "action")
        self.toolbar.toggle_visibility_btn.setMinimumHeight(32)
        self.toolbar.toggle_visibility_btn.setCheckable(True)
        self.toolbar.toggle_visibility_btn.clicked.connect(self.main_window.toggle_canvas_visibility)
        buttons.append(self.toolbar.toggle_visibility_btn)
        
        self.toolbar.single_draw_mode_btn = QPushButton("1️⃣ 单次")
        self.toolbar.single_draw_mode_btn.setProperty("class", "action")
        self.toolbar.single_draw_mode_btn.setMinimumHeight(32)
        self.toolbar.single_draw_mode_btn.setCheckable(True)
        self.toolbar.single_draw_mode_btn.clicked.connect(self.main_window.toggle_single_draw_mode)
        buttons.append(self.toolbar.single_draw_mode_btn)
        
        # 文件操作按钮
        self.toolbar.import_btn = QPushButton("📥 导入")
        self.toolbar.import_btn.setProperty("class", "action primary")
        self.toolbar.import_btn.setMinimumHeight(32)
        self.toolbar.import_btn.clicked.connect(self.main_window.import_canvas_content)
        buttons.append(self.toolbar.import_btn)
        
        self.toolbar.export_btn = QPushButton("📤 导出")
        self.toolbar.export_btn.setProperty("class", "action success")
        self.toolbar.export_btn.setMinimumHeight(32)
        self.toolbar.export_btn.clicked.connect(self.main_window.export_canvas_content)
        buttons.append(self.toolbar.export_btn)
        
        self.toolbar.save_config_btn = QPushButton("💾 保存")
        self.toolbar.save_config_btn.setProperty("class", "action")
        self.toolbar.save_config_btn.setMinimumHeight(32)
        self.toolbar.save_config_btn.clicked.connect(self.main_window.save_current_config)
        buttons.append(self.toolbar.save_config_btn)
        
        # 系统操作按钮
        self.toolbar.settings_btn = QPushButton("⚙️ 设置")
        self.toolbar.settings_btn.setProperty("class", "action")
        self.toolbar.settings_btn.setMinimumHeight(32)
        self.toolbar.settings_btn.clicked.connect(self.main_window.open_hotkey_settings)
        buttons.append(self.toolbar.settings_btn)
        
        # 标尺功能按钮
        self.toolbar.ruler_settings_btn = QPushButton("📏 标尺设置")
        self.toolbar.ruler_settings_btn.setProperty("class", "action")
        self.toolbar.ruler_settings_btn.setMinimumHeight(32)
        self.toolbar.ruler_settings_btn.clicked.connect(self.main_window.open_ruler_settings)
        buttons.append(self.toolbar.ruler_settings_btn)

        self.toolbar.ruler_calibration_btn = QPushButton("📐 快速标定")
        self.toolbar.ruler_calibration_btn.setProperty("class", "action")
        self.toolbar.ruler_calibration_btn.setMinimumHeight(32)
        self.toolbar.ruler_calibration_btn.clicked.connect(self.main_window.start_ruler_calibration)
        buttons.append(self.toolbar.ruler_calibration_btn)
        
        self.toolbar.exit_btn = QPushButton("❌ 退出")
        self.toolbar.exit_btn.setProperty("class", "action danger")
        self.toolbar.exit_btn.setMinimumHeight(32)
        self.toolbar.exit_btn.clicked.connect(self.main_window.close_application)
        buttons.append(self.toolbar.exit_btn)
        
        # 使用通用方法创建按钮行（每行3个按钮）
        self._create_button_rows(layout, buttons, buttons_per_row=3)

    def _create_button_rows(self, layout: QVBoxLayout, buttons: List[QPushButton], buttons_per_row: int = 3) -> None:
        """通用的按钮行创建方法（自动排列）
        
        Args:
            layout: 目标布局
            buttons: 按钮列表
            buttons_per_row: 每行按钮数量，默认为3
        """
        total_buttons = len(buttons)
        rows_needed = (total_buttons + buttons_per_row - 1) // buttons_per_row
        
        # 逐行创建按钮
        for row_index in range(rows_needed):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(6)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            # 计算当前行的按钮范围
            start_index = row_index * buttons_per_row
            end_index = min(start_index + buttons_per_row, total_buttons)
            
            # 添加当前行的按钮
            for button in buttons[start_index:end_index]:
                # 确保按钮有一致的尺寸策略
                button.setSizePolicy(button.sizePolicy().Expanding, button.sizePolicy().Fixed)
                row_layout.addWidget(button)
            
            # 为了保持布局一致性，最后一行如果按钮不足也要保持对齐
            buttons_in_row = end_index - start_index
            if buttons_in_row < buttons_per_row:
                # 添加空白占位，确保按钮分布均匀
                for _ in range(buttons_per_row - buttons_in_row):
                    spacer = QWidget()
                    spacer.setSizePolicy(spacer.sizePolicy().Expanding, spacer.sizePolicy().Fixed)
                    spacer.setMinimumHeight(32)
                    row_layout.addWidget(spacer)
            
            layout.addLayout(row_layout)
    
    def setup_scrollable_sections(self, scrollable_content) -> None:
        """设置可滚动的分组区域"""
        # 创建工具选择区域
        tools_widget = QWidget()
        self.setup_tools_section_for_scrollable(tools_widget)
        scrollable_content.add_section("tools", "🎨 绘制工具", tools_widget, collapsible=True, start_collapsed=False)
        
        # 创建属性控制区域
        attrs_widget = QWidget()
        self.setup_attributes_section_for_scrollable(attrs_widget)
        scrollable_content.add_section("attributes", "⚙️ 绘制属性", attrs_widget, collapsible=True, start_collapsed=False)
        
        # 创建操作区域
        actions_widget = QWidget()
        self.setup_actions_section_for_scrollable(actions_widget)
        scrollable_content.add_section("actions", "🔧 操作功能", actions_widget, collapsible=True, start_collapsed=False)
        
        # 如果有更多功能，可以继续添加新的区域
        self._setup_advanced_features_section(scrollable_content)
    
    def setup_tools_section_for_scrollable(self, container_widget: QWidget) -> None:
        """为可滚动区域设置工具选择区域"""
        layout = QVBoxLayout(container_widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        
        # 工具按钮定义
        tool_buttons = self._get_tool_button_definitions()
        
        self.toolbar.tool_button_group = {}
        
        # 创建工具按钮行
        self._create_tool_button_rows(layout, tool_buttons)
        
        # 默认选择直线工具
        if "line" in self.toolbar.tool_button_group:
            self.toolbar.tool_button_group["line"].setChecked(True)
    
    def setup_attributes_section_for_scrollable(self, container_widget: QWidget) -> None:
        """为可滚动区域设置属性控制区域"""
        layout = QVBoxLayout(container_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        
        # 创建各种属性控件
        self._create_color_selection(layout)
        self._create_thickness_control(layout)
        self._create_drawing_opacity_control(layout)
        self._create_canvas_opacity_control(layout)
        self._create_text_style_control(layout)
        self._create_fill_mode_control(layout)
        self._create_freehand_auto_correct_control(layout)
    
    def setup_actions_section_for_scrollable(self, container_widget: QWidget) -> None:
        """为可滚动区域设置操作功能区域"""
        layout = QVBoxLayout(container_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 创建所有操作按钮
        self._create_all_action_buttons(layout)
    
    def _setup_advanced_features_section(self, scrollable_content) -> None:
        """设置高级功能区域（示例，展示如何添加更多功能区域）"""
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 创建高级功能按钮
        buttons = []

        
        # 图层管理按钮
        layer_btn = QPushButton("📚 图层管理")
        layer_btn.setProperty("class", "action")
        layer_btn.setMinimumHeight(32)
        layer_btn.setToolTip("管理标注图层")
        layer_btn.clicked.connect(lambda: self._show_layer_manager())
        buttons.append(layer_btn)
        
        
        # 折叠/展开所有区域的快捷按钮
        collapse_all_btn = QPushButton("📁 折叠所有")
        collapse_all_btn.setProperty("class", "action warning")
        collapse_all_btn.setMinimumHeight(32)
        collapse_all_btn.setToolTip("折叠所有功能区域")
        collapse_all_btn.clicked.connect(self.toolbar.collapse_all_sections)
        buttons.append(collapse_all_btn)
        
        expand_all_btn = QPushButton("📂 展开所有")
        expand_all_btn.setProperty("class", "action warning")
        expand_all_btn.setMinimumHeight(32)
        expand_all_btn.setToolTip("展开所有功能区域")
        expand_all_btn.clicked.connect(self.toolbar.expand_all_sections)
        buttons.append(expand_all_btn)
        
        # 使用通用方法创建按钮行（每行3个按钮）
        self._create_button_rows(layout, buttons, buttons_per_row=3)
        
        scrollable_content.add_section("advanced", "🚀 高级功能（未实现的未来规划）", advanced_widget, 
                                     collapsible=True, start_collapsed=True)

    def _show_layer_manager(self) -> None:
        """显示图层管理器（占位符实现）"""
        # 这里可以实现图层管理功能
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage("图层管理功能待实现", 2000)

    def _open_github_repo(self) -> None:
        """打开GitHub仓库页面"""
        import webbrowser
        repo_url = "https://github.com/shakugannosaints/IMScreenNotation"
        try:
            webbrowser.open(repo_url)
            if hasattr(self.main_window, '_status_bar'):
                self.main_window._status_bar.showMessage("正在打开GitHub仓库...", 2000)
        except Exception as e:
            print(f"无法打开GitHub仓库: {e}")
            if hasattr(self.main_window, '_status_bar'):
                self.main_window._status_bar.showMessage("无法打开GitHub仓库", 3000)
