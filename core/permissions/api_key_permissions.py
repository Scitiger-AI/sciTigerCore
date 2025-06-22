"""
API密钥权限类

提供基于API密钥的权限检查
"""

import logging
from rest_framework import permissions

logger = logging.getLogger('sciTigerCore')


class HasApiKeyScope(permissions.BasePermission):
    """
    检查API密钥是否有指定的作用域权限
    
    使用方法：
    class MyViewSet(viewsets.ModelViewSet):
        permission_classes = [HasApiKeyScope]
        required_scopes = {
            'list': {'service': 'auth_service', 'resource': 'users', 'action': 'read'},
            'create': {'service': 'auth_service', 'resource': 'users', 'action': 'write'},
        }
    """
    
    def has_permission(self, request, view):
        """
        检查API密钥是否有权限访问视图
        
        Args:
            request: 请求对象
            view: 视图对象
            
        Returns:
            bool: 是否有权限
        """
        # 如果不是API密钥认证，跳过此权限检查
        if not hasattr(request, 'api_key'):
            return True
        
        # 获取API密钥
        api_key = request.api_key
        
        # 获取当前操作
        action = getattr(view, 'action', None)
        if not action:
            # 对于APIView，使用HTTP方法小写作为action
            action = request.method.lower()
        
        # 获取视图所需的作用域
        required_scopes = getattr(view, 'required_scopes', {})
        
        # 如果视图没有定义所需作用域，或当前操作没有定义所需作用域，则允许访问
        if not required_scopes or action not in required_scopes:
            return True
        
        # 获取当前操作所需的作用域
        scope = required_scopes.get(action)
        if not scope:
            return True
        
        # 检查API密钥是否有所需的作用域
        service = scope.get('service')
        resource = scope.get('resource')
        action_scope = scope.get('action')
        
        # 如果没有指定作用域参数，则允许访问
        if not service or not resource or not action_scope:
            return True
        
        # 检查API密钥是否有所需的作用域
        has_scope = api_key.scopes.filter(
            service=service,
            resource=resource,
            action=action_scope
        ).exists()
        
        if not has_scope:
            logger.warning(
                f"API key {api_key.id} ({api_key.name}) does not have required scope: "
                f"{service}:{resource}:{action_scope}"
            )
            return False
        
        return True


class IsSystemApiKey(permissions.BasePermission):
    """
    检查是否是系统级API密钥
    """
    
    def has_permission(self, request, view):
        """
        检查是否是系统级API密钥
        
        Args:
            request: 请求对象
            view: 视图对象
            
        Returns:
            bool: 是否是系统级API密钥
        """
        # 检查是否通过API密钥认证
        if not hasattr(request, 'api_key'):
            return False
        
        # 检查是否是系统级API密钥
        from apps.auth_service.models import ApiKey
        return request.api_key.key_type == ApiKey.TYPE_SYSTEM


class IsUserApiKey(permissions.BasePermission):
    """
    检查是否是用户级API密钥
    """
    
    def has_permission(self, request, view):
        """
        检查是否是用户级API密钥
        
        Args:
            request: 请求对象
            view: 视图对象
            
        Returns:
            bool: 是否是用户级API密钥
        """
        # 检查是否通过API密钥认证
        if not hasattr(request, 'api_key'):
            return False
        
        # 检查是否是用户级API密钥
        from apps.auth_service.models import ApiKey
        return request.api_key.key_type == ApiKey.TYPE_USER 