# src/utils/import_helper.py
import os
import sys
import importlib


def setup_import_paths():
    """设置导入路径，处理打包环境和开发环境"""
    if getattr(sys, 'frozen', False):
        # 打包环境 - PyInstaller
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 添加基础路径
    if base_path not in sys.path:
        sys.path.insert(0, base_path)

    # 添加src目录
    src_path = os.path.join(base_path, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    return base_path


def dynamic_import(module_path, attribute_name=None):
    """动态导入模块或属性"""
    try:
        if attribute_name:
            module = importlib.import_module(module_path)
            return getattr(module, attribute_name)
        else:
            return importlib.import_module(module_path)
    except ImportError as e:
        print(f"动态导入失败: {module_path}, 错误: {e}")
        return None


# 设置路径
setup_import_paths()