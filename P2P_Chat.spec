# spec/p2p_chat_detailed.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 添加src目录到Python路径
import sys
import os
sys.path.insert(0, 'src')

# 收集所有需要包含的模块
def collect_modules():
    modules = []
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                # 转换为模块名
                module_name = full_path.replace('src/', '').replace('/', '.').replace('.py', '')
                modules.append(module_name)
    return modules

def collect_data_files():
    data_files = []
    # 包含配置文件
    config_files = []
    for root, dirs, files in os.walk('src/config'):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                config_files.append((full_path, 'config'))

    # 包含可能的其他数据文件
    data_files.extend(config_files)
    return data_files

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=collect_data_files(),
    hiddenimports=collect_modules(),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy'],  # 排除不需要的库
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='p2p_chat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 收集所有依赖文件
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='p2p_chat'
)