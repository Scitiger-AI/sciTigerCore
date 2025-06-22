"""
认证服务平台 API URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.auth_service.views.platform import (
    PermissionViewSet,
    LoginView,
    LogoutView,
    TokenRefreshView,
    RegisterView,
    UserViewSet,
    RoleViewSet,
    ApiKeyViewSet,
    VerifyApiKeyView,
    MicroserviceVerifyTokenView,
    MicroserviceVerifyApiKeyView
)
from apps.auth_service.views.platform.api_key_demo_view import ApiKeyDemoViewSet, ApiKeyDemoView

router = DefaultRouter()
router.register(r'permissions', PermissionViewSet)
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'api-keys', ApiKeyViewSet, basename='api-key')
router.register(r'api-key-demo', ApiKeyDemoViewSet, basename='api-key-demo')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('refresh-token/', TokenRefreshView.as_view(), name='auth-refresh-token'),
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('verify-api-key/', VerifyApiKeyView.as_view(), name='auth-verify-api-key'),
    path('api-key-demo-view/', ApiKeyDemoView.as_view(), name='api-key-demo-view'),
    
    # 微服务认证API
    path('microservice/verify-token/', MicroserviceVerifyTokenView.as_view(), name='microservice-verify-token'),
    path('microservice/verify-api-key/', MicroserviceVerifyApiKeyView.as_view(), name='microservice-verify-api-key'),
]
