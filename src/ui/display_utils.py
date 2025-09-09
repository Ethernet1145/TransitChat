# src/ui/display_utils.py
import os
import sys

# 处理打包环境的导入问题
try:
    # 尝试直接导入
    from src.config.settings import DISPLAY_WIDTH, LEFT_ALIGN, RIGHT_ALIGN
except ImportError:
    # 如果直接导入失败，尝试添加路径
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    try:
        from config.settings import DISPLAY_WIDTH, LEFT_ALIGN, RIGHT_ALIGN
    except ImportError:
        # 如果还是失败，使用默认值
        DISPLAY_WIDTH = 80
        LEFT_ALIGN = "LEFT"
        RIGHT_ALIGN = "RIGHT"


def clear_screen():
    """清屏函数"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_centered(text, width=DISPLAY_WIDTH):
    """居中打印文本"""
    padding = (width - len(text)) // 2
    print(" " * max(0, padding) + text)


def print_banner(title):
    """打印横幅"""
    print("=" * DISPLAY_WIDTH)
    print_centered(title)
    print("=" * DISPLAY_WIDTH)


def format_message(message, alignment, sender=None, timestamp=None):
    """格式化消息显示"""
    # 动态导入，避免循环导入问题
    try:
        from src.p2pu.core_utils import get_current_time
    except ImportError:
        from src.p2pu.core_utils import get_current_time

    if timestamp is None:
        timestamp = get_current_time()

    time_part = f"[{timestamp}] "
    sender_part = f"{sender}: " if sender and alignment == LEFT_ALIGN else ""
    message_text = f"{sender_part}{message}"

    # 计算布局
    if alignment == RIGHT_ALIGN:
        padding = DISPLAY_WIDTH - len(time_part) - len(message_text) - 2
        return f"{' ' * max(0, padding)}{time_part}{message_text}"
    else:
        return f"{time_part}{message_text}"


def display_chat_message(message_data, is_own_message=False):
    """显示聊天消息"""
    if is_own_message:
        formatted = format_message(
            message_data.get('message', ''),
            RIGHT_ALIGN,
            timestamp=message_data.get('timestamp')
        )
        print(formatted)
    else:
        formatted = format_message(
            message_data.get('message', ''),
            LEFT_ALIGN,
            sender=message_data.get('sender', 'Unknown'),
            timestamp=message_data.get('timestamp')
        )
        print(formatted)


def display_system_message(message):
    """显示系统消息"""
    print(f"\n[系统] {message}")
    print("> ", end="", flush=True)


def display_network_info(network_info):
    """显示网络信息"""
    print("网络状态:")
    print("-" * 40)
    print(f"IPv4 支持: {'是' if network_info.get('ipv4') else '否'}")
    print(f"IPv6 支持: {'是' if network_info.get('ipv6_available', False) else '否'}")

    if network_info.get('ipv4'):
        print("IPv4 地址:")
        for ip in network_info['ipv4']:
            print(f"  {ip}")

    if network_info.get('ipv6'):
        print("IPv6 地址:")
        for ip in network_info['ipv6']:
            print(f"  {ip}")
    print("-" * 40)