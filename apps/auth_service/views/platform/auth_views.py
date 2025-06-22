"""
认证平台视图
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.mixins import ResponseMixin
from apps.auth_service.services import AuthService
from apps.auth_service.serializers import (
    LoginSerializer,
    TokenRefreshSerializer,
    LogoutSerializer,
    RegisterSerializer
)
from apps.tenant_service.services import TenantUserService


class LoginView(ResponseMixin, APIView):
    """
    用户登录视图
    
    提供用户登录功能，返回JWT令牌
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        用户登录
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # 认证用户
        user, tokens, error_message = AuthService.authenticate_user(
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
                'last_login': user.last_login
            },
            'tokens': tokens,
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh']
        }, message="登录成功")


class LogoutView(ResponseMixin, APIView):
    """
    用户登出视图
    
    提供用户登出功能，使当前令牌失效
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        用户登出
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
        return self.get_success_response(None, message="登出成功")


class TokenRefreshView(ResponseMixin, APIView):
    """
    令牌刷新视图
    
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
        tokens, error_message = AuthService.refresh_token(refresh_token)
        
        if error_message:
            return self.get_error_response(error_message, status_code=status.HTTP_401_UNAUTHORIZED)
        
        # 返回新令牌
        return self.get_success_response({
            'tokens': tokens,
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh']
        }, message="令牌刷新成功")


class RegisterView(ResponseMixin, APIView):
    """
    用户注册视图
    
    提供用户注册功能
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        用户注册
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 移除确认密码字段
        user_data = serializer.validated_data.copy()
        user_data.pop('password_confirm')
        
        # 注册用户
        user, error_message = AuthService.register_user(
            username=user_data.pop('username'),
            email=user_data.pop('email'),
            password=user_data.pop('password'),
            **user_data
        )
        
        if error_message:
            return self.get_error_response(error_message, status_code=status.HTTP_400_BAD_REQUEST)
        
        # 获取当前租户
        tenant = getattr(request, 'tenant', None)
        if tenant:
            # 将用户添加到租户中
            try:
                TenantUserService.create_tenant_user(tenant=tenant, user=user)
            except Exception as e:
                # 如果添加到租户失败，记录错误但不影响注册流程
                pass
        
        # 返回用户信息
        return self.get_success_response({
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email
            }
        }, message="注册成功", status_code=status.HTTP_201_CREATED) 