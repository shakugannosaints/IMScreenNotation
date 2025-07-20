"""
文本编辑对话框
提供多行文本编辑功能，支持编辑已存在的文本标注
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QTimer, QCoreApplication
from PyQt5.QtGui import QFont, QTextCursor, QKeyEvent


class CustomTextEdit(QTextEdit):
    """自定义文本编辑器，支持特殊键盘快捷键"""
    
    def __init__(self, parent_dialog):
        super().__init__()
        self.parent_dialog = parent_dialog
        # 设置输入法属性，优化中文输入体验
        self.setAttribute(Qt.WA_InputMethodEnabled, True)
    
    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件"""
        # 处理 Ctrl+Enter 或 Ctrl+Return 快捷键为确定
        if (event.modifiers() == Qt.ControlModifier and 
            event.key() in (Qt.Key_Return, Qt.Key_Enter)):
            self.parent_dialog.accept_text()
            return
        
        # 处理 Escape 键为取消，但要检查是否在输入法组字状态
        if event.key() == Qt.Key_Escape and not self.isComposing():
            self.parent_dialog.reject()
            return
        
        # 其他键盘事件正常处理
        super().keyPressEvent(event)
    
    def isComposing(self):
        """检查是否在输入法组字状态"""
        try:
            # 通过检查输入法状态来判断是否在组字
            return self.inputMethodQuery(Qt.ImCursorPosition) != self.inputMethodQuery(Qt.ImAnchorPosition)
        except:
            return False


