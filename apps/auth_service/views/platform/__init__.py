"""
认证平台视图模块
"""

from apps.auth_service.views.platform.auth_views import (
    LoginView,
    LogoutView,
    TokenRefreshView,
    RegisterView
)

from apps.auth_service.views.platform.permission_views import (
    PermissionViewSet
)

from apps.auth_service.views.platform.user_views import (
    UserViewSet
)

from apps.auth_service.views.platform.role_views import (
    RoleViewSet
)

from apps.auth_service.views.platform.api_key_views import (
    ApiKeyViewSet,
    VerifyApiKeyView
)

from apps.auth_service.views.platform.microservice_auth_views import (
    MicroserviceVerifyTokenView,
    MicroserviceVerifyApiKeyView
)

__all__ = [
    # 认证视图
    'LoginView',
    'LogoutView',
    'TokenRefreshView',
    'RegisterView',
    
    # 权限视图
    'PermissionViewSet',
    
    # 用户视图
    'UserViewSet',
    
    # 角色视图
    'RoleViewSet',
    
    # API密钥视图
    'ApiKeyViewSet',
    'VerifyApiKeyView',
    
    # 微服务认证视图
    'MicroserviceVerifyTokenView',
    'MicroserviceVerifyApiKeyView',
]
