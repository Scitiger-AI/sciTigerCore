"""
用户验证模型定义
"""

import uuid
import secrets
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings


class UserVerification(models.Model):
    """
    用户验证模型
    
    用于邮箱验证、手机验证、密码重置等场景
    """
    # 验证类型选项
    TYPE_EMAIL_VERIFICATION = 'email_verification'
    TYPE_PHONE_VERIFICATION = 'phone_verification'
    TYPE_PASSWORD_RESET = 'password_reset'
    TYPE_TWO_FACTOR = 'two_factor'
    
    TYPE_CHOICES = (
        (TYPE_EMAIL_VERIFICATION, _('邮箱验证')),
        (TYPE_PHONE_VERIFICATION, _('手机验证')),
        (TYPE_PASSWORD_RESET, _('密码重置')),
        (TYPE_TWO_FACTOR, _('双因素认证')),
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
        related_name='verifications',
        verbose_name=_('用户')
    )
    verification_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        verbose_name=_('验证类型')
    )
    token = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('验证令牌')
    )
    code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_('验证码')
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name=_('是否已使用')
    )
    expires_at = models.DateTimeField(
        verbose_name=_('过期时间')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('创建时间')
    )
    used_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('使用时间')
    )
    
    class Meta:
        verbose_name = _('用户验证')
        verbose_name_plural = _('用户验证')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.get_verification_type_display()}"
    
    def save(self, *args, **kwargs):
        """
        保存前生成令牌和验证码
        """
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        
        if not self.code and self.verification_type in [self.TYPE_PHONE_VERIFICATION, self.TYPE_TWO_FACTOR]:
            import random
            self.code = ''.join(random.choices('0123456789', k=6))
        
        if not self.expires_at:
            # 设置过期时间，默认24小时
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """
        检查验证是否已过期
        
        Returns:
            bool: 是否已过期
        """
        return timezone.now() > self.expires_at
    
    def use(self):
        """
        标记验证为已使用
        """
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])
    
    @classmethod
    def create_verification(cls, user, verification_type, expiry_hours=24):
        """
        创建新的验证记录
        
        Args:
            user: 用户对象
            verification_type: 验证类型
            expiry_hours: 过期小时数
            
        Returns:
            UserVerification: 创建的验证对象
        """
        # 使旧的同类型验证失效
        cls.objects.filter(
            user=user,
            verification_type=verification_type,
            is_used=False
        ).update(is_used=True)
        
        # 创建新验证
        return cls.objects.create(
            user=user,
            verification_type=verification_type,
            expires_at=timezone.now() + timezone.timedelta(hours=expiry_hours)
        ) 