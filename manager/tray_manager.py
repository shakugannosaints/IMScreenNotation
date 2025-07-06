"""
系统托盘管理模块
"""
from typing import TYPE_CHECKING, Optional
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QStyle
from PyQt5.QtGui import QIcon
from utils import load_icon_with_fallback, create_default_icon
from constants import (TRAY_TOOLTIP, TRAY_NOTIFICATION_TITLE, 
                      TRAY_NOTIFICATION_MESSAGE, TRAY_NOTIFICATION_TIMEOUT,
                      STATUS_MESSAGE_TIMEOUT)

if TYPE_CHECKING:
    from main import AnnotationTool


class TrayManager:
    """系统托盘管理器"""
    
    def __init__(self, main_window: 'AnnotationTool'):
        self.main_window = main_window
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.tray_icon_visible: bool = False
    
    def setup_system_tray(self) -> None:
        """设置系统托盘"""
        # 检查系统是否支持系统托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("系统托盘不可用")
            return
        
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self.main_window)
        
        # 断言确保 tray_icon 不为 None
        assert self.tray_icon is not None
        
        # 设置托盘图标
        icon = self._load_tray_icon()
        self.tray_icon.setIcon(icon)
        print(f"托盘图标设置完成，图标有效性: {not icon.isNull()}")
        
        # 设置托盘提示
        self.tray_icon.setToolTip(TRAY_TOOLTIP)
        
        # 创建托盘菜单
        self._create_tray_menu()
        
        # 托盘图标单击事件
        self.tray_icon.activated.connect(self._tray_icon_activated)
        
        # 默认不显示托盘图标
        self.tray_icon_visible = False
    
    def _load_tray_icon(self) -> QIcon:
        """加载托盘图标"""
        try:
            # 尝试加载1.ico文件
            icon = load_icon_with_fallback("1.ico")
            if not icon.isNull():
                return icon
        except Exception as e:
            print(f"加载托盘图标失败: {e}")
        
        # 尝试使用系统标准图标
        try:
            style = self.main_window.style()
            if style:
                icon = style.standardIcon(QStyle.SP_ComputerIcon)
                if not icon.isNull():
                    return icon
        except Exception as e:
            print(f"使用系统图标失败: {e}")
        
        # 最后使用默认图标
        return create_default_icon()
    
    def _create_tray_menu(self) -> None:
        """创建托盘菜单"""
        tray_menu: QMenu = QMenu()
        
        # 显示主窗口动作
        show_action: QAction = QAction("显示主窗口", self.main_window)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)
        
        # 分隔符
        tray_menu.addSeparator()
        
        # 退出动作
        quit_action: QAction = QAction("退出程序", self.main_window)
        quit_action.triggered.connect(self.main_window.close_application)
        tray_menu.addAction(quit_action)
        
        # 设置托盘菜单
        if self.tray_icon:
            self.tray_icon.setContextMenu(tray_menu)
    
    def show_from_tray(self) -> None:
        """从托盘恢复窗口显示"""
        # 显示主窗口和工具栏
        self.main_window.show()
        # 只在非穿透模式下激活主窗口，避免抢夺焦点
        if not getattr(self.main_window, 'passthrough_state', False):
            self.main_window.activateWindow()
        self.main_window.raise_()
        
        # 显示工具栏
        if hasattr(self.main_window, 'toolbar'):
            self.main_window.toolbar.show()
            self.main_window.toolbar_completely_hidden = False
            # 直接调用确保工具栏在最前面的逻辑
            if (hasattr(self.main_window, 'toolbar') and 
                self.main_window.toolbar and 
                not self.main_window.toolbar_completely_hidden):
                self.main_window.toolbar.raise_()
                # 只在非穿透模式下激活工具栏，避免抢夺焦点
                if not getattr(self.main_window, 'passthrough_state', False):
                    self.main_window.toolbar.activateWindow()
                self.main_window.toolbar.show()
        
        # 隐藏托盘图标
        if self.tray_icon is not None:
            self.tray_icon.hide()
            self.tray_icon_visible = False
        
        self.main_window._status_bar.showMessage("窗口已从托盘恢复", STATUS_MESSAGE_TIMEOUT)
        print("窗口已从托盘恢复")
    
    def _tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """托盘图标被点击"""
        if reason == QSystemTrayIcon.Trigger:  # 左键单击
            self.show_from_tray()
        elif reason == QSystemTrayIcon.DoubleClick:  # 双击
            self.show_from_tray()
    
    def hide_to_tray(self) -> None:
        """隐藏到系统托盘"""
        # 隐藏主窗口
        self.main_window.hide()
        
        # 隐藏工具栏
        if hasattr(self.main_window, 'toolbar'):
            self.main_window.toolbar.hide()
        
        self.main_window.toolbar_completely_hidden = True
        
        # 显示托盘图标
        if (self.tray_icon is not None and 
            QSystemTrayIcon.isSystemTrayAvailable()):
            self.tray_icon.show()
            self.tray_icon_visible = True
            # 显示托盘通知
            self.tray_icon.showMessage(
                TRAY_NOTIFICATION_TITLE,
                TRAY_NOTIFICATION_MESSAGE,
                QSystemTrayIcon.Information,
                TRAY_NOTIFICATION_TIMEOUT
            )
        
        print("程序已隐藏到系统托盘")
    
    def cleanup(self) -> None:
        """清理托盘资源"""
        if self.tray_icon is not None:
            self.tray_icon.hide()
