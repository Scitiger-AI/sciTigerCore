"""
角色平台视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
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


class RoleViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    角色视图集
    
    提供角色相关的API
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RoleSerializer
    filterset_class = RoleFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'is_system', 'is_default', 'created_at', 'updated_at']
    ordering = ['name']  # 默认按名称升序排序
    
    def get_queryset(self):
        """
        获取角色查询集
        
        根据当前用户的权限和租户过滤角色列表
        """
         # 获取当前租户ID
        tenant_id = self.request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 获取角色列表
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取当前租户ID
        tenant_id = getattr(request, 'tenant', None)
        tenant_id = tenant_id.id if tenant_id else None
        
        # 如果请求中没有指定租户，使用当前租户
        if 'tenant' not in serializer.validated_data and tenant_id:
            serializer.validated_data['tenant_id'] = tenant_id
        
        # 创建角色
        role, error_message = RoleService.create_role(
            name=serializer.validated_data['name'],
            code=serializer.validated_data['code'],
            tenant_id=serializer.validated_data.get('tenant_id'),
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
    
    @action(detail=True, methods=['post'])
    def assign_to_user(self, request, pk=None):
        """
        将角色分配给用户
        """
        # 验证数据
        user_id = request.data.get('user_id')
        if not user_id:
            return self.get_error_response("缺少用户ID")
        
        # 分配角色
        success, error_message = RoleService.assign_role_to_user(pk, user_id)
        
        if not success:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="角色分配成功")
    
    @action(detail=True, methods=['post'])
    def remove_from_user(self, request, pk=None):
        """
        从用户中移除角色
        """
        # 验证数据
        user_id = request.data.get('user_id')
        if not user_id:
            return self.get_error_response("缺少用户ID")
        
        # 移除角色
        success, error_message = RoleService.remove_role_from_user(pk, user_id)
        
        if not success:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="角色移除成功") 