"""
认证管理API路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.auth_service.views.management import (
    user_views,
    role_views,
    auth_views,
    api_key_views,
    permission_views,
    login_attempt_views,
    service_scope_views
)

# 创建路由器
router = DefaultRouter()
router.register(r'users', user_views.UserManagementViewSet, basename='management-user')
router.register(r'roles', role_views.RoleManagementViewSet, basename='management-role')
router.register(r'api-keys', api_key_views.ApiKeyManagementViewSet, basename='management-api-key')
router.register(r'permissions', permission_views.ManagementPermissionViewSet, basename='management-permission')
router.register(r'login-attempts', login_attempt_views.LoginAttemptManagementViewSet, basename='management-login-attempt')
router.register(r'service-scopes', service_scope_views.ServiceScopeViewSet, basename='management-service-scope')

# 定义URL模式
urlpatterns = [
    # 路由器URL
    path('', include(router.urls)),
    
    # 认证相关URL
    path('login/', auth_views.ManagementLoginView.as_view(), name='management-login'),
    path('logout/', auth_views.ManagementLogoutView.as_view(), name='management-logout'),
    path('refresh-token/', auth_views.ManagementTokenRefreshView.as_view(), name='management-refresh-token'),
    path('profile/', auth_views.AdminProfileView.as_view(), name='admin-profile'),
]
