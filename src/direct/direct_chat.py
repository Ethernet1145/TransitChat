# src/direct/direct_chat.py
import socket
import threading
import time

# 处理导入问题 - 使用绝对导入
try:
    # 尝试直接导入
    from src.p2pu.core_utils import get_or_create_uid, receive_json, send_json, get_current_time
    from src.p2pu.ipv4_utils import is_ipv4_address
    from src.p2pu.ipv6_utils import create_dual_stack_socket, get_all_network_addresses, is_ipv6_address
    from src.ui.display_utils import display_chat_message, display_system_message, display_network_info
    from src.ui.input_utils import get_input, get_choice
    from src.config.settings import DEFAULT_PORT
except ImportError:

        # 如果相对导入也失败，使用动态导入
        import sys
        import os

        # 添加路径
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if base_path not in sys.path:
            sys.path.insert(0, base_path)

        # 动态导入
        import importlib

        p2pu_core = importlib.import_module('p2pu.core_utils')
        p2pu_ipv4 = importlib.import_module('p2pu.ipv4_utils')
        p2pu_ipv6 = importlib.import_module('p2pu.ipv6_utils')
        ui_display = importlib.import_module('ui.display_utils')
        ui_input = importlib.import_module('ui.input_utils')
        config_settings = importlib.import_module('config.settings')

        # 获取函数引用
        get_or_create_uid = p2pu_core.get_or_create_uid
        receive_json = p2pu_core.receive_json
        send_json = p2pu_core.send_json
        get_current_time = p2pu_core.get_current_time
        is_ipv4_address = p2pu_ipv4.is_ipv4_address
        create_dual_stack_socket = p2pu_ipv6.create_dual_stack_socket
        get_all_network_addresses = p2pu_ipv6.get_all_network_addresses
        is_ipv6_address = p2pu_ipv6.is_ipv6_address
        display_chat_message = ui_display.display_chat_message
        display_system_message = ui_display.display_system_message
        display_network_info = ui_display.display_network_info
        get_input = ui_input.get_input
        get_choice = ui_input.get_choice
        DEFAULT_PORT = config_settings.DEFAULT_PORT


class DirectChat:
    def __init__(self, port=DEFAULT_PORT):
        self.uid = get_or_create_uid()
        self.port = port
        self.peer_socket = None
        self.connected = False
        self.peer_uid = "Unknown"

    def start_listening(self):
        """启动监听模式"""
        try:
            sock = create_dual_stack_socket()
            if hasattr(sock, 'family') and sock.family == socket.AF_INET6:
                sock.bind(('::', self.port))
            else:
                sock.bind(('0.0.0.0', self.port))
            sock.listen(1)

            network_info = get_all_network_addresses()
            display_system_message("等待连接中...")
            display_network_info(network_info)

            self.peer_socket, address = sock.accept()
            sock.close()

            self._handle_connection(self.peer_socket, address, is_incoming=True)

        except Exception as e:
            display_system_message(f"监听失败: {e}")
            time.sleep(2)

    def connect_to_peer(self, host_input):
        """连接到对等体"""
        try:
            # 解析地址
            addresses = []
            if is_ipv4_address(host_input) or is_ipv6_address(host_input):
                # 直接使用IP地址
                if ':' in host_input:  # IPv6
                    addresses = [(host_input, self.port, 0, 0)]
                else:  # IPv4
                    addresses = [(host_input, self.port)]
            else:
                # 解析主机名
                try:
                    addrinfos = socket.getaddrinfo(host_input, self.port)
                    addresses = [addrinfo[4] for addrinfo in addrinfos]
                except:
                    pass

            if not addresses:
                display_system_message(f"无法解析: {host_input}")
                return

            # 尝试连接
            for addr in addresses:
                try:
                    if len(addr) == 2:  # IPv4
                        family = socket.AF_INET
                    else:  # IPv6
                        family = socket.AF_INET6

                    self.peer_socket = socket.socket(family, socket.SOCK_STREAM)
                    self.peer_socket.settimeout(10)
                    self.peer_socket.connect(addr)
                    self._handle_connection(self.peer_socket, addr, is_incoming=False)
                    return
                except:
                    continue

            display_system_message("所有连接尝试都失败了")

        except Exception as e:
            display_system_message(f"连接失败: {e}")
        time.sleep(2)

    def _handle_connection(self, peer_socket, address, is_incoming):
        """处理连接"""
        self.connected = True

        # 交换UID
        try:
            if is_incoming:
                handshake = receive_json(peer_socket)
                if handshake and handshake.get('type') == 'handshake':
                    self.peer_uid = handshake.get('uid', 'Unknown')
                send_json(peer_socket, {'type': 'handshake', 'uid': self.uid})
            else:
                send_json(peer_socket, {'type': 'handshake', 'uid': self.uid})
                handshake = receive_json(peer_socket)
                if handshake and handshake.get('type') == 'handshake':
                    self.peer_uid = handshake.get('uid', 'Unknown')
        except:
            self.peer_uid = "Unknown"

        display_system_message(f"已连接到 {self.peer_uid}")
        display_system_message("开始聊天吧! (输入 '/quit' 退出)")

        # 启动消息接收线程
        receive_thread = threading.Thread(target=self._receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        self._send_messages()

    def _receive_messages(self):
        """接收消息（他人消息左对齐）"""
        while self.connected:
            try:
                message_data = receive_json(self.peer_socket)
                if not message_data:
                    break

                if message_data.get('type') == 'message':
                    display_chat_message(message_data, is_own_message=False)
                    print("> ", end="", flush=True)

            except:
                break

        display_system_message("连接已断开")
        self.connected = False
        if self.peer_socket:
            self.peer_socket.close()

    def _send_messages(self):
        """发送消息（自己消息右对齐）"""
        while self.connected:
            try:
                message = input("> ")
                if not self.connected:
                    break

                if message.lower() == '/quit':
                    break

                if message.strip():
                    message_data = {
                        'type': 'message',
                        'message': message,
                        'sender': self.uid,
                        'timestamp': get_current_time()
                    }
                    send_json(self.peer_socket, message_data)
                    # 显示自己发送的消息（右对齐）
                    display_chat_message(message_data, is_own_message=True)

            except KeyboardInterrupt:
                break
            except EOFError:
                break

        self.connected = False
        if self.peer_socket:
            self.peer_socket.close()


def start_direct_chat():
    """启动点对点聊天"""
    from ..ui.display_utils import print_banner

    print_banner("点对点直接聊天")

    options = ["等待他人连接", "连接他人", "返回主菜单"]
    choice = get_choice(options)

    if choice == 0:
        chat = DirectChat(DEFAULT_PORT)
        chat.start_listening()
    elif choice == 1:
        host_input = get_input("输入对方地址 (IP/主机名)")
        if host_input:
            chat = DirectChat(DEFAULT_PORT)
            chat.connect_to_peer(host_input)
    # choice == 2: 返回主菜单