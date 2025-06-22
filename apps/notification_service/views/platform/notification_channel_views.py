"""
通知渠道平台API视图
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.notification_service.models import NotificationChannel
from apps.notification_service.serializers import (
    NotificationChannelSerializer, NotificationChannelCreateSerializer,
    NotificationChannelUpdateSerializer
)
from apps.notification_service.permissions import NotificationChannelPermission
from apps.notification_service.services import NotificationService
from apps.notification_service.filters import NotificationChannelFilter


class NotificationChannelViewSet(ResponseMixin, viewsets.ModelViewSet):
    """通知渠道视图集"""
    
    permission_classes = [NotificationChannelPermission]
    filterset_class = NotificationChannelFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'channel_type', 'is_active', 'created_at', 'updated_at']
    ordering = ['name']  # 默认排序
    
    def get_queryset(self):
        """获取查询集"""
        tenant_id = getattr(self.request, 'tenant', None)
        tenant_id = tenant_id.id if tenant_id else None
        
        return NotificationService.get_notification_channels(tenant_id=tenant_id)
    
    def get_serializer_class(self):
        """获取序列化器类"""
        if self.action == 'create':
            return NotificationChannelCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NotificationChannelUpdateSerializer
        return NotificationChannelSerializer
    
    def list(self, request, *args, **kwargs):
        """获取通知渠道列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建通知渠道"""
        # 设置当前租户
        if not request.data.get('tenant') and hasattr(request, 'tenant'):
            request.data['tenant'] = request.tenant.id
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return self.get_success_response(
            serializer.data,
            message="通知渠道创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """获取通知渠道详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.get_success_response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """更新通知渠道"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return self.get_success_response(
            serializer.data,
            message="通知渠道更新成功"
        )
    
    def destroy(self, request, *args, **kwargs):
        """删除通知渠道"""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return self.get_success_response(
            message="通知渠道删除成功",
        ) 