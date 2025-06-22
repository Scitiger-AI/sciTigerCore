"""
用户授权认证服务序列化器模块
"""

from apps.auth_service.serializers.permission_serializers import (
    PermissionSerializer,
    PermissionDetailSerializer,
    PermissionCreateSerializer,
    PermissionUpdateSerializer
)

from apps.auth_service.serializers.auth_serializers import (
    LoginSerializer,
    TokenRefreshSerializer,
    LogoutSerializer,
    RegisterSerializer
)

from apps.auth_service.serializers.user_serializers import (
    UserSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    SimpleUserSerializer
)

from apps.auth_service.serializers.role_serializers import (
    RoleSerializer,
    RoleDetailSerializer,
    RoleCreateSerializer,
    RoleUpdateSerializer,
    SimpleRoleSerializer
)

from apps.auth_service.serializers.api_key_serializers import (
    ApiKeySerializer,
    ApiKeyDetailSerializer,
    ApiKeyCreateSerializer,
    SystemApiKeyCreateSerializer,
    UserApiKeyCreateSerializer,
    ApiKeyUpdateSerializer,
    ApiKeyScopeSerializer,
    ApiKeyUsageLogSerializer,
    ApiKeyVerifySerializer,
    ApiKeyHashSerializer
)

from apps.auth_service.serializers.login_attempt_serializers import (
    LoginAttemptSerializer,
    LoginAttemptDetailSerializer
)

__all__ = [
    # 权限序列化器
    'PermissionSerializer',
    'PermissionDetailSerializer',
    'PermissionCreateSerializer',
    'PermissionUpdateSerializer',
    
    # 认证序列化器
    'LoginSerializer',
    'TokenRefreshSerializer',
    'LogoutSerializer',
    'RegisterSerializer',
    
    # 用户序列化器
    'UserSerializer',
    'UserDetailSerializer',
    'UserCreateSerializer',
    'UserUpdateSerializer',
    'ChangePasswordSerializer',
    'SimpleUserSerializer',
    
    # 角色序列化器
    'RoleSerializer',
    'RoleDetailSerializer',
    'RoleCreateSerializer',
    'RoleUpdateSerializer',
    'SimpleRoleSerializer',
    
    # API密钥序列化器
    'ApiKeySerializer',
    'ApiKeyDetailSerializer',
    'ApiKeyCreateSerializer',
    'SystemApiKeyCreateSerializer',
    'UserApiKeyCreateSerializer',
    'ApiKeyUpdateSerializer',
    'ApiKeyScopeSerializer',
    'ApiKeyUsageLogSerializer',
    'ApiKeyVerifySerializer',
    'ApiKeyHashSerializer',
    
    # 登录尝试序列化器
    'LoginAttemptSerializer',
    'LoginAttemptDetailSerializer',
]
