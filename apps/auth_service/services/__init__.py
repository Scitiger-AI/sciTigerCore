"""
认证服务模块
"""

from apps.auth_service.services.auth_service import AuthService
from apps.auth_service.services.permission_service import PermissionService
from apps.auth_service.services.user_service import UserService
from apps.auth_service.services.role_service import RoleService
from apps.auth_service.services.api_key_service import ApiKeyService
from apps.auth_service.services.service_scope_service import ServiceScopeService

__all__ = [
    'AuthService',
    'PermissionService',
    'UserService',
    'RoleService',
    'ApiKeyService',
    'ServiceScopeService',
]
