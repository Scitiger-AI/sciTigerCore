"""
登录尝试记录模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class LoginAttempt(models.Model):
    """
    登录尝试记录模型
    
    用于记录用户登录尝试，防止暴力破解
    """
    # 登录状态选项
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_BLOCKED = 'blocked'
    
    STATUS_CHOICES = (
        (STATUS_SUCCESS, _('成功')),
        (STATUS_FAILED, _('失败')),
        (STATUS_BLOCKED, _('已阻止')),
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_attempts',
        blank=True,
        null=True,
        verbose_name=_('用户')
    )
    email = models.EmailField(
        verbose_name=_('邮箱地址')
    )
    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP地址')
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('用户代理')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name=_('状态')
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('原因')
    )
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='login_attempts',
        blank=True,
        null=True,
        verbose_name=_('所属租户')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('时间戳')
    )
    is_admin_login = models.BooleanField(
        default=False,
        verbose_name=_('是否管理员登录')
    )
    failure_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('失败原因')
    )
    
    class Meta:
        verbose_name = _('登录尝试')
        verbose_name_plural = _('登录尝试')
        ordering = ['-timestamp']
        
    def __str__(self):
        login_type = "管理员" if self.is_admin_login else "普通用户"
        return f"{self.email} ({login_type}) - {self.get_status_display()} ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
    
    @classmethod
    def record_attempt(cls, email, ip_address, status, user=None, tenant=None, user_agent=None, reason=None, is_admin_login=False):
        """
        记录登录尝试
        
        Args:
            email: 邮箱地址
            ip_address: IP地址
            status: 状态
            user: 用户对象
            tenant: 租户对象
            user_agent: 用户代理
            reason: 原因
            is_admin_login: 是否管理员登录
            
        Returns:
            LoginAttempt: 创建的登录尝试记录
        """
        return cls.objects.create(
            user=user,
            email=email,
            ip_address=ip_address,
            status=status,
            tenant=tenant,
            user_agent=user_agent,
            reason=reason,
            is_admin_login=is_admin_login
        )
    
    @classmethod
    def check_login_attempts(cls, email, ip_address, max_attempts=5, window_minutes=30, is_admin_login=False):
        """
        检查登录尝试次数
        
        Args:
            email: 邮箱地址
            ip_address: IP地址
            max_attempts: 最大尝试次数
            window_minutes: 时间窗口（分钟）
            is_admin_login: 是否管理员登录
            
        Returns:
            bool: 是否允许登录
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # 计算时间窗口
        window_start = timezone.now() - timedelta(minutes=window_minutes)
        
        # 查询失败的登录尝试次数
        attempts_count = cls.objects.filter(
            email=email,
            ip_address=ip_address,
            status=cls.STATUS_FAILED,
            timestamp__gte=window_start,
            is_admin_login=is_admin_login
        ).count()
        
        return attempts_count < max_attempts 