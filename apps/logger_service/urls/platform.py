"""
日志记录服务平台 API URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.logger_service.views.platform import (
    LogCategoryViewSet,
    LogEntryViewSet,
    LogRetentionPolicyViewSet
)

# 创建路由器
router = DefaultRouter()
router.register(r'categories', LogCategoryViewSet, basename='platform-log-category')
router.register(r'entries', LogEntryViewSet, basename='platform-log-entry')
router.register(r'retention-policies', LogRetentionPolicyViewSet, basename='platform-log-retention-policy')

urlpatterns = [
    path('', include(router.urls)),
]
