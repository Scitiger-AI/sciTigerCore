"""
API 密钥相关模型定义
"""

import uuid
import secrets
import hashlib
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ApiKey(models.Model):
    """
    API 密钥模型
    
    用于第三方应用访问 API 时的认证
    """
    # API 密钥类型选项
    TYPE_SYSTEM = 'system'
    TYPE_USER = 'user'
    
    TYPE_CHOICES = (
        (TYPE_SYSTEM, _('系统级')),
        (TYPE_USER, _('用户级')),
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    key_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_USER,
        verbose_name=_('密钥类型')
    )
    key_hash = models.CharField(
        max_length=128,
        unique=True,
        verbose_name=_('密钥哈希')
    )
    prefix = models.CharField(
        max_length=8,
        verbose_name=_('密钥前缀')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('密钥名称')
    )
    # 关联信息
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='api_keys',
        blank=True,
        null=True,
        verbose_name=_('所属租户')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_keys',
        blank=True,
        null=True,
        verbose_name=_('所属用户')
    )
    created_by_key = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='created_keys',
        blank=True,
        null=True,
        verbose_name=_('创建此密钥的密钥')
    )
    # 状态信息
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('是否激活')
    )
    # 时间信息
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('创建时间')
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('过期时间')
    )
    last_used_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('最后使用时间')
    )
    # 元数据
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('元数据')
    )
    application_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('应用名称')
    )
    
    class Meta:
        verbose_name = _('API密钥')
        verbose_name_plural = _('API密钥')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.prefix}...)"
    
    @classmethod
    def generate_key(cls):
        """
        生成新的 API 密钥
        
        Returns:
            tuple: (密钥, 密钥前缀, 密钥哈希)
        """
        # 生成随机密钥
        key = secrets.token_hex(32)
        prefix = key[:8]
        
        # 计算密钥哈希
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        return key, prefix, key_hash
    
    @classmethod
    def create_key(cls, name, key_type, tenant=None, user=None, created_by_key=None, **kwargs):
        """
        创建新的 API 密钥
        
        Args:
            name: 密钥名称
            key_type: 密钥类型
            tenant: 所属租户
            user: 所属用户
            created_by_key: 创建此密钥的密钥
            **kwargs: 其他参数
            
        Returns:
            tuple: (ApiKey 对象, 明文密钥)
        """
        # 验证参数
        if key_type == cls.TYPE_SYSTEM and tenant is None:
            raise ValueError(_('系统级 API 密钥必须关联租户'))
        
        if key_type == cls.TYPE_USER and user is None:
            raise ValueError(_('用户级 API 密钥必须关联用户'))
        
        # 生成密钥
        key, prefix, key_hash = cls.generate_key()
        
        # 创建 API 密钥对象
        api_key = cls.objects.create(
            key_type=key_type,
            key_hash=key_hash,
            prefix=prefix,
            name=name,
            tenant=tenant,
            user=user,
            created_by_key=created_by_key,
            **kwargs
        )
        
        return api_key, key
    
    @classmethod
    def verify_key(cls, key):
        """
        验证 API 密钥
        
        Args:
            key: API 密钥
            
        Returns:
            ApiKey: 验证成功的 API 密钥对象，验证失败则返回 None
        """
        if not key:
            return None
        
        # 计算密钥哈希
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        try:
            # 查找匹配的 API 密钥
            api_key = cls.objects.get(key_hash=key_hash, is_active=True)
            
            # 检查是否过期
            from django.utils import timezone
            if api_key.expires_at and api_key.expires_at < timezone.now():
                return None
            
            # 更新最后使用时间
            api_key.last_used_at = timezone.now()
            api_key.save(update_fields=['last_used_at'])
            
            return api_key
        except cls.DoesNotExist:
            return None
    
    @property
    def is_expired(self):
        """
        检查 API 密钥是否已过期
        
        Returns:
            bool: 是否已过期
        """
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at


class ApiKeyScope(models.Model):
    """
    API 密钥作用域模型
    
    定义 API 密钥可访问的服务和操作
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    api_key = models.ForeignKey(
        ApiKey,
        on_delete=models.CASCADE,
        related_name='scopes',
        verbose_name=_('API密钥')
    )
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
    
    class Meta:
        verbose_name = _('API密钥作用域')
        verbose_name_plural = _('API密钥作用域')
        unique_together = ('api_key', 'service', 'resource', 'action')
        
    def __str__(self):
        return f"{self.api_key.name} - {self.service}:{self.resource}:{self.action}"


class ApiKeyUsageLog(models.Model):
    """
    API 密钥使用日志模型
    
    记录 API 密钥的使用情况
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    api_key = models.ForeignKey(
        ApiKey,
        on_delete=models.CASCADE,
        related_name='usage_logs',
        verbose_name=_('API密钥')
    )
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='api_key_logs',
        blank=True,
        null=True,
        verbose_name=_('所属租户')
    )
    request_path = models.CharField(
        max_length=255,
        verbose_name=_('请求路径')
    )
    request_method = models.CharField(
        max_length=10,
        verbose_name=_('请求方法')
    )
    response_status = models.IntegerField(
        verbose_name=_('响应状态码')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('时间戳')
    )
    client_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('客户端IP')
    )
    request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('请求ID')
    )
    
    class Meta:
        verbose_name = _('API密钥使用日志')
        verbose_name_plural = _('API密钥使用日志')
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.api_key.name} - {self.request_method} {self.request_path} ({self.response_status})" 