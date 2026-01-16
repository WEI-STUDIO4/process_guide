#!/usr/bin/env python3
"""
工序按键引导程序打包脚本
使用PyInstaller将Python脚本打包为可执行文件
"""

import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """检查是否安装了PyInstaller"""
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
        return True
    except ImportError:
        print("✗ PyInstaller未安装")
        print("请运行: pip install pyinstaller")
        return False

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✓ 已清理目录: {dir_name}")
            except Exception as e:
                print(f"✗ 清理目录失败 {dir_name}: {e}")

def build_executable():
    """使用PyInstaller构建可执行文件"""
    print("\n开始构建可执行文件...")
    
    # PyInstaller命令参数
    # --onefile: 打包为单个可执行文件
    # --windowed: 不显示控制台窗口（GUI应用）
    # --name: 可执行文件名称
    # --icon: 图标文件（如果有）
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'ProcessKeyGuide',
        'process_guide.py'
    ]
    
    try:
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 构建成功完成")
        
        # 显示构建输出
        if result.stdout:
            print("构建输出:", result.stdout[:500])  # 只显示前500字符
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        if e.stderr:
            print("错误输出:", e.stderr)
        return False
    except FileNotFoundError:
        print("✗ 找不到PyInstaller，请确保已安装")
        return False

def create_zip_package():
    """创建ZIP打包文件"""
    print("\n创建ZIP打包文件...")
    
    dist_dir = 'dist'
    exe_name = 'ProcessKeyGuide.exe'
    zip_name = 'ProcessKeyGuide-windows.zip'
    
    exe_path = os.path.join(dist_dir, exe_name)
    zip_path = os.path.join(dist_dir, zip_name)
    
    if not os.path.exists(exe_path):
        print(f"✗ 找不到可执行文件: {exe_path}")
        return False
    
    try:
        import zipfile
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(exe_path, exe_name)
            print(f"✓ 已创建ZIP文件: {zip_path}")
        
        # 显示文件大小
        file_size = os.path.getsize(zip_path) / (1024 * 1024)  # MB
        print(f"✓ ZIP文件大小: {file_size:.2f} MB")
        
        return True
    except Exception as e:
        print(f"✗ 创建ZIP文件失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("工序按键引导程序 - 打包工具")
    print("=" * 60)
    
    # 检查当前目录
    if not os.path.exists('process_guide.py'):
        print("✗ 错误: 请在项目根目录运行此脚本")
        print(f"当前目录: {os.getcwd()}")
        return 1
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return 1
    
    # 清理旧构建
    print("\n清理旧构建文件...")
    clean_build_dirs()
    
    # 构建可执行文件
    if not build_executable():
        return 1
    
    # 创建ZIP包
    if not create_zip_package():
        return 1
    
    print("\n" + "=" * 60)
    print("打包完成！")
    print("=" * 60)
    print("\n生成的文件:")
    print(f"  可执行文件: dist/ProcessKeyGuide.exe")
    print(f"  打包文件:   dist/ProcessKeyGuide-windows.zip")
    print("\n下一步:")
    print("  1. 测试dist/ProcessKeyGuide.exe是否正常运行")
    print("  2. 将ZIP文件分发给其他Windows用户")
    print("  3. 用户无需安装Python即可运行")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
