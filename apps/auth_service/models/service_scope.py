"""
服务范围模型定义

定义了系统中的服务、资源和操作类型，用于权限管理和API密钥作用域。
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Service(models.Model):
    """
    服务模型
    
    服务分为两种类型：
    1. 系统服务 (is_system=True)：系统预设的服务，适用于所有租户，不关联特定租户
    2. 租户级服务 (is_system=False)：特定租户的自定义服务，必须关联到特定租户
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('服务ID')
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('服务代码')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('服务名称')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('服务描述')
    )
    is_system = models.BooleanField(
        default=True,  # 默认为系统服务
        verbose_name=_('是否系统服务'),
        help_text=_('系统服务适用于所有租户，不关联特定租户')
    )
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='services',
        blank=True,
        null=True,
        verbose_name=_('所属租户'),
        help_text=_('租户级服务必须关联租户，系统服务不关联租户')
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
        verbose_name = _('服务')
        verbose_name_plural = _('服务')
        unique_together = ('code', 'tenant')
        ordering = ['-created_at', 'code']
        
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def clean(self):
        """
        验证服务类型和租户关联的一致性
        """
        # 确保租户级服务必须关联租户
        if not self.is_system and self.tenant is None:
            raise ValidationError({
                'tenant': _("租户级服务必须关联租户")
            })
            
        # 确保系统服务不关联租户
        if self.is_system and self.tenant is not None:
            raise ValidationError({
                'tenant': _("系统服务不应关联到特定租户")
            })
    
    def save(self, *args, **kwargs):
        """
        保存前验证服务类型
        """
        # 运行验证
        self.clean()
        super().save(*args, **kwargs)


class Resource(models.Model):
    """
    资源模型
    
    资源分为两种类型：
    1. 系统资源：关联到系统服务的资源
    2. 租户级资源：关联到租户级服务的资源
    
    资源的类型由其关联的服务类型决定。
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('资源ID')
    )
    code = models.CharField(
        max_length=100,
        verbose_name=_('资源代码')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('资源名称')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('资源描述')
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name=_('所属服务')
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
        verbose_name = _('资源')
        verbose_name_plural = _('资源')
        ordering = ['-created_at', 'service', 'code']
        unique_together = ('service', 'code')
        
    def __str__(self):
        return f"{self.name} ({self.service.code}:{self.code})"
    
    @property
    def is_system(self):
        """
        根据关联的服务确定资源是否为系统资源
        """
        return self.service.is_system
    
    @property
    def tenant(self):
        """
        获取资源关联的租户（如果是租户级资源）
        """
        return self.service.tenant
    
    def clean(self):
        """
        确保资源的租户属性与其服务一致
        """
        if self.service_id:  # 确保service已设置
            # 不需要额外验证，因为资源的租户属性完全由服务决定
            pass
    
    def save(self, *args, **kwargs):
        """
        保存前验证资源
        """
        self.clean()
        super().save(*args, **kwargs)


class Action(models.Model):
    """
    操作模型
    
    操作分为两种类型：
    1. 系统操作 (is_system=True)：系统预设的操作，适用于所有租户，不关联特定租户
    2. 租户级操作 (is_system=False)：特定租户的自定义操作，必须关联到特定租户
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('操作ID')
    )
    code = models.CharField(
        max_length=100,
        verbose_name=_('操作代码')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('操作名称')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('操作描述')
    )
    is_system = models.BooleanField(
        default=True,  # 默认为系统操作
        verbose_name=_('是否系统操作'),
        help_text=_('系统操作适用于所有租户，不关联特定租户')
    )
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='actions',
        blank=True,
        null=True,
        verbose_name=_('所属租户'),
        help_text=_('租户级操作必须关联租户，系统操作不关联租户')
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
        verbose_name = _('操作')
        verbose_name_plural = _('操作')
        ordering = ['-created_at', 'code']
        unique_together = (('code', 'tenant'), ('code', 'is_system'))  # 确保系统操作代码全局唯一，租户操作在租户内唯一
        
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def clean(self):
        """
        验证操作类型和租户关联的一致性
        """
        # 确保租户级操作必须关联租户
        if not self.is_system and self.tenant is None:
            raise ValidationError({
                'tenant': _("租户级操作必须关联租户")
            })
            
        # 确保系统操作不关联租户
        if self.is_system and self.tenant is not None:
            raise ValidationError({
                'tenant': _("系统操作不应关联到特定租户")
            })
    
    def save(self, *args, **kwargs):
        """
        保存前验证操作类型
        """
        # 运行验证
        self.clean()
        super().save(*args, **kwargs) 