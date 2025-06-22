"""
日志记录服务管理 API URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.logger_service.views.management import (
    LogCategoryViewSet,
    LogEntryViewSet,
    LogRetentionPolicyViewSet
)

# 创建路由器
router = DefaultRouter()
router.register(r'categories', LogCategoryViewSet, basename='management-log-category')
router.register(r'entries', LogEntryViewSet, basename='management-log-entry')
router.register(r'retention-policies', LogRetentionPolicyViewSet, basename='management-log-retention-policy')

urlpatterns = [
    path('', include(router.urls)),
]
