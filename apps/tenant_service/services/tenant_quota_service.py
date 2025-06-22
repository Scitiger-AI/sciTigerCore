"""
租户配额服务
"""

import logging
from django.utils import timezone
from apps.tenant_service.models import TenantQuota

logger = logging.getLogger('sciTigerCore')


class TenantQuotaService:
    """
    租户配额服务类
    
    提供租户配额的业务逻辑处理
    """
    
    @staticmethod
    def get_tenant_quota(tenant):
        """
        获取租户配额
        
        Args:
            tenant: 租户对象
            
        Returns:
            TenantQuota: 租户配额对象，如果不存在则创建
        """
        quota, created = TenantQuota.objects.get_or_create(tenant=tenant)
        
        if created:
            logger.info(f"Created default quota for tenant: {tenant.name} (ID: {tenant.id})")
            
        return quota
    
    @staticmethod
    def update_tenant_quota(tenant, **update_data):
        """
        更新租户配额
        
        Args:
            tenant: 租户对象
            update_data: 更新数据
            
        Returns:
            TenantQuota: 更新后的租户配额对象
        """
        quota = TenantQuotaService.get_tenant_quota(tenant)
        
        # 验证更新数据
        if 'max_users' in update_data and update_data['max_users'] < quota.current_user_count:
            raise ValueError(f"最大用户数不能小于当前用户数 ({quota.current_user_count})")
            
        if 'max_storage_gb' in update_data and update_data['max_storage_gb'] < quota.current_storage_used_gb:
            raise ValueError(f"最大存储空间不能小于当前使用空间 ({quota.current_storage_used_gb})")
            
        if 'max_api_keys' in update_data and update_data['max_api_keys'] < quota.current_api_key_count:
            raise ValueError(f"最大API密钥数不能小于当前API密钥数 ({quota.current_api_key_count})")
        
        # 更新配额字段
        for key, value in update_data.items():
            if hasattr(quota, key):
                setattr(quota, key, value)
            
        quota.save()
        logger.info(f"Updated quota for tenant: {tenant.name} (ID: {tenant.id})")
        
        return quota
    
    @staticmethod
    def check_user_quota(tenant):
        """
        检查用户配额是否已满
        
        Args:
            tenant: 租户对象
            
        Returns:
            bool: 是否有可用配额
        """
        quota = TenantQuotaService.get_tenant_quota(tenant)
        
        # 检查是否已达到最大用户数
        return quota.current_user_count < quota.max_users
    
    @staticmethod
    def check_storage_quota(tenant, required_space):
        """
        检查存储配额是否足够
        
        Args:
            tenant: 租户对象
            required_space: 所需空间大小（GB）
            
        Returns:
            bool: 是否有足够配额
        """
        quota = TenantQuotaService.get_tenant_quota(tenant)
        
        # 检查是否有足够的存储空间
        return (quota.current_storage_used_gb + required_space) <= quota.max_storage_gb
    
    @staticmethod
    def check_project_quota(tenant):
        """
        检查项目配额是否已满
        
        Args:
            tenant: 租户对象
            
        Returns:
            bool: 是否有可用配额
        """
        quota = TenantQuotaService.get_tenant_quota(tenant)
        
        # 检查是否已达到最大项目数
        return quota.current_projects < quota.max_projects
    
    @staticmethod
    def check_api_call_quota(tenant):
        """
        检查API调用配额是否已满
        
        Args:
            tenant: 租户对象
            
        Returns:
            bool: 是否有可用配额
        """
        quota = TenantQuotaService.get_tenant_quota(tenant)
        
        # 检查是否已达到每日API调用限制
        return quota.current_api_requests_count < quota.max_api_requests_per_day
    
    @staticmethod
    def increment_api_call_count(tenant):
        """
        增加API调用计数
        
        Args:
            tenant: 租户对象
            
        Returns:
            TenantQuota: 更新后的租户配额对象
        """
        quota = TenantQuotaService.get_tenant_quota(tenant)
        
        # 检查是否需要重置每日计数
        today = timezone.now().date()
        if quota.last_reset_date != today:
            quota.current_api_requests_count = 0
            quota.last_reset_date = today
            
        # 增加API调用计数
        quota.current_api_requests_count += 1
        
        quota.save()
        return quota
    
    @staticmethod
    def check_api_key_quota(tenant):
        """
        检查API密钥配额是否已满
        
        Args:
            tenant: 租户对象
            
        Returns:
            bool: 是否有可用配额
        """
        quota = TenantQuotaService.get_tenant_quota(tenant)
        
        # 检查是否已达到最大API密钥数
        return quota.current_api_key_count < quota.max_api_keys 