"""
租户服务平台 API URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tenant_service.views.platform import (
    TenantViewSet,
    TenantUserViewSet,
    TenantSettingsViewSet,
    TenantQuotaViewSet
)

router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='platform-tenant')
router.register(r'tenant-users', TenantUserViewSet, basename='platform-tenant-user')
router.register(r'tenant-settings', TenantSettingsViewSet, basename='platform-tenant-settings')
router.register(r'tenant-quotas', TenantQuotaViewSet, basename='platform-tenant-quota')

urlpatterns = [
    path('', include(router.urls)),
]
