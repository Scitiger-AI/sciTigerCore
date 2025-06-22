"""
用户通知偏好设置平台API视图
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.notification_service.models import UserNotificationPreference
from apps.notification_service.serializers import (
    UserNotificationPreferenceSerializer, UserNotificationPreferenceCreateSerializer,
    UserNotificationPreferenceUpdateSerializer
)
from apps.notification_service.permissions import UserNotificationPreferencePermission
from apps.notification_service.services import NotificationService
from apps.notification_service.filters import UserNotificationPreferenceFilter


class UserNotificationPreferenceViewSet(ResponseMixin, viewsets.ModelViewSet):
    """用户通知偏好设置视图集"""
    
    permission_classes = [UserNotificationPreferencePermission]
    filterset_class = UserNotificationPreferenceFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['user__username', 'notification_type__name']
    ordering_fields = ['user__username', 'notification_type__name', 'created_at', 'updated_at']
    ordering = ['user__username', 'notification_type__name']  # 默认排序
    
    def get_queryset(self):
        """获取查询集"""
        tenant_id = getattr(self.request, 'tenant', None)
        tenant_id = tenant_id.id if tenant_id else None
        
        # 普通用户只能查看自己的通知偏好设置
        if not self.request.user.is_tenant_admin:
            return NotificationService.get_user_notification_preferences(
                tenant_id=tenant_id, 
                user_id=self.request.user.id
            )
        
        # 租户管理员可以查看租户内所有用户的通知偏好设置
        return NotificationService.get_user_notification_preferences(tenant_id=tenant_id)
    
    def get_serializer_class(self):
        """获取序列化器类"""
        if self.action == 'create':
            return UserNotificationPreferenceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserNotificationPreferenceUpdateSerializer
        return UserNotificationPreferenceSerializer
    
    def list(self, request, *args, **kwargs):
        """获取用户通知偏好设置列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建用户通知偏好设置"""
        # 如果没有指定用户，默认为当前用户
        if not request.data.get('user'):
            request.data['user'] = request.user.id
            
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return self.get_success_response(
            serializer.data,
            message="用户通知偏好设置创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """获取用户通知偏好设置详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.get_success_response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """更新用户通知偏好设置"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return self.get_success_response(
            serializer.data,
            message="用户通知偏好设置更新成功"
        )
    
    def destroy(self, request, *args, **kwargs):
        """删除用户通知偏好设置"""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return self.get_success_response(
            message="用户通知偏好设置删除成功",
        ) 