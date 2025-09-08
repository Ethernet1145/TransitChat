import os
import uuid
import json
import socket
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from ..config.settings import DEFAULT_PORT


def get_or_create_uid(uid_file: str = '.uid') -> str:
    """
    获取或创建唯一用户ID
    Args:
        uid_file: 存储UID的文件路径
    Returns:
        用户UID字符串
    """
    try:
        file_path = Path(uid_file)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_uid = f.read().strip()
                if existing_uid:  # 验证现有UID是否有效
                    return existing_uid

        # 生成新UID并保存
        new_uid = str(uuid.uuid4())[:8]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_uid)
        return new_uid
    except Exception as e:
        print(f"无法获取或创建UID: {e}")
        # 紧急情况下的回退方案
        return str(uuid.uuid4())[:8]


def create_room_uid(room_name: str, host_uid: str) -> str:
    """
    创建聊天室唯一ID
    Args:
        room_name: 房间名称
        host_uid: 主机UID
    Returns:
        格式为"房间名_主机UID"的字符串，最多20字符
    """
    base_str = f"{room_name}_{host_uid}"
    # 使用SHA-256哈希确保唯一性，然后截取前20字符
    return hashlib.sha256(base_str.encode()).hexdigest()[:20]


def send_json(sock: socket.socket, data: Dict[str, Any]) -> bool:
    """
    安全发送JSON数据
    Args:
        sock: 已连接的socket对象
        data: 要发送的字典数据
    Returns:
        是否发送成功
    """
    try:
        # 添加数据校验和
        checksum = hashlib.md5(json.dumps(data).encode()).hexdigest()
        data_with_checksum = {
            'payload': data,
            'checksum': checksum,
            'timestamp': get_current_time()
        }

        message = json.dumps(data_with_checksum).encode('utf-8')
        # 先发送消息长度(4字节)
        sock.send(len(message).to_bytes(4, 'big'))
        # 再发送消息内容
        sock.send(message)
        return True
    except (socket.error, TypeError, ValueError) as e:
        print(f"发送JSON失败: {e}")
        return False


def receive_json(sock: socket.socket, buffer_size: int = 4096) -> Optional[Dict[str, Any]]:
    """
    安全接收JSON数据
    Args:
        sock: 已连接的socket对象
        buffer_size: 初始缓冲区大小
    Returns:
        解析后的字典数据或None
    """
    try:
        # 先读取消息长度
        length_bytes = sock.recv(4)
        if not length_bytes:
            return None

        length = int.from_bytes(length_bytes, 'big')
        received = bytearray()

        # 分段接收直到收完所有数据
        while len(received) < length:
            chunk = sock.recv(min(buffer_size, length - len(received)))
            if not chunk:
                break
            received.extend(chunk)

        if not received:
            return None

        data = json.loads(received.decode('utf-8'))

        # 验证校验和
        calculated_checksum = hashlib.md5(json.dumps(data['payload']).encode()).hexdigest()
        if calculated_checksum != data.get('checksum'):
            print("校验和不匹配，数据可能损坏")
            return None

        return data['payload']
    except (socket.error, json.JSONDecodeError, KeyError) as e:
        print(f"接收JSON失败: {e}")
        return None


def get_current_time(fmt: str = "%H:%M:%S") -> str:
    """
    获取当前格式化时间字符串
    Args:
        fmt: 时间格式字符串
    Returns:
        格式化后的时间字符串
    """
    return datetime.now().strftime(fmt)


def validate_ip_address(ip_str: str) -> bool:
    """
    验证IP地址是否有效
    Args:
        ip_str: 要验证的IP地址字符串
    Returns:
        是否是有效的IP地址
    """
    try:
        socket.inet_pton(socket.AF_INET, ip_str)
        return True
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, ip_str)
            return True
        except socket.error:
            return False


def get_local_ip() -> Optional[str]:
    """
    获取本地IP地址(非127.0.0.1)
    Returns:
        本地IP地址字符串或None
    """
    try:
        # 创建一个UDP socket连接到公共DNS
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return None


def generate_session_id() -> str:
    """
    生成会话ID
    Returns:
        基于时间戳和随机数的唯一会话ID
    """
    timestamp = int(datetime.now().timestamp() * 1000)
    random_part = uuid.uuid4().hex[:6]
    return f"{timestamp}-{random_part}"