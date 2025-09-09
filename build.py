# build.py
import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build_dirs():
    """清理构建目录"""
    directories = ['build', 'dist', 'spec']
    for dir_name in directories:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理目录: {dir_name}")


def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 添加src目录到Python路径
import sys
sys.path.insert(0, 'src')

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 添加所有Python文件
for dirpath, dirnames, filenames in os.walk('src'):
    for filename in filenames:
        if filename.endswith('.py'):
            module_path = os.path.join(dirpath, filename)
            # 转换为模块格式
            module_name = module_path.replace('src/', '').replace('/', '.').replace('.py', '')
            if module_name not in a.hiddenimports:
                a.hiddenimports.append(module_name)

# 包含配置文件和数据文件
datas = []
for dirpath, dirnames, filenames in os.walk('src'):
    for filename in filenames:
        if filename.endswith('.py') or filename == '.uid':
            continue
        full_path = os.path.join(dirpath, filename)
        # 保持目录结构
        dest_path = os.path.dirname(full_path.replace('src/', ''))
        datas.append((full_path, dest_path))

a.datas += datas

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='p2p_chat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)

# 单文件模式
# exe = EXE(pyz, a.scripts, exclude_binaries=True, name='p2p_chat', debug=False, strip=False, upx=True, console=True)
'''

    os.makedirs('spec', exist_ok=True)
    with open('spec/p2p_chat.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)


def build_with_pyinstaller():
    """使用PyInstaller构建"""
    # 创建spec文件
    create_spec_file()

    # 构建命令
    cmd = [
        'pyinstaller',
        'spec/p2p_chat.spec',
        '--clean',
        '--noconfirm'
    ]

    # 添加平台特定参数
    if sys.platform == 'win32':
        cmd.extend(['--icon', 'assets/icon.ico'] if os.path.exists('assets/icon.ico') else [])
    elif sys.platform == 'darwin':  # macOS
        cmd.extend(['--osx-bundle-identifier', 'com.p2p.chat'])

    print("开始构建...")
    print("执行命令:", ' '.join(cmd))

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("构建失败!")
        print("错误输出:", e.stderr)
        print("标准输出:", e.stdout)
        return False


def create_installer():
    """创建安装包（可选）"""
    if sys.platform == 'win32':
        # 对于Windows，可以使用Inno Setup等工具创建安装程序
        print("Windows安装包创建需要额外配置Inno Setup")
    elif sys.platform == 'darwin':
        print("macOS应用包创建需要额外配置")
    else:
        print("Linux打包需要额外配置")

    # 简单的压缩包方式
    import zipfile
    import datetime

    dist_dir = 'dist/p2p_chat'
    if os.path.exists(dist_dir):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f'p2p_chat_{sys.platform}_{timestamp}.zip'

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, dist_dir)
                    zipf.write(file_path, arcname)

        print(f"已创建压缩包: {zip_filename}")


def main():
    """主构建函数"""
    print("P2P聊天系统打包工具")
    print("=" * 50)

    # 清理旧构建
    if input("是否清理旧构建文件? (y/n): ").lower() in ['y', 'yes']:
        clean_build_dirs()

    # 检查PyInstaller是否安装
    try:
        import pyinstaller
    except ImportError:
        print("PyInstaller未安装，正在安装...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

    # 构建
    if build_with_pyinstaller():
        # 创建安装包
        if input("是否创建分发压缩包? (y/n): ").lower() in ['y', 'yes']:
            create_installer()

        print("\n构建完成!")
        print("可执行文件位于: dist/p2p_chat/")
        print("运行主程序: dist/p2p_chat/p2p_chat")
    else:
        print("\n构建失败，请检查错误信息")


if __name__ == '__main__':
    main()