"""
用户授权认证服务视图模块
"""

from apps.auth_service.views.platform import (
    PermissionViewSet,
    LoginView,
    TokenRefreshView,
    RegisterView
)

from apps.auth_service.views.management import (
    ManagementPermissionViewSet
)

__all__ = [
    # 平台视图
    'PermissionViewSet',
    'LoginView',
    'TokenRefreshView',
    'RegisterView',
    
    # 管理视图
    'ManagementPermissionViewSet',
]
