"""
用户平台视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.auth_service.services import UserService
from apps.auth_service.filters import UserFilter
from apps.auth_service.serializers import (
    UserSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)


class UserViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    用户视图集
    
    提供用户相关的API
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    filterset_class = UserFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['username', 'email', 'date_joined', 'last_login', 'is_active']
    ordering = ['-date_joined']  # 默认按注册时间降序排序
    
    def get_queryset(self):
        """
        获取用户查询集
        
        根据当前用户的权限和租户过滤用户列表
        """
        # 获取当前租户ID
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            tenant_id = tenant_id.id
        else:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 获取用户列表
        return UserService.get_users(tenant_id=tenant_id)
    
    def get_serializer_class(self):
        """
        获取序列化器类
        
        根据不同的操作返回不同的序列化器
        """
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
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
    
    def update(self, request, pk=None, partial=False):
        """
        更新用户信息
        """
        # 检查是否是当前用户或有管理权限
        if str(request.user.id) != pk:
            # 这里可以添加权限检查
            pass
        
        # 获取用户
        user = UserService.get_user_by_id(pk)
        if not user:
            return self.get_error_response("用户不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 验证数据
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 更新用户
        updated_user, error_message = UserService.update_user(
            user_id=pk,
            **serializer.validated_data
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回更新后的用户信息
        result_serializer = UserDetailSerializer(updated_user)
        return self.get_success_response(result_serializer.data, message="用户信息更新成功")
    
    def partial_update(self, request, pk=None):
        """
        部分更新用户信息
        """
        return self.update(request, pk, partial=True)
    
    @action(detail=False, methods=['get'])
    def userInfo(self, request):
        """
        获取当前登录用户的信息
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
    def change_password(self, request, pk=None):
        """
        修改密码
        """
        # 只允许修改自己的密码
        if str(request.user.id) != pk:
            return self.get_error_response("只能修改自己的密码", status_code=status.HTTP_403_FORBIDDEN)
        
        # 获取用户
        user = UserService.get_user_by_id(pk)
        if not user:
            return self.get_error_response("用户不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 验证数据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 验证旧密码
        if not user.check_password(serializer.validated_data['old_password']):
            return self.get_error_response("旧密码不正确")
        
        # 更新密码
        updated_user, error_message = UserService.update_user(
            user_id=pk,
            password=serializer.validated_data['new_password']
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="密码修改成功")
    
    @action(detail=True, methods=['post'])
    def verify_email(self, request, pk=None):
        """
        验证邮箱
        
        通常这个API会在用户点击验证邮件中的链接时被调用
        这里简化处理，直接验证
        """
        # 这里应该有权限检查或验证码检查
        
        # 验证邮箱
        user, error_message = UserService.verify_user_email(pk)
        
        if error_message:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="邮箱验证成功") 