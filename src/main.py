import os
import sys
import time
from src.p2pu import get_or_create_uid, get_all_network_addresses
from src.ui.display_utils import clear_screen, print_banner, display_network_info
from src.ui.input_utils import get_choice
from src.config.settings import DEFAULT_PORT

# 处理打包后的路径问题
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_path)


def show_startup_animation():
    """显示启动动画"""
    clear_screen()
    banner = r"""
 ________    _______  ________           ________  ___  ___  ________  _________   
|\   __  \  /  ___  \|\   __  \         |\   ____\|\  \|\  \|\   __  \|\___   ___\ 
\ \  \|\  \/__/|_/  /\ \  \|\  \        \ \  \___|\ \  \\\  \ \  \|\  \|___ \  \_| 
 \ \   ____\__|//  / /\ \   ____\        \ \  \    \ \   __  \ \   __  \   \ \  \  
  \ \  \___|   /  /_/__\ \  \___|         \ \  \____\ \  \ \  \ \  \ \  \   \ \  \ 
   \ \__\     |\________\ \__\             \ \_______\ \__\ \__\ \__\ \__\   \ \__\
    \|__|      \|_______|\|__|              \|_______|\|__|\|__|\|__|\|__|    \|__|                                                   
    """
    print("\033[1;36m" + banner + "\033[0m")  # 青色加粗文字

    # 模拟加载进度
    print("\n初始化系统...")
    for i in range(1, 6):
        time.sleep(0.3)
        print(f"⏳ 加载模块 [{'=' * i}{' ' * (5 - i)}] {i * 20}%", end='\r')
    print("\n")


def show_main_menu():
    """显示主菜单"""
    clear_screen()
    print_banner("P2P 链接聊天系统")
    print(f"端口号: {DEFAULT_PORT}")
    print(f"你的UID: {get_or_create_uid()}")

    try:
        network_info = get_all_network_addresses()
        display_network_info(network_info)
    except Exception as e:
        print(f"获取网络信息失败: {e}")

    options = [
        "创建新的聊天室",
        "加入聊天室",
        "点对点直接聊天",
        "退出程序"
    ]

    return get_choice(options, "主菜单")


def main():
    show_startup_animation()
    print("\033[1;32m✓ 系统准备就绪\033[0m\n")
    time.sleep(1)

    while True:
        try:
            choice = show_main_menu()

            if choice is None:  # 用户取消
                continue

            if choice == 0:
                from room.room_host import create_chat_room
                create_chat_room()
            elif choice == 1:
                from room.room_join import join_chat_room
                join_chat_room()
            elif choice == 2:
                from direct.direct_chat import start_direct_chat
                start_direct_chat()
            elif choice == 3:
                print("\n\033[1;35m感谢使用P2P链接聊天系统，再见！\033[0m")
                break

        except Exception as e:
            print(f"\033[1;31m发生错误: {e}\033[0m")
            import traceback
            traceback.print_exc()
            input("按回车继续...")


if __name__ == "__main__":
    main()