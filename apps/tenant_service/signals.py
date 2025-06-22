"""
租户服务信号处理器
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Tenant, TenantUser, TenantSettings, TenantQuota

logger = logging.getLogger('sciTigerCore')


@receiver(post_save, sender=Tenant)
def create_tenant_related_models(sender, instance, created, **kwargs):
    """
    创建租户时自动创建相关模型
    
    Args:
        sender: 发送信号的模型类
        instance: 租户实例
        created: 是否为新创建的实例
    """
    if created:
        # 创建租户设置
        TenantSettings.objects.create(tenant=instance)
        
        # 创建租户配额
        TenantQuota.objects.create(tenant=instance)
        
        logger.info(f"Created settings and quota for tenant: {instance.name} (ID: {instance.id})")


@receiver(post_save, sender=TenantUser)
def update_tenant_user_count(sender, instance, **kwargs):
    """
    更新租户用户数量
    
    Args:
        sender: 发送信号的模型类
        instance: 租户用户实例
    """
    # 更新租户配额中的用户数量
    if hasattr(instance.tenant, 'quota'):
        instance.tenant.quota.update_user_count()
        logger.debug(f"Updated user count for tenant: {instance.tenant.name}")


@receiver(post_delete, sender=TenantUser)
def update_tenant_user_count_on_delete(sender, instance, **kwargs):
    """
    删除租户用户时更新用户数量
    
    Args:
        sender: 发送信号的模型类
        instance: 租户用户实例
    """
    # 更新租户配额中的用户数量
    try:
        if hasattr(instance.tenant, 'quota'):
            instance.tenant.quota.update_user_count()
            logger.debug(f"Updated user count after deletion for tenant: {instance.tenant.name}")
    except Exception as e:
        logger.error(f"Error updating user count after deletion: {e}") 