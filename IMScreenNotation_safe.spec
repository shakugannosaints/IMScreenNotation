# -*- mode: python ; coding: utf-8 -*-
"""
保守优化的PyInstaller spec文件
确保兼容性的同时减小体积
"""

# 数据文件 - 只包含必需的文件
datas = [
    ('1.ico', '.'),
    ('config.json', '.'),
]

# 二进制文件
binaries = []

# 隐藏导入 - 包含所有必需的模块
hiddenimports = [
    # canvas 模块
    'canvas',
    'canvas.drawing_canvas',
    'canvas.events',
    'canvas.painter',
    'canvas.properties',
    'canvas.state_manager',
    'canvas.types',
    
    # toolbar 模块
    'toolbar',
    'toolbar.toolbar',
    'toolbar.toolbar_widgets',
    'toolbar.toolbar_events', 
    'toolbar.toolbar_scrollable',
    'toolbar.toolbar_theme',
    
    # hotkey 模块
    'hotkey',
    'hotkey.hotkey_manager',
    'hotkey.hotkey_handler',
    'hotkey.hotkey_settings',
    
    # manager 模块
    'manager',
    'manager.window_manager',
    'manager.transparency_manager',
    'manager.tool_manager',
    'manager.tray_manager',
    'manager.config_manager',
    
    # ruler 模块
    'ruler',
    'ruler.ruler_manager',
    'ruler.ruler_settings',
    
    # shapes 包及其子模块
    'shapes',
    'shapes.base',
    'shapes.basic',
    'shapes.advanced',
    'shapes.interactive',
    'shapes.ruler',
    
    # text_style 模块
    'text_style',
    'text_style.text_style_dialog',
    'text_style.ui_builder', 
    'text_style.event_handler',
    'text_style.theme_manager',
    'text_style.settings_manager',
    
    # 其他核心模块
    'config',
    'file_operations',
    'constants',
    'utils',
    
    # PyQt5核心模块
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.sip',
    
    # 系统模块（保守包含）
    'sys',
    'os',
    'json',
    'typing',
    'threading',
    'traceback',
    'inspect',  # PyInstaller需要
    'dis',      # PyInstaller需要
]

# 只排除明确不需要的大型模块
excludes = [
    # 数据科学库
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'sklearn',
    'seaborn',
    'plotly',
    
    # Web相关
    'requests',
    'urllib3',
    'tornado',
    'flask',
    'django',
    
    # 测试框架
    'pytest',
    'unittest2',
    'nose',
    'mock',
    
    # 文档工具
    'sphinx',
    'docutils',
    'markdown',
    
    # 不需要的PyQt5模块
    'PyQt5.QtNetwork',
    'PyQt5.QtWebKit',
    'PyQt5.QtWebKitWidgets', 
    'PyQt5.QtWebEngine',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtSql',
    'PyQt5.QtXml',
    'PyQt5.QtXmlPatterns',
    'PyQt5.QtHelp',
    'PyQt5.QtDesigner',
    'PyQt5.QtTest',
    'PyQt5.QtMultimedia',
    'PyQt5.QtMultimediaWidgets',
    'PyQt5.QtOpenGL',
    'PyQt5.QtQml',
    'PyQt5.QtQuick',
    'PyQt5.QtQuickWidgets',
    'PyQt5.QtSvg',
    'PyQt5.QtBluetooth',
    'PyQt5.QtNfc',
    'PyQt5.QtPositioning',
    'PyQt5.QtLocation',
    'PyQt5.QtSensors',
    'PyQt5.QtSerialPort',
    'PyQt5.QtWebChannel',
    'PyQt5.QtWebSockets',
    
    # tkinter (如果不需要)
    'tkinter',
]

# 手动添加PyQt5的核心组件，而不是collect_all
from PyInstaller.utils.hooks import collect_submodules

# 只收集真正需要的PyQt5模块
pyqt5_modules = collect_submodules('PyQt5.QtCore')
pyqt5_modules += collect_submodules('PyQt5.QtGui') 
pyqt5_modules += collect_submodules('PyQt5.QtWidgets')

hiddenimports.extend(pyqt5_modules)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=1,  # 降低优化级别，避免兼容性问题
)

# 轻量的文件过滤，只移除明显不需要的文件
def remove_unused_files(a):
    """移除不需要的文件"""
    
    # 要移除的文件模式（更保守）
    patterns_to_remove = [
        # 只移除明确不需要的Qt模块
        'Qt5Network',
        'Qt5Sql',
        'Qt5Xml',
        'Qt5WebKit',
        'Qt5WebEngine',
        'Qt5Multimedia',
        'Qt5Test',
        
        # 一些翻译文件
        'qt_ar.qm',
        'qt_bg.qm', 
        'qt_cs.qm',
        'qt_da.qm',
        'qt_de.qm',
        'qt_es.qm',
        'qt_fi.qm',
        'qt_fr.qm',
        'qt_he.qm',
        'qt_hu.qm',
        'qt_it.qm',
        'qt_ja.qm',
        'qt_ko.qm',
        'qt_lv.qm',
        'qt_pl.qm',
        'qt_ru.qm',
        'qt_sk.qm',
        'qt_sl.qm',
        'qt_sv.qm',
        'qt_uk.qm',
    ]
    
    # 过滤TOC
    for collection in [a.binaries, a.datas]:
        collection[:] = [
            item for item in collection
            if not any(pattern in item[0] for pattern in patterns_to_remove)
        ]

# 应用文件过滤
remove_unused_files(a)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='IMScreenNotation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # 暂时禁用strip避免问题
    upx=True,   # 保持UPX压缩
    upx_exclude=[
        'vcruntime140.dll',
        'msvcp140.dll', 
        'api-ms-win-*.dll',
        'Qt5Core.dll',  # Qt核心dll不要用UPX压缩
        'Qt5Gui.dll',
        'Qt5Widgets.dll',
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='1.ico',
)
