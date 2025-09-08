import socket
import ipaddress
import platform
from typing import Dict, List, Optional

try:
    import ifaddr
except ImportError:
    ifaddr = None


def get_network_interfaces() -> Dict[str, Dict]:
    """
    获取详细的网络接口信息
    返回字典结构: {
        "接口名": {
            "ipv4": [{"address": str, "netmask": str, "is_public": bool}],
            "ipv6": [{"address": str, "scope": str}],
            "mac": Optional[str],
            "status": str
        }
    }
    """

    def detect_interface_status(interface_name: str) -> str:
        """检测接口状态（Linux/Windows）"""
        if platform.system() == 'Linux':
            try:
                with open(f'/sys/class/net/{interface_name}/operstate') as f:
                    return 'up' if 'up' in f.read() else 'down'
            except:
                return 'unknown'
        return 'up'  # 其他系统默认认为接口是活跃的

    interfaces = {}

    # 优先使用ifaddr获取详细信息
    if ifaddr:
        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            interface_name = adapter.name
            interfaces[interface_name] = {
                'ipv4': [],
                'ipv6': [],
                'mac': getattr(adapter, 'nice_name', None),
                'status': detect_interface_status(interface_name)
            }

            for ip in adapter.ips:
                try:
                    if ip.is_IPv4:
                        ip_obj = ipaddress.IPv4Address(ip.ip)
                        interfaces[interface_name]['ipv4'].append({
                            'address': ip.ip,
                            'netmask': prefix_to_netmask(ip.network_prefix),
                            'is_public': not ip_obj.is_private,
                            'is_link_local': ip_obj.is_link_local
                        })
                    elif ip.is_IPv6:
                        ip_obj = ipaddress.IPv6Address(ip.ip.split('%')[0])
                        interfaces[interface_name]['ipv6'].append({
                            'address': ip.ip,
                            'scope': get_ipv6_scope(ip_obj),
                            'is_link_local': ip_obj.is_link_local
                        })
                except Exception as e:
                    print(f"解析接口 {interface_name} IP地址失败: {e}")
        return interfaces

    # ifaddr不可用时的回退方案
    return get_basic_network_info()


def prefix_to_netmask(prefix_len: int) -> str:
    """将前缀长度转换为子网掩码"""
    if not 0 <= prefix_len <= 32:
        return '255.255.255.0'
    mask = (0xffffffff << (32 - prefix_len)) & 0xffffffff
    return socket.inet_ntoa(mask.to_bytes(4, 'big'))


def get_ipv6_scope(ip_obj: ipaddress.IPv6Address) -> str:
    """判断IPv6地址作用域"""
    if ip_obj.is_link_local:
        return 'link-local'
    elif ip_obj.is_private:
        return 'unique-local'
    elif ip_obj.is_global:
        return 'global'
    return 'unknown'


def get_basic_network_info() -> Dict[str, Dict]:
    """基础网络信息获取（不使用ifaddr）"""
    interfaces = {}
    hostname = socket.gethostname()

    try:
        # 获取所有网络接口（Linux/Windows）
        if platform.system() == 'Linux':
            import netifaces
            for iface in netifaces.interfaces():
                interfaces[iface] = {
                    'ipv4': [],
                    'ipv6': [],
                    'mac': None,
                    'status': 'up'
                }
        else:
            interfaces['default'] = {
                'ipv4': [],
                'ipv6': [],
                'mac': None,
                'status': 'up'
            }

        # IPv4地址
        for addr in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = addr[4][0]
            ip_obj = ipaddress.IPv4Address(ip)
            for iface in interfaces:
                interfaces[iface]['ipv4'].append({
                    'address': ip,
                    'netmask': '255.255.255.0',
                    'is_public': not ip_obj.is_private,
                    'is_link_local': ip_obj.is_link_local
                })

        # IPv6地址
        for addr in socket.getaddrinfo(hostname, None, socket.AF_INET6):
            ip = addr[4][0].split('%')[0]
            ip_obj = ipaddress.IPv6Address(ip)
            for iface in interfaces:
                interfaces[iface]['ipv6'].append({
                    'address': ip,
                    'scope': get_ipv6_scope(ip_obj),
                    'is_link_local': ip_obj.is_link_local
                })

    except Exception as e:
        print(f"获取基础网络信息失败: {e}")

    return interfaces