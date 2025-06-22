"""
租户服务管理 API URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tenant_service.views.management import (
    ManagementTenantViewSet,
    ManagementTenantUserViewSet,
    ManagementTenantSettingsViewSet,
    ManagementTenantQuotaViewSet
)

router = DefaultRouter()
router.register(r'tenants', ManagementTenantViewSet, basename='management-tenant')
router.register(r'tenant-users', ManagementTenantUserViewSet, basename='management-tenant-user')
router.register(r'tenant-settings', ManagementTenantSettingsViewSet, basename='management-tenant-settings')
router.register(r'tenant-quotas', ManagementTenantQuotaViewSet, basename='management-tenant-quota')

urlpatterns = [
    path('', include(router.urls)),
]
