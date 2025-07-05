"""
文件操作模块
处理标注内容的导入导出功能
"""
from typing import TYPE_CHECKING
from PyQt5.QtWidgets import QFileDialog
from constants import JSON_FILE_FILTER, STATUS_MESSAGE_TIMEOUT

if TYPE_CHECKING:
    from main import AnnotationTool


class FileOperations:
    """文件操作管理器"""
    
    def __init__(self, main_window: 'AnnotationTool'):
        self.main_window = main_window
    
    def import_canvas_content(self) -> None:
        """导入标注内容"""
        file_name, _ = QFileDialog.getOpenFileName(
            self.main_window, 
            "导入标注", 
            "", 
            JSON_FILE_FILTER
        )
        if file_name:
            try:
                with open(file_name, "r") as f:
                    json_data: str = f.read()
                self.main_window.canvas.from_json_data(json_data)
                self.main_window._status_bar.showMessage("标注导入成功", STATUS_MESSAGE_TIMEOUT)
            except Exception as e:
                self.main_window._status_bar.showMessage(f"导入失败: {e}", STATUS_MESSAGE_TIMEOUT)
    
    def export_canvas_content(self) -> None:
        """导出标注内容"""
        file_name, _ = QFileDialog.getSaveFileName(
            self.main_window, 
            "导出标注", 
            "", 
            JSON_FILE_FILTER
        )
        if file_name:
            try:
                json_data: str = self.main_window.canvas.to_json_data()
                with open(file_name, "w") as f:
                    f.write(json_data)
                self.main_window._status_bar.showMessage("标注导出成功", STATUS_MESSAGE_TIMEOUT)
            except Exception as e:
                self.main_window._status_bar.showMessage(f"导出失败: {e}", STATUS_MESSAGE_TIMEOUT)
