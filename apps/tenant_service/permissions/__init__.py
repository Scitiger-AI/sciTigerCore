"""
权限模块初始化文件
从core.permissions导入通用权限类
"""

from core.permissions import (
    IsTenantAdmin,
    IsTenantOwner,
    IsTenantMember,
    IsSuperAdmin
)

__all__ = [
    'IsTenantAdmin',
    'IsTenantOwner',
    'IsTenantMember',
    'IsSuperAdmin',
]
