"""
租户用户关联模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class TenantUser(models.Model):
    """
    租户用户关联模型
    
    定义用户与租户的关系，包括用户在租户中的角色
    """
    
    # 用户角色选项
    ROLE_OWNER = 'owner'
    ROLE_ADMIN = 'admin'
    ROLE_MEMBER = 'member'
    
    ROLE_CHOICES = (
        (ROLE_OWNER, _('所有者')),
        (ROLE_ADMIN, _('管理员')),
        (ROLE_MEMBER, _('成员')),
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
        related_name='tenant_users',
        verbose_name=_('租户')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tenant_users',
        verbose_name=_('用户')
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER,
        verbose_name=_('角色')
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
        verbose_name = _('租户用户')
        verbose_name_plural = _('租户用户')
        unique_together = ('tenant', 'user')
        ordering = ['tenant', 'role', 'user']
        
    def __str__(self):
        return f"{self.tenant.name} - {self.user.username} ({self.get_role_display()})"
    
    @property
    def is_owner(self):
        """
        检查用户是否为租户所有者
        
        Returns:
            bool: 是否为所有者
        """
        return self.role == self.ROLE_OWNER
    
    @property
    def is_admin(self):
        """
        检查用户是否为租户管理员
        
        Returns:
            bool: 是否为管理员
        """
        return self.role in (self.ROLE_OWNER, self.ROLE_ADMIN) 