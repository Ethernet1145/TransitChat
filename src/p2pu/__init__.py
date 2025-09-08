"""
P2P网络核心功能模块
提供网络通信、地址管理和唯一标识生成等基础功能
"""

from .core_utils import (
    get_or_create_uid,
    create_room_uid,
    send_json,
    receive_json,
    get_current_time,
    generate_session_id,
    validate_ip_address,
    get_local_ip
)
from .ipv4_utils import (
    get_ipv4_addresses,
    create_ipv4_socket,
    is_ipv4_address,
    get_best_ipv4_address,
    get_public_ipv4,
    is_behind_nat
)
from .ipv6_utils import (
    get_ipv6_addresses,
    create_dual_stack_socket,
    check_ipv6_connectivity,
    ensure_ipv6_support,
    is_ipv6_address,
    get_all_network_addresses,
    prefer_ipv6_connections,
    resolve_hostname,
    connect_to_any_address,
    get_public_ipv6
)

# 按功能分组导出
__all__ = [
    # 核心工具
    'get_or_create_uid',
    'create_room_uid',
    'send_json',
    'receive_json',
    'get_current_time',
    'generate_session_id',

    # 网络诊断
    'validate_ip_address',
    'get_local_ip',
    'is_behind_nat',

    # IPv4功能
    'get_ipv4_addresses',
    'create_ipv4_socket',
    'is_ipv4_address',
    'get_best_ipv4_address',
    'get_public_ipv4',

    # IPv6功能
    'get_ipv6_addresses',
    'create_dual_stack_socket',
    'check_ipv6_connectivity',
    'ensure_ipv6_support',
    'is_ipv6_address',
    'get_public_ipv6',

    # 高级网络功能
    'get_all_network_addresses',
    'prefer_ipv6_connections',
    'resolve_hostname',
    'connect_to_any_address'
]

# 版本信息
__version__ = "3.1.0"
__author__ = "P2P开发团队"
__description__ = "P2P网络核心功能库"


def get_network_capabilities():
    """获取当前系统的网络能力报告"""
    from .ipv4_utils import get_best_ipv4_address
    from .ipv6_utils import check_ipv6_connectivity

    return {
        "ipv4": {
            "available": bool(get_best_ipv4_address()[0]),
            "public": bool(get_public_ipv4())
        },
        "ipv6": {
            "available": ensure_ipv6_support(),
            "connected": check_ipv6_connectivity()
        },
        "nat": {
            "behind_nat": is_behind_nat()
        }
    }

from .core_utils import get_or_create_uid, create_room_uid, send_json, receive_json, get_current_time
from .ipv4_utils import get_ipv4_addresses, create_ipv4_socket, is_ipv4_address, get_public_ipv4
from .ipv6_utils import (
    get_ipv6_addresses, create_dual_stack_socket, check_ipv6_connectivity,
    ensure_ipv6_support, is_ipv6_address, get_all_network_addresses,
    prefer_ipv6_connections, resolve_hostname, connect_to_any_address,
    get_public_ipv6, print_network_addresses  # 新增导出
)

__all__ = [
    'get_or_create_uid', 'create_room_uid', 'send_json', 'receive_json', 'get_current_time',
    'get_ipv4_addresses', 'create_ipv4_socket', 'is_ipv4_address', 'get_public_ipv4',
    'get_ipv6_addresses', 'create_dual_stack_socket', 'check_ipv6_connectivity',
    'ensure_ipv6_support', 'is_ipv6_address', 'get_all_network_addresses',
    'prefer_ipv6_connections', 'resolve_hostname', 'connect_to_any_address',
    'get_public_ipv6', 'print_network_addresses'  # 新增
]