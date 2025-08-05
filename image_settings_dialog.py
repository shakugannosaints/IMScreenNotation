"""
图片设置对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSlider, QGroupBox, QGridLayout,
                             QLineEdit, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from shapes.image import Image


class ImageSettingsDialog(QDialog):
    """图片设置对话框"""
    
    def __init__(self, parent=None, image_shape=None):
        super().__init__(parent)
        self.image_shape = image_shape
        self.selected_image_path = ""
        
        self.setWindowTitle("图片设置")
        self.setModal(True)
        self.setMinimumSize(400, 300)
        
        self.setup_ui()
        
        # 如果是编辑现有图片，加载当前设置
        if self.image_shape:
            self.load_current_settings()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 图片选择组
        image_group = QGroupBox("图片选择")
        image_layout = QGridLayout(image_group)
        
        # 图片路径显示
        image_layout.addWidget(QLabel("图片文件:"), 0, 0)
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setReadOnly(True)
        self.image_path_edit.setPlaceholderText("请选择图片文件...")
        image_layout.addWidget(self.image_path_edit, 0, 1)
        
        # 选择文件按钮
        self.select_file_btn = QPushButton("选择文件")
        self.select_file_btn.clicked.connect(self.select_image_file)
        image_layout.addWidget(self.select_file_btn, 0, 2)
        
        layout.addWidget(image_group)
        
        # 图片属性组
        props_group = QGroupBox("图片属性")
        props_layout = QGridLayout(props_group)
        
        # 缩放比例控制
        props_layout.addWidget(QLabel("缩放比例:"), 0, 0)
        self.scale_label = QLabel("100%")
        props_layout.addWidget(self.scale_label, 0, 1)
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(10)  # 10%
        self.scale_slider.setMaximum(500)  # 500%
        self.scale_slider.setValue(100)  # 100%
        self.scale_slider.valueChanged.connect(self.update_scale_label)
        props_layout.addWidget(self.scale_slider, 1, 0, 1, 2)
        
        layout.addWidget(props_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def select_image_file(self):
        """选择图片文件"""
        file_path = Image.select_image_file(self)
        if file_path:
            self.selected_image_path = file_path
            self.image_path_edit.setText(file_path)
    
    def update_scale_label(self, value):
        """更新缩放比例标签"""
        self.scale_label.setText(f"{value}%")
    
    def load_current_settings(self):
        """加载当前图片的设置"""
        if self.image_shape:
            # 设置图片路径
            self.selected_image_path = self.image_shape.image_path
            self.image_path_edit.setText(self.image_shape.image_path)
            
            # 设置缩放比例
            scale_percent = int(self.image_shape.scale_factor * 100)
            self.scale_slider.setValue(scale_percent)
            self.scale_label.setText(f"{scale_percent}%")
    
    def get_settings(self):
        """获取设置结果"""
        if not self.selected_image_path:
            return None
        
        return {
            'image_path': self.selected_image_path,
            'scale_factor': self.scale_slider.value() / 100.0
        }
    
    def accept(self):
        """确认设置"""
        if not self.selected_image_path:
            QMessageBox.warning(self, "警告", "请先选择图片文件！")
            return
        
        # 验证图片文件是否存在且可读
        try:
            test_pixmap = QPixmap(self.selected_image_path)
            if test_pixmap.isNull():
                QMessageBox.warning(self, "错误", "无法加载选择的图片文件！")
                return
        except Exception as e:
            QMessageBox.warning(self, "错误", f"图片文件加载失败：{e}")
            return
        
        super().accept()
    
    @staticmethod
    def get_image_settings(parent=None, image_shape=None):
        """静态方法：获取图片设置"""
        dialog = ImageSettingsDialog(parent, image_shape)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_settings()
        return None
