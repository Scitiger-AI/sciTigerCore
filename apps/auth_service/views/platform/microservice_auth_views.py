"""
微服务认证视图

提供专门用于微服务的认证验证API
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from core.mixins import ResponseMixin
from apps.auth_service.services import AuthService, ApiKeyService
from apps.auth_service.models import User
from apps.auth_service.serializers import ApiKeyDetailSerializer

logger = logging.getLogger('sciTigerCore')


class MicroserviceVerifyTokenView(ResponseMixin, APIView):
    """
    微服务JWT令牌验证视图
    
    提供专门用于微服务的JWT令牌验证功能，无需认证即可调用
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        验证JWT令牌
        
        请求体格式：
        {
            "token": "JWT令牌",
            "service": "服务名称(可选)",
            "resource": "资源类型(可选)",
            "action": "操作类型(可选)"
        }
        """
        # 获取请求数据
        token = request.data.get('token')
        service = request.data.get('service')
        resource = request.data.get('resource')
        action = request.data.get('action')
        
        if not token:
            return self.get_error_response("缺少令牌参数", status_code=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 验证令牌
            valid, user_info = self._verify_token(token)
            
            if not valid:
                return self.get_error_response("无效的令牌", status_code=status.HTTP_401_UNAUTHORIZED)
            
            # 如果指定了服务、资源和操作，则检查权限
            if service and resource and action:
                logger.info(f"检查权限: {service}, {resource}, {action}")
                has_permission = self._check_permission(user_info, service, resource, action)
                if not has_permission:
                    return self.get_error_response("用户没有所需的权限", status_code=status.HTTP_403_FORBIDDEN)
            
            # 返回用户信息
            return self.get_success_response({
                'id': user_info.get('user_id'),
                'username': user_info.get('username'),
                'email': user_info.get('email'),
                'is_active': user_info.get('is_active', True),
                'tenant_id': user_info.get('tenant_id'),
                'roles': user_info.get('roles', []),
                'permissions': user_info.get('permissions', [])
            }, message="令牌验证成功")
        
        except Exception as e:
            logger.error(f"微服务令牌验证错误: {str(e)}")
            return self.get_error_response(f"令牌验证失败: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _verify_token(self, token):
        """
        验证JWT令牌并获取用户信息
        
        Args:
            token: JWT令牌
            
        Returns:
            tuple: (valid, user_info)
                valid: 令牌是否有效
                user_info: 用户信息字典
        """
        try:
            # 解析令牌
            token_obj = AccessToken(token)
            payload = token_obj.payload
            
            # 检查令牌是否在黑名单中
            from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
            jti = payload.get('jti')
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                return False, None
            
            # 获取用户ID
            user_id = payload.get('user_id')
            if not user_id:
                return False, None
            
            # 获取用户信息
            try:
                user = User.objects.get(id=user_id)
                
                # 检查用户状态
                if not user.is_active:
                    return False, None
                
                # 获取用户角色和权限
                from apps.auth_service.services import RoleService, PermissionService
                roles = RoleService.get_user_roles(user.id)
                permissions = PermissionService.get_user_permissions(user.id)
                
                # 获取用户的租户信息
                tenant_id = None
                from apps.tenant_service.models import TenantUser
                tenant_user = TenantUser.objects.filter(user=user).first()
                if tenant_user:
                    tenant_id = str(tenant_user.tenant.id)
                
                # 构建用户信息
                user_info = {
                    'user_id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'tenant_id': tenant_id,
                    'roles': [{'id': str(r.id), 'name': r.name} for r in roles],
                    'permissions': [{'id': str(p.id), 'code': p.code} for p in permissions]
                }
                
                return True, user_info
            except User.DoesNotExist:
                return False, None
        
        except (TokenError, InvalidToken):
            return False, None
    
    def _check_permission(self, user_info, service, resource, action):
        """
        检查用户是否有权限执行指定操作
        
        Args:
            user_info: 用户信息字典
            service: 服务名称
            resource: 资源类型
            action: 操作类型
            
        Returns:
            bool: 是否有权限
        """
        # 超级管理员拥有所有权限
        if user_info.get('is_superuser'):
            return True
        
        # 检查权限
        permission_code = f"{service}:{resource}:{action}"
        permissions = user_info.get('permissions', [])
        
        logger.info(f"检查权限: {permission_code}, 用户permissions:{permissions}")
        for permission in permissions:
            if permission['code'] == permission_code:
                return True
        
        return False


class MicroserviceVerifyApiKeyView(ResponseMixin, APIView):
    """
    微服务API密钥验证视图
    
    提供专门用于微服务的API密钥验证功能，无需认证即可调用
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        验证API密钥
        
        请求体格式：
        {
            "key": "API密钥",
            "service": "服务名称(可选)",
            "resource": "资源类型(可选)",
            "action": "操作类型(可选)"
        }
        """
        # 获取请求数据
        key = request.data.get('key')
        service = request.data.get('service')
        resource = request.data.get('resource')
        action = request.data.get('action')
        logger.info(f"MicroserviceVerifyApiKeyView: {key}, {service}, {resource}, {action}")
        if not key:
            return self.get_error_response("缺少API密钥参数", status_code=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 验证API密钥
            api_key, error_message = ApiKeyService.verify_api_key(
                key_value=key,
                service=service,
                resource=resource,
                action=action
            )
            
            if not api_key:
                return self.get_error_response(error_message or "无效的API密钥", 
                                               status_code=status.HTTP_401_UNAUTHORIZED)
            
            # 记录API密钥使用
            client_ip = self._get_client_ip(request)
            ApiKeyService.log_api_key_usage(
                api_key=api_key,
                request_path=request.path,
                request_method=request.method,
                response_status=200,
                client_ip=client_ip,
                request_id=getattr(request, 'request_id', None)
            )
            logger.info(f"返回API密钥信息: {api_key},  {api_key.tenant}, {api_key.tenant.id}")
            # 返回API密钥信息
            result = {
                'id': str(api_key.id),
                'key_type': api_key.key_type,
                'name': api_key.name,
                'prefix': api_key.prefix,
                'is_active': api_key.is_active,
                'tenant_id': str(api_key.tenant.id) if api_key.tenant else None,
                'user_id': str(api_key.user.id) if api_key.user else None,
                'application_name': api_key.application_name
            }
            
            # 添加API密钥作用域信息
            scopes = api_key.scopes.all()
            scopes_list = []
            for scope in scopes:
                scopes_list.append({
                    'id': str(scope.id),
                    'service': scope.service,
                    'resource': scope.resource,
                    'action': scope.action
                })
            result['scopes'] = scopes_list
            
            logger.info(f"返回API密钥信息: {result}")
            # 如果是用户级API密钥，添加用户信息
            if api_key.key_type == 'user' and api_key.user:
                user = api_key.user
                
                # 获取用户角色和权限
                from apps.auth_service.services import RoleService, PermissionService
                
                # 正确传递用户ID
                roles = RoleService.get_user_roles(user.id)
                permissions = PermissionService.get_user_permissions(user.id)
                
                # 添加错误处理
                roles_list = []
                if roles is not None:  # 如果返回了有效的角色集
                    roles_list = [{'id': str(r.id), 'name': r.name} for r in roles]
                
                permissions_list = []
                if permissions is not None:  # 如果返回了有效的权限集
                    permissions_list = [{'id': str(p.id), 'code': p.code} for p in permissions]
                
                logger.info(f"返回用户信息: {user.id}, {user.username}, {user.email}, {user.is_active}")
                result['user'] = {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'is_active': user.is_active,
                    'roles': roles_list,
                    'permissions': permissions_list
                }
            
            return self.get_success_response(result, message="API密钥验证成功")
        
        except Exception as e:
            logger.error(f"微服务API密钥验证错误: {str(e)}")
            return self.get_error_response(f"API密钥验证失败: {str(e)}", 
                                           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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