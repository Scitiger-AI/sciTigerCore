"""
认证服务
"""

import logging
from django.db import transaction
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.auth_service.models import User, LoginAttempt
from apps.tenant_service.services import TenantUserService

logger = logging.getLogger('sciTigerCore')


class AuthService:
    """
    认证服务类
    
    提供认证相关的业务逻辑处理
    """
    
    @staticmethod
    def authenticate_user(username, password, request=None):
        """
        用户认证
        
        Args:
            username: 用户名或邮箱
            password: 密码
            request: 请求对象，用于获取IP等信息
            
        Returns:
            tuple: (user, tokens, error_message)
                user: 认证成功的用户对象，认证失败时为None
                tokens: 包含access和refresh令牌的字典，认证失败时为None
                error_message: 错误信息，认证成功时为None
        """
        # 记录登录尝试
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT')
        
        # 尝试认证
        user = authenticate(username=username, password=password)
        
        if not user:
            # 记录失败的登录尝试
            LoginAttempt.record_attempt(
                email=username,
                ip_address=ip_address or '0.0.0.0',
                status=LoginAttempt.STATUS_FAILED,
                user_agent=user_agent,
                reason="用户名或密码不正确"
            )
            logger.warning(f"Failed login attempt for: {username}")
            return None, None, "用户名或密码不正确"
        
        # 检查用户状态
        if not user.is_active:
            LoginAttempt.record_attempt(
                email=username,
                ip_address=ip_address or '0.0.0.0',
                status=LoginAttempt.STATUS_FAILED,
                user=user,
                user_agent=user_agent,
                reason="账户未激活"
            )
            logger.warning(f"Login attempt for inactive user: {user.username}")
            return None, None, "账户未激活，请联系管理员"
        
        # 检查用户是否属于当前租户
        tenant = None
        if request:
            tenant = getattr(request, 'tenant', None)
            
        if tenant:
            # 检查用户是否是租户成员
            tenant_user = TenantUserService.get_tenant_user(tenant=tenant, user=user)
            if not tenant_user or not tenant_user.is_active:
                LoginAttempt.record_attempt(
                    email=username,
                    ip_address=ip_address or '0.0.0.0',
                    status=LoginAttempt.STATUS_FAILED,
                    user=user,
                    user_agent=user_agent,
                    reason="用户不属于当前租户或未激活"
                )
                logger.warning(f"Login attempt for user not in tenant: {user.username}, tenant: {tenant.name}")
                return None, None, "用户不属于当前租户或未激活"
        
        # 生成令牌
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        # 更新用户最后登录时间
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # 记录成功的登录尝试
        LoginAttempt.record_attempt(
            email=username,
            ip_address=ip_address or '0.0.0.0',
            status=LoginAttempt.STATUS_SUCCESS,
            user=user,
            user_agent=user_agent
        )
        logger.info(f"Successful login: {user.username}")
        
        return user, tokens, None
    
    @staticmethod
    def authenticate_admin(username, password, request=None):
        """
        管理员认证
        
        Args:
            username: 用户名或邮箱
            password: 密码
            request: 请求对象，用于获取IP等信息
            
        Returns:
            tuple: (user, tokens, error_message)
                user: 认证成功的管理员对象，认证失败时为None
                tokens: 包含access和refresh令牌的字典，认证失败时为None
                error_message: 错误信息，认证成功时为None
        """
        # 记录登录尝试
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT')
        
        # 尝试认证
        user = authenticate(username=username, password=password)
        
        if not user:
            # 记录失败的登录尝试
            LoginAttempt.record_attempt(
                email=username,
                ip_address=ip_address or '0.0.0.0',
                status=LoginAttempt.STATUS_FAILED,
                user_agent=user_agent,
                is_admin_login=True,
                reason="用户名或密码不正确"
            )
            logger.warning(f"Failed admin login attempt for username: {username}")
            return None, None, "用户名或密码不正确"
        
        # 检查用户状态
        if not user.is_active:
            LoginAttempt.record_attempt(
                email=username,
                ip_address=ip_address or '0.0.0.0',
                status=LoginAttempt.STATUS_FAILED,
                user=user,
                user_agent=user_agent,
                reason="账户未激活",
                is_admin_login=True
            )
            logger.warning(f"Admin login attempt for inactive user: {user.username}")
            return None, None, "账户未激活，请联系超级管理员"
        
        # 检查管理员权限
        if not (user.is_staff or user.is_superuser):
            LoginAttempt.record_attempt(
                email=username,
                ip_address=ip_address or '0.0.0.0',
                status=LoginAttempt.STATUS_FAILED,
                user=user,
                user_agent=user_agent,
                reason="非管理员用户",
                is_admin_login=True
            )
            logger.warning(f"Admin login attempt by non-admin user: {user.username}")
            return None, None, "您没有管理员权限"
        
        # 生成管理员令牌，包含额外的管理员信息
        refresh = RefreshToken.for_user(user)
        
        # 添加管理员特定的声明
        refresh['is_admin'] = True
        refresh['is_staff'] = user.is_staff
        refresh['is_superuser'] = user.is_superuser
        
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        # 更新用户最后登录时间
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # 记录成功的登录尝试
        LoginAttempt.record_attempt(
            email=username,
            ip_address=ip_address or '0.0.0.0',
            status=LoginAttempt.STATUS_SUCCESS,
            user=user,
            user_agent=user_agent,
            is_admin_login=True
        )
        logger.info(f"Successful admin login: {user.username}")
        
        return user, tokens, None
    
    @staticmethod
    @transaction.atomic
    def register_user(username, email, password, **user_data):
        """
        用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            user_data: 其他用户数据
            
        Returns:
            tuple: (user, error_message)
                user: 创建的用户对象，创建失败时为None
                error_message: 错误信息，创建成功时为None
        """
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return None, "用户名已存在"
        
        # 检查邮箱是否已存在
        if User.objects.filter(email=email).exists():
            return None, "邮箱已被注册"
        
        # 创建用户
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                **user_data
            )
            logger.info(f"User registered: {user.username}")
            return user, None
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return None, f"注册失败: {str(e)}"
    
    @staticmethod
    def refresh_token(refresh_token):
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            tuple: (tokens, error_message)
                tokens: 包含新的access和refresh令牌的字典，刷新失败时为None
                error_message: 错误信息，刷新成功时为None
        """
        try:
            refresh = RefreshToken(refresh_token)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return tokens, None
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None, "无效的刷新令牌"
    
    @staticmethod
    def refresh_admin_token(refresh_token):
        """
        刷新管理员访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            tuple: (tokens, error_message)
                tokens: 包含新的access和refresh令牌的字典，刷新失败时为None
                error_message: 错误信息，刷新成功时为None
        """
        try:
            refresh = RefreshToken(refresh_token)
            
            # 验证是否为管理员令牌
            if not refresh.get('is_admin', False):
                return None, "非管理员令牌"
            
            # 保留管理员特定的声明
            is_admin = refresh.get('is_admin', False)
            is_staff = refresh.get('is_staff', False)
            is_superuser = refresh.get('is_superuser', False)
            
            # 确保新的访问令牌也包含这些声明
            refresh['is_admin'] = is_admin
            refresh['is_staff'] = is_staff
            refresh['is_superuser'] = is_superuser
            refresh.access_token['is_admin'] = is_admin
            refresh.access_token['is_staff'] = is_staff
            refresh.access_token['is_superuser'] = is_superuser
            
            # 创建新的令牌
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            return tokens, None
        except Exception as e:
            logger.error(f"Error refreshing admin token: {str(e)}")
            return None, "无效的刷新令牌"
    
    @staticmethod
    def logout(refresh_token, request=None):
        """
        用户登出
        
        将刷新令牌加入黑名单，使其失效
        
        Args:
            refresh_token: 刷新令牌
            request: 请求对象，用于获取IP等信息
            
        Returns:
            tuple: (success, error_message)
                success: 是否成功登出
                error_message: 错误信息，登出成功时为None
        """
        try:
            # 获取令牌对象
            token = RefreshToken(refresh_token)
            
            # 获取用户ID
            user_id = token.get('user_id')
            
            # 将令牌加入黑名单
            token.blacklist()
            
            # 记录日志
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    logger.info(f"User logged out: {user.username}")
                except User.DoesNotExist:
                    logger.info(f"User logged out with ID: {user_id}")
            
            return True, None
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return False, f"登出失败: {str(e)}" 