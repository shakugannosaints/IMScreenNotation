"""
可滚动工具栏扩展模块
为工具栏添加滚动和分组折叠功能，解决内容过长问题
"""

from typing import Dict, List, Optional, Union
from PyQt5.QtWidgets import (QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QPixmap, QPainter, QMouseEvent


class CollapsibleSection(QWidget):
    """可折叠的区域组件"""
    
    def __init__(self, title: str, content_widget: QWidget, parent=None):
        super().__init__(parent)
        self.content_widget = content_widget
        self.is_collapsed = False
        self.animation_duration = 200
        
        self.setup_ui(title)
        self.setup_animation()
    
    def setup_ui(self, title: str) -> None:
        """设置界面"""
        self.setObjectName("collapsibleSection")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 设置尺寸策略，当折叠时最小化空间占用
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        
        # 标题栏（点击可折叠）
        self.header = QWidget()
        self.header.setObjectName("sectionHeader")
        self.header.setCursor(Qt.PointingHandCursor)
        self.header.setMinimumHeight(28)  # 减小高度，让折叠时更紧凑
        self.header.setMaximumHeight(28)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(8, 4, 8, 4)  # 减小垂直边距
        header_layout.setSpacing(8)
        
        # 折叠指示器
        self.collapse_indicator = QLabel("▼")
        self.collapse_indicator.setObjectName("collapseIndicator")
        self.collapse_indicator.setMinimumWidth(16)
        self.collapse_indicator.setMaximumWidth(16)
        self.collapse_indicator.setAlignment(Qt.AlignCenter)
        
        # 标题文本
        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")
        
        header_layout.addWidget(self.collapse_indicator)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        # 内容容器
        self.content_container = QWidget()
        self.content_container.setObjectName("sectionContent")
        content_container_layout = QVBoxLayout(self.content_container)
        content_container_layout.setContentsMargins(8, 0, 8, 4)  # 减少上边距，让展开内容更贴近标题
        content_container_layout.addWidget(self.content_widget)
        
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.content_container)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """重写鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 检查点击是否在标题栏内
            if self.header.geometry().contains(event.pos()):
                self.toggle_collapse()
        super().mousePressEvent(event)
    
    def setup_animation(self) -> None:
        """设置折叠动画"""
        self.animation = QPropertyAnimation(self.content_container, b"maximumHeight")
        self.animation.setDuration(self.animation_duration)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    
    def toggle_collapse(self, event=None) -> None:
        """切换折叠状态"""
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()
    
    def collapse(self) -> None:
        """折叠区域"""
        if self.is_collapsed:
            return
            
        self.is_collapsed = True
        self.collapse_indicator.setText("▶")
        
        # 获取当前高度并动画到0
        current_height = self.content_container.height()
        self.animation.setStartValue(current_height)
        self.animation.setEndValue(0)
        
        # 当折叠完成后，调整组件的尺寸策略以减少占用空间
        def on_collapse_finished():
            self.content_container.hide()  # 隐藏内容容器
            # 设置折叠后的精确高度：标题栏高度 + 1px分隔线
            collapsed_height = self.header.height() + 1
            self.setFixedHeight(collapsed_height)
            # 设置折叠时的尺寸策略，最小化垂直空间
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            # 添加底部细线作为视觉分隔
            self.setStyleSheet("""
                CollapsibleSection[collapsed="true"] {
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
            """)
            self.setProperty("collapsed", True)
            self.updateGeometry()  # 通知父组件更新布局
            # 通知工具栏内容已变化，需要重新计算窗口大小
            self._notify_content_changed()
        
        # 断开之前的信号连接，避免重复连接
        try:
            self.animation.finished.disconnect()
        except:
            pass
        
        self.animation.finished.connect(on_collapse_finished)
        self.animation.start()
    
    def expand(self) -> None:
        """展开区域"""
        if not self.is_collapsed:
            return
            
        self.is_collapsed = False
        self.collapse_indicator.setText("▼")
        
        # 清除折叠时的样式
        self.setStyleSheet("")
        self.setProperty("collapsed", False)
        
        # 恢复组件的自然尺寸
        self.setFixedHeight(16777215)  # 取消固定高度
        # 恢复展开时的尺寸策略
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.content_container.show()  # 显示内容容器
        
        # 计算目标高度
        self.content_container.setMaximumHeight(16777215)  # 重置最大高度
        target_height = self.content_widget.sizeHint().height() + 8  # 减少边距补偿
        
        # 断开之前的信号连接，避免重复连接
        try:
            self.animation.finished.disconnect()
        except:
            pass
        
        self.animation.setStartValue(0)
        self.animation.setEndValue(target_height)
        
        def on_expand_finished():
            self.updateGeometry()  # 通知父组件更新布局
            # 通知工具栏内容已变化，需要重新计算窗口大小
            self._notify_content_changed()
        
        self.animation.finished.connect(on_expand_finished)
        self.animation.start()
    
    def sizeHint(self):
        """重写尺寸提示，折叠时返回最小尺寸"""
        if self.is_collapsed:
            return self.header.sizeHint()
        else:
            return super().sizeHint()
    
    def minimumSizeHint(self):
        """重写最小尺寸提示"""
        if self.is_collapsed:
            return self.header.minimumSizeHint()
        else:
            return super().minimumSizeHint()
    
    def _notify_content_changed(self):
        """通知父级工具栏内容已变化，需要重新计算大小"""
        # 向上查找ScrollableToolbarContent
        parent = self.parent()
        while parent:
            if hasattr(parent, '_on_content_changed'):
                try:
                    parent._on_content_changed()  # type: ignore
                    break
                except Exception as e:
                    print(f"调用_on_content_changed时出错: {e}")
                    break
            parent = parent.parent()


class ScrollableToolbarContent(QScrollArea):
    """可滚动的工具栏内容区域"""
    
    def __init__(self, toolbar, parent=None):
        super().__init__(parent)
        self.toolbar = toolbar
        self.sections: Dict[str, Union[CollapsibleSection, QWidget]] = {}
        
        self.setup_scroll_area()
        self.setup_content_widget()
    
    def setup_scroll_area(self) -> None:
        """设置滚动区域"""
        self.setObjectName("scrollableContent")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setFrameStyle(QFrame.NoFrame)
        
        # 设置滚动条样式
        self.setStyleSheet("""
            QScrollArea#scrollableContent {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.5);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar:vertical[darkTheme="true"] {
                background: rgba(0, 0, 0, 0.2);
            }
            QScrollBar::handle:vertical[darkTheme="true"] {
                background: rgba(255, 255, 255, 0.4);
            }
            QScrollBar::handle:vertical:hover[darkTheme="true"] {
                background: rgba(255, 255, 255, 0.6);
            }
        """)
    
    def setup_content_widget(self) -> None:
        """设置内容组件"""
        self.content_widget = QWidget()
        self.content_widget.setObjectName("scrollContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 8, 0)  # 右侧留空间给滚动条
        self.content_layout.setSpacing(0)  # 设置为0，让折叠的标签完全贴合
        
        self.setWidget(self.content_widget)
    
    def add_section(self, section_id: str, title: str, content_widget: QWidget, 
                   collapsible: bool = True, start_collapsed: bool = False) -> Union[CollapsibleSection, QWidget]:
        """添加一个区域"""
        if collapsible:
            section = CollapsibleSection(title, content_widget, self.content_widget)
            if start_collapsed:
                section.collapse()
        else:
            # 非折叠区域，直接添加内容，并添加小的间距
            section = QWidget()
            section_layout = QVBoxLayout(section)
            section_layout.setContentsMargins(0, 0, 0, 4)  # 底部添加小间距
            section_layout.addWidget(content_widget)
        
        self.sections[section_id] = section
        self.content_layout.addWidget(section)
        
        return section
    
    def get_section(self, section_id: str) -> Optional[Union[CollapsibleSection, QWidget]]:
        """获取指定区域"""
        return self.sections.get(section_id)
    
    def collapse_all_sections(self) -> None:
        """折叠所有区域"""
        for section in self.sections.values():
            if isinstance(section, CollapsibleSection) and not section.is_collapsed:
                section.collapse()
    
    def expand_all_sections(self) -> None:
        """展开所有区域"""
        for section in self.sections.values():
            if isinstance(section, CollapsibleSection) and section.is_collapsed:
                section.expand()
    
    def get_total_content_height(self) -> int:
        """获取内容的总高度"""
        return self.content_widget.sizeHint().height()
    
    def is_scrollable(self) -> bool:
        """检查内容是否需要滚动"""
        content_height = self.get_total_content_height()
        viewport_height = self.viewport().height()
        return content_height > viewport_height
    
    def scroll_to_section(self, section_id: str) -> None:
        """滚动到指定区域"""
        section = self.get_section(section_id)
        if section:
            # 确保区域可见
            self.ensureWidgetVisible(section, 0, 50)
    
    def get_visible_content_height(self) -> int:
        """获取当前可见内容的实际高度（考虑折叠状态）"""
        total_height = 0
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, CollapsibleSection):
                    # 对于可折叠区域，根据折叠状态计算高度
                    if widget.is_collapsed:
                        total_height += widget.header.sizeHint().height() + 1  # 标题高度 + 分隔线
                    else:
                        total_height += widget.sizeHint().height()
                else:
                    # 对于普通区域，直接使用sizeHint
                    total_height += widget.sizeHint().height()
                
                # 添加布局间距
                if i < self.content_layout.count() - 1:
                    total_height += self.content_layout.spacing()
        
        return total_height
    
    def _on_content_changed(self):
        """内容变化时的回调，通知工具栏重新计算大小"""
        if hasattr(self.toolbar, 'on_content_size_changed'):
            # 延迟执行，确保所有动画和布局更新完成
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(250, self.toolbar.on_content_size_changed)


class ToolbarSizeManager:
    """工具栏尺寸管理器"""
    
    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.min_height = 200  # 降低最小高度，让工具栏可以更紧凑
        self.max_height = 800
        self.preferred_height = 650
        self.screen_height_ratio = 0.8  # 最大使用屏幕高度的80%
    
    def get_screen_height(self) -> int:
        """获取屏幕可用高度"""
        try:
            from PyQt5.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                return screen.availableGeometry().height()
        except:
            pass
        return 1080  # 默认值
    
    def calculate_optimal_size(self, visible_content_height: int) -> tuple:
        """根据可见内容高度计算最优尺寸"""
        screen_height = self.get_screen_height()
        max_allowed_height = int(screen_height * self.screen_height_ratio)
        
        # 标题栏高度
        title_height = self.toolbar.title_container.sizeHint().height() if self.toolbar.title_container else 50
        
        # 计算内容区域需要的高度（加上内边距）
        content_padding = 20  # 内容区域的上下边距
        total_needed_height = title_height + visible_content_height + content_padding
        
        # 确定最终高度
        if total_needed_height <= self.min_height:
            # 内容很少时，使用最小高度
            final_height = self.min_height
        elif total_needed_height <= max_allowed_height:
            # 内容适中，使用实际需要的高度
            final_height = total_needed_height
        else:
            # 内容过多，限制在最大允许高度内，此时需要滚动
            final_height = max_allowed_height
        
        # 计算最优宽度（基于字体大小调整）
        base_width = 380
        font_scale = getattr(self.toolbar, 'font_size', 11) / 11.0
        optimal_width = int(base_width * font_scale)
        # 确保宽度在合理范围内
        optimal_width = max(320, min(optimal_width, 500))
        
        return optimal_width, final_height
    
    def should_use_scrolling(self, visible_content_height: int) -> bool:
        """判断是否需要使用滚动"""
        _, calculated_height = self.calculate_optimal_size(visible_content_height)
        title_height = self.toolbar.title_container.sizeHint().height() if self.toolbar.title_container else 50
        content_padding = 20
        available_content_height = calculated_height - title_height - content_padding
        
        return visible_content_height > available_content_height
