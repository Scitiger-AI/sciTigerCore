"""
支付网关配置模型
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentGatewayConfig(models.Model):
    """
    支付网关配置模型
    
    存储不同支付网关的配置信息
    """
    # 支付网关类型选项
    TYPE_ALIPAY = 'alipay'
    TYPE_WECHAT = 'wechat'
    TYPE_BANK = 'bank'
    TYPE_PAYPAL = 'paypal'
    TYPE_STRIPE = 'stripe'
    TYPE_OTHER = 'other'
    
    GATEWAY_TYPE_CHOICES = (
        (TYPE_ALIPAY, _('支付宝')),
        (TYPE_WECHAT, _('微信支付')),
        (TYPE_BANK, _('银行支付')),
        (TYPE_PAYPAL, _('PayPal')),
        (TYPE_STRIPE, _('Stripe')),
        (TYPE_OTHER, _('其他')),
    )
    
    # 环境选项
    ENV_SANDBOX = 'sandbox'
    ENV_PRODUCTION = 'production'
    
    ENVIRONMENT_CHOICES = (
        (ENV_SANDBOX, _('沙箱环境')),
        (ENV_PRODUCTION, _('生产环境')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('ID'))
    tenant = models.ForeignKey('tenant_service.Tenant', on_delete=models.CASCADE, related_name='payment_gateways', verbose_name=_('租户'))
    name = models.CharField(max_length=100, verbose_name=_('网关名称'))
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_TYPE_CHOICES, verbose_name=_('网关类型'))
    environment = models.CharField(max_length=20, choices=ENVIRONMENT_CHOICES, default=ENV_SANDBOX, verbose_name=_('环境'))
    is_default = models.BooleanField(default=False, verbose_name=_('是否默认'))
    is_active = models.BooleanField(default=True, verbose_name=_('是否激活'))
    
    # 配置信息
    config = models.JSONField(verbose_name=_('配置信息'), help_text=_('存储支付网关的配置参数，如API密钥等'))
    
    # 回调URL
    return_url = models.URLField(blank=True, null=True, verbose_name=_('返回URL'), help_text=_('支付成功后跳转的URL'))
    notify_url = models.URLField(blank=True, null=True, verbose_name=_('通知URL'), help_text=_('支付结果异步通知URL'))
    
    # 备注
    description = models.TextField(blank=True, null=True, verbose_name=_('描述'))
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    created_by = models.ForeignKey(
        'auth_service.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_payment_gateways', 
        verbose_name=_('创建者')
    )
    
    class Meta:
        verbose_name = _('支付网关配置')
        verbose_name_plural = _('支付网关配置')
        ordering = ['-is_default', 'name']
        indexes = [
            models.Index(fields=['tenant', 'gateway_type']),
            models.Index(fields=['tenant', 'is_active']),
        ]
        unique_together = [('tenant', 'gateway_type', 'environment')]
    
    def __str__(self):
        return f"{self.name} ({self.get_gateway_type_display()} - {self.get_environment_display()})"
    
    def save(self, *args, **kwargs):
        """
        保存配置时，如果设置为默认，则将同类型的其他配置设置为非默认
        """
        if self.is_default:
            # 将同一租户下同类型的其他配置设置为非默认
            PaymentGatewayConfig.objects.filter(
                tenant=self.tenant,
                gateway_type=self.gateway_type
            ).exclude(pk=self.pk).update(is_default=False)
            
        super().save(*args, **kwargs)
    
    @property
    def gateway_name(self):
        """
        获取支付网关名称
        """
        return f"{self.get_gateway_type_display()} ({self.get_environment_display()})"
    
    @classmethod
    def get_default_gateway(cls, tenant, gateway_type):
        """
        获取指定租户和网关类型的默认配置
        
        Args:
            tenant: 租户对象或ID
            gateway_type: 网关类型
            
        Returns:
            PaymentGatewayConfig: 默认配置对象，如果不存在则返回None
        """
        try:
            return cls.objects.filter(
                tenant=tenant,
                gateway_type=gateway_type,
                is_active=True,
                is_default=True
            ).first() or cls.objects.filter(
                tenant=tenant,
                gateway_type=gateway_type,
                is_active=True
            ).first()
        except cls.DoesNotExist:
            return None 