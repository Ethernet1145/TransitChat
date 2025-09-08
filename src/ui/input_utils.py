# src/ui/input_utils.py
import sys
import os

# 添加路径处理
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_path)

try:
    import readline  # 用于输入历史记录
except ImportError:
    # Windows系统可能没有readline
    readline = None


def get_input(prompt, default=None, validator=None):
    """获取用户输入，支持默认值和验证"""
    while True:
        try:
            if default:
                user_input = input(f"{prompt} [{default}]: ").strip()
            else:
                user_input = input(f"{prompt}: ").strip()

            if not user_input and default:
                user_input = default

            if validator:
                if validator(user_input):
                    return user_input
                else:
                    print("输入无效，请重新输入")
            else:
                return user_input

        except KeyboardInterrupt:
            print("\n操作已取消")
            return None
        except EOFError:
            return None


def get_choice(options, prompt="请选择"):
    """获取用户选择"""
    print(f"\n{prompt}:")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = input(f"请输入选项 (1-{len(options)}): ").strip()
            if not choice:
                continue

            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return choice_num - 1
            else:
                print(f"请输入 1-{len(options)} 之间的数字")

        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            return None


def confirm_action(prompt="确认执行此操作吗？"):
    """确认操作"""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes', '是']:
            return True
        elif response in ['n', 'no', '否']:
            return False
        else:
            print("请输入 y/n 或 是/否")