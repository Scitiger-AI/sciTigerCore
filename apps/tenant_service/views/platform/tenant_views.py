"""
租户平台视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from core.permissions import IsTenantMember, IsTenantAdmin, IsTenantOwner
from apps.tenant_service.models import Tenant
from apps.tenant_service.services import TenantService
from apps.tenant_service.filters import PlatformTenantFilter
from apps.tenant_service.serializers import (
    TenantSerializer,
    TenantDetailSerializer,
    TenantUpdateSerializer
)


class TenantViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    租户平台视图集
    
    提供租户相关的API接口
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PlatformTenantFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'slug', 'subdomain', 'description']
    ordering_fields = ['name', 'slug', 'created_at', 'updated_at', 'is_active']
    ordering = ['-created_at']  # 默认按创建时间降序排序
    
    def get_serializer_class(self):
        """
        根据操作选择序列化器
        """
        if self.action == 'retrieve':
            return TenantDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return TenantUpdateSerializer
        return TenantSerializer
    
    def get_permissions(self):
        """
        根据操作选择权限类
        """
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsTenantAdmin]
        elif self.action in ['transfer_ownership']:
            self.permission_classes = [IsAuthenticated, IsTenantOwner]
        elif self.action in ['retrieve', 'list', 'current']:
            self.permission_classes = [IsAuthenticated, IsTenantMember]
        
        return super().get_permissions()
    
    def list(self, request):
        """
        获取当前用户的租户列表，支持分页、过滤、搜索和排序
        """
        # 获取用户的租户列表
        tenants = TenantService.get_user_tenants(request.user)
        
        # 应用过滤、搜索和排序
        queryset = self.filter_queryset(tenants)
        
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
        获取租户详情
        """
        tenant = self.get_object()
        serializer = self.get_serializer(tenant)
        return self.get_success_response(serializer.data)
    
    def update(self, request, pk=None, *args, **kwargs):
        """
        更新租户信息
        """
        tenant = self.get_object()
        serializer = self.get_serializer(tenant, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        # 更新租户
        tenant = TenantService.update_tenant(tenant.id, **serializer.validated_data)
        
        return self.get_success_response(
            TenantDetailSerializer(tenant).data,
            message="租户信息已更新"
        )
    
    def partial_update(self, request, pk=None):
        """
        部分更新租户信息
        """
        return self.update(request, pk, partial=True)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        获取当前租户信息
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = TenantDetailSerializer(request.tenant)
        return self.get_success_response(serializer.data) 