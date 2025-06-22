"""
租户中间件

用于识别当前请求的租户，并设置租户上下文
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.urls import resolve
from django.http import HttpResponseForbidden

logger = logging.getLogger('sciTigerCore')


class TenantMiddleware(MiddlewareMixin):
    """
    租户中间件
    
    从请求中识别租户，并设置租户上下文
    """
    
    def process_request(self, request):
        """
        处理请求，识别租户
        
        Args:
            request: HTTP请求对象
        """
        # 初始化租户为None
        request.tenant = None
        
        # 排除不需要租户的路径
        if self._should_bypass_tenant_check(request):
            return None
        
        # 尝试从不同来源识别租户
        tenant_id = self._get_tenant_id_from_request(request)
        
        if tenant_id:
            # 尝试加载租户
            tenant = self._get_tenant_by_id(tenant_id)
            
            if tenant:
                # 设置租户上下文
                request.tenant = tenant
                logger.debug(f"Tenant identified: {tenant.name} (ID: {tenant.id})")
            else:
                # 租户ID无效
                if self._is_tenant_required(request):
                    logger.warning(f"Invalid tenant ID: {tenant_id}")
                    return HttpResponseForbidden("Invalid tenant")
        else:
            # 没有提供租户ID
            if self._is_tenant_required(request):
                logger.warning("No tenant ID provided for tenant-required endpoint")
                return HttpResponseForbidden("Tenant ID is required")
    
    def _should_bypass_tenant_check(self, request):
        """
        检查是否应该跳过租户检查
        
        Args:
            request: HTTP请求对象
            
        Returns:
            bool: 是否应该跳过租户检查
        """
        # 获取当前URL的解析结果
        url_name = resolve(request.path_info).url_name
        
        # 管理API不需要租户检查
        if request.path.startswith('/api/management/'):
            return True
        
        # 认证相关的API不需要租户检查
        if url_name in ['login', 'register', 'token_refresh', 'token_verify', 'auth-verify-api-key',
                         'microservice-verify-token', 'microservice-verify-api-key']:
            return True
        
        # 健康检查API不需要租户检查
        if url_name in ['health_check']:
            return True
        
        return False
    
    def _get_tenant_id_from_request(self, request):
        """
        从请求中获取租户ID
        
        按照以下顺序尝试获取租户ID:
        1. 请求头 X-Tenant-ID
        2. 查询参数 tenant_id
        3. 子域名
        4. JWT令牌中的租户信息
        5. API密钥关联的租户
        
        Args:
            request: HTTP请求对象
            
        Returns:
            str: 租户ID，如果未找到则为None
        """
        # 1. 从请求头获取
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            return tenant_id
        
        # 2. 从查询参数获取
        tenant_id = request.GET.get('tenant_id')
        if tenant_id:
            return tenant_id
        
        # 3. 从子域名获取
        host = request.get_host().split(':')[0]  # 移除端口号
        domain_parts = host.split('.')
        if len(domain_parts) > 2:
            # 检查子域名是否对应租户
            subdomain = domain_parts[0]
            tenant = self._get_tenant_by_subdomain(subdomain)
            if tenant:
                return tenant.id
        
        # 4. 从JWT令牌获取
        # 注意：这需要自定义JWT认证类来支持
        if hasattr(request, 'auth') and hasattr(request.auth, 'get'):
            tenant_id = request.auth.get('tenant_id')
            if tenant_id:
                return tenant_id
        
        # 5. 从API密钥关联的租户获取
        if hasattr(request, 'api_key') and request.api_key and request.api_key.tenant:
            return request.api_key.tenant.id
        
        return None
    
    def _get_tenant_by_id(self, tenant_id):
        """
        根据ID获取租户
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            Tenant: 租户对象，如果未找到则为None
        """
        try:
            # 动态导入，避免循环导入
            from apps.tenant_service.models import Tenant
            return Tenant.objects.filter(id=tenant_id, is_active=True).first()
        except Exception as e:
            logger.error(f"Error fetching tenant: {e}")
            return None
    
    def _get_tenant_by_subdomain(self, subdomain):
        """
        根据子域名获取租户
        
        Args:
            subdomain: 子域名
            
        Returns:
            Tenant: 租户对象，如果未找到则为None
        """
        try:
            # 动态导入，避免循环导入
            from apps.tenant_service.models import Tenant
            return Tenant.objects.filter(subdomain=subdomain, is_active=True).first()
        except Exception as e:
            logger.error(f"Error fetching tenant by subdomain: {e}")
            return None
    
    def _is_tenant_required(self, request):
        """
        检查当前请求是否需要租户
        
        Args:
            request: HTTP请求对象
            
        Returns:
            bool: 是否需要租户
        """
        # 平台API需要租户
        if request.path.startswith('/api/platform/'):
            # 获取当前URL的解析结果
            url_name = resolve(request.path_info).url_name
            
            # 某些平台API不需要租户
            if url_name in ['login', 'register', 'token_refresh', 'token_verify', 'auth-verify-api-key']:
                return False
            
            return True
        
        return False 