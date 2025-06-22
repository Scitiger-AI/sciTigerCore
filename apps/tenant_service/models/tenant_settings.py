"""
租户设置模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class TenantSettings(models.Model):
    """
    租户设置模型
    
    存储租户特定的设置和首选项
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
        related_name='settings',
        verbose_name=_('租户')
    )
    # 主题设置
    theme_primary_color = models.CharField(
        max_length=20,
        default='#1976D2',
        verbose_name=_('主题主色')
    )
    theme_secondary_color = models.CharField(
        max_length=20,
        default='#424242',
        verbose_name=_('主题辅色')
    )
    # 功能开关
    enable_notifications = models.BooleanField(
        default=True,
        verbose_name=_('启用通知')
    )
    enable_api_keys = models.BooleanField(
        default=True,
        verbose_name=_('启用API密钥')
    )
    enable_two_factor_auth = models.BooleanField(
        default=False,
        verbose_name=_('启用双因素认证')
    )
    # 安全设置
    password_expiry_days = models.IntegerField(
        default=90,
        verbose_name=_('密码过期天数')
    )
    max_login_attempts = models.IntegerField(
        default=5,
        verbose_name=_('最大登录尝试次数')
    )
    session_timeout_minutes = models.IntegerField(
        default=30,
        verbose_name=_('会话超时分钟数')
    )
    # 通知设置
    default_notification_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('默认通知邮箱')
    )
    # 其他设置
    timezone = models.CharField(
        max_length=50,
        default='Asia/Shanghai',
        verbose_name=_('时区')
    )
    date_format = models.CharField(
        max_length=20,
        default='YYYY-MM-DD',
        verbose_name=_('日期格式')
    )
    time_format = models.CharField(
        max_length=20,
        default='HH:mm:ss',
        verbose_name=_('时间格式')
    )
    # 元数据
    settings_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('扩展设置')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('创建时间')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('更新时间')
    )
    
    class Meta:
        verbose_name = _('租户设置')
        verbose_name_plural = _('租户设置')
        
    def __str__(self):
        return f"{self.tenant.name} 设置"
    
    def get_setting(self, key, default=None):
        """
        获取扩展设置值
        
        Args:
            key: 设置键
            default: 默认值
            
        Returns:
            设置值或默认值
        """
        return self.settings_json.get(key, default)
    
    def set_setting(self, key, value):
        """
        设置扩展设置值
        
        Args:
            key: 设置键
            value: 设置值
        """
        self.settings_json[key] = value
        self.save(update_fields=['settings_json', 'updated_at']) 