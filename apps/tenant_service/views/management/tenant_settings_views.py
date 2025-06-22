"""
租户设置管理视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.tenant_service.models import TenantSettings
from apps.tenant_service.services import TenantService, TenantSettingsService
from apps.tenant_service.filters import TenantSettingsFilter
from apps.tenant_service.serializers import (
    TenantSettingsSerializer,
    TenantSettingsUpdateSerializer
)
from apps.tenant_service.permissions import IsSuperAdmin


class ManagementTenantSettingsViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    租户设置管理视图集
    
    提供租户设置管理的API接口
    """
    queryset = TenantSettings.objects.all()
    serializer_class = TenantSettingsSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    filterset_class = TenantSettingsFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['tenant__name', 'tenant__slug', 'default_notification_email', 'timezone']
    ordering_fields = ['created_at', 'updated_at', 'tenant__name', 'timezone', 'password_expiry_days', 'max_login_attempts']
    ordering = ['-created_at']  # 默认按创建时间降序排序
    
    def get_serializer_class(self):
        """
        根据操作选择序列化器
        """
        if self.action in ['update', 'partial_update']:
            return TenantSettingsUpdateSerializer
        return TenantSettingsSerializer
    
    def get_queryset(self):
        """
        获取租户设置列表
        
        支持按租户ID过滤
        """
        queryset = super().get_queryset()
        
        # 支持按租户ID过滤
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
            
        return queryset
    
    def list(self, request):
        """
        获取租户设置列表，支持分页、过滤、搜索和排序
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # 使用DRF的分页机制
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # 如果没有分页或分页被禁用，返回所有数据
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        获取租户设置详情
        """
        settings = self.get_object()
        serializer = self.get_serializer(settings)
        return self.get_success_response(serializer.data)
    
    def update(self, request, pk=None, *args, **kwargs):
        """
        更新租户设置
        """
        settings = self.get_object()
        serializer = self.get_serializer(settings, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        # 更新租户设置
        settings = TenantSettingsService.update_tenant_settings(
            tenant=settings.tenant,
            **serializer.validated_data
        )
        
        return self.get_success_response(
            TenantSettingsSerializer(settings).data,
            message="租户设置已更新"
        )
    
    def partial_update(self, request, pk=None):
        """
        部分更新租户设置
        """
        return self.update(request, pk, partial=True)
    
    @action(detail=False, methods=['get'])
    def by_tenant(self, request):
        """
        根据租户ID获取设置
        """
        tenant_id = request.query_params.get('tenant_id')
        if not tenant_id:
            return self.get_error_response("必须指定租户ID")
            
        tenant = TenantService.get_tenant_by_id(tenant_id)
        if not tenant:
            return self.get_error_response("指定的租户不存在")
            
        settings = TenantSettingsService.get_tenant_settings(tenant)
        serializer = self.get_serializer(settings)
        return self.get_success_response(serializer.data) 