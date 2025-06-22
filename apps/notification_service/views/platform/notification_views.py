"""
通知记录平台API视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.notification_service.models import Notification
from apps.notification_service.serializers import (
    NotificationSerializer, NotificationCreateSerializer,
    NotificationListSerializer, NotificationMarkReadSerializer
)
from apps.notification_service.permissions import NotificationPermission
from apps.notification_service.services import NotificationService
from apps.notification_service.filters import NotificationFilter


class NotificationViewSet(ResponseMixin, viewsets.ModelViewSet):
    """通知记录视图集"""
    
    permission_classes = [NotificationPermission]
    filterset_class = NotificationFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['subject', 'content']
    ordering_fields = ['created_at', 'scheduled_at', 'sent_at', 'is_read', 'status']
    ordering = ['-created_at']  # 默认按创建时间降序排序
    
    def get_queryset(self):
        """获取查询集"""
        tenant_id = getattr(self.request, 'tenant', None)
        tenant_id = tenant_id.id if tenant_id else None
        
        # 普通用户只能查看自己的通知
        if not self.request.user.is_tenant_admin:
            return NotificationService.get_notifications(
                tenant_id=tenant_id, 
                user_id=self.request.user.id
            )
        
        # 租户管理员可以查看租户内所有通知
        return NotificationService.get_notifications(tenant_id=tenant_id)
    
    def get_serializer_class(self):
        """获取序列化器类"""
        if self.action == 'create':
            return NotificationCreateSerializer
        elif self.action == 'list':
            return NotificationListSerializer
        elif self.action == 'mark_read':
            return NotificationMarkReadSerializer
        return NotificationSerializer
    
    def list(self, request, *args, **kwargs):
        """获取通知记录列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建通知记录"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()
        
        if notification:
            result_serializer = NotificationSerializer(notification)
            return self.get_success_response(
                result_serializer.data,
                message="通知创建成功",
                status_code=status.HTTP_201_CREATED
            )
        else:
            return self.get_success_response(
                message="通知已创建，但由于用户设置，可能已被延迟发送或已被禁用",
                status_code=status.HTTP_201_CREATED
            )
    
    def retrieve(self, request, *args, **kwargs):
        """获取通知记录详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.get_success_response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """更新通知记录 - 不允许"""
        return self.get_error_response(
            "通知记录不允许更新",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        """删除通知记录"""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return self.get_success_response(
            message="通知记录删除成功",
        )
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """标记通知为已读"""
        success = NotificationService.mark_notification_as_read(pk)
        
        if not success:
            return self.get_error_response("标记通知为已读失败，可能是通知不存在")
        
        return self.get_success_response(message="通知已标记为已读")
    
    @action(detail=True, methods=['post'])
    def mark_as_unread(self, request, pk=None):
        """标记通知为未读"""
        success = NotificationService.mark_notification_as_unread(pk)
        
        if not success:
            return self.get_error_response("标记通知为未读失败，可能是通知不存在")
        
        return self.get_success_response(message="通知已标记为未读")
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """批量标记通知为已读"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tenant_id = getattr(request, 'tenant', None)
        tenant_id = tenant_id.id if tenant_id else None
        user_id = request.user.id
        
        # 标记所有通知为已读
        if serializer.validated_data.get('mark_all'):
            count = NotificationService.mark_all_notifications_as_read(tenant_id, user_id)
            return self.get_success_response(
                {'count': count},
                message=f"已将所有通知标记为已读，共 {count} 条"
            )
        
        # 标记指定通知为已读
        notification_ids = serializer.validated_data.get('notification_ids', [])
        success_count = 0
        
        for notification_id in notification_ids:
            if NotificationService.mark_notification_as_read(notification_id):
                success_count += 1
        
        return self.get_success_response(
            {'count': success_count},
            message=f"已将 {success_count}/{len(notification_ids)} 条通知标记为已读"
        ) 