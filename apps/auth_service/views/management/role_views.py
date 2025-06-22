"""
角色管理视图
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.auth_service.services import RoleService
from apps.auth_service.filters import RoleFilter
from apps.auth_service.serializers import (
    RoleSerializer,
    RoleDetailSerializer,
    RoleCreateSerializer,
    RoleUpdateSerializer
)

logger = logging.getLogger('sciTigerCore')


class RoleManagementViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    角色管理视图集
    
    提供角色管理相关的API
    """
    permission_classes = [IsAdminUser]
    serializer_class = RoleSerializer
    filterset_class = RoleFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'is_system', 'is_default', 'created_at', 'updated_at']
    ordering = ['-created_at']  # 默认按名称升序排序
    
    def get_queryset(self):
        """
        获取角色查询集
        
        管理员可以查看所有角色，包括系统角色
        """
         # 获取当前租户ID
        tenant_id = self.request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 超级管理员可以查看所有租户的角色
        if self.request.user.is_superuser:
            return RoleService.get_roles(tenant_id=tenant_id)
        
        # 租户管理员只能查看自己租户的角色
        return RoleService.get_roles(tenant_id=tenant_id)
    
    def get_serializer_class(self):
        """
        获取序列化器类
        
        根据不同的操作返回不同的序列化器
        """
        if self.action == 'retrieve':
            return RoleDetailSerializer
        elif self.action == 'create':
            return RoleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RoleUpdateSerializer
        return self.serializer_class
    
    def list(self, request):
        """
        获取角色列表，支持过滤、搜索和排序
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
        获取角色详情
        """
        role = RoleService.get_role_by_id(pk)
        if not role:
            return self.get_error_response("角色不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(role)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建角色
        """
        # 验证数据
        logger.debug(f"RoleManagementViewSet create: {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 创建角色
        role, error_message = RoleService.create_role(
            name=serializer.validated_data['name'],
            code=serializer.validated_data['code'],
            tenant_id=serializer.validated_data.get('tenant').id,
            permissions=serializer.validated_data.get('permissions'),
            description=serializer.validated_data.get('description'),
            is_system=serializer.validated_data.get('is_system', False),
            is_default=serializer.validated_data.get('is_default', False)
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回创建的角色信息
        result_serializer = RoleDetailSerializer(role)
        return self.get_success_response(
            result_serializer.data,
            message="角色创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None, partial=False):
        """
        更新角色
        """
        # 获取角色
        role = RoleService.get_role_by_id(pk)
        if not role:
            return self.get_error_response("角色不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 验证数据
        serializer = self.get_serializer(role, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 更新角色
        updated_role, error_message = RoleService.update_role(
            role_id=pk,
            **serializer.validated_data
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回更新后的角色信息
        result_serializer = RoleDetailSerializer(updated_role)
        return self.get_success_response(result_serializer.data, message="角色更新成功")
    
    def partial_update(self, request, pk=None):
        """
        部分更新角色
        """
        return self.update(request, pk, partial=True)
    
    def destroy(self, request, pk=None):
        """
        删除角色
        """
        # 删除角色
        success = RoleService.delete_role(pk)
        
        if not success:
            return self.get_error_response("角色删除失败，可能是系统角色或角色不存在")
        
        return self.get_success_response(message="角色删除成功")
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        获取拥有此角色的用户列表
        """
        # 获取角色
        role = RoleService.get_role_by_id(pk)
        if not role:
            return self.get_error_response("角色不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 获取用户列表
        users = role.users.all()
        
        # 应用过滤器
        from apps.auth_service.filters import UserFilter
        from apps.auth_service.serializers import UserSerializer
        
        # 创建过滤器
        filterset = UserFilter(request.query_params, queryset=users)
        filtered_users = filterset.qs
        
        # 应用排序
        ordering = request.query_params.get('ordering', 'username')
        if ordering:
            if ordering.startswith('-'):
                field = ordering[1:]
                filtered_users = filtered_users.order_by(f'-{field}')
            else:
                filtered_users = filtered_users.order_by(ordering)
        
        # 使用DRF的分页机制
        page = self.paginate_queryset(filtered_users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # 如果没有分页或分页被禁用，返回所有数据
        serializer = UserSerializer(filtered_users, many=True)
        return self.get_success_response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_permissions(self, request, pk=None):
        """
        为角色分配权限
        """
        # 验证数据
        permission_ids = request.data.get('permission_ids')
        if not permission_ids:
            return self.get_error_response("缺少权限ID列表")
        
        # 分配权限
        success, error_message = RoleService.assign_permissions_to_role(pk, permission_ids)
        
        if not success:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="权限分配成功")
    
    @action(detail=True, methods=['post'])
    def remove_permissions(self, request, pk=None):
        """
        从角色中移除权限
        """
        # 验证数据
        permission_ids = request.data.get('permission_ids')
        if not permission_ids:
            return self.get_error_response("缺少权限ID列表")
        
        # 移除权限
        success, error_message = RoleService.remove_permissions_from_role(pk, permission_ids)
        
        if not success:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="权限移除成功")
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        设置为默认角色
        """
        # 设置默认角色
        success, error_message = RoleService.set_role_as_default(pk)
        
        if not success:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="已设置为默认角色")
    
    @action(detail=True, methods=['post'])
    def unset_default(self, request, pk=None):
        """
        取消默认角色设置
        """
        # 取消默认角色
        success, error_message = RoleService.unset_role_as_default(pk)
        
        if not success:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="已取消默认角色设置") 