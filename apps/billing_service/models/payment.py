"""
支付模型
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    """
    支付记录模型
    
    记录所有支付交易的详细信息
    """
    # 支付状态选项
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    STATUS_PARTIALLY_REFUNDED = 'partially_refunded'
    
    PAYMENT_STATUS_CHOICES = (
        (STATUS_PENDING, _('待处理')),
        (STATUS_PROCESSING, _('处理中')),
        (STATUS_SUCCESS, _('成功')),
        (STATUS_FAILED, _('失败')),
        (STATUS_REFUNDED, _('已退款')),
        (STATUS_PARTIALLY_REFUNDED, _('部分退款')),
    )
    
    # 支付方式选项
    METHOD_ALIPAY = 'alipay'
    METHOD_WECHAT = 'wechat'
    METHOD_BANK_TRANSFER = 'bank_transfer'
    METHOD_CREDIT_CARD = 'credit_card'
    METHOD_PAYPAL = 'paypal'
    METHOD_POINTS = 'points'
    METHOD_OTHER = 'other'
    
    PAYMENT_METHOD_CHOICES = (
        (METHOD_ALIPAY, _('支付宝')),
        (METHOD_WECHAT, _('微信支付')),
        (METHOD_BANK_TRANSFER, _('银行转账')),
        (METHOD_CREDIT_CARD, _('信用卡')),
        (METHOD_PAYPAL, _('PayPal')),
        (METHOD_POINTS, _('积分支付')),
        (METHOD_OTHER, _('其他')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('ID'))
    tenant = models.ForeignKey('tenant_service.Tenant', on_delete=models.CASCADE, related_name='payments', verbose_name=_('租户'))
    order = models.ForeignKey('billing_service.Order', on_delete=models.CASCADE, related_name='payments', verbose_name=_('关联订单'))
    user = models.ForeignKey('auth_service.User', on_delete=models.SET_NULL, null=True, related_name='payments', verbose_name=_('用户'))
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, verbose_name=_('支付方式'))
    payment_gateway = models.CharField(max_length=50, verbose_name=_('支付网关'), help_text=_('如：alipay, wechat, stripe等'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('支付金额'))
    currency = models.CharField(max_length=3, default='CNY', verbose_name=_('货币'))
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=STATUS_PENDING, verbose_name=_('支付状态'))
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('交易ID'), help_text=_('支付平台返回的交易ID'))
    transaction_data = models.JSONField(default=dict, verbose_name=_('交易数据'), help_text=_('存储支付平台返回的完整交易数据'))
    payment_url = models.TextField(blank=True, null=True, verbose_name=_('支付链接'))
    callback_url = models.URLField(blank=True, null=True, verbose_name=_('回调URL'))
    return_url = models.URLField(blank=True, null=True, verbose_name=_('返回URL'))
    notify_url = models.URLField(blank=True, null=True, verbose_name=_('通知URL'))
    error_message = models.TextField(blank=True, null=True, verbose_name=_('错误信息'))
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name=_('支付时间'))
    refunded_at = models.DateTimeField(blank=True, null=True, verbose_name=_('退款时间'))
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('退款金额'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('IP地址'))
    user_agent = models.TextField(blank=True, null=True, verbose_name=_('用户代理'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('备注'))
    
    class Meta:
        verbose_name = _('支付记录')
        verbose_name_plural = _('支付记录')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'transaction_id']),
            models.Index(fields=['tenant', 'order']),
            models.Index(fields=['tenant', 'user']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_payment_method_display()} - {self.amount} {self.currency} ({self.get_status_display()})"
    
    def mark_as_success(self, transaction_id=None, transaction_data=None):
        """
        将支付标记为成功
        
        Args:
            transaction_id: 支付平台返回的交易ID
            transaction_data: 支付平台返回的交易数据
        """
        self.status = self.STATUS_SUCCESS
        self.paid_at = timezone.now()
        
        if transaction_id:
            self.transaction_id = transaction_id
            
        if transaction_data:
            # 合并现有交易数据和新的交易数据
            current_data = self.transaction_data or {}
            if isinstance(transaction_data, dict):
                current_data.update(transaction_data)
            else:
                current_data['raw_data'] = transaction_data
                
            current_data['paid_at'] = self.paid_at.isoformat() if self.paid_at else None
            self.transaction_data = current_data
            
        self.save()
        
        # 更新关联订单状态
        if self.order:
            self.order.mark_as_paid(
                transaction_id=self.transaction_id,
                payment_method=self.payment_method,
                payment_data=self.transaction_data
            )
    
    def mark_as_failed(self, error_message=None):
        """
        将支付标记为失败
        
        Args:
            error_message: 错误信息
        """
        self.status = self.STATUS_FAILED
        
        if error_message:
            self.error_message = error_message
            
            # 更新交易数据
            current_data = self.transaction_data or {}
            current_data.update({
                'error_message': error_message,
                'failed_at': timezone.now().isoformat()
            })
            self.transaction_data = current_data
            
        self.save()
        
        # 更新关联订单状态
        if self.order:
            self.order.mark_as_failed(failure_reason=error_message)
    
    def refund(self, amount=None, reason=None):
        """
        退款
        
        Args:
            amount: 退款金额，如果为None则全额退款
            reason: 退款原因
        """
        if self.status != self.STATUS_SUCCESS:
            raise ValueError(_('只有支付成功的记录才能退款'))
            
        if amount is None:
            # 全额退款
            self.refunded_amount = self.amount
            self.status = self.STATUS_REFUNDED
        else:
            # 部分退款
            if amount > self.amount:
                raise ValueError(_('退款金额不能大于支付金额'))
                
            self.refunded_amount = amount
            if self.refunded_amount == self.amount:
                self.status = self.STATUS_REFUNDED
            else:
                self.status = self.STATUS_PARTIALLY_REFUNDED
                
        self.refunded_at = timezone.now()
        
        # 更新交易数据
        current_data = self.transaction_data or {}
        current_data.update({
            'refund_reason': reason,
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None,
            'refunded_amount': str(self.refunded_amount)
        })
        self.transaction_data = current_data
        
        self.save()
        
        # 更新关联订单状态
        if self.order:
            self.order.refund(amount=self.refunded_amount, reason=reason) 