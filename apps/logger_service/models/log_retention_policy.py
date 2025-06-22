"""
日志保留策略模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class LogRetentionPolicy(models.Model):
    """
    日志保留策略模型
    
    定义不同类型日志的保留期限
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='log_retention_policies',
        blank=True,
        null=True,
        verbose_name=_('所属租户')
    )
    category = models.ForeignKey(
        'logger_service.LogCategory',
        on_delete=models.CASCADE,
        related_name='retention_policies',
        verbose_name=_('日志分类')
    )
    retention_days = models.IntegerField(
        default=30,
        verbose_name=_('保留天数')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('是否激活')
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
        verbose_name = _('日志保留策略')
        verbose_name_plural = _('日志保留策略')
        unique_together = ('tenant', 'category')
        ordering = ['category__name']
    
    def __str__(self):
        tenant_name = self.tenant.name if self.tenant else '全局'
        return f"{tenant_name} - {self.category.name} ({self.retention_days}天)" 