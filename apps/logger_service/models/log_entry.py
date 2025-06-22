"""
日志条目模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class LogEntry(models.Model):
    """
    日志条目模型
    
    注意：这是一个临时模型，实际数据存储在MongoDB中
    该模型主要用于定义日志结构和提供ORM接口
    """
    # 日志级别选项
    LEVEL_DEBUG = 'debug'
    LEVEL_INFO = 'info'
    LEVEL_WARNING = 'warning'
    LEVEL_ERROR = 'error'
    LEVEL_CRITICAL = 'critical'
    
    LEVEL_CHOICES = (
        (LEVEL_DEBUG, _('调试')),
        (LEVEL_INFO, _('信息')),
        (LEVEL_WARNING, _('警告')),
        (LEVEL_ERROR, _('错误')),
        (LEVEL_CRITICAL, _('严重')),
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.DO_NOTHING,
        related_name='logs',
        blank=True,
        null=True,
        verbose_name=_('所属租户')
    )
    category = models.ForeignKey(
        'logger_service.LogCategory',
        on_delete=models.SET_NULL,
        related_name='logs',
        blank=True,
        null=True,
        verbose_name=_('日志分类')
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default=LEVEL_INFO,
        verbose_name=_('日志级别')
    )
    message = models.TextField(
        verbose_name=_('日志消息')
    )
    source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('来源')
    )
    user = models.ForeignKey(
        'auth_service.User',
        on_delete=models.SET_NULL,
        related_name='logs',
        blank=True,
        null=True,
        verbose_name=_('用户')
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('IP地址')
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('用户代理')
    )
    request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('请求ID')
    )
    metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('元数据')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('时间戳')
    )
    
    class Meta:
        verbose_name = _('日志条目')
        verbose_name_plural = _('日志条目')
        ordering = ['-timestamp']
        # 这个模型不会在数据库中创建表
        managed = False
    
    def __str__(self):
        return f"{self.get_level_display()} - {self.message[:50]}"
    
    @classmethod
    def create_log(cls, message, level=LEVEL_INFO, category=None, tenant=None, user=None, 
                  source=None, ip_address=None, user_agent=None, request_id=None, metadata=None):
        """
        创建日志条目
        
        注意：此方法不会真正创建数据库记录，而是通过LoggerService将日志写入MongoDB
        
        Args:
            message: 日志消息
            level: 日志级别
            category: 日志分类
            tenant: 所属租户
            user: 相关用户
            source: 日志来源
            ip_address: IP地址
            user_agent: 用户代理
            request_id: 请求ID
            metadata: 元数据
            
        Returns:
            dict: 创建的日志数据
        """
        # 构建日志数据
        log_data = {
            'id': str(uuid.uuid4()),
            'message': message,
            'level': level,
            'timestamp': None,  # 由LoggerService填充
            'source': source,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'request_id': request_id,
            'metadata': metadata or {}
        }
        
        # 添加关联对象的ID
        if tenant:
            log_data['tenant_id'] = str(tenant.id)
            log_data['tenant_name'] = tenant.name
            
        if category:
            log_data['category_id'] = str(category.id)
            log_data['category_name'] = category.name
            log_data['category_code'] = category.code
            
        if user:
            log_data['user_id'] = str(user.id)
            log_data['username'] = user.username
            
        # 将日志数据传递给LoggerService处理
        from apps.logger_service.services import LoggerService
        return LoggerService.log(log_data) 