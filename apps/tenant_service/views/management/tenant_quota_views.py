"""
租户配额管理视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.tenant_service.models import TenantQuota
from apps.tenant_service.services import TenantService, TenantQuotaService
from apps.tenant_service.filters import TenantQuotaFilter
from apps.tenant_service.serializers import TenantQuotaSerializer
from apps.tenant_service.permissions import IsSuperAdmin


class ManagementTenantQuotaViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    租户配额管理视图集
    
    提供租户配额管理的API接口
    """
    queryset = TenantQuota.objects.all()
    serializer_class = TenantQuotaSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    filterset_class = TenantQuotaFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['tenant__name', 'tenant__slug']
    ordering_fields = [
        'created_at', 'updated_at', 'tenant__name', 
        'max_users', 'max_api_keys', 'max_api_requests_per_day', 
        'max_storage_gb', 'current_user_count', 'current_storage_used_gb'
    ]
    ordering = ['-created_at']  # 默认按创建时间降序排序
    
    def get_queryset(self):
        """
        获取租户配额列表
        
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
        获取租户配额列表，支持分页、过滤、搜索和排序
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
        获取租户配额详情
        """
        quota = self.get_object()
        serializer = self.get_serializer(quota)
        return self.get_success_response(serializer.data)
    
    def update(self, request, pk=None, *args, **kwargs):
        """
        更新租户配额
        """
        quota = self.get_object()
        
        try:
            # 更新租户配额
            quota = TenantQuotaService.update_tenant_quota(
                tenant=quota.tenant,
                max_users=request.data.get('max_users', quota.max_users),
                max_storage_gb=request.data.get('max_storage_gb', quota.max_storage_gb),
                max_api_keys=request.data.get('max_api_keys', quota.max_api_keys),
                max_api_requests_per_day=request.data.get('max_api_requests_per_day', quota.max_api_requests_per_day),
                max_log_retention_days=request.data.get('max_log_retention_days', quota.max_log_retention_days),
                max_notifications_per_day=request.data.get('max_notifications_per_day', quota.max_notifications_per_day)
            )
            
            serializer = self.get_serializer(quota)
            return self.get_success_response(
                serializer.data,
                message="租户配额已更新"
            )
        except ValueError as e:
            return self.get_error_response(str(e))
    
    def partial_update(self, request, pk=None):
        """
        部分更新租户配额
        """
        return self.update(request, pk)
    
    @action(detail=False, methods=['get'])
    def by_tenant(self, request):
        """
        根据租户ID获取配额
        """
        tenant_id = request.query_params.get('tenant_id')
        if not tenant_id:
            return self.get_error_response("必须指定租户ID")
            
        tenant = TenantService.get_tenant_by_id(tenant_id)
        if not tenant:
            return self.get_error_response("指定的租户不存在")
            
        quota = TenantQuotaService.get_tenant_quota(tenant)
        serializer = self.get_serializer(quota)
        return self.get_success_response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reset_api_calls(self, request, pk=None):
        """
        重置API调用计数
        """
        quota = self.get_object()
        
        # 重置API调用计数
        quota.current_api_calls_today = 0
        quota.current_api_calls_this_month = 0
        quota.save()
        
        return self.get_success_response(
            self.get_serializer(quota).data,
            message="API调用计数已重置"
        ) 