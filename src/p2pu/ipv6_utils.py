import socket
import ipaddress
import platform
import subprocess
import time
from typing import List, Optional, Dict, Tuple
from .ipv4_utils import create_ipv4_socket, get_ipv4_addresses, get_public_ipv4


def get_ipv6_addresses() -> List[str]:
    """获取所有IPv6地址"""
    ipv6_addresses = []
    try:
        hostname = socket.gethostname()
        addrinfos = socket.getaddrinfo(hostname, None, socket.AF_INET6, socket.SOCK_STREAM)

        for addrinfo in addrinfos:
            addr = addrinfo[4][0]
            try:
                # 处理带作用域的地址
                if isinstance(addr, tuple):
                    addr = addr[0]  # IPv6地址通常是元组的第一个元素

                ip_obj = ipaddress.IPv6Address(addr.split('%')[0])
                if (not ip_obj.is_loopback and
                        not ip_obj.is_link_local and
                        not ip_obj.is_private):
                    ipv6_addresses.append(addr)
            except:
                continue

    except Exception as e:
        print(f"获取IPv6地址失败: {e}")

    return list(set(ipv6_addresses))


def create_dual_stack_socket():
    """创建双栈socket"""
    try:
        # 尝试创建IPv6双栈socket
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock
    except:
        # 回退到IPv4
        return create_ipv4_socket()


def check_ipv6_connectivity() -> bool:
    """检查IPv6连通性"""
    try:
        test_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        test_socket.settimeout(5)
        test_socket.connect(('2400:3200::1', 80))
        test_socket.close()
        return True
    except:
        return False


def ensure_ipv6_support() -> bool:
    """确保IPv6支持"""
    if check_ipv6_connectivity():
        return True
    return False


def is_ipv6_address(ip_str: str) -> bool:
    """检查是否为IPv6地址"""
    try:
        ipaddress.IPv6Address(ip_str)
        return True
    except:
        return False


def get_all_network_addresses() -> Dict:
    """获取所有网络地址（修复缺失的函数）"""
    ipv4_addresses = get_ipv4_addresses()
    public_ipv4 = get_public_ipv4()
    ipv6_available = ensure_ipv6_support()
    ipv6_addresses = get_ipv6_addresses() if ipv6_available else []
    public_ipv6 = None

    # 获取公网IPv6
    if ipv6_available:
        for addr in ipv6_addresses:
            try:
                ip_obj = ipaddress.IPv6Address(addr.split('%')[0])
                if ip_obj.is_global:
                    public_ipv6 = addr
                    break
            except:
                continue

    return {
        'ipv4': {
            'all': ipv4_addresses,
            'public': public_ipv4,
            'private': [ip for ip in ipv4_addresses if ipaddress.IPv4Address(ip).is_private]
        },
        'ipv6': {
            'all': ipv6_addresses,
            'public': public_ipv6,
            'global': [ip for ip in ipv6_addresses
                       if ipaddress.IPv6Address(ip.split('%')[0]).is_global]
        },
        'ipv6_available': ipv6_available
    }


def prefer_ipv6_connections(hostname: str, port: int) -> Optional[socket.socket]:
    """优先尝试IPv6连接"""
    try:
        # 获取所有地址信息
        addrinfos = socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM)

        # 分离IPv4和IPv6地址
        ipv6_addresses = []
        ipv4_addresses = []

        for addrinfo in addrinfos:
            family, socktype, proto, canonname, sockaddr = addrinfo
            if family == socket.AF_INET6:
                ipv6_addresses.append(sockaddr)
            elif family == socket.AF_INET:
                ipv4_addresses.append(sockaddr)

        # 优先尝试IPv6连接
        all_addresses = ipv6_addresses + ipv4_addresses

        for addr in all_addresses:
            try:
                if len(addr) == 2:  # IPv4: (host, port)
                    family = socket.AF_INET
                else:  # IPv6: (host, port, flowinfo, scopeid)
                    family = socket.AF_INET6

                sock = socket.socket(family, socket.SOCK_STREAM)
                sock.settimeout(8)
                sock.connect(addr)
                return sock
            except socket.error:
                continue

    except Exception as e:
        print(f"解析主机名失败: {e}")

    return None


def resolve_hostname(hostname: str, port: int) -> List:
    """解析主机名，返回所有地址"""
    addresses = []
    try:
        addrinfos = socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM)

        for addrinfo in addrinfos:
            family, socktype, proto, canonname, sockaddr = addrinfo
            addresses.append(sockaddr)

    except Exception as e:
        print(f"解析主机名失败: {e}")

    return addresses


def connect_to_any_address(addresses: List, timeout: int = 10) -> Optional[socket.socket]:
    """尝试连接到地址列表中的任何一个"""
    for addr in addresses:
        try:
            if len(addr) == 2:  # IPv4: (host, port)
                family = socket.AF_INET
            else:  # IPv6: (host, port, flowinfo, scopeid)
                family = socket.AF_INET6

            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect(addr)
            return sock

        except Exception:
            continue

    return None


def get_public_ipv6() -> Optional[str]:
    """获取公网IPv6地址"""
    ipv6_addresses = get_ipv6_addresses()
    for addr in ipv6_addresses:
        try:
            ip_obj = ipaddress.IPv6Address(addr.split('%')[0])
            if ip_obj.is_global:
                return addr
        except:
            continue
    return None


def print_network_addresses():
    """打印所有网络地址信息（新增功能）"""
    network_info = get_all_network_addresses()

    print("\n=== 网络地址信息 ===")

    # IPv4信息
    print("IPv4地址:")
    if network_info['ipv4']['public']:
        print(f"  公网IPv4: {network_info['ipv4']['public']}")

    if network_info['ipv4']['private']:
        print("  内网IPv4:")
        for ip in network_info['ipv4']['private']:
            print(f"    - {ip}")

    # IPv6信息
    print("IPv6地址:")
    if network_info['ipv6']['public']:
        print(f"  公网IPv6: {network_info['ipv6']['public']}")

    if network_info['ipv6']['global']:
        print("  全局IPv6:")
        for ip in network_info['ipv6']['global']:
            print(f"    - {ip}")

    if network_info['ipv6']['all'] and not network_info['ipv6']['public']:
        print("  检测到IPv6地址但无公网IPv6")

    print("=" * 50)