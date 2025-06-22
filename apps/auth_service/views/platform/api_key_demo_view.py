"""
API密钥认证示例视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import ResponseMixin
from core.authentication.api_key_authentication import ApiKeyAuthentication
from core.permissions.api_key_permissions import HasApiKeyScope, IsSystemApiKey, IsUserApiKey
from rest_framework.permissions import IsAuthenticated


class ApiKeyDemoViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    API密钥认证示例视图集
    
    用于演示如何使用API密钥认证
    """
    # 添加API密钥认证类
    authentication_classes = [ApiKeyAuthentication]
    
    # 添加权限类，要求API密钥具有特定作用域
    permission_classes = [IsAuthenticated, HasApiKeyScope]
    
    # 定义各操作所需的作用域
    required_scopes = {
        'list': {'service': 'auth_service', 'resource': 'api_keys', 'action': 'read'},
        'create': {'service': 'auth_service', 'resource': 'api_keys', 'action': 'write'},
        'retrieve': {'service': 'auth_service', 'resource': 'api_keys', 'action': 'read'},
        'update': {'service': 'auth_service', 'resource': 'api_keys', 'action': 'write'},
        'delete': {'service': 'auth_service', 'resource': 'api_keys', 'action': 'delete'},
    }
    
    def list(self, request):
        """
        列表接口示例
        
        需要 auth_service:api_keys:read 作用域
        """
        return self.get_success_response({
            'message': '成功访问列表接口',
            'api_key_info': {
                'key_type': getattr(request.api_key, 'key_type', None),
                'name': getattr(request.api_key, 'name', None),
                'tenant_id': str(request.api_key.tenant_id) if hasattr(request.api_key, 'tenant_id') and request.api_key.tenant_id else None,
                'user_id': str(request.api_key.user_id) if hasattr(request.api_key, 'user_id') and request.api_key.user_id else None,
            } if hasattr(request, 'api_key') else None,
            'user_info': {
                'id': str(request.user.id) if hasattr(request.user, 'id') else None,
                'username': getattr(request.user, 'username', None),
                'is_authenticated': request.user.is_authenticated,
                'is_system_api': getattr(request.user, 'is_system_api', False),
            }
        })
    
    def retrieve(self, request, pk=None):
        """
        详情接口示例
        
        需要 auth_service:api_keys:read 作用域
        """
        return self.get_success_response({
            'message': f'成功访问详情接口，ID: {pk}',
            'api_key_info': {
                'key_type': getattr(request.api_key, 'key_type', None),
                'name': getattr(request.api_key, 'name', None),
            } if hasattr(request, 'api_key') else None
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsSystemApiKey])
    def system_only(self, request):
        """
        仅系统级API密钥可访问的接口示例
        """
        return self.get_success_response({
            'message': '成功访问仅系统级API密钥可访问的接口',
            'api_key_type': request.api_key.key_type
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsUserApiKey])
    def user_only(self, request):
        """
        仅用户级API密钥可访问的接口示例
        """
        return self.get_success_response({
            'message': '成功访问仅用户级API密钥可访问的接口',
            'api_key_type': request.api_key.key_type,
            'user_id': str(request.user.id) if hasattr(request.user, 'id') else None
        })


class ApiKeyDemoView(ResponseMixin, APIView):
    """
    API密钥认证示例视图
    
    用于演示在APIView中如何使用API密钥认证
    """
    # 添加API密钥认证类
    authentication_classes = [ApiKeyAuthentication]
    
    # 添加权限类
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET请求示例
        """
        return self.get_success_response({
            'message': '成功通过API密钥认证访问GET接口',
            'api_key_info': {
                'key_type': getattr(request.api_key, 'key_type', None),
                'name': getattr(request.api_key, 'name', None),
            } if hasattr(request, 'api_key') else None,
            'user_info': {
                'id': str(request.user.id) if hasattr(request.user, 'id') else None,
                'username': getattr(request.user, 'username', None),
                'is_authenticated': request.user.is_authenticated,
            }
        })
    
    def post(self, request):
        """
        POST请求示例
        """
        return self.get_success_response({
            'message': '成功通过API密钥认证访问POST接口',
            'request_data': request.data
        }) 