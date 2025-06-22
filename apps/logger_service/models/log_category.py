"""
日志分类模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class LogCategory(models.Model):
    """
    日志分类模型
    
    定义不同类型的日志分类
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('分类名称')
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('分类代码')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('描述')
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name=_('是否系统分类')
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
        verbose_name = _('日志分类')
        verbose_name_plural = _('日志分类')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_or_create_category(cls, code, name=None, description=None):
        """
        获取或创建日志分类
        
        Args:
            code: 分类代码
            name: 分类名称，如果不提供则使用代码作为名称
            description: 分类描述
            
        Returns:
            LogCategory: 日志分类对象
        """
        if not name:
            name = code
            
        category, created = cls.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'description': description,
                'is_system': True
            }
        )
        
        return category 