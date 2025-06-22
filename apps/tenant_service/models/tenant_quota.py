"""
租户配额模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class TenantQuota(models.Model):
    """
    租户资源配额管理模型
    
    定义租户可使用的资源限制
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    tenant = models.OneToOneField(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='quota',
        verbose_name=_('租户')
    )
    # 用户配额
    max_users = models.IntegerField(
        default=10,
        verbose_name=_('最大用户数')
    )
    # API配额
    max_api_keys = models.IntegerField(
        default=5,
        verbose_name=_('最大API密钥数')
    )
    max_api_requests_per_day = models.IntegerField(
        default=10000,
        verbose_name=_('每日最大API请求数')
    )
    # 存储配额
    max_storage_gb = models.IntegerField(
        default=5,
        verbose_name=_('最大存储空间(GB)')
    )
    # 日志配额
    max_log_retention_days = models.IntegerField(
        default=30,
        verbose_name=_('最大日志保留天数')
    )
    # 通知配额
    max_notifications_per_day = models.IntegerField(
        default=1000,
        verbose_name=_('每日最大通知数')
    )
    # 使用统计
    current_user_count = models.IntegerField(
        default=0,
        verbose_name=_('当前用户数')
    )
    current_api_key_count = models.IntegerField(
        default=0,
        verbose_name=_('当前API密钥数')
    )
    current_storage_used_gb = models.FloatField(
        default=0.0,
        verbose_name=_('当前已使用存储空间(GB)')
    )
    # 元数据
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('创建时间')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('更新时间')
    )
    
    class Meta:
        verbose_name = _('租户配额')
        verbose_name_plural = _('租户配额')
        
    def __str__(self):
        return f"{self.tenant.name} 配额"
    
    def check_user_quota(self):
        """
        检查用户配额是否已达上限
        
        Returns:
            bool: 是否可以添加更多用户
        """
        return self.current_user_count < self.max_users
    
    def check_api_key_quota(self):
        """
        检查API密钥配额是否已达上限
        
        Returns:
            bool: 是否可以创建更多API密钥
        """
        return self.current_api_key_count < self.max_api_keys
    
    def update_user_count(self):
        """
        更新当前用户数
        """
        self.current_user_count = self.tenant.tenant_users.filter(is_active=True).count()
        self.save(update_fields=['current_user_count', 'updated_at'])
    
    def update_api_key_count(self):
        """
        更新当前API密钥数
        """
        # 注意：这里假设API密钥模型已经存在
        # 实际实现时需要确保此逻辑正确
        from apps.auth_service.models import ApiKey
        self.current_api_key_count = ApiKey.objects.filter(
            tenant_id=self.tenant.id,
            is_active=True
        ).count()
        self.save(update_fields=['current_api_key_count', 'updated_at']) 