"""
权限平台视图
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from core.permissions import IsTenantAdmin
from apps.auth_service.models import Permission
from apps.auth_service.services import PermissionService
from apps.auth_service.filters import PermissionFilter
from apps.auth_service.serializers import (
    PermissionSerializer,
    PermissionDetailSerializer,
    PermissionCreateSerializer,
    PermissionUpdateSerializer
)


class PermissionViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    权限平台视图集
    
    提供权限相关的API接口
    
    权限分为两种类型：
    1. 系统全局权限 (is_system=True)：系统预设的权限，适用于所有租户，不关联特定租户
    2. 租户级权限 (is_tenant_level=True)：特定租户的自定义权限，必须关联到特定租户
    
    这两种类型互斥，一个权限不能同时是系统权限和租户级权限。
    
    租户管理员可以：
    - 查看系统权限和本租户的权限
    - 创建本租户的权限（必须设置is_tenant_level=True）
    - 更新本租户的权限
    - 删除本租户的权限
    
    租户管理员不能：
    - 创建、更新或删除系统权限
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    filterset_class = PermissionFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description', 'service', 'resource', 'action']
    ordering_fields = ['name', 'code', 'service', 'resource', 'action', 'is_system', 'created_at', 'updated_at']
    ordering = ['service', 'resource', 'action']  # 默认排序
    
    def get_serializer_class(self):
        """
        根据操作选择序列化器
        """
        if self.action == 'retrieve':
            return PermissionDetailSerializer
        elif self.action == 'create':
            return PermissionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PermissionUpdateSerializer
        return PermissionSerializer
    
    def get_queryset(self):
        """
        获取权限列表，只返回当前租户的权限和系统权限
        """
        # 获取当前租户ID
        tenant_id = self.request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 获取系统权限和当前租户的权限
        if tenant_id:
            # 使用优化后的查询方法获取权限
            return PermissionService.get_permissions_by_service(
                service='*',  # 通配符表示所有服务
                tenant_id=tenant_id
            )
        else:
            # 如果没有租户上下文，只返回系统权限
            return PermissionService.get_permissions(is_system=True)
    
    def list(self, request):
        """
        获取权限列表，支持过滤、搜索和排序
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
        获取权限详情
        """
        permission = self.get_object()
        serializer = self.get_serializer(permission)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建权限
        
        租户管理员只能创建租户级权限，不能创建系统权限
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 设置为租户级权限
        tenant = getattr(request, 'tenant', None)
        if tenant:
            serializer.validated_data['tenant'] = tenant
            serializer.validated_data['is_tenant_level'] = True
            serializer.validated_data['is_system'] = False
        else:
            return self.get_error_response(
                "无法创建权限：缺少租户上下文",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 创建权限
            permission = PermissionService.create_permission(
                **serializer.validated_data
            )
            
            return self.get_success_response(
                PermissionDetailSerializer(permission).data,
                message="权限创建成功",
                status_code=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return self.get_error_response(
                str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, pk=None, *args, **kwargs):
        """
        更新权限
        
        租户管理员只能更新租户级权限，不能更新系统权限
        """
        permission = self.get_object()
        
        # 检查是否是系统权限
        if permission.is_system:
            return self.get_error_response(
                "系统权限不允许修改",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # 检查是否是当前租户的权限
        tenant = getattr(request, 'tenant', None)
        if tenant and permission.tenant_id != tenant.id:
            return self.get_error_response(
                "无权修改其他租户的权限",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(permission, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        # 确保权限类型不变
        serializer.validated_data['is_tenant_level'] = True
        serializer.validated_data['is_system'] = False
        serializer.validated_data['tenant'] = tenant
        
        try:
            # 更新权限
            permission = PermissionService.update_permission(
                permission.id,
                **serializer.validated_data
            )
            
            return self.get_success_response(
                PermissionDetailSerializer(permission).data,
                message="权限更新成功"
            )
        except ValueError as e:
            return self.get_error_response(
                str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    def partial_update(self, request, pk=None):
        """
        部分更新权限
        """
        return self.update(request, pk, partial=True)
    
    def destroy(self, request, pk=None):
        """
        删除权限
        
        租户管理员只能删除租户级权限，不能删除系统权限
        """
        permission = self.get_object()
        
        # 系统权限不允许删除
        if permission.is_system:
            return self.get_error_response(
                "系统权限不允许删除",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # 检查是否是当前租户的权限
        tenant = getattr(request, 'tenant', None)
        if tenant and permission.tenant_id != tenant.id:
            return self.get_error_response(
                "无权删除其他租户的权限",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # 删除权限
        result = PermissionService.delete_permission(permission.id)
        
        if result:
            return self.get_success_response(
                None,
                message="权限删除成功",
            )
        else:
            return self.get_error_response(
                "权限删除失败",
                status_code=status.HTTP_400_BAD_REQUEST
            ) 