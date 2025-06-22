"""
租户管理视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from core.permissions import IsSuperAdmin
from apps.tenant_service.models import Tenant
from apps.tenant_service.services import TenantService
from apps.tenant_service.filters import TenantFilter
from apps.tenant_service.serializers import (
    TenantSerializer,
    TenantDetailSerializer,
    TenantCreateSerializer,
    TenantUpdateSerializer
)


class ManagementTenantViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    租户管理视图集
    
    提供租户管理的API接口
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    filterset_class = TenantFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'slug', 'subdomain', 'description', 'contact_email', 'contact_phone', 'address']
    ordering_fields = ['name', 'slug', 'subdomain', 'created_at', 'updated_at', 'expires_at', 'is_active']
    ordering = ['-created_at']  # 默认按创建时间降序排序
    
    def get_serializer_class(self):
        """
        根据操作选择序列化器
        """
        if self.action == 'create':
            return TenantCreateSerializer
        elif self.action == 'retrieve':
            return TenantDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return TenantUpdateSerializer
        return TenantSerializer
    
    def list(self, request):
        """
        获取所有租户列表，支持分页、过滤、搜索和排序
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
        获取租户详情
        """
        tenant = self.get_object()
        serializer = self.get_serializer(tenant)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建租户
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取Django用户模型
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # 检查所有者用户
        owner_user_id = request.data.get('owner_user_id')
        if not owner_user_id:
            # 未指定所有者，获取系统中的超级管理员作为租户所有者
            try:
                # 获取第一个超级管理员用户
                owner_user = User.objects.filter(is_superuser=True).first()
                if not owner_user:
                    return self.get_error_response("系统中没有超级管理员用户，无法创建租户")
            except Exception as e:
                return self.get_error_response(f"获取超级管理员失败: {str(e)}")
        else:
            # 指定了所有者ID，获取对应用户
            try:
                owner_user = User.objects.get(id=owner_user_id)
            except User.DoesNotExist:
                return self.get_error_response("指定的所有者用户不存在")
        
        # 创建租户
        tenant = TenantService.create_tenant(
            name=serializer.validated_data['name'],
            slug=serializer.validated_data['slug'],
            subdomain=serializer.validated_data['subdomain'],
            owner_user=owner_user,
            **{k: v for k, v in serializer.validated_data.items() if k not in ['name', 'slug', 'subdomain']}
        )
        
        return self.get_success_response(
            TenantDetailSerializer(tenant).data,
            message="租户创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
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
    
    def destroy(self, request, pk=None):
        """
        删除租户
        """
        tenant = self.get_object()
        
        # 删除租户
        success = TenantService.delete_tenant(tenant.id)
        
        if success:
            return self.get_success_response(
                None,
                message="租户已删除",
            )
        else:
            return self.get_error_response("租户删除失败") 