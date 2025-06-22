"""
API密钥服务
"""

import logging
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from apps.auth_service.models import ApiKey, ApiKeyScope, ApiKeyUsageLog
from django.db.models import Count, Q

logger = logging.getLogger('sciTigerCore')


class ApiKeyService:
    """
    API密钥服务类
    
    提供API密钥相关的业务逻辑处理
    """
    
    @staticmethod
    def get_api_keys(tenant_id=None, user_id=None, key_type=None, is_active=None, **filters):
        """
        获取API密钥列表
        
        Args:
            tenant_id: 租户ID，None表示所有租户
            user_id: 用户ID，None表示所有用户
            key_type: 密钥类型，None表示所有类型
            is_active: 是否激活，None表示所有状态
            filters: 其他过滤条件
            
        Returns:
            QuerySet: API密钥查询集
        """
        queryset = ApiKey.objects.all()
        
        # 租户ID过滤
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
            
        # 用户ID过滤
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # 密钥类型过滤
        if key_type:
            queryset = queryset.filter(key_type=key_type)
            
        # 激活状态过滤
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_api_key_by_id(api_key_id):
        """
        根据ID获取API密钥
        
        Args:
            api_key_id: API密钥ID
            
        Returns:
            ApiKey: API密钥对象，如果不存在则返回None
        """
        try:
            return ApiKey.objects.get(id=api_key_id)
        except ApiKey.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def create_system_api_key(name, tenant_id=None, tenant=None, application_name=None, expires_in_days=None, scopes=None, **key_data):
        """
        创建系统级API密钥
        
        Args:
            name: 密钥名称
            tenant_id: 租户ID (如果没有提供tenant对象，则使用此ID)
            tenant: 租户对象 (优先使用此对象)
            application_name: 应用名称
            expires_in_days: 过期天数，None表示永不过期
            scopes: 作用域列表，格式为[{'service': 'xxx', 'resource': 'xxx', 'action': 'xxx'}, ...]
            key_data: 其他密钥数据
            
        Returns:
            tuple: (api_key, key, error_message)
                api_key: 创建的API密钥对象，创建失败时为None
                key: 明文密钥，创建失败时为None
                error_message: 错误信息，创建成功时为None
        """
        try:
            # 设置过期时间
            expires_at = None
            if expires_in_days:
                expires_at = timezone.now() + timedelta(days=expires_in_days)
            
            # 获取租户对象
            tenant_obj = tenant
            if not tenant_obj and tenant_id:
                from apps.tenant_service.models import Tenant
                try:
                    tenant_obj = Tenant.objects.get(id=tenant_id)
                except Tenant.DoesNotExist:
                    return None, None, f"租户不存在: {tenant_id}"
            
            # 检查是否提供了租户
            if not tenant_obj:
                return None, None, "系统级API密钥必须关联租户"
            
            logger.warning(f"创建系统级API密钥: {name}, 租户ID: {tenant_obj.id if tenant_obj else None}, 应用名称: {application_name}, 过期时间: {expires_at}")
            
            # 创建API密钥
            api_key, key = ApiKey.create_key(
                name=name,
                key_type=ApiKey.TYPE_SYSTEM,
                tenant=tenant_obj,
                application_name=application_name,
                expires_at=expires_at,
                **key_data
            )
            
            # 创建作用域
            if scopes:
                for scope in scopes:
                    ApiKeyScope.objects.create(
                        api_key=api_key,
                        service=scope['service'],
                        resource=scope['resource'],
                        action=scope['action']
                    )
            
            logger.info(f"Created system API key: {api_key.name} (ID: {api_key.id})")
            
            return api_key, key, None
        except ValueError as e:
            logger.error(f"Error creating system API key: {str(e)}")
            return None, None, str(e)
        except Exception as e:
            logger.error(f"Error creating system API key: {str(e)}")
            return None, None, f"创建系统级API密钥失败: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def create_user_api_key(name, user_id=None, user=None, tenant_id=None, tenant=None, expires_in_days=None, scopes=None, created_by_key_id=None, created_by_key=None, **key_data):
        """
        创建用户级API密钥
        
        Args:
            name: 密钥名称
            user_id: 用户ID (如果没有提供user对象，则使用此ID)
            user: 用户对象 (优先使用此对象)
            tenant_id: 租户ID (如果没有提供tenant对象，则使用此ID)
            tenant: 租户对象 (优先使用此对象)
            expires_in_days: 过期天数，None表示永不过期
            scopes: 作用域列表，格式为[{'service': 'xxx', 'resource': 'xxx', 'action': 'xxx'}, ...]
            created_by_key_id: 创建此密钥的系统级密钥ID (如果没有提供created_by_key对象，则使用此ID)
            created_by_key: 创建此密钥的系统级密钥对象 (优先使用此对象)
            key_data: 其他密钥数据
            
        Returns:
            tuple: (api_key, key, error_message)
                api_key: 创建的API密钥对象，创建失败时为None
                key: 明文密钥，创建失败时为None
                error_message: 错误信息，创建成功时为None
        """
        try:
            # 设置过期时间
            expires_at = None
            if expires_in_days:
                expires_at = timezone.now() + timedelta(days=expires_in_days)
            
            # 获取用户对象
            user_obj = user
            if not user_obj and user_id:
                from apps.auth_service.models import User
                try:
                    user_obj = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return None, None, f"用户不存在: {user_id}"
            
            # 检查是否提供了用户
            if not user_obj:
                return None, None, "用户级API密钥必须关联用户"
            
            # 获取租户对象
            tenant_obj = tenant
            if not tenant_obj and tenant_id:
                from apps.tenant_service.models import Tenant
                try:
                    tenant_obj = Tenant.objects.get(id=tenant_id)
                except Tenant.DoesNotExist:
                    return None, None, f"租户不存在: {tenant_id}"
            
            # 获取创建此密钥的系统级密钥
            created_by_key_obj = created_by_key
            if not created_by_key_obj and created_by_key_id:
                try:
                    created_by_key_obj = ApiKey.objects.get(id=created_by_key_id, key_type=ApiKey.TYPE_SYSTEM)
                except ApiKey.DoesNotExist:
                    return None, None, "创建此密钥的系统级密钥不存在"
            
            # 创建API密钥
            api_key, key = ApiKey.create_key(
                name=name,
                key_type=ApiKey.TYPE_USER,
                user=user_obj,
                tenant=tenant_obj,
                created_by_key=created_by_key_obj,
                expires_at=expires_at,
                **key_data
            )
            
            # 创建作用域
            if scopes:
                for scope in scopes:
                    ApiKeyScope.objects.create(
                        api_key=api_key,
                        service=scope['service'],
                        resource=scope['resource'],
                        action=scope['action']
                    )
            
            logger.info(f"Created user API key: {api_key.name} (ID: {api_key.id})")
            
            return api_key, key, None
        except ValueError as e:
            logger.error(f"Error creating user API key: {str(e)}")
            return None, None, str(e)
        except Exception as e:
            logger.error(f"Error creating user API key: {str(e)}")
            return None, None, f"创建用户级API密钥失败: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def update_api_key(api_key_id, **update_data):
        """
        更新API密钥
        
        Args:
            api_key_id: API密钥ID
            update_data: 更新数据
            
        Returns:
            tuple: (api_key, error_message)
                api_key: 更新后的API密钥对象，更新失败时为None
                error_message: 错误信息，更新成功时为None
        """
        try:
            api_key = ApiKey.objects.get(id=api_key_id)
            
            # 不允许修改密钥类型
            update_data.pop('key_type', None)
            
            # 不允许修改密钥哈希和前缀
            update_data.pop('key_hash', None)
            update_data.pop('prefix', None)
            
            # 处理作用域更新
            scopes = update_data.pop('scopes', None)
            if scopes is not None:
                # 删除现有作用域
                api_key.scopes.all().delete()
                
                # 创建新作用域
                for scope in scopes:
                    ApiKeyScope.objects.create(
                        api_key=api_key,
                        service=scope['service'],
                        resource=scope['resource'],
                        action=scope['action']
                    )
            
            # 更新其他字段
            for key, value in update_data.items():
                setattr(api_key, key, value)
            
            api_key.save()
            logger.info(f"Updated API key: {api_key.name} (ID: {api_key.id})")
            
            return api_key, None
        except ApiKey.DoesNotExist:
            logger.warning(f"Attempted to update non-existent API key: {api_key_id}")
            return None, "API密钥不存在"
        except Exception as e:
            logger.error(f"Error updating API key: {str(e)}")
            return None, f"更新API密钥失败: {str(e)}"
    
    @staticmethod
    def change_api_key_status(api_key_id, is_active):
        """
        修改API密钥状态
        
        Args:
            api_key_id: API密钥ID
            is_active: 是否激活
            
        Returns:
            tuple: (api_key, error_message)
                api_key: 更新后的API密钥对象，更新失败时为None
                error_message: 错误信息，更新成功时为None
        """
        try:
            api_key = ApiKey.objects.get(id=api_key_id)
            api_key.is_active = is_active
            api_key.save(update_fields=['is_active'])
            
            status_text = "激活" if is_active else "禁用"
            logger.info(f"{status_text} API密钥: {api_key.name} (ID: {api_key.id})")
            
            return api_key, None
        except ApiKey.DoesNotExist:
            return None, "API密钥不存在"
        except Exception as e:
            return None, f"修改API密钥状态失败: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def delete_api_key(api_key_id):
        """
        删除API密钥
        
        Args:
            api_key_id: API密钥ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            api_key = ApiKey.objects.get(id=api_key_id)
            api_key_name = api_key.name
            
            # 删除API密钥
            api_key.delete()
            logger.info(f"Deleted API key: {api_key_name} (ID: {api_key_id})")
            
            return True
        except ApiKey.DoesNotExist:
            logger.warning(f"Attempted to delete non-existent API key: {api_key_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting API key: {str(e)}")
            return False
    
    @staticmethod
    def verify_api_key(key_value, service=None, resource=None, action=None):
        """
        验证API密钥
        
        Args:
            key_value: API密钥值
            service: 服务名称
            resource: 资源类型
            action: 操作类型
            
        Returns:
            tuple: (api_key, error_message)
                api_key: 验证成功的API密钥对象，验证失败时为None
                error_message: 错误信息，验证成功时为None
        """
        # 验证密钥
        api_key = ApiKey.verify_key(key_value)
        
        if not api_key:
            return None, "无效的API密钥"
        
        # 检查是否过期
        if api_key.is_expired:
            return None, "API密钥已过期"
        logger.info(f"API密钥验证服务资源：service:{service}, resource:{resource}, action:{action}")
        logger.info(f"API密钥验scopes api_key.scopes:{api_key.scopes.all()}")
        # 如果指定了服务、资源和操作，则检查权限
        if service and resource and action:
            # 检查是否有对应的作用域
            has_scope = api_key.scopes.filter(
                service=service,
                resource=resource,
                action=action
            ).exists()
            
            if not has_scope:
                return None, "API密钥没有所需的权限"
        
        return api_key, None
    
    @staticmethod
    def log_api_key_usage(api_key, request_path, request_method, response_status, client_ip=None, request_id=None):
        """
        记录API密钥使用日志
        
        Args:
            api_key: API密钥对象
            request_path: 请求路径
            request_method: 请求方法
            response_status: 响应状态码
            client_ip: 客户端IP
            request_id: 请求ID
            
        Returns:
            ApiKeyUsageLog: 创建的日志对象
        """
        try:
            logger.info(f"log_api_key_usage: {api_key}, {api_key.tenant}, {request_path}, {request_method}, {response_status}, {client_ip}, {request_id}")
            log = ApiKeyUsageLog.objects.create(
                api_key=api_key,
                tenant=api_key.tenant,
                request_path=request_path,
                request_method=request_method,
                response_status=response_status,
                client_ip=client_ip,
                request_id=request_id
            )
            return log
        except Exception as e:
            logger.error(f"Error logging API key usage: {str(e)}")
            return None
    
    @staticmethod
    def get_api_key_usage_logs(api_key_id=None, tenant_id=None, start_time=None, end_time=None, **filters):
        """
        获取API密钥使用日志
        
        Args:
            api_key_id: API密钥ID
            tenant_id: 租户ID
            start_time: 开始时间
            end_time: 结束时间
            filters: 其他过滤条件
            
        Returns:
            QuerySet: 日志查询集
        """
        queryset = ApiKeyUsageLog.objects.all()
        
        # API密钥ID过滤
        if api_key_id:
            queryset = queryset.filter(api_key_id=api_key_id)
            
        # 租户ID过滤
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
            
        # 时间范围过滤
        if start_time:
            queryset = queryset.filter(timestamp__gte=start_time)
        if end_time:
            queryset = queryset.filter(timestamp__lte=end_time)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_api_key_stats(tenant_id=None):
        """
        获取API密钥统计信息
        
        Args:
            tenant_id: 租户ID，None表示所有租户
            
        Returns:
            dict: 统计信息
        """
        # 基础查询集
        queryset = ApiKey.objects.all()
        
        # 租户ID过滤
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        # 统计信息
        total_keys = queryset.count()
        system_keys = queryset.filter(key_type=ApiKey.TYPE_SYSTEM).count()
        user_keys = queryset.filter(key_type=ApiKey.TYPE_USER).count()
        active_keys = queryset.filter(is_active=True).count()
        inactive_keys = queryset.filter(is_active=False).count()
        expired_keys = queryset.filter(expires_at__lt=timezone.now()).count()
        
        # 最近7天创建的密钥数量
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        recent_keys = queryset.filter(created_at__gte=seven_days_ago).count()
        
        # 最近7天的使用日志数量
        usage_logs_query = ApiKeyUsageLog.objects.all()
        if tenant_id:
            usage_logs_query = usage_logs_query.filter(tenant_id=tenant_id)
        recent_usage = usage_logs_query.filter(timestamp__gte=seven_days_ago).count()
        
        # 按状态码分组的使用日志数量
        status_counts = usage_logs_query.values('response_status').annotate(
            count=Count('id')
        ).order_by('response_status')
        
        status_stats = {
            str(item['response_status']): item['count'] 
            for item in status_counts
        }
        
        return {
            'total_keys': total_keys,
            'system_keys': system_keys,
            'user_keys': user_keys,
            'active_keys': active_keys,
            'inactive_keys': inactive_keys,
            'expired_keys': expired_keys,
            'recent_keys': recent_keys,
            'recent_usage': recent_usage,
            'status_stats': status_stats
        } 