"""
通知类型平台API视图
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.notification_service.models import NotificationType
from apps.notification_service.serializers import (
    NotificationTypeSerializer, NotificationTypeCreateSerializer,
    NotificationTypeUpdateSerializer
)
from apps.notification_service.permissions import NotificationTypePermission
from apps.notification_service.services import NotificationService
from apps.notification_service.filters import NotificationTypeFilter


class NotificationTypeViewSet(ResponseMixin, viewsets.ModelViewSet):
    """通知类型视图集"""
    
    permission_classes = [NotificationTypePermission]
    filterset_class = NotificationTypeFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'category', 'priority', 'is_active', 'created_at', 'updated_at']
    ordering = ['category', 'priority', 'name']  # 默认排序
    
    def get_queryset(self):
        """获取查询集"""
        return NotificationService.get_notification_types()
    
    def get_serializer_class(self):
        """获取序列化器类"""
        if self.action == 'create':
            return NotificationTypeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NotificationTypeUpdateSerializer
        return NotificationTypeSerializer
    
    def list(self, request, *args, **kwargs):
        """获取通知类型列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建通知类型"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return self.get_success_response(
            serializer.data,
            message="通知类型创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """获取通知类型详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.get_success_response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """更新通知类型"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return self.get_success_response(
            serializer.data,
            message="通知类型更新成功"
        )
    
    def destroy(self, request, *args, **kwargs):
        """删除通知类型"""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return self.get_success_response(
            message="通知类型删除成功",
        ) 