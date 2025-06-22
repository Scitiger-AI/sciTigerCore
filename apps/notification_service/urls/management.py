"""
通知中心服务管理 API URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.notification_service.views.management import (
    NotificationTypeManagementViewSet
)

# 创建路由器
router = DefaultRouter()
router.register(r'types', NotificationTypeManagementViewSet, basename='notification-type-management')

urlpatterns = [
    path('', include(router.urls)),
]
