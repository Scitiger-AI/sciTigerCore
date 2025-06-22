"""
通知类型模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationType(models.Model):
    """
    通知类型模型
    
    定义系统中的通知类型，用于分类不同种类的通知
    """
    # 通知类型分类
    CATEGORY_CHOICES = (
        ('system', _('系统通知')),
        ('account', _('账户通知')),
        ('business', _('业务通知')),
        ('transaction', _('交易通知')),
        ('collaboration', _('协作通知')),
        ('integration', _('集成通知')),
    )
    
    # 通知优先级
    PRIORITY_CHOICES = (
        ('urgent', _('紧急')),
        ('high', _('高')),
        ('medium', _('中')),
        ('low', _('低')),
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('通知类型代码'),
        help_text=_('系统内部使用的唯一标识符，如 system.maintenance, account.password_reset')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('通知类型名称')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('通知类型描述')
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name=_('通知分类')
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('通知优先级')
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
        verbose_name = _('通知类型')
        verbose_name_plural = _('通知类型')
        ordering = ['category', 'priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})" 