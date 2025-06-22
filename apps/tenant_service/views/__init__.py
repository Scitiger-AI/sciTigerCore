from apps.tenant_service.views.platform import (
    TenantViewSet,
    TenantUserViewSet,
    TenantSettingsViewSet,
    TenantQuotaViewSet
)

from apps.tenant_service.views.management import (
    ManagementTenantViewSet,
    ManagementTenantUserViewSet,
    ManagementTenantSettingsViewSet,
    ManagementTenantQuotaViewSet
)

__all__ = [
    # 平台视图
    'TenantViewSet',
    'TenantUserViewSet',
    'TenantSettingsViewSet',
    'TenantQuotaViewSet',
    
    # 管理视图
    'ManagementTenantViewSet',
    'ManagementTenantUserViewSet',
    'ManagementTenantSettingsViewSet',
    'ManagementTenantQuotaViewSet',
]
