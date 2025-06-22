"""
通知中心服务平台 API URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.notification_service.views.platform import (
    NotificationTypeViewSet,
    NotificationChannelViewSet,
    NotificationTemplateViewSet,
    NotificationViewSet,
    UserNotificationPreferenceViewSet
)

# 创建路由器
router = DefaultRouter()
router.register(r'types', NotificationTypeViewSet, basename='notification-type')
router.register(r'channels', NotificationChannelViewSet, basename='notification-channel')
router.register(r'templates', NotificationTemplateViewSet, basename='notification-template')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'preferences', UserNotificationPreferenceViewSet, basename='notification-preference')

urlpatterns = [
    path('', include(router.urls)),
]
