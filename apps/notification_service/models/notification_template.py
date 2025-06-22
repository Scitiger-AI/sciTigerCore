"""
通知模板模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationTemplate(models.Model):
    """
    通知模板模型
    
    定义通知的内容模板，支持不同类型和渠道的通知
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    code = models.CharField(
        max_length=100,
        verbose_name=_('模板代码'),
        help_text=_('系统内部使用的唯一标识符')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('模板名称')
    )
    notification_type = models.ForeignKey(
        'notification_service.NotificationType',
        on_delete=models.CASCADE,
        related_name='templates',
        verbose_name=_('通知类型')
    )
    channel = models.ForeignKey(
        'notification_service.NotificationChannel',
        on_delete=models.CASCADE,
        related_name='templates',
        verbose_name=_('通知渠道')
    )
    subject_template = models.CharField(
        max_length=255,
        verbose_name=_('主题模板'),
        help_text=_('支持变量插值，如 "您的订单 {{order_id}} 已确认"')
    )
    content_template = models.TextField(
        verbose_name=_('内容模板'),
        help_text=_('支持变量插值和基本格式化')
    )
    html_template = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('HTML模板'),
        help_text=_('用于支持HTML的渠道，如电子邮件')
    )
    language = models.CharField(
        max_length=10,
        default='zh-cn',
        verbose_name=_('语言')
    )
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='notification_templates',
        null=True,
        blank=True,
        verbose_name=_('所属租户'),
        help_text=_('为空表示系统级模板，所有租户共享')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('是否启用')
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
        verbose_name = _('通知模板')
        verbose_name_plural = _('通知模板')
        ordering = ['notification_type', 'channel', 'language']
        unique_together = [['code', 'channel', 'language', 'tenant']]
    
    def __str__(self):
        return f"{self.name} ({self.notification_type.name} - {self.channel.name})" 