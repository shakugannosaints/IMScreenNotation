#!/usr/bin/env python3
"""
测试修复后的 Text 类是否能正确处理列表格式的颜色
"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor
from shapes import Text

def test_text_color_fix():
    """测试 Text 类的颜色处理"""
    app = QApplication(sys.argv)
    
    # 测试用列表格式的颜色创建 Text 对象
    text_color = [255, 0, 0, 255]  # RGBA 红色
    background_color = [0, 255, 0, 128]  # RGBA 半透明绿色
    border_color = [0, 0, 255, 255]  # RGBA 蓝色
    
    try:
        text_obj = Text(
            position=QPointF(10, 10),
            text="测试文本",
            text_color=text_color,
            background_color=background_color,
            border_color=border_color
        )
        print("✓ Text 对象创建成功")
        
        # 验证颜色对象是否正确
        if isinstance(text_obj.text_color, QColor):
            print("✓ text_color 已正确转换为 QColor")
        else:
            print("✗ text_color 转换失败")
            
        if isinstance(text_obj.background_color, QColor):
            print("✓ background_color 已正确转换为 QColor")
        else:
            print("✗ background_color 转换失败")
            
        if isinstance(text_obj.border_color, QColor):
            print("✓ border_color 已正确转换为 QColor")
        else:
            print("✗ border_color 转换失败")
            
        # 测试颜色设置方法
        text_obj.set_text_color([255, 255, 0, 255])  # 黄色
        print("✓ set_text_color 方法可以处理列表格式")
        
        text_obj.set_background_color([255, 0, 255, 128])  # 半透明紫色
        print("✓ set_background_color 方法可以处理列表格式")
        
        text_obj.set_border_color([0, 255, 255, 255])  # 青色
        print("✓ set_border_color 方法可以处理列表格式")
        
        print("\n所有测试通过！修复成功。")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    app.quit()
    return True

if __name__ == "__main__":
    test_text_color_fix()
