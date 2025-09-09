# src/room/room_join.py
import socket
import threading
import time
from ..p2pu import (
    get_or_create_uid, send_json, receive_json, get_current_time,
    prefer_ipv6_connections, is_ipv4_address, is_ipv6_address
)
from ..ui.display_utils import display_system_message, display_chat_message
from ..ui.input_utils import get_input
from ..config.settings import DEFAULT_PORT


class ChatRoomClient:
    def __init__(self, port=DEFAULT_PORT):
        self.uid = get_or_create_uid()
        self.port = port
        self.socket = None
        self.connected = False
        self.room_uid = None
        self.room_name = "未知房间"

    def join_room(self, host_input, room_uid):
        """加入聊天室"""
        try:
            self.room_uid = room_uid

            # 解析主机地址
            if is_ipv4_address(host_input) or is_ipv6_address(host_input):
                # 直接使用IP地址
                if ':' in host_input:  # IPv6
                    address = (host_input, self.port)
                else:  # IPv4
                    address = (host_input, self.port)

                family = socket.AF_INET6 if ':' in host_input else socket.AF_INET
                self.socket = socket.socket(family, socket.SOCK_STREAM)
                self.socket.settimeout(10)
                self.socket.connect(address)

            else:
                # 使用主机名，优先IPv6连接
                self.socket = prefer_ipv6_connections(host_input, self.port)
                if not self.socket:
                    display_system_message("无法连接到服务器")
                    return False

            self.connected = True

            # 发送加入请求
            join_request = {
                'type': 'join_room',
                'uid': self.uid,
                'room_uid': self.room_uid
            }

            if not send_json(self.socket, join_request):
                display_system_message("发送加入请求失败")
                return False

            # 等待服务器响应
            response = receive_json(self.socket)
            if response and response.get('type') == 'join_success':
                welcome_msg = response.get('message', '成功加入聊天室!')
                display_system_message(welcome_msg)
                display_system_message("输入 '/quit' 退出聊天室")

                # 启动消息接收线程
                receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
                receive_thread.start()

                # 启动消息发送
                self._send_messages()
                return True
            else:
                error_msg = response.get('message', '加入聊天室失败') if response else '服务器无响应'
                display_system_message(f"加入失败: {error_msg}")
                return False

        except socket.timeout:
            display_system_message("连接超时")
        except ConnectionRefusedError:
            display_system_message("连接被拒绝，服务器可能未启动")
        except Exception as e:
            display_system_message(f"连接失败: {e}")

        return False

    def _receive_messages(self):
        """接收消息"""
        while self.connected:
            try:
                message_data = receive_json(self.socket)
                if not message_data:
                    break

                message_type = message_data.get('type')

                if message_type == 'message':
                    # 显示他人消息（左对齐，带名字）
                    display_chat_message(message_data, is_own_message=False)
                    print("> ", end="", flush=True)

                elif message_type == 'system':
                    # 显示系统消息
                    display_system_message(message_data.get('message', ''))
                    print("> ", end="", flush=True)

                elif message_type == 'room_closing':
                    display_system_message("聊天室即将关闭")
                    break

            except Exception as e:
                display_system_message(f"接收消息时出错: {e}")
                break

        display_system_message("已断开与聊天室的连接")
        self.connected = False
        self._cleanup()

    def _send_messages(self):
        """发送消息"""
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

                    if send_json(self.socket, message_data):
                        # 显示自己发送的消息（右对齐，不带名字）
                        display_chat_message(message_data, is_own_message=True)
                    else:
                        display_system_message("发送消息失败")
                        break

            except KeyboardInterrupt:
                break
            except EOFError:
                break

        self.connected = False
        self._cleanup()

    def _cleanup(self):
        """清理连接"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None


def join_chat_room():
    """加入聊天室函数"""
    from ..ui.display_utils import print_banner
    from ..ui.input_utils import get_input

    print_banner("加入聊天室")

    host_input = get_input("输入聊天室主机地址 (IP/主机名)")
    if not host_input:
        display_system_message("加入聊天室取消")
        return

    room_uid = get_input("输入聊天室ID")
    if not room_uid:
        display_system_message("需要聊天室ID才能加入")
        return

    port_input = get_input("输入端口号", str(DEFAULT_PORT))
    try:
        port = int(port_input) if port_input else DEFAULT_PORT
    except ValueError:
        display_system_message("端口号无效，使用默认端口")
        port = DEFAULT_PORT

    client = ChatRoomClient(port)
    success = client.join_room(host_input, room_uid)

    if success:
        # 等待连接结束
        while client.connected:
            time.sleep(1)
    else:
        display_system_message("加入聊天室失败")

    time.sleep(2)