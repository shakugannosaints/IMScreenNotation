#!/usr/bin/env python3
"""
体积优化构建脚本
目标：将打包体积从120MB减少到30-50MB
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """清理构建目录"""
    print("🧹 清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"  删除目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理.pyc文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
        
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))

def analyze_current_size():
    """分析当前打包体积"""
    print("📊 分析当前构建体积...")
    
    dist_dir = Path('dist')
    if dist_dir.exists():
        exe_files = list(dist_dir.glob('*.exe'))
        if exe_files:
            current_size = exe_files[0].stat().st_size / 1024 / 1024
            print(f"  当前体积: {current_size:.2f} MB")
            return current_size
    
    print("  未找到现有的可执行文件")
    return None

def check_dependencies():
    """检查依赖项"""
    print("🔍 检查依赖项...")
    
    required_files = [
        'main.py',
        'gui.py', 
        'toolbar/toolbar.py',
        'hotkey/hotkey_manager.py',
        'config.py',
        'shapes/__init__.py',  # shapes 现在是一个包
        '1.ico',
        'config.json'
    ]
    
    missing_files = []
    for file_name in required_files:
        if not os.path.exists(file_name):
            missing_files.append(file_name)
    
    if missing_files:
        print(f"  ❌ 缺少文件: {missing_files}")
        return False
    
    print("  ✅ 所有依赖文件都存在")
    return True

def install_upx():
    """安装UPX压缩工具"""
    print("🔧 检查UPX压缩工具...")
    
    # 检查是否在CI环境中
    is_ci = any(env_var in os.environ for env_var in ['CI', 'GITHUB_ACTIONS', 'GITHUB_WORKFLOW'])
    
    # 检查多个可能的UPX路径（包括GitHub Actions常用路径）
    upx_paths = [
        r"C:\ProgramData\chocolatey\bin\upx.exe",
        r"C:\tools\upx\upx.exe", 
        "upx.exe",  # PATH中
        "/usr/bin/upx",  # Linux路径
        "/usr/local/bin/upx",  # Linux路径
        "upx",  # 通用命令
    ]
    
    for upx_path in upx_paths:
        if os.path.exists(upx_path) or shutil.which(upx_path):
            print(f"  ✅ 找到UPX: {upx_path}")
            return upx_path
    
    print("  ❌ 未找到UPX压缩工具")
    
    if is_ci:
        print("  🤖 在CI环境中运行，自动继续构建（不使用UPX）")
        print("  💡 可以在GitHub Actions中安装UPX:")
        print("     - 添加步骤: sudo apt-get install upx-ucl (Ubuntu)")
        print("     - 添加步骤: choco install upx (Windows)")
        return False
    else:
        print("  💡 建议安装UPX以获得更好的压缩效果:")
        print("     方法1: choco install upx")
        print("     方法2: 从 https://upx.github.io/ 下载")
        
        # 询问是否继续（仅在非CI环境中）
        try:
            response = input("  是否继续构建（不使用UPX）？ [y/N]: ")
            if response.lower() != 'y':
                return None
        except (EOFError, KeyboardInterrupt):
            # 处理在无交互环境中运行的情况
            print("  🤖 检测到无交互环境，自动继续构建")
        
        return False

def build_with_optimized_spec():
    """使用优化的spec文件构建"""
    print("🚀 使用安全优化spec文件构建...")
    
    spec_file = "IMScreenNotation_safe.spec"
    
    if not os.path.exists(spec_file):
        print(f"  ❌ 找不到安全优化的spec文件: {spec_file}")
        return False
    
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        spec_file
    ]
    
    try:
        print("  🔄 开始构建...")
        print(f"  📝 执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
        
        print(f"  📤 标准输出:")
        if result.stdout:
            # 只显示最后几行重要输出
            stdout_lines = result.stdout.strip().split('\n')
            for line in stdout_lines[-10:]:  # 显示最后10行
                print(f"    {line}")
        
        if result.stderr:
            print(f"  ⚠️  标准错误:")
            stderr_lines = result.stderr.strip().split('\n')
            for line in stderr_lines[-5:]:  # 显示最后5行错误
                print(f"    {line}")
        
        if result.returncode == 0:
            print("  ✅ 构建成功!")
            
            # 立即检查构建结果
            print("  🔍 检查构建输出:")
            dist_dir = Path('dist')
            if dist_dir.exists():
                files = list(dist_dir.iterdir())
                print(f"    📁 dist目录包含 {len(files)} 个项目:")
                for item in files:
                    if item.is_file():
                        size_mb = item.stat().st_size / 1024 / 1024
                        print(f"      📄 {item.name}: {size_mb:.2f} MB")
                    else:
                        print(f"      📁 {item.name}/")
            
            return True
        else:
            print(f"  ❌ 构建失败，退出代码: {result.returncode}")
            return False
    
    except Exception as e:
        print(f"  ❌ 构建过程中发生错误: {e}")
        return False

def build_with_minimal_approach():
    """使用最小化方法构建（备选方案）"""
    print("🎯 使用最小化方法构建...")
    
    cmd = [
        'pyinstaller',
        '--clean',
        '--onefile',
        '--windowed',
        '--name=IMScreenNotation_minimal',
        '--icon=1.ico',
        '--optimize=2',
        '--strip',
        
        # 只添加必需的数据文件
        '--add-data=1.ico;.',
        '--add-data=config.json;.',
        
        # 只包含必需的模块
        '--hidden-import=gui',
        '--hidden-import=toolbar.toolbar',
        '--hidden-import=toolbar.toolbar_widgets',
        '--hidden-import=toolbar.toolbar_events',
        '--hidden-import=toolbar.toolbar_scrollable', 
        '--hidden-import=toolbar.toolbar_theme',
        '--hidden-import=hotkey.hotkey_manager',
        '--hidden-import=hotkey.hotkey_settings',
        '--hidden-import=config',
        '--hidden-import=shapes',
        '--hidden-import=shapes.base',
        '--hidden-import=shapes.basic',
        '--hidden-import=shapes.advanced',
        '--hidden-import=shapes.interactive',
        '--hidden-import=text_style_dialog',
        '--hidden-import=packaging_fix',
        '--hidden-import=manager.window_manager',
        '--hidden-import=manager.transparency_manager',
        '--hidden-import=manager.tool_manager',
        '--hidden-import=manager.tray_manager',
        '--hidden-import=file_operations',
        '--hidden-import=hotkey.hotkey_handler',
        '--hidden-import=manager.config_manager',
        '--hidden-import=constants',
        '--hidden-import=utils',
        '--hidden-import=inspect',  # PyInstaller需要
        '--hidden-import=dis',      # PyInstaller需要
        
        # 排除大型模块
        '--exclude-module=matplotlib',
        '--exclude-module=numpy', 
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=tkinter',
        '--exclude-module=PyQt5.QtNetwork',
        '--exclude-module=PyQt5.QtWebKit',
        '--exclude-module=PyQt5.QtWebEngine',
        '--exclude-module=PyQt5.QtSql',
        '--exclude-module=PyQt5.QtXml',
        '--exclude-module=PyQt5.QtMultimedia',
        '--exclude-module=PyQt5.QtOpenGL',
        '--exclude-module=PyQt5.uic',
        
        'main.py'
    ]
    
    try:
        print("  🔄 开始最小化构建...")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("  ✅ 最小化构建成功!")
            return True
        else:
            print(f"  ❌ 最小化构建失败: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"  ❌ 最小化构建错误: {e}")
        return False

def analyze_build_result():
    """分析构建结果"""
    print("📈 分析构建结果...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("  ❌ dist目录不存在")
        return False
    
    # 检查dist目录内容
    all_files = list(dist_dir.iterdir())
    print(f"  📁 dist目录包含 {len(all_files)} 个文件/目录:")
    for item in all_files:
        if item.is_file():
            size_mb = item.stat().st_size / 1024 / 1024
            print(f"    📄 {item.name}: {size_mb:.2f} MB")
        else:
            print(f"    📁 {item.name}/")
    
    # 查找可执行文件（包括不同平台的可执行文件）
    executable_files = []
    
    # 检测操作系统
    import platform
    is_windows = platform.system() == 'Windows'
    
    if is_windows:
        # Windows: 查找.exe文件
        exe_files = list(dist_dir.glob('*.exe'))
        executable_files.extend(exe_files)
        print(f"  🔍 在Windows上查找.exe文件: 找到 {len(exe_files)} 个")
    else:
        # Linux/macOS: 查找无扩展名的可执行文件
        print(f"  🔍 在{platform.system()}上查找可执行文件...")
        
        # 优先查找已知的可执行文件名
        known_names = ['IMScreenNotation', 'IMScreenNotation_minimal', 'main']
        for name in known_names:
            exe_path = dist_dir / name
            if exe_path.exists() and exe_path.is_file():
                executable_files.append(exe_path)
                print(f"    ✅ 找到已知可执行文件: {name}")
        
        # 如果没找到已知文件，查找所有无扩展名且可执行的文件
        if not executable_files:
            for item in dist_dir.iterdir():
                if item.is_file() and not item.suffix:
                    # 检查是否是可执行文件（有执行权限或包含特定关键词）
                    if (os.access(item, os.X_OK) or 
                        any(keyword in item.name.lower() for keyword in ['imscreen', 'notation', 'main', 'app'])):
                        executable_files.append(item)
                        print(f"    ✅ 找到可执行文件: {item.name}")
    
    # 也检查任何大文件（可能是打包的可执行文件）
    if not executable_files:
        print("  🔍 未找到明确的可执行文件，检查大文件...")
        large_files = [f for f in all_files if f.is_file() and f.stat().st_size > 10 * 1024 * 1024]  # 大于10MB
        if large_files:
            print(f"    发现 {len(large_files)} 个大文件，可能是可执行文件:")
            for f in large_files:
                size_mb = f.stat().st_size / 1024 / 1024
                print(f"    � {f.name}: {size_mb:.2f} MB")
            executable_files.extend(large_files)
    
    if not executable_files:
        print("  ❌ 未找到任何可执行文件")
        print("  💡 构建可能失败或可执行文件在其他位置")
        return False
    
    print(f"  ✅ 分析 {len(executable_files)} 个可执行文件:")
    for exe_file in executable_files:
        file_size = exe_file.stat().st_size / 1024 / 1024
        print(f"  📦 {exe_file.name}: {file_size:.2f} MB")
        
        # 提供体积评估
        if file_size < 30:
            print(f"    ✅ 优秀！体积很小")
        elif file_size < 50:
            print(f"    👍 良好！体积合理")
        elif file_size < 80:
            print(f"    ⚠️  一般，还有优化空间")
        else:
            print(f"    ❌ 体积过大，需要进一步优化")
    
    return True

def provide_optimization_tips():
    """提供进一步优化建议"""
    print("\n💡 进一步优化建议:")
    print("1. 如果体积仍然过大，考虑:")
    print("   - 移除不必要的功能模块")
    print("   - 使用更轻量的GUI框架（如tkinter）")
    print("   - 考虑使用目录模式而非单文件模式")
    
    print("\n2. 替代压缩方案:")
    print("   - 7-Zip压缩最终的exe文件")
    print("   - 使用NSIS创建安装程序")
    
    print("\n3. 运行时优化:")
    print("   - 延迟加载某些模块")
    print("   - 使用插件架构")

def main():
    print("=" * 50)
    print("🎯 IMScreenNotation 体积优化构建脚本")
    print("   目标：将体积从120MB减少到30-50MB")
    print("=" * 50)
    
    # 1. 分析当前体积
    current_size = analyze_current_size()
    
    # 2. 清理构建目录
    clean_build_dirs()
    
    # 3. 检查依赖项
    if not check_dependencies():
        print("❌ 依赖项检查失败，退出构建")
        sys.exit(1)
    
    # 4. 检查UPX
    upx_result = install_upx()
    if upx_result is None:
        print("❌ 用户取消构建")
        sys.exit(1)
    
    # 5. 尝试优化构建
    build_success = False
    
    # 首先尝试使用优化的spec文件
    if build_with_optimized_spec():
        build_success = True
    else:
        print("⚠️  优化spec构建失败，尝试最小化方法...")
        if build_with_minimal_approach():
            build_success = True
    
    if not build_success:
        print("❌ 所有构建方法都失败了")
        sys.exit(1)
    
    # 6. 分析结果
    if not analyze_build_result():
        print("❌ 结果分析失败")
        sys.exit(1)
    
    # 7. 提供优化建议
    provide_optimization_tips()
    
    print("\n" + "=" * 50)
    print("🎉 优化构建完成！")
    print("📁 可执行文件位于 dist/ 目录中")
    print("🧪 请测试所有功能以确保正常工作")
    print("=" * 50)

if __name__ == "__main__":
    main()
