"""
租户服务序列化器模块
"""

from apps.tenant_service.serializers.tenant_serializers import (
    TenantSerializer,
    TenantDetailSerializer,
    TenantCreateSerializer,
    TenantUpdateSerializer
)

from apps.tenant_service.serializers.tenant_user_serializers import (
    TenantUserSerializer,
    TenantUserCreateSerializer,
    TenantUserUpdateSerializer
)

from apps.tenant_service.serializers.tenant_settings_serializers import (
    TenantSettingsSerializer,
    TenantSettingsUpdateSerializer
)

from apps.tenant_service.serializers.tenant_quota_serializers import (
    TenantQuotaSerializer,
    TenantQuotaUpdateSerializer
)

__all__ = [
    'TenantSerializer',
    'TenantDetailSerializer',
    'TenantCreateSerializer',
    'TenantUpdateSerializer',
    'TenantUserSerializer',
    'TenantUserCreateSerializer',
    'TenantUserUpdateSerializer',
    'TenantSettingsSerializer',
    'TenantSettingsUpdateSerializer',
    'TenantQuotaSerializer',
    'TenantQuotaUpdateSerializer',
]
