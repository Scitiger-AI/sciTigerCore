"""
租户设置服务
"""

import logging
from apps.tenant_service.models import TenantSettings

logger = logging.getLogger('sciTigerCore')


class TenantSettingsService:
    """
    租户设置服务类
    
    提供租户设置的业务逻辑处理
    """
    
    @staticmethod
    def get_tenant_settings(tenant):
        """
        获取租户设置
        
        Args:
            tenant: 租户对象
            
        Returns:
            TenantSettings: 租户设置对象，如果不存在则创建
        """
        settings, created = TenantSettings.objects.get_or_create(tenant=tenant)
        
        if created:
            logger.info(f"Created default settings for tenant: {tenant.name} (ID: {tenant.id})")
            
        return settings
    
    @staticmethod
    def update_tenant_settings(tenant, **update_data):
        """
        更新租户设置
        
        Args:
            tenant: 租户对象
            update_data: 更新数据
            
        Returns:
            TenantSettings: 更新后的租户设置对象
        """
        settings = TenantSettingsService.get_tenant_settings(tenant)
        
        # 更新设置字段
        for key, value in update_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
            
        settings.save()
        logger.info(f"Updated settings for tenant: {tenant.name} (ID: {tenant.id})")
        
        return settings
    
    @staticmethod
    def get_tenant_theme(tenant):
        """
        获取租户主题设置
        
        Args:
            tenant: 租户对象
            
        Returns:
            dict: 包含主题相关设置的字典
        """
        settings = TenantSettingsService.get_tenant_settings(tenant)
        
        return {
            'theme': settings.theme,
            'logo_url': settings.logo_url,
            'favicon_url': settings.favicon_url,
            'custom_css': settings.custom_css,
            'custom_js': settings.custom_js,
            'custom_header': settings.custom_header,
            'custom_footer': settings.custom_footer
        }
    
    @staticmethod
    def get_tenant_localization(tenant):
        """
        获取租户本地化设置
        
        Args:
            tenant: 租户对象
            
        Returns:
            dict: 包含本地化相关设置的字典
        """
        settings = TenantSettingsService.get_tenant_settings(tenant)
        
        return {
            'language': settings.language,
            'timezone': settings.timezone,
            'date_format': settings.date_format,
            'time_format': settings.time_format,
            'currency': settings.currency
        }
    
    @staticmethod
    def get_tenant_signup_settings(tenant):
        """
        获取租户注册设置
        
        Args:
            tenant: 租户对象
            
        Returns:
            dict: 包含注册相关设置的字典
        """
        settings = TenantSettingsService.get_tenant_settings(tenant)
        
        return {
            'enable_signup': settings.enable_signup,
            'enable_social_login': settings.enable_social_login
        } 