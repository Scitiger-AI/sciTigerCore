"""
API密钥认证类

实现基于API密钥的认证机制
"""

import logging
from rest_framework import authentication
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from apps.auth_service.models import ApiKey
from apps.auth_service.services import ApiKeyService

logger = logging.getLogger('sciTigerCore')


class ApiKeyAuthentication(authentication.BaseAuthentication):
    """
    API密钥认证类
    
    从请求中提取API密钥并验证，支持从以下位置提取API密钥：
    1. Authorization头: Bearer {api_key} 或 ApiKey {api_key}
    2. 自定义头: X-Api-Key
    3. 查询参数: api_key
    """
    
    keyword = 'ApiKey'
    
    def authenticate(self, request):
        """
        认证方法
        
        从请求中提取API密钥并验证
        
        Args:
            request: 请求对象
            
        Returns:
            tuple: (user, api_key) 认证成功时返回用户对象和API密钥对象
            
        Raises:
            AuthenticationFailed: 认证失败时抛出异常
        """
        # 尝试从不同位置获取API密钥
        key = self._get_key_from_request(request)
        
        if not key:
            # 没有提供API密钥，返回None表示尝试其他认证方式
            return None
        
        # 验证API密钥
        api_key, error_message = ApiKeyService.verify_api_key(key_value=key)
        
        if not api_key:
            # API密钥无效
            logger.warning(f"Invalid API key used: {key[:8]}...")
            raise exceptions.AuthenticationFailed(_(error_message or '无效的API密钥'))
        
        # 记录API密钥使用
        ApiKeyService.log_api_key_usage(
            api_key=api_key,
            request_path=request.path,
            request_method=request.method,
            response_status=200,  # 假设认证成功
            client_ip=self._get_client_ip(request),
            request_id=getattr(request, 'request_id', None)
        )
        
        # 确定用户
        user = None
        
        # 如果是用户级API密钥，直接使用关联的用户
        if api_key.key_type == ApiKey.TYPE_USER and api_key.user:
            user = api_key.user
            
            # 检查用户状态
            if not user.is_active:
                logger.warning(f"API key used for inactive user: {user.username}")
                raise exceptions.AuthenticationFailed(_('用户账户未激活'))
        
        # 如果是系统级API密钥，创建一个匿名用户对象
        elif api_key.key_type == ApiKey.TYPE_SYSTEM:
            # 使用AnonymousUser或创建一个特殊的系统用户
            from django.contrib.auth.models import AnonymousUser
            user = AnonymousUser()
            
            # 为系统级API密钥设置特殊属性，以便在权限检查时使用
            user.is_system_api = True
            user.api_key = api_key
            
            # 如果API密钥关联了租户，设置租户属性
            if api_key.tenant:
                user.tenant = api_key.tenant
        
        # 设置API密钥属性，以便在视图中使用
        request.api_key = api_key
        
        # 返回(user, auth)元组
        return (user, api_key)
    
    def _get_key_from_request(self, request):
        """
        从请求中提取API密钥
        
        按以下顺序尝试获取API密钥：
        1. Authorization头: Bearer {api_key} 或 ApiKey {api_key}
        2. 自定义头: X-Api-Key
        3. 查询参数: api_key
        
        Args:
            request: 请求对象
            
        Returns:
            str: API密钥，如果未找到则为None
        """
        # 1. 从Authorization头获取
        auth_header = authentication.get_authorization_header(request).decode('utf-8')
        
        if auth_header:
            auth_parts = auth_header.split()
            
            # 支持 "ApiKey xxx" 或 "Bearer xxx" 格式
            if len(auth_parts) == 2 and auth_parts[0].lower() in ['apikey', 'bearer']:
                return auth_parts[1]
        
        # 2. 从自定义头获取
        api_key_header = request.META.get('HTTP_X_API_KEY')
        if api_key_header:
            return api_key_header
        
        # 3. 从查询参数获取
        api_key_param = request.GET.get('api_key')
        if api_key_param:
            return api_key_param
        
        return None
    
    def _get_client_ip(self, request):
        """
        获取客户端IP地址
        
        Args:
            request: 请求对象
            
        Returns:
            str: 客户端IP地址
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # 如果有X-Forwarded-For头，取第一个IP
            return x_forwarded_for.split(',')[0].strip()
        else:
            # 否则使用REMOTE_ADDR
            return request.META.get('REMOTE_ADDR', '0.0.0.0')
    
    def authenticate_header(self, request):
        """
        返回认证头部
        
        用于生成401响应中的WWW-Authenticate头
        
        Args:
            request: 请求对象
            
        Returns:
            str: 认证头部
        """
        return self.keyword 