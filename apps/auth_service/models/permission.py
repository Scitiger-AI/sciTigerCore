"""
权限模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Permission(models.Model):
    """
    权限模型
    
    权限分为两种类型：
    1. 系统全局权限 (is_system=True)：系统预设的权限，适用于所有租户，不关联特定租户
    2. 租户级权限 (is_tenant_level=True)：特定租户的自定义权限，必须关联到特定租户
    
    这两种类型互斥，一个权限不能同时是系统权限和租户级权限。
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('权限ID')
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('权限代码')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('权限名称')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('权限描述')
    )
    # 权限分类
    service = models.CharField(
        max_length=50,
        verbose_name=_('服务名称')
    )
    resource = models.CharField(
        max_length=50,
        verbose_name=_('资源类型')
    )
    action = models.CharField(
        max_length=50,
        verbose_name=_('操作类型')
    )
    # 权限属性
    is_system = models.BooleanField(
        default=True,  # 默认为系统权限
        verbose_name=_('是否系统权限'),
        help_text=_('系统权限适用于所有租户，不关联特定租户')
    )
    is_tenant_level = models.BooleanField(
        default=False,
        verbose_name=_('是否租户级权限'),
        help_text=_('租户级权限特定于某个租户，必须关联到特定租户')
    )

    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='permissions',
        blank=True,
        null=True,
        verbose_name=_('所属租户'),
        help_text=_('租户级权限必须关联租户，系统权限不关联租户')
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
        verbose_name = _('权限')
        verbose_name_plural = _('权限')
        ordering = ['service', 'resource', 'action']
        unique_together = ('service', 'resource', 'action')
        
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def clean(self):
        """
        验证权限类型和租户关联的一致性
        """
        # 确保is_system和is_tenant_level互斥
        if self.is_system and self.is_tenant_level:
            raise ValidationError({
                'is_system': _("系统权限和租户级权限不能同时为真"),
                'is_tenant_level': _("系统权限和租户级权限不能同时为真")
            })
            
        # 确保租户级权限必须关联租户
        if self.is_tenant_level and self.tenant is None:
            raise ValidationError({
                'tenant': _("租户级权限必须关联租户")
            })
            
        # 确保系统权限不关联租户
        if self.is_system and self.tenant is not None:
            raise ValidationError({
                'tenant': _("系统权限不应关联到特定租户")
            })
    
    def save(self, *args, **kwargs):
        """
        保存前自动生成权限代码和验证权限类型
        """
        # 运行验证
        self.clean()
        
        # 如果没有指定代码，则自动生成
        if not self.code:
            self.code = f"{self.service}:{self.resource}:{self.action}"
        
        super().save(*args, **kwargs) 