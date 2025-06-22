"""
认证管理视图
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from core.mixins import ResponseMixin
from apps.auth_service.services import AuthService
from apps.auth_service.serializers import (
    LoginSerializer,
    TokenRefreshSerializer,
    LogoutSerializer
)


class ManagementLoginView(ResponseMixin, APIView):
    """
    管理员登录视图
    
    提供管理员登录功能，返回JWT令牌
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        管理员登录
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # 认证用户
        user, tokens, error_message = AuthService.authenticate_admin(
            username=username,
            password=password,
            request=request
        )
        
        if error_message:
            return self.get_error_response(error_message, status_code=status.HTTP_401_UNAUTHORIZED)
        
        # 返回令牌
        return self.get_success_response({
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'last_login': user.last_login
            },
            'tokens': tokens,
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh']
        }, message="管理员登录成功")


class ManagementLogoutView(ResponseMixin, APIView):
    """
    管理员登出视图
    
    提供管理员登出功能，使当前令牌失效
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        管理员登出
        """
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = serializer.validated_data['refresh']
        
        # 登出处理
        success, error_message = AuthService.logout(
            refresh_token=refresh_token,
            request=request
        )
        
        if not success:
            return self.get_error_response(error_message, status_code=status.HTTP_400_BAD_REQUEST)
        
        # 返回成功响应
        return self.get_success_response(None, message="管理员登出成功")


class ManagementTokenRefreshView(ResponseMixin, APIView):
    """
    管理令牌刷新视图
    
    提供刷新JWT访问令牌的功能
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        刷新令牌
        """
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = serializer.validated_data['refresh']
        
        # 刷新令牌
        tokens, error_message = AuthService.refresh_admin_token(refresh_token)
        
        if error_message:
            return self.get_error_response(error_message, status_code=status.HTTP_401_UNAUTHORIZED)
        
        # 返回新令牌
        return self.get_success_response({
            'tokens': tokens,
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh']
        }, message="令牌刷新成功")


class AdminProfileView(ResponseMixin, APIView):
    """
    管理员个人资料视图
    
    提供获取和更新管理员个人资料的功能
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        获取管理员个人资料
        """
        user = request.user
        
        # 返回管理员信息
        return self.get_success_response({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'last_login': user.last_login,
            'date_joined': user.date_joined,
            'permissions': self._get_admin_permissions(user)
        })
    
    def _get_admin_permissions(self, user):
        """
        获取管理员权限列表
        """
        # 如果是超级用户，返回所有权限
        if user.is_superuser:
            return ["*"]  # 表示拥有所有权限
        
        # 否则返回用户角色关联的权限
        permissions = []
        for role in user.roles.all():
            for permission in role.permissions.all():
                permission_code = f"{permission.service}:{permission.resource}:{permission.action}"
                if permission_code not in permissions:
                    permissions.append(permission_code)
        
        return permissions 