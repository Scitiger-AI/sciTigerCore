"""
权限管理视图
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from core.permissions import IsSuperAdmin
from apps.auth_service.models import Permission
from apps.auth_service.services import PermissionService
from apps.auth_service.filters import PermissionFilter
from apps.auth_service.serializers import (
    PermissionSerializer,
    PermissionDetailSerializer,
    PermissionCreateSerializer,
    PermissionUpdateSerializer
)
import logging

logger = logging.getLogger('sciTigerCore')


class ManagementPermissionViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    权限管理视图集
    
    提供管理员权限相关的API接口
    
    权限分为两种类型：
    1. 系统全局权限 (is_system=True)：系统预设的权限，适用于所有租户，不关联特定租户
    2. 租户级权限 (is_tenant_level=True)：特定租户的自定义权限，必须关联到特定租户
    
    这两种类型互斥，一个权限不能同时是系统权限和租户级权限。
    
    超级管理员可以：
    - 查看所有权限（系统权限和所有租户的权限）
    - 创建系统权限和租户级权限
    - 更新任何权限
    - 删除租户级权限（系统权限通常不允许删除）
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    filterset_class = PermissionFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description', 'service', 'resource', 'action']
    ordering_fields = ['name', 'code', 'service', 'resource', 'action', 'is_system', 'is_tenant_level', 'created_at', 'updated_at']
    ordering = ['-created_at', 'service', 'resource', 'action', ]  # 默认排序
    
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
        获取权限列表，管理员可以查看所有权限
        """
        # 获取查询参数
        tenant_id = self.request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        if tenant_id:   
             # 获取系统权限
            system_permissions = PermissionService.get_permissions(is_system=True)
            logger.debug(f"system_permissions: {system_permissions}")
            # 获取当前租户的权限
            tenant_permissions = PermissionService.get_permissions(tenant_id=tenant_id)
            logger.debug(f"tenant_permissions: {tenant_permissions}")
            logger.debug(f"system_permissions | tenant_permissions: {system_permissions | tenant_permissions}")
            # 合并查询集
            return system_permissions | tenant_permissions
        else:
            return Permission.objects.all()
    
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
        
        超级管理员可以创建系统权限或租户级权限
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
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
        
        超级管理员可以更新任何权限
        """
        permission = self.get_object()
        serializer = self.get_serializer(permission, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
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
        
        超级管理员可以删除租户级权限，但通常不允许删除系统权限
        """
        permission = self.get_object()
        
        # # 系统权限不允许删除
        # if permission.is_system:
        #     return self.get_error_response(
        #         "系统权限不允许删除",
        #         status_code=status.HTTP_403_FORBIDDEN
        #     )
        
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
            
    @action(detail=False, methods=['post'])
    def import_default(self, request):
        """
        导入默认的系统权限
        """
        # 只允许超级管理员执行此操作
        if not request.user.is_superuser:
            return self.get_error_response("只有超级管理员可以导入默认权限", status_code=status.HTTP_403_FORBIDDEN)
        
        # 导入默认数据
        stats = PermissionService.import_default_permissions()
        
        return self.get_success_response(stats, message="默认权限数据导入完成") 