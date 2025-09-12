#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransitChat 构建脚本
版本: 0.1.0
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_banner():
    """打印横幅"""
    print("=" * 50)
    print("       TransitChat v0.1.0 构建脚本")
    print("=" * 50)


def check_python():
    """检查Python环境"""
    try:
        result = subprocess.run([sys.executable, '--version'],
                                capture_output=True, text=True, check=True)
        print(f"Python版本: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到Python或Python不可用")
        return False


def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        subprocess.run([sys.executable, '-c', 'import pyinstaller'],
                       capture_output=True, check=True)
        print("PyInstaller: 已安装")
        return True
    except subprocess.CalledProcessError:
        print("安装PyInstaller...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
                           check=True)
            print("PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("错误: PyInstaller安装失败")
            return False


def clean_build():
    """清理构建文件"""
    directories = ['build', 'dist', '__pycache__']
    files = [f for f in os.listdir('.') if f.endswith('.spec')]

    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"清理目录: {directory}")

    for file in files:
        os.remove(file)
        print(f"清理文件: {file}")


def build_transitchat():
    """构建TransitChat"""
    # 检查图标文件
    icon_option = '--icon=icon.ico' if os.path.exists('icon.ico') else ''
    if not icon_option:
        print("警告: 未找到icon.ico，使用默认图标")

    # 构建命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=TransitChat',
        icon_option,
        '--add-data=src;src',
        '--add-data=version.py;.',
        '--add-data=icon.ico;.',
        '--hidden-import=p2pu.core_utils',
        '--hidden-import=p2pu.ipv4_utils',
        '--hidden-import=p2pu.ipv6_utils',
        '--hidden-import=ui.display_utils',
        '--hidden-import=ui.input_utils',
        '--hidden-import=config.settings',
        '--hidden-import=direct.direct_chat',
        '--hidden-import=room.room_host',
        '--hidden-import=room.room_join',
        '--hidden-import=version',
        '--console',
        '--clean',
        '--onedir',
        '--noconfirm',
        'src/main.py'
    ]

    # 移除空参数
    cmd = [arg for arg in cmd if arg]

    print("执行构建命令...")
    print("命令:", ' '.join(cmd))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print("错误输出:", e.stderr)
        return False


def main():
    """主函数"""
    print_banner()

    # 检查环境
    if not check_python():
        return False

    if not check_pyinstaller():
        return False

    # 清理旧构建
    print("\n清理旧构建文件...")
    clean_build()

    # 执行构建
    print("\n开始构建TransitChat...")
    if build_transitchat():
        print("\n" + "=" * 50)
        print("构建成功完成！")
        print("程序名称: TransitChat")
        print("版本号: v0.1.0 Beta")
        print("输出位置: dist/TransitChat/")
        print("主程序: dist/TransitChat/TransitChat.exe")
        print("=" * 50)
        return True
    else:
        print("\n构建失败！")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)