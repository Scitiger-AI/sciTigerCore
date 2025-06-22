"""
通知渠道模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationChannel(models.Model):
    """
    通知渠道模型
    
    定义系统支持的通知发送渠道，如邮件、短信、系统内通知、推送通知等
    """
    CHANNEL_TYPE_CHOICES = (
        ('email', _('电子邮件')),
        ('sms', _('短信')),
        ('in_app', _('系统内通知')),
        ('push', _('推送通知')),
        ('webhook', _('Webhook')),
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('渠道代码'),
        help_text=_('系统内部使用的唯一标识符，如 email, sms, in_app')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('渠道名称')
    )
    channel_type = models.CharField(
        max_length=20,
        choices=CHANNEL_TYPE_CHOICES,
        verbose_name=_('渠道类型')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('渠道描述')
    )
    config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('渠道配置'),
        help_text=_('渠道特定的配置参数，如SMTP服务器设置、API密钥等')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('是否启用')
    )
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='notification_channels',
        null=True,
        blank=True,
        verbose_name=_('所属租户'),
        help_text=_('为空表示系统级渠道，所有租户共享')
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
        verbose_name = _('通知渠道')
        verbose_name_plural = _('通知渠道')
        ordering = ['name']
        unique_together = [['code', 'tenant']]
    
    def __str__(self):
        tenant_name = self.tenant.name if self.tenant else _('系统')
        return f"{self.name} ({tenant_name})" 