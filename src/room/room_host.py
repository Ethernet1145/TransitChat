# src/room/room_host.py
import socket
import threading
import time
from ..p2pu import (
    get_or_create_uid, send_json, receive_json, get_all_network_addresses,
    create_dual_stack_socket, get_current_time
)
from ..ui.display_utils import display_system_message, display_network_info, display_chat_message
from ..ui.input_utils import get_input
from ..config.settings import DEFAULT_PORT


class ChatRoomHost:
    def __init__(self, port=DEFAULT_PORT):
        self.uid = get_or_create_uid()
        self.port = port
        self.room_uid = None
        self.room_name = None
        self.clients = {}
        self.running = False
        self.server_socket = None

    def create_room(self, room_name):
        """创建聊天室"""
        self.room_name = room_name
        self.room_uid = f"{room_name}_{self.uid}"[:20]
        return self.room_uid

    def start_hosting(self):
        """开始托管聊天室"""
        try:
            self.server_socket = create_dual_stack_socket()
            if not self.server_socket:
                display_system_message("无法创建服务器socket")
                return False

            # 设置socket选项
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # 绑定到所有接口
            try:
                if hasattr(self.server_socket, 'family') and self.server_socket.family == socket.AF_INET6:
                    self.server_socket.bind(('::', self.port))
                    display_system_message("使用 IPv4/IPv6 双栈模式")
                else:
                    self.server_socket.bind(('0.0.0.0', self.port))
                    display_system_message("使用 IPv4 模式")
            except OSError as e:
                display_system_message(f"绑定端口失败: {e}")
                return False

            self.server_socket.listen(8)
            self.running = True

            # 显示网络信息
            network_info = get_all_network_addresses()
            display_system_message(f"聊天室 '{self.room_name}' 创建成功!")
            display_system_message(f"房间ID: {self.room_uid}")
            display_system_message(f"端口: {self.port}")
            display_network_info(network_info)
            display_system_message("等待用户加入...")
            display_system_message("输入 '/quit' 关闭聊天室")

            # 启动接受连接线程
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()

            # 处理主机消息输入
            self._host_message_loop()
            return True

        except Exception as e:
            display_system_message(f"启动失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _accept_connections(self):
        """接受客户端连接"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_socket.settimeout(30)

                # 处理握手
                handshake = receive_json(client_socket)
                if handshake and handshake.get('type') == 'join_room':
                    client_uid = handshake.get('uid', 'Unknown')
                    room_uid = handshake.get('room_uid', '')

                    if room_uid == self.room_uid:
                        # 验证成功，允许加入
                        send_json(client_socket, {
                            'type': 'join_success',
                            'message': f'欢迎来到聊天室 {self.room_name}',
                            'room_uid': self.room_uid
                        })

                        # 添加到客户端列表
                        self.clients[client_socket] = {
                            'uid': client_uid,
                            'address': address
                        }

                        # 显示连接信息
                        addr_str = f"{address[0]}:{address[1]}" if len(address) == 2 else f"[{address[0]}]:{address[1]}"
                        display_system_message(f"{client_uid} 加入了聊天室 ({addr_str})")

                        # 广播用户加入消息
                        self._broadcast({
                            'type': 'system',
                            'message': f'{client_uid} 加入了聊天室',
                            'sender': '系统',
                            'timestamp': get_current_time()
                        }, exclude=client_socket)

                        # 启动客户端消息处理线程
                        client_thread = threading.Thread(
                            target=self._handle_client,
                            args=(client_socket, client_uid),
                            daemon=True
                        )
                        client_thread.start()
                    else:
                        # Room UID 不匹配
                        send_json(client_socket, {
                            'type': 'join_failed',
                            'message': '无效的房间ID'
                        })
                        client_socket.close()
                else:
                    client_socket.close()

            except OSError:
                break  # Socket closed
            except Exception as e:
                display_system_message(f"接受连接时出错: {e}")
                continue

    def _handle_client(self, client_socket, client_uid):
        """处理客户端消息"""
        while self.running:
            try:
                message_data = receive_json(client_socket)
                if not message_data:
                    break

                if message_data.get('type') == 'message':
                    # 广播聊天消息
                    broadcast_data = {
                        'type': 'message',
                        'message': message_data['message'],
                        'sender': client_uid,
                        'timestamp': get_current_time()
                    }
                    self._broadcast(broadcast_data)

            except Exception as e:
                display_system_message(f"处理客户端消息时出错: {e}")
                break

        # 客户端断开连接
        self._remove_client(client_socket, client_uid)

    def _remove_client(self, client_socket, client_uid):
        """移除客户端"""
        if client_socket in self.clients:
            del self.clients[client_socket]
            try:
                client_socket.close()
            except:
                pass

            display_system_message(f"{client_uid} 离开了聊天室")
            self._broadcast({
                'type': 'system',
                'message': f'{client_uid} 离开了聊天室',
                'sender': '系统',
                'timestamp': get_current_time()
            })

    def _broadcast(self, message_data, exclude=None):
        """广播消息给所有客户端"""
        for client_socket in list(self.clients.keys()):
            if client_socket != exclude:
                try:
                    send_json(client_socket, message_data)
                except:
                    # 发送失败，移除客户端
                    if client_socket in self.clients:
                        client_info = self.clients[client_socket]
                        self._remove_client(client_socket, client_info['uid'])

    def _host_message_loop(self):
        """主机消息循环"""
        while self.running:
            try:
                message = input()
                if not self.running:
                    break

                if message.lower() == '/quit':
                    break

                if message.strip():
                    # 广播主机消息
                    message_data = {
                        'type': 'message',
                        'message': message,
                        'sender': f"{self.uid} (房主)",
                        'timestamp': get_current_time()
                    }
                    self._broadcast(message_data)
                    # 显示自己发送的消息
                    display_chat_message(message_data, is_own_message=True)

            except KeyboardInterrupt:
                break
            except EOFError:
                break

        self.stop_hosting()

    def stop_hosting(self):
        """停止托管"""
        display_system_message("正在关闭聊天室...")
        self.running = False

        # 通知所有客户端
        for client_socket in list(self.clients.keys()):
            try:
                send_json(client_socket, {
                    'type': 'system',
                    'message': '聊天室已关闭',
                    'sender': '系统'
                })
            except:
                pass
            self._remove_client(client_socket, self.clients[client_socket]['uid'])

        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        display_system_message("聊天室已关闭")
        time.sleep(1)


def create_chat_room():
    """创建聊天室函数"""
    from ..ui.display_utils import print_banner
    from ..ui.input_utils import get_input

    print_banner("创建聊天室")

    room_name = get_input("输入聊天室名称", "MyChatRoom")
    if not room_name:
        display_system_message("聊天室创建取消")
        return

    port_input = get_input("输入端口号", str(DEFAULT_PORT))
    try:
        port = int(port_input) if port_input else DEFAULT_PORT
    except ValueError:
        display_system_message("端口号无效，使用默认端口")
        port = DEFAULT_PORT

    host = ChatRoomHost(port)
    room_uid = host.create_room(room_name)

    if host.start_hosting():
        display_system_message(f"聊天室 '{room_name}' 运行结束")
    else:
        display_system_message("聊天室启动失败")

    time.sleep(2)