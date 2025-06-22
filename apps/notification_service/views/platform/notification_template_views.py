"""
通知模板平台API视图
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.notification_service.models import NotificationTemplate
from apps.notification_service.serializers import (
    NotificationTemplateSerializer, NotificationTemplateCreateSerializer,
    NotificationTemplateUpdateSerializer
)
from apps.notification_service.permissions import NotificationTemplatePermission
from apps.notification_service.services import NotificationService
from apps.notification_service.filters import NotificationTemplateFilter


class NotificationTemplateViewSet(ResponseMixin, viewsets.ModelViewSet):
    """通知模板视图集"""
    
    permission_classes = [NotificationTemplatePermission]
    filterset_class = NotificationTemplateFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'subject_template']
    ordering_fields = ['name', 'code', 'notification_type__name', 'channel__name', 'language', 'is_active', 'created_at', 'updated_at']
    ordering = ['notification_type__name', 'channel__name', 'language']  # 默认排序
    
    def get_queryset(self):
        """获取查询集"""
        tenant_id = getattr(self.request, 'tenant', None)
        tenant_id = tenant_id.id if tenant_id else None
        
        return NotificationService.get_notification_templates(tenant_id=tenant_id)
    
    def get_serializer_class(self):
        """获取序列化器类"""
        if self.action == 'create':
            return NotificationTemplateCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NotificationTemplateUpdateSerializer
        return NotificationTemplateSerializer
    
    def list(self, request, *args, **kwargs):
        """获取通知模板列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建通知模板"""
        # 设置当前租户
        if not request.data.get('tenant') and hasattr(request, 'tenant'):
            request.data['tenant'] = request.tenant.id
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return self.get_success_response(
            serializer.data,
            message="通知模板创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """获取通知模板详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.get_success_response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """更新通知模板"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return self.get_success_response(
            serializer.data,
            message="通知模板更新成功"
        )
    
    def destroy(self, request, *args, **kwargs):
        """删除通知模板"""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return self.get_success_response(
            message="通知模板删除成功",
        ) 