class TextEditDialog(QDialog):
    """文本编辑对话框"""
    
    def __init__(self, parent=None, text="", title="编辑文本"):
        super().__init__(parent)
        self.parent_widget = parent  # 保存父窗口引用
        self.setWindowTitle(title)
        self.setModal(True)
        
        # 设置窗口标志，确保对话框在最顶层且能获得焦点
        self.setWindowFlags(
            Qt.Dialog | 
            Qt.WindowCloseButtonHint | 
            Qt.WindowStaysOnTopHint
        )
        
        # 设置对话框大小
        self.setMinimumSize(400, 300)
        self.resize(500, 400)
        
        self.text_result = text
        self.setup_ui()
        self.text_edit.setPlainText(text)
        
        # 简化焦点设置，避免中断中文输入法
        self._center_on_screen()
    
    def _delayed_focus_setup(self):
        """延迟设置焦点和选中文本（简化版本）"""
        try:
            # 仅设置焦点，不重复激活窗口
            self.text_edit.setFocus()
            self.text_edit.selectAll()
        except Exception as e:
            print(f"Error setting focus: {e}")
    
    def _center_on_screen(self):
        """将对话框居中显示在屏幕上"""
        try:
            desktop = QApplication.desktop()
            screen_geometry = desktop.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
        except Exception as e:
            print(f"Error centering dialog: {e}")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题标签
        title_label = QLabel("请输入或编辑文本内容：")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # 文本编辑器
        self.text_edit = CustomTextEdit(self)
        self.text_edit.setPlaceholderText("在此输入文本内容...\n支持多行文本")
        
        # 设置字体
        font = QFont("SimSun", 12)  # 使用宋体，便于中文显示
        self.text_edit.setFont(font)
        
        # 设置样式
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                background-color: #ffffff;
                selection-background-color: #3399ff;
                font-size: 12px;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border-color: #3399ff;
                outline: none;
            }
        """)
        
        layout.addWidget(self.text_edit)
        
        # 提示标签
        hint_label = QLabel("提示：支持多行文本，使用 Enter 键换行，Ctrl+Enter 确定，Esc 取消\n已优化中文输入法支持，输入期间不会被工具栏定时器中断")
        hint_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #666666;
                font-style: italic;
                line-height: 1.4;
            }
        """)
        layout.addWidget(hint_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(80, 35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border-color: #b0b0b0;
            }
            QPushButton:pressed {
                background-color: #d8d8d8;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.setFixedSize(80, 35)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #3399ff;
                border: 1px solid #2288ee;
                border-radius: 6px;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2288ee;
                border-color: #1177dd;
            }
            QPushButton:pressed {
                background-color: #1177dd;
            }
        """)
        ok_btn.clicked.connect(self.accept_text)
        ok_btn.setDefault(True)  # 设置为默认按钮，可以用 Enter 触发
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 10px;
            }
        """)
        
    def accept_text(self):
        """确认文本输入"""
        text = self.text_edit.toPlainText().strip()
        if not text:
            # 如果文本为空，询问用户是否确认
            reply = QMessageBox.question(
                self, 
                "确认", 
                "文本内容为空，是否要删除此文本标注？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.text_result = ""  # 空文本表示删除
                self.accept()
            return
        
        self.text_result = text
        self.accept()
    
    def get_text(self):
        """获取编辑后的文本"""
        return self.text_result
    
    @staticmethod
    def get_text_input(parent=None, title="文本输入", label="请输入文本:", text=""):
        """静态方法：获取文本输入
        
        Args:
            parent: 父窗口
            title: 对话框标题
            label: 提示文本（暂未使用，保持与QInputDialog兼容）
            text: 初始文本
            
        Returns:
            tuple: (text, ok) - 输入的文本和是否确认
        """
        dialog = TextEditDialog(parent, text, title)
        result = dialog.exec_()
        return dialog.get_text(), result == QDialog.Accepted
    
    def showEvent(self, event):
        """重写显示事件以确保对话框稳定显示"""
        super().showEvent(event)
        
        # 暂停主窗口的工具栏定时器，防止中断中文输入法
        self._pause_toolbar_timer()
        
        # 确保对话框正常显示，但避免过度激活以免中断输入法
        self.raise_()
        # 移除 activateWindow() 调用，减少对输入法的干扰
        
        # 仅在对话框首次显示时设置焦点，使用更长的延迟避免中断输入法
        if not hasattr(self, '_focus_set'):
            self._focus_set = True
            QTimer.singleShot(200, self._initial_focus_setup)
    
    def _pause_toolbar_timer(self):
        """暂停工具栏定时器以避免中断输入法"""
        try:
            if (hasattr(self, 'parent_widget') and 
                self.parent_widget and 
                hasattr(self.parent_widget, 'toolbar_timer')):
                self.parent_widget.toolbar_timer.stop()
                # 设置一个标志，表示对话框正在使用中
                self.parent_widget._text_dialog_active = True
                print("文本编辑对话框：已暂停工具栏定时器")
        except Exception as e:
            print(f"Error pausing toolbar timer: {e}")
    
    def _resume_toolbar_timer(self):
        """恢复工具栏定时器"""
        try:
            if (hasattr(self, 'parent_widget') and 
                self.parent_widget and 
                hasattr(self.parent_widget, 'toolbar_timer') and
                hasattr(self.parent_widget, 'passthrough_state')):
                # 清除对话框活动标志
                self.parent_widget._text_dialog_active = False
                # 只在非穿透模式下恢复定时器
                if not self.parent_widget.passthrough_state:
                    from constants import TOOLBAR_CHECK_INTERVAL
                    self.parent_widget.toolbar_timer.start(TOOLBAR_CHECK_INTERVAL)
                    print("文本编辑对话框：已恢复工具栏定时器")
        except Exception as e:
            print(f"Error resuming toolbar timer: {e}")
    
    def _initial_focus_setup(self):
        """初始焦点设置（仅执行一次）"""
        try:
            if self.isVisible():
                # 使用更温和的方式设置焦点，避免中断输入法
                self.text_edit.setFocus(Qt.OtherFocusReason)
                # 延迟选中文本，给输入法更多时间初始化
                QTimer.singleShot(50, lambda: self.text_edit.selectAll() if self.text_edit.hasFocus() else None)
        except Exception as e:
            print(f"Error in initial focus setup: {e}")
    
    def _ensure_dialog_focus(self):
        """确保对话框保持焦点（移除定期检查以避免中断输入法）"""
        # 移除此方法的实现，因为它会中断中文输入法
        pass
    
    def closeEvent(self, event):
        """重写关闭事件以恢复工具栏焦点"""
        try:
            # 恢复工具栏定时器
            self._resume_toolbar_timer()
            
            # 如果有父窗口，延迟恢复工具栏焦点，避免立即抢夺焦点
            if (hasattr(self, 'parent_widget') and 
                self.parent_widget and 
                hasattr(self.parent_widget, 'window_manager')):
                # 使用较长的延迟，确保对话框完全关闭后再处理工具栏
                QTimer.singleShot(300, self.parent_widget.window_manager.ensure_toolbar_on_top)  # type: ignore
            
            event.accept()
            # 延迟清理资源，避免立即删除造成的问题
            QTimer.singleShot(50, self.deleteLater)
        except Exception as e:
            print(f"Error in close event: {e}")
            event.accept()
