"""
租户用户平台视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.tenant_service.models import TenantUser
from apps.tenant_service.services import TenantUserService
from apps.tenant_service.filters import PlatformTenantUserFilter
from apps.tenant_service.serializers import (
    TenantUserSerializer,
    TenantUserCreateSerializer,
    TenantUserUpdateSerializer
)
from apps.tenant_service.permissions import IsTenantMember, IsTenantAdmin, IsTenantOwner


class TenantUserViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    租户用户平台视图集
    
    提供租户用户关联的API接口
    """
    queryset = TenantUser.objects.all()
    serializer_class = TenantUserSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filterset_class = PlatformTenantUserFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['role', 'created_at', 'updated_at', 'is_active', 'user__username', 'user__email']
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
    
    def get_permissions(self):
        """
        根据操作选择权限类
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsTenantAdmin]
        elif self.action in ['transfer_ownership']:
            self.permission_classes = [IsAuthenticated, IsTenantOwner]
        else:
            self.permission_classes = [IsAuthenticated, IsTenantMember]
        
        return super().get_permissions()
    
    def get_queryset(self):
        """
        获取当前租户的用户列表
        """
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            return TenantUser.objects.none()
            
        return TenantUser.objects.filter(tenant=self.request.tenant)
    
    def list(self, request):
        """
        获取当前租户的用户列表，支持分页、过滤、搜索和排序
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
        添加用户到当前租户
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # 创建租户用户关联
            tenant_user = TenantUserService.create_tenant_user(
                tenant=request.tenant,
                user_id=serializer.validated_data['user_id'],
                role=serializer.validated_data.get('role', TenantUser.ROLE_MEMBER),
                is_active=serializer.validated_data.get('is_active', True)
            )
            
            return self.get_success_response(
                TenantUserSerializer(tenant_user).data,
                message="用户已添加到租户",
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
                message="租户用户信息已更新"
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
        从租户中移除用户
        """
        tenant_user = self.get_object()
        
        try:
            # 删除租户用户关联
            TenantUserService.delete_tenant_user(tenant_user_id=tenant_user.id)
            
            return self.get_success_response(
                None,
                message="用户已从租户中移除",
            )
        except ValueError as e:
            return self.get_error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        获取当前用户在租户中的信息
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        tenant_user = TenantUserService.get_tenant_user(request.tenant, request.user)
        if not tenant_user:
            return self.get_error_response("您不是该租户的成员", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = self.get_serializer(tenant_user)
        return self.get_success_response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def transfer_ownership(self, request, pk=None):
        """
        转移租户所有权
        """
        tenant_user = self.get_object()
        
        try:
            # 转移所有权
            success = TenantUserService.transfer_ownership(
                tenant=request.tenant,
                from_user=request.user,
                to_user=tenant_user.user
            )
            
            if success:
                return self.get_success_response(
                    None,
                    message=f"租户所有权已转移给 {tenant_user.user.username}"
                )
            else:
                return self.get_error_response("所有权转移失败")
        except ValueError as e:
            return self.get_error_response(str(e)) 