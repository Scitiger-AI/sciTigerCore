"""
用户管理视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.auth_service.services import UserService, AuthService
from apps.auth_service.filters import UserFilter
from apps.auth_service.serializers import (
    UserSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    UserUpdateSerializer
)
from apps.tenant_service.services import TenantUserService
from apps.tenant_service.models import Tenant


class UserManagementViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    用户管理视图集
    
    提供用户管理相关的API
    """
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    filterset_class = UserFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['username', 'email', 'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser']
    ordering = ['-date_joined']  # 默认按注册时间降序排序
    
    def get_queryset(self):
        """
        获取用户查询集
        
        管理员可以查看所有用户，包括非活跃用户
        """
        # 获取当前租户ID
        tenant_id = self.request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
     
        # 超级管理员可以查看所有租户的用户
        if self.request.user.is_superuser:
            return UserService.get_users(tenant_id=tenant_id, include_inactive=True)
        
        # 租户管理员只能查看自己租户的用户
        return UserService.get_users(tenant_id=tenant_id, include_inactive=True)
    
    def get_serializer_class(self):
        """
        获取序列化器类
        
        根据不同的操作返回不同的序列化器
        """
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return self.serializer_class
    
    def list(self, request):
        """
        获取用户列表，支持过滤、搜索和排序
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # 获取当前租户ID
        tenant_id = request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 准备序列化器上下文
        context = self.get_serializer_context()
        context['current_tenant_id'] = tenant_id
        
        # 使用DRF的分页机制
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        
        # 如果没有分页或分页被禁用，返回所有数据
        serializer = self.get_serializer(queryset, many=True, context=context)
        return self.get_success_response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        获取用户详情
        """
        user = UserService.get_user_by_id(pk)
        if not user:
            return self.get_error_response("用户不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 获取当前租户ID
        tenant_id = request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 准备序列化器上下文
        context = self.get_serializer_context()
        context['current_tenant_id'] = tenant_id
        
        serializer = self.get_serializer(user, context=context)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建用户
        """
        # 验证数据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 移除确认密码字段
        user_data = serializer.validated_data.copy()
        user_data.pop('password_confirm')
        
        # 处理角色
        roles = user_data.pop('roles', None)
        
        # 提取租户相关参数
        tenant_id = user_data.pop('tenant_id', None)
        tenant_role = user_data.pop('tenant_role', 'member')
        
        # 注册用户
        user, error_message = AuthService.register_user(
            username=user_data.pop('username'),
            email=user_data.pop('email'),
            password=user_data.pop('password'),
            **user_data
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 添加角色
        if roles:
            user.roles.set(roles)
        
        # 如果提供了租户ID，将用户添加到租户
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id)
                TenantUserService.create_tenant_user(
                    tenant=tenant,
                    user=user,
                    role=tenant_role
                )
            except Tenant.DoesNotExist:
                return self.get_error_response(f"租户ID {tenant_id} 不存在")
            except Exception as e:
                # 记录错误但不影响用户创建
                pass
        
        # 返回用户信息
        result_serializer = UserDetailSerializer(user)
        return self.get_success_response(
            result_serializer.data,
            message="用户创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None, partial=False):
        """
        更新用户信息
        """
        # 获取用户
        user = UserService.get_user_by_id(pk)
        if not user:
            return self.get_error_response("用户不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 验证数据
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 处理角色
        roles = serializer.validated_data.pop('roles', None)
        
        # 更新用户
        updated_user, error_message = UserService.update_user(
            user_id=pk,
            **serializer.validated_data
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 更新角色
        if roles is not None:
            updated_user.roles.set(roles)
        
        # 返回更新后的用户信息
        result_serializer = UserDetailSerializer(updated_user)
        return self.get_success_response(result_serializer.data, message="用户信息更新成功")
    
    def partial_update(self, request, pk=None):
        """
        部分更新用户信息
        """
        return self.update(request, pk, partial=True)
    
    def destroy(self, request, pk=None):
        """
        删除用户
        """
        # 删除用户
        success = UserService.delete_user(pk)
        
        if not success:
            return self.get_error_response("用户删除失败，可能是用户不存在")
        
        return self.get_success_response(message="用户删除成功")
    
    @action(detail=False, methods=['get'])
    def userInfo(self, request):
        """
        获取当前登录管理员的信息
        """
        # 获取当前用户
        user = request.user
        
        # 获取当前租户ID
        tenant_id = request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 准备序列化器上下文
        context = self.get_serializer_context()
        context['current_tenant_id'] = tenant_id
        
        # 序列化用户信息
        serializer = UserDetailSerializer(user, context=context)
        
        # 返回用户信息
        return self.get_success_response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        激活用户
        """
        # 激活用户
        user, error_message = UserService.change_user_status(pk, True)
        
        if error_message:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="用户已激活")
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        禁用用户
        """
        # 禁用用户
        user, error_message = UserService.change_user_status(pk, False)
        
        if error_message:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="用户已禁用")
    
    @action(detail=True, methods=['post'])
    def verify_email(self, request, pk=None):
        """
        验证用户邮箱
        """
        # 验证邮箱
        user, error_message = UserService.verify_user_email(pk)
        
        if error_message:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="用户邮箱已验证")
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        重置用户密码
        """
        # 获取新密码
        new_password = request.data.get('new_password')
        if not new_password:
            return self.get_error_response("必须提供新密码")
        
        # 重置密码
        user, error_message = UserService.update_user(
            user_id=pk,
            password=new_password
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="用户密码已重置") 