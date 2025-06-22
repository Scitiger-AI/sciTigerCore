"""
租户用户管理视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.tenant_service.models import Tenant, TenantUser
from apps.tenant_service.services import TenantService, TenantUserService
from apps.tenant_service.filters import TenantUserFilter
from apps.tenant_service.serializers import (
    TenantUserSerializer,
    TenantUserCreateSerializer,
    TenantUserUpdateSerializer
)
from apps.tenant_service.permissions import IsSuperAdmin


class ManagementTenantUserViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    租户用户管理视图集
    
    提供租户用户管理的API接口
    """
    queryset = TenantUser.objects.all()
    serializer_class = TenantUserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    filterset_class = TenantUserFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'tenant__name', 'tenant__slug']
    ordering_fields = ['role', 'created_at', 'updated_at', 'is_active', 'tenant__name', 'user__username', 'user__email']
    ordering = ['-created_at']  # 默认按创建时间降序排序
    
    def get_serializer_class(self):
        """
        根据操作选择序列化器
        """
        if self.action == 'create':
            return TenantUserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TenantUserUpdateSerializer
        return TenantUserSerializer
    
    def get_queryset(self):
        """
        获取租户用户列表
        
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
        获取租户用户列表，支持分页、过滤、搜索和排序
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
        获取租户用户详情
        """
        tenant_user = self.get_object()
        serializer = self.get_serializer(tenant_user)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建租户用户关联
        """
        # 检查租户ID
        tenant_id = request.data.get('tenant_id')
        if not tenant_id:
            return self.get_error_response("必须指定租户ID")
            
        # 获取租户
        tenant = TenantService.get_tenant_by_id(tenant_id)
        if not tenant:
            return self.get_error_response("指定的租户不存在")
            
        # 设置序列化器上下文
        context = self.get_serializer_context()
        context['tenant'] = tenant
        
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        
        try:
            # 获取用户ID
            user_id = serializer.validated_data['user_id']
            
            # 获取用户
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            
            # 创建租户用户关联
            tenant_user = TenantUserService.create_tenant_user(
                tenant=tenant,
                user=user,
                role=serializer.validated_data.get('role', TenantUser.ROLE_MEMBER),
                is_active=serializer.validated_data.get('is_active', True)
            )
            
            return self.get_success_response(
                TenantUserSerializer(tenant_user).data,
                message="租户用户关联创建成功",
                status_code=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return self.get_error_response(str(e))
    
    def update(self, request, pk=None, *args, **kwargs):
        """
        更新租户用户关联
        """
        tenant_user = self.get_object()
        serializer = self.get_serializer(tenant_user, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        try:
            # 更新租户用户关联
            tenant_user = TenantUserService.update_tenant_user(
                tenant_user_id=tenant_user.id,
                **serializer.validated_data
            )
            
            return self.get_success_response(
                TenantUserSerializer(tenant_user).data,
                message="租户用户关联已更新"
            )
        except ValueError as e:
            return self.get_error_response(str(e))
    
    def partial_update(self, request, pk=None):
        """
        部分更新租户用户关联
        """
        return self.update(request, pk, partial=True)
    
    def destroy(self, request, pk=None):
        """
        删除租户用户关联
        """
        tenant_user = self.get_object()
        
        try:
            # 删除租户用户关联
            success = TenantUserService.delete_tenant_user(tenant_user_id=tenant_user.id)
            
            if success:
                return self.get_success_response(
                    None,
                    message="租户用户关联已删除",
                )
            else:
                return self.get_error_response("租户用户关联删除失败")
        except ValueError as e:
            return self.get_error_response(str(e)) 