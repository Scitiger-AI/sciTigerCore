"""
订单模型
"""

import uuid
import json
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.billing_service.utils.payment_utils import generate_order_number


class Order(models.Model):
    """
    订单模型
    
    记录系统中的所有订单信息
    """
    # 订单类型选项
    TYPE_SUBSCRIPTION = 'subscription'
    TYPE_POINTS = 'points'
    TYPE_PRODUCT = 'product'
    TYPE_SERVICE = 'service'
    TYPE_OTHER = 'other'
    
    ORDER_TYPE_CHOICES = (
        (TYPE_SUBSCRIPTION, _('订阅')),
        (TYPE_POINTS, _('积分')),
        (TYPE_PRODUCT, _('产品')),
        (TYPE_SERVICE, _('服务')),
        (TYPE_OTHER, _('其他')),
    )
    
    # 订单状态选项
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'
    STATUS_PARTIALLY_REFUNDED = 'partially_refunded'
    
    ORDER_STATUS_CHOICES = (
        (STATUS_PENDING, _('待支付')),
        (STATUS_PAID, _('已支付')),
        (STATUS_FAILED, _('支付失败')),
        (STATUS_CANCELLED, _('已取消')),
        (STATUS_REFUNDED, _('已退款')),
        (STATUS_PARTIALLY_REFUNDED, _('部分退款')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('ID'))
    tenant = models.ForeignKey('tenant_service.Tenant', on_delete=models.CASCADE, related_name='orders', verbose_name=_('租户'))
    user = models.ForeignKey('auth_service.User', on_delete=models.SET_NULL, null=True, related_name='orders', verbose_name=_('用户'))
    order_number = models.CharField(max_length=50, unique=True, verbose_name=_('订单编号'), default=generate_order_number)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default=TYPE_OTHER, verbose_name=_('订单类型'))
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=STATUS_PENDING, verbose_name=_('订单状态'))
    title = models.CharField(max_length=255, verbose_name=_('订单标题'))
    description = models.TextField(blank=True, null=True, verbose_name=_('订单描述'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('订单金额'))
    points = models.IntegerField(default=0, verbose_name=_('积分数量'), help_text=_('如果是积分订单，记录积分数量'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('折扣金额'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('税费'))
    currency = models.CharField(max_length=3, default='CNY', verbose_name=_('货币'))
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('支付方式'))
    payment_gateway = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('支付网关'))
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('交易ID'), help_text=_('支付平台返回的交易ID'))
    callback_data = models.JSONField(default=dict, verbose_name=_('回调数据'), help_text=_('存储支付回调数据或其他相关信息'))
    payment_url = models.TextField(blank=True, null=True, verbose_name=_('支付链接'))
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name=_('支付时间'))
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name=_('过期时间'))
    refunded_at = models.DateTimeField(blank=True, null=True, verbose_name=_('退款时间'))
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('退款金额'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    created_by = models.ForeignKey(
        'auth_service.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_orders', 
        verbose_name=_('创建者')
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('IP地址'))
    user_agent = models.TextField(blank=True, null=True, verbose_name=_('用户代理'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('备注'))
    
    class Meta:
        verbose_name = _('订单')
        verbose_name_plural = _('订单')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'order_number']),
            models.Index(fields=['tenant', 'user']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.order_number} - {self.title} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """
        保存订单时，如果没有订单编号，则生成一个
        """
        if not self.order_number:
            self.order_number = generate_order_number()
            
        # 设置订单过期时间，默认为创建后24小时
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
            
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """
        判断订单是否过期
        """
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    @property
    def total_amount(self):
        """
        计算订单总金额（含税费，减去折扣）
        """
        return self.amount + self.tax_amount - self.discount_amount
    
    def mark_as_paid(self, transaction_id=None, payment_method=None, payment_data=None):
        """
        将订单标记为已支付
        
        Args:
            transaction_id: 支付平台返回的交易ID
            payment_method: 支付方式
            payment_data: 支付相关数据
        """
        self.status = self.STATUS_PAID
        self.paid_at = timezone.now()
        
        if transaction_id:
            self.transaction_id = transaction_id
            
        if payment_method:
            self.payment_method = payment_method
            
        if payment_data:
            # 合并现有回调数据和新的支付数据
            current_data = self.callback_data or {}
            if isinstance(payment_data, str):
                try:
                    payment_data = json.loads(payment_data)
                except:
                    payment_data = {'raw_data': payment_data}
            
            current_data.update({
                'payment_data': payment_data,
                'paid_at': self.paid_at.isoformat() if self.paid_at else None
            })
            self.callback_data = current_data
            
        self.save()
        
    def mark_as_failed(self, failure_reason=None):
        """
        将订单标记为支付失败
        
        Args:
            failure_reason: 失败原因
        """
        self.status = self.STATUS_FAILED
        
        if failure_reason:
            current_data = self.callback_data or {}
            current_data.update({
                'failure_reason': failure_reason,
                'failed_at': timezone.now().isoformat()
            })
            self.callback_data = current_data
            
        self.save()
        
    def cancel(self, reason=None):
        """
        取消订单
        
        Args:
            reason: 取消原因
        """
        if self.status == self.STATUS_PAID:
            raise ValueError(_('已支付的订单不能直接取消，请先退款'))
            
        self.status = self.STATUS_CANCELLED
        
        if reason:
            current_data = self.callback_data or {}
            current_data.update({
                'cancel_reason': reason,
                'cancelled_at': timezone.now().isoformat()
            })
            self.callback_data = current_data
            
        self.save()
        
    def refund(self, amount=None, reason=None):
        """
        退款
        
        Args:
            amount: 退款金额，如果为None则全额退款
            reason: 退款原因
        """
        if self.status != self.STATUS_PAID:
            raise ValueError(_('只有已支付的订单才能退款'))
            
        if amount is None:
            # 全额退款
            self.refunded_amount = self.amount
            self.status = self.STATUS_REFUNDED
        else:
            # 部分退款
            if amount > self.amount:
                raise ValueError(_('退款金额不能大于订单金额'))
                
            self.refunded_amount = amount
            if self.refunded_amount == self.amount:
                self.status = self.STATUS_REFUNDED
            else:
                self.status = self.STATUS_PARTIALLY_REFUNDED
                
        self.refunded_at = timezone.now()
        
        if reason:
            current_data = self.callback_data or {}
            current_data.update({
                'refund_reason': reason,
                'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None,
                'refunded_amount': str(self.refunded_amount)
            })
            self.callback_data = current_data
            
        self.save() 