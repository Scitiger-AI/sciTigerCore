"""
用户模型定义
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    自定义用户管理器
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        创建普通用户
        
        Args:
            email: 用户邮箱
            password: 用户密码
            extra_fields: 额外字段
            
        Returns:
            User: 创建的用户对象
        """
        if not email:
            raise ValueError(_('必须提供邮箱地址'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        创建超级管理员
        
        Args:
            email: 用户邮箱
            password: 用户密码
            extra_fields: 额外字段
            
        Returns:
            User: 创建的超级管理员对象
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('超级管理员必须设置 is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('超级管理员必须设置 is_superuser=True'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    自定义用户模型
    
    使用邮箱作为唯一标识符
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('用户ID')
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_('邮箱地址')
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_('用户名')
    )
    first_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_('名')
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('姓')
    )
    # 用户状态
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('是否激活')
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('是否职员')
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name=_('是否超级管理员')
    )
    # 用户资料
    avatar = models.ImageField(
        upload_to='avatars',
        blank=True,
        null=True,
        verbose_name=_('头像')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('电话')
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('简介')
    )
    # 安全相关
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_('邮箱已验证')
    )
    phone_verified = models.BooleanField(
        default=False,
        verbose_name=_('电话已验证')
    )
    two_factor_enabled = models.BooleanField(
        default=False,
        verbose_name=_('双因素认证已启用')
    )
    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('最后登录IP')
    )
    password_changed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('密码修改时间')
    )
    # 时间相关
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('注册时间')
    )
    last_active = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('最后活跃时间')
    )
    
    # 关系字段
    roles = models.ManyToManyField(
        'Role',
        related_name='user_roles',
        verbose_name=_('角色')
    )

    # 指定用户管理器
    objects = UserManager()
    
    # 指定用户名字段
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """
        获取用户全名
        
        Returns:
            str: 用户全名
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
    
    def get_short_name(self):
        """
        获取用户简称
        
        Returns:
            str: 用户简称
        """
        return self.first_name or self.username
    
    def update_last_active(self):
        """
        更新最后活跃时间
        """
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])
    
    @property
    def requires_password_change(self):
        """
        检查用户是否需要修改密码
        
        Returns:
            bool: 是否需要修改密码
        """
        if not self.password_changed_at:
            return False
        
        # 检查密码是否过期
        from django.utils import timezone
        from datetime import timedelta
        
        # 获取当前租户的密码过期天数设置
        # 这里简化处理，实际应该根据用户所在租户的设置获取
        password_expiry_days = 90
        
        expiry_date = self.password_changed_at + timedelta(days=password_expiry_days)
        return timezone.now() > expiry_date 