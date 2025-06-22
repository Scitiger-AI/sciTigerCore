"""
认证管理视图模块
"""

from apps.auth_service.views.management.permission_views import (
    ManagementPermissionViewSet
)

from apps.auth_service.views.management.user_views import (
    UserManagementViewSet
)

from apps.auth_service.views.management.role_views import (
    RoleManagementViewSet
)

from apps.auth_service.views.management.api_key_views import (
    ApiKeyManagementViewSet
)

from apps.auth_service.views.management.auth_views import (
    ManagementLoginView,
    ManagementLogoutView,
    ManagementTokenRefreshView,
    AdminProfileView
)

from apps.auth_service.views.management.service_scope_views import (
    ServiceScopeViewSet
)

from apps.auth_service.views.management.login_attempt_views import (
    LoginAttemptManagementViewSet
)

__all__ = [
    # 权限管理视图
    'ManagementPermissionViewSet',
    
    # 用户管理视图
    'UserManagementViewSet',
    
    # 角色管理视图
    'RoleManagementViewSet',
    
    # API密钥管理视图
    'ApiKeyManagementViewSet',
    
    # 认证管理视图
    'ManagementLoginView',
    'ManagementLogoutView',
    'ManagementTokenRefreshView',
    'AdminProfileView',
    
    # 服务作用域视图
    'ServiceScopeViewSet',
    
    # 登录尝试视图
    'LoginAttemptManagementViewSet',
]
