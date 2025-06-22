"""
租户服务
"""

import logging
from django.db import transaction
from apps.tenant_service.models import Tenant, TenantUser

logger = logging.getLogger('sciTigerCore')


class TenantService:
    """
    租户服务类
    
    提供租户相关的业务逻辑处理
    """
    
    @staticmethod
    def get_tenants(tenant_id=None, is_active=None, **filters):
        """
        获取租户列表
        
        Args:
            tenant_id: 租户ID，None表示所有租户
            is_active: 是否激活，None表示所有状态
            filters: 其他过滤条件
            
        Returns:
            QuerySet: 租户查询集
        """
        queryset = Tenant.objects.all()
        
        # 租户ID过滤
        if tenant_id:
            queryset = queryset.filter(id=tenant_id)
            
        # 激活状态过滤
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_tenant_by_id(tenant_id):
        """
        根据ID获取租户
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            Tenant: 租户对象，如果不存在则返回None
        """
        try:
            return Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return None
    
    @staticmethod
    def get_tenant_by_slug(slug):
        """
        根据标识符获取租户
        
        Args:
            slug: 租户标识符
            
        Returns:
            Tenant: 租户对象，如果不存在则返回None
        """
        try:
            return Tenant.objects.get(slug=slug)
        except Tenant.DoesNotExist:
            return None
    
    @staticmethod
    def get_tenant_by_subdomain(subdomain):
        """
        根据子域名获取租户
        
        Args:
            subdomain: 子域名
            
        Returns:
            Tenant: 租户对象，如果不存在则返回None
        """
        try:
            return Tenant.objects.get(subdomain=subdomain)
        except Tenant.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def create_tenant(name, slug, subdomain, owner_user, **tenant_data):
        """
        创建租户
        
        Args:
            name: 租户名称
            slug: 租户标识符
            subdomain: 子域名
            owner_user: 所有者用户对象
            tenant_data: 其他租户数据
            
        Returns:
            Tenant: 创建的租户对象
        """
        # 创建租户
        tenant = Tenant.objects.create(
            name=name,
            slug=slug,
            subdomain=subdomain,
            **tenant_data
        )
        
        # 创建租户所有者关联
        TenantUser.objects.create(
            tenant=tenant,
            user=owner_user,
            role=TenantUser.ROLE_OWNER
        )
        
        logger.info(f"Created tenant: {tenant.name} (ID: {tenant.id}) with owner: {owner_user.username}")
        
        return tenant
    
    @staticmethod
    def update_tenant(tenant_id, **update_data):
        """
        更新租户
        
        Args:
            tenant_id: 租户ID
            update_data: 更新数据
            
        Returns:
            Tenant: 更新后的租户对象，如果不存在则返回None
        """
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            
            # 更新租户字段
            for key, value in update_data.items():
                setattr(tenant, key, value)
                
            tenant.save()
            logger.info(f"Updated tenant: {tenant.name} (ID: {tenant.id})")
            
            return tenant
        except Tenant.DoesNotExist:
            logger.warning(f"Attempted to update non-existent tenant: {tenant_id}")
            return None
    
    @staticmethod
    @transaction.atomic
    def delete_tenant(tenant_id):
        """
        删除租户
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            tenant_name = tenant.name
            
            # 先删除MongoDB中与该租户相关的日志
            try:
                from apps.logger_service.services import LoggerService
                logs_deleted = LoggerService.delete_logs(tenant_id=str(tenant_id))
                logger.info(f"Deleted {logs_deleted} logs for tenant: {tenant_name} (ID: {tenant_id})")
            except Exception as e:
                logger.warning(f"Failed to delete logs for tenant {tenant_name} (ID: {tenant_id}): {str(e)}")
            
            # 删除租户
            tenant.delete()
            logger.info(f"Deleted tenant: {tenant_name} (ID: {tenant_id})")
            
            return True
        except Tenant.DoesNotExist:
            logger.warning(f"Attempted to delete non-existent tenant: {tenant_id}")
            return False
    
    @staticmethod
    def get_user_tenants(user):
        """
        获取用户所属的租户列表
        
        Args:
            user: 用户对象
            
        Returns:
            QuerySet: 租户查询集
        """
        # 获取用户关联的所有租户
        tenant_users = TenantUser.objects.filter(
            user=user,
            is_active=True
        )
        
        # 获取这些租户的ID列表
        tenant_ids = tenant_users.values_list('tenant_id', flat=True)
        
        # 返回这些租户
        return Tenant.objects.filter(
            id__in=tenant_ids,
            is_active=True
        )
    
    @staticmethod
    def is_user_tenant_admin(user, tenant):
        """
        检查用户是否为租户管理员
        
        Args:
            user: 用户对象
            tenant: 租户对象
            
        Returns:
            bool: 是否为租户管理员
        """
        try:
            tenant_user = TenantUser.objects.get(
                tenant=tenant,
                user=user,
                is_active=True
            )
            return tenant_user.is_admin
        except TenantUser.DoesNotExist:
            return False
    
    @staticmethod
    def is_user_tenant_owner(user, tenant):
        """
        检查用户是否为租户所有者
        
        Args:
            user: 用户对象
            tenant: 租户对象
            
        Returns:
            bool: 是否为租户所有者
        """
        try:
            tenant_user = TenantUser.objects.get(
                tenant=tenant,
                user=user,
                is_active=True
            )
            return tenant_user.is_owner
        except TenantUser.DoesNotExist:
            return False 