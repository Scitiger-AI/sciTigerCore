"""
通知记录模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """
    通知记录模型
    
    记录系统发送的通知，包含发送状态和阅读状态
    """
    # 通知状态
    STATUS_CHOICES = (
        ('pending', _('待发送')),
        ('sending', _('发送中')),
        ('sent', _('已发送')),
        ('delivered', _('已送达')),
        ('failed', _('发送失败')),
        ('cancelled', _('已取消')),
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('所属租户')
    )
    user = models.ForeignKey(
        'auth_service.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('接收用户')
    )
    notification_type = models.ForeignKey(
        'notification_service.NotificationType',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('通知类型')
    )
    channel = models.ForeignKey(
        'notification_service.NotificationChannel',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('通知渠道')
    )
    template = models.ForeignKey(
        'notification_service.NotificationTemplate',
        on_delete=models.SET_NULL,
        null=True,
        related_name='notifications',
        verbose_name=_('使用模板')
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_('通知主题')
    )
    content = models.TextField(
        verbose_name=_('通知内容')
    )
    html_content = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('HTML内容')
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('通知数据'),
        help_text=_('用于存储通知相关的数据，如订单ID、用户操作等')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('发送状态')
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('是否已读')
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('阅读时间')
    )
    recipient_address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('接收地址'),
        help_text=_('如邮箱地址、手机号码等')
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('错误信息')
    )
    external_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('外部ID'),
        help_text=_('外部系统的消息ID，如邮件ID、短信ID等')
    )
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('计划发送时间')
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('实际发送时间')
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
        verbose_name = _('通知记录')
        verbose_name_plural = _('通知记录')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'user', 'is_read']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} ({self.user.username})"
    
    def mark_as_read(self):
        """
        将通知标记为已读
        """
        from django.utils import timezone
        
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])
    
    def mark_as_unread(self):
        """
        将通知标记为未读
        """
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at', 'updated_at']) 