"""
租户模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Tenant(models.Model):
    """
    租户模型
    
    代表系统中的一个独立租户，拥有自己的用户、数据和设置
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('租户ID')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('租户名称')
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_('租户标识符')
    )
    subdomain = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('子域名')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('租户描述')
    )
    logo = models.ImageField(
        upload_to='tenant_logos',
        blank=True,
        null=True,
        verbose_name=_('租户Logo')
    )
    contact_email = models.EmailField(
        verbose_name=_('联系邮箱')
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('联系电话')
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('地址')
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
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('过期时间')
    )
    
    class Meta:
        verbose_name = _('租户')
        verbose_name_plural = _('租户')
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name
    
    @property
    def is_expired(self):
        """
        检查租户是否已过期
        
        Returns:
            bool: 是否已过期
        """
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at 