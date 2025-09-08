import socket
import ipaddress
import requests
from typing import List, Dict, Tuple, Optional

try:
    import ifaddr  # 替代netifaces的轻量级方案
except ImportError:
    ifaddr = None


def get_ipv4_addresses():
    """获取所有IPv4地址"""
    ipv4_addresses = []
    try:
        hostname = socket.gethostname()
        addrinfos = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)

        for addrinfo in addrinfos:
            addr = addrinfo[4][0]
            try:
                ip_obj = ipaddress.IPv4Address(addr)
                if not ip_obj.is_loopback and not ip_obj.is_link_local:
                    ipv4_addresses.append(addr)
            except:
                continue

    except Exception as e:
        print(f"获取IPv4地址失败: {e}")

    return list(set(ipv4_addresses))


def create_ipv4_socket():
    """创建IPv4 socket"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock
    except Exception as e:
        print(f"创建IPv4 socket失败: {e}")
        return None


def is_ipv4_address(ip_str):
    """检查是否为IPv4地址"""
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except:
        return False


def get_public_ipv4() -> Optional[str]:
    """获取公网IPv4地址"""
    services = [
        'https://api.ipify.org',
        'https://ident.me',
        'https://ifconfig.me/ip'
    ]
    for service in services:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except:
            continue
    return None


def get_best_ipv4_address() -> Tuple[Optional[str], bool]:
    """获取最佳IPv4地址，返回(地址, 是否是公网)"""
    try:
        # 先尝试获取公网IP
        public_ip = get_public_ipv4()
        if public_ip:
            return public_ip, True

        # 使用ifaddr获取接口IP
        if ifaddr:
            adapters = ifaddr.get_adapters()
            for adapter in adapters:
                for ip in adapter.ips:
                    if ip.is_IPv4:
                        ip_str = ip.ip
                        if not ipaddress.IPv4Address(ip_str).is_private:
                            return ip_str, True

            # 返回第一个私有地址
            for adapter in adapters:
                for ip in adapter.ips:
                    if ip.is_IPv4:
                        return ip.ip, False
        else:
            # 回退到socket方案
            ipv4_addresses = get_ipv4_addresses()
            for addr in ipv4_addresses:
                if not ipaddress.IPv4Address(addr).is_private:
                    return addr, True

            if ipv4_addresses:
                return ipv4_addresses[0], False

        return None, False
    except Exception as e:
        print(f"获取最佳IPv4地址失败: {e}")
        return None, False


def is_behind_nat():
    return None