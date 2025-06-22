"""
发票模型
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Invoice(models.Model):
    """
    发票模型
    
    记录系统中的所有发票信息
    """
    # 发票状态选项
    STATUS_DRAFT = 'draft'
    STATUS_PENDING = 'pending'
    STATUS_ISSUED = 'issued'
    STATUS_PAID = 'paid'
    STATUS_VOID = 'void'
    STATUS_CANCELED = 'canceled'
    
    INVOICE_STATUS_CHOICES = (
        (STATUS_DRAFT, _('草稿')),
        (STATUS_PENDING, _('待开具')),
        (STATUS_ISSUED, _('已开具')),
        (STATUS_PAID, _('已支付')),
        (STATUS_VOID, _('作废')),
        (STATUS_CANCELED, _('已取消')),
    )
    
    # 发票类型选项
    TYPE_REGULAR = 'regular'
    TYPE_RECEIPT = 'receipt'
    TYPE_VAT = 'vat'
    TYPE_CREDIT_NOTE = 'credit_note'
    
    INVOICE_TYPE_CHOICES = (
        (TYPE_REGULAR, _('普通发票')),
        (TYPE_RECEIPT, _('收据')),
        (TYPE_VAT, _('增值税发票')),
        (TYPE_CREDIT_NOTE, _('贷记通知单')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('ID'))
    tenant = models.ForeignKey('tenant_service.Tenant', on_delete=models.CASCADE, related_name='invoices', verbose_name=_('租户'))
    user = models.ForeignKey('auth_service.User', on_delete=models.SET_NULL, null=True, related_name='invoices', verbose_name=_('用户'))
    order = models.ForeignKey('billing_service.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices', verbose_name=_('关联订单'))
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name=_('发票编号'))
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES, default=TYPE_REGULAR, verbose_name=_('发票类型'))
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default=STATUS_DRAFT, verbose_name=_('发票状态'))
    
    # 金额信息
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('发票金额'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('税额'))
    currency = models.CharField(max_length=3, default='CNY', verbose_name=_('货币'))
    
    # 发票信息
    title = models.CharField(max_length=255, verbose_name=_('发票抬头'))
    tax_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('税号'))
    address = models.TextField(blank=True, null=True, verbose_name=_('地址'))
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('电话'))
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('开户行'))
    bank_account = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('银行账号'))
    
    # 发票项目
    items = models.JSONField(default=list, verbose_name=_('发票项目'), help_text=_('发票包含的商品或服务项目列表'))
    
    # 备注和说明
    notes = models.TextField(blank=True, null=True, verbose_name=_('备注'))
    terms = models.TextField(blank=True, null=True, verbose_name=_('条款'))
    
    # 时间信息
    issue_date = models.DateField(blank=True, null=True, verbose_name=_('开具日期'))
    due_date = models.DateField(blank=True, null=True, verbose_name=_('到期日期'))
    paid_date = models.DateField(blank=True, null=True, verbose_name=_('支付日期'))
    
    # 电子发票信息
    pdf_url = models.URLField(blank=True, null=True, verbose_name=_('PDF链接'))
    download_url = models.URLField(blank=True, null=True, verbose_name=_('下载链接'))
    
    # 元数据
    metadata = models.JSONField(default=dict, verbose_name=_('元数据'))
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    created_by = models.ForeignKey(
        'auth_service.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_invoices', 
        verbose_name=_('创建者')
    )
    
    class Meta:
        verbose_name = _('发票')
        verbose_name_plural = _('发票')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'invoice_number']),
            models.Index(fields=['tenant', 'user']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'issue_date']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.title} ({self.get_status_display()})"
    
    @property
    def total_amount(self):
        """
        计算发票总金额（含税）
        """
        return self.amount + self.tax_amount
    
    def issue(self, issue_date=None):
        """
        开具发票
        
        Args:
            issue_date: 开具日期，默认为当前日期
        """
        if self.status not in [self.STATUS_DRAFT, self.STATUS_PENDING]:
            raise ValueError(_('只有草稿或待开具状态的发票才能开具'))
            
        self.status = self.STATUS_ISSUED
        self.issue_date = issue_date or timezone.now().date()
        
        # 设置默认到期日期为开具日期后30天
        if not self.due_date:
            self.due_date = self.issue_date + timezone.timedelta(days=30)
            
        self.save()
    
    def mark_as_paid(self, paid_date=None):
        """
        将发票标记为已支付
        
        Args:
            paid_date: 支付日期，默认为当前日期
        """
        if self.status not in [self.STATUS_ISSUED, self.STATUS_PENDING]:
            raise ValueError(_('只有已开具或待开具状态的发票才能标记为已支付'))
            
        self.status = self.STATUS_PAID
        self.paid_date = paid_date or timezone.now().date()
        self.save()
    
    def void(self, reason=None):
        """
        作废发票
        
        Args:
            reason: 作废原因
        """
        if self.status == self.STATUS_PAID:
            raise ValueError(_('已支付的发票不能作废'))
            
        self.status = self.STATUS_VOID
        
        if reason:
            self.notes = (self.notes or '') + f"\n作废原因: {reason}"
            
        self.save()
    
    def cancel(self, reason=None):
        """
        取消发票
        
        Args:
            reason: 取消原因
        """
        if self.status not in [self.STATUS_DRAFT, self.STATUS_PENDING]:
            raise ValueError(_('只有草稿或待开具状态的发票才能取消'))
            
        self.status = self.STATUS_CANCELED
        
        if reason:
            self.notes = (self.notes or '') + f"\n取消原因: {reason}"
            
        self.save() 