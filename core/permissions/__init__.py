"""
权限模块初始化文件
"""

from core.permissions.base_permissions import (
    IsSuperAdmin,
    IsTenantMember,
    IsTenantAdmin,
    IsTenantOwner
)

__all__ = [
    'IsSuperAdmin',
    'IsTenantMember',
    'IsTenantAdmin',
    'IsTenantOwner'
]
