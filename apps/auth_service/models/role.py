"""
角色模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Role(models.Model):
    """
    角色模型
    
    定义系统中的角色，可关联多个权限
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('角色ID')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('角色名称')
    )
    code = models.CharField(
        max_length=100,
        verbose_name=_('角色代码')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('角色描述')
    )
    # 角色属性
    is_system = models.BooleanField(
        default=False,
        verbose_name=_('是否系统角色')
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('是否默认角色')
    )
    # 角色关联
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='roles',
        blank=True,
        null=True,
        verbose_name=_('所属租户')
    )
    permissions = models.ManyToManyField(
        'Permission',
        related_name='roles',
        blank=True,
        verbose_name=_('权限')
    )
    # 用户关联 - 这里不需要显式定义，因为在User模型中已经定义了反向关系
    # 但为了代码清晰，我们也在这里定义
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='role_users',  # 修改为不同的related_name避免冲突
        verbose_name=_('用户')
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
        verbose_name = _('角色')
        verbose_name_plural = _('角色')
        ordering = ['-created_at']
        unique_together = ('code', 'tenant')
        
    def __str__(self):
        if self.tenant:
            return f"{self.name} ({self.tenant.name})"
        return f"{self.name} (系统)"
    
    @property
    def is_global(self):
        """
        检查是否为全局角色
        
        Returns:
            bool: 是否为全局角色
        """
        return self.tenant is None 