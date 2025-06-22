"""
订阅模型
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from dateutil.relativedelta import relativedelta


class SubscriptionPlan(models.Model):
    """
    订阅计划模型
    
    定义系统中可用的订阅计划
    """
    # 计费周期选项
    BILLING_CYCLE_MONTHLY = 'monthly'
    BILLING_CYCLE_QUARTERLY = 'quarterly'
    BILLING_CYCLE_YEARLY = 'yearly'
    
    BILLING_CYCLE_CHOICES = (
        (BILLING_CYCLE_MONTHLY, _('月度')),
        (BILLING_CYCLE_QUARTERLY, _('季度')),
        (BILLING_CYCLE_YEARLY, _('年度')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('ID'))
    tenant = models.ForeignKey('tenant_service.Tenant', on_delete=models.CASCADE, related_name='subscription_plans', verbose_name=_('租户'))
    name = models.CharField(max_length=100, verbose_name=_('计划名称'))
    code = models.CharField(max_length=50, verbose_name=_('计划代码'), help_text=_('系统内部使用的唯一标识符'))
    description = models.TextField(blank=True, null=True, verbose_name=_('计划描述'))
    is_active = models.BooleanField(default=True, verbose_name=_('是否激活'))
    is_public = models.BooleanField(default=True, verbose_name=_('是否公开'), help_text=_('是否在订阅页面公开显示'))
    
    # 价格信息
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('月度价格'))
    quarterly_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('季度价格'))
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('年度价格'))
    currency = models.CharField(max_length=3, default='CNY', verbose_name=_('货币'))
    
    # 功能配置
    features = models.JSONField(default=dict, verbose_name=_('功能配置'), help_text=_('定义此计划包含的功能和限制'))
    
    # 排序和显示
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('排序顺序'))
    highlight = models.BooleanField(default=False, verbose_name=_('是否突出显示'))
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('订阅计划')
        verbose_name_plural = _('订阅计划')
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['tenant', 'code']),
            models.Index(fields=['tenant', 'is_active']),
        ]
        unique_together = [('tenant', 'code')]
    
    def __str__(self):
        return f"{self.name} ({self.get_price_display()})"
    
    def get_price_display(self):
        """
        获取价格显示字符串
        """
        return f"{self.monthly_price} {self.currency}/{_('月')}"
    
    def get_price_for_cycle(self, billing_cycle):
        """
        根据计费周期获取价格
        
        Args:
            billing_cycle: 计费周期
            
        Returns:
            Decimal: 对应周期的价格
        """
        if billing_cycle == self.BILLING_CYCLE_MONTHLY:
            return self.monthly_price
        elif billing_cycle == self.BILLING_CYCLE_QUARTERLY:
            return self.quarterly_price
        elif billing_cycle == self.BILLING_CYCLE_YEARLY:
            return self.yearly_price
        else:
            raise ValueError(_('无效的计费周期'))


class Subscription(models.Model):
    """
    订阅模型
    
    记录用户的订阅信息
    """
    # 订阅状态选项
    STATUS_ACTIVE = 'active'
    STATUS_CANCELED = 'canceled'
    STATUS_EXPIRED = 'expired'
    STATUS_TRIAL = 'trial'
    STATUS_PAST_DUE = 'past_due'
    STATUS_UNPAID = 'unpaid'
    
    SUBSCRIPTION_STATUS_CHOICES = (
        (STATUS_ACTIVE, _('激活')),
        (STATUS_CANCELED, _('已取消')),
        (STATUS_EXPIRED, _('已过期')),
        (STATUS_TRIAL, _('试用期')),
        (STATUS_PAST_DUE, _('逾期')),
        (STATUS_UNPAID, _('未支付')),
    )
    
    # 计费周期选项，与SubscriptionPlan保持一致
    BILLING_CYCLE_MONTHLY = 'monthly'
    BILLING_CYCLE_QUARTERLY = 'quarterly'
    BILLING_CYCLE_YEARLY = 'yearly'
    
    BILLING_CYCLE_CHOICES = (
        (BILLING_CYCLE_MONTHLY, _('月度')),
        (BILLING_CYCLE_QUARTERLY, _('季度')),
        (BILLING_CYCLE_YEARLY, _('年度')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('ID'))
    tenant = models.ForeignKey('tenant_service.Tenant', on_delete=models.CASCADE, related_name='subscriptions', verbose_name=_('租户'))
    user = models.ForeignKey('auth_service.User', on_delete=models.CASCADE, related_name='subscriptions', verbose_name=_('用户'))
    plan = models.ForeignKey('billing_service.SubscriptionPlan', on_delete=models.PROTECT, related_name='subscriptions', verbose_name=_('订阅计划'))
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default=STATUS_ACTIVE, verbose_name=_('订阅状态'))
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default=BILLING_CYCLE_MONTHLY, verbose_name=_('计费周期'))
    auto_renew = models.BooleanField(default=True, verbose_name=_('自动续订'))
    
    # 时间信息
    start_date = models.DateTimeField(verbose_name=_('开始日期'))
    end_date = models.DateTimeField(verbose_name=_('结束日期'))
    trial_end_date = models.DateTimeField(blank=True, null=True, verbose_name=_('试用期结束日期'))
    canceled_at = models.DateTimeField(blank=True, null=True, verbose_name=_('取消日期'))
    current_period_start = models.DateTimeField(verbose_name=_('当前计费周期开始日期'))
    current_period_end = models.DateTimeField(verbose_name=_('当前计费周期结束日期'))
    
    # 价格信息
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('订阅价格'), help_text=_('订阅时的价格，可能与计划当前价格不同'))
    currency = models.CharField(max_length=3, default='CNY', verbose_name=_('货币'))
    
    # 其他信息
    metadata = models.JSONField(default=dict, verbose_name=_('元数据'), help_text=_('存储额外的订阅相关信息'))
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('订阅')
        verbose_name_plural = _('订阅')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'user']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.plan.name} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """
        保存订阅时，如果没有设置当前计费周期，则根据开始日期和计费周期自动计算
        """
        if not self.current_period_start:
            self.current_period_start = self.start_date
            
        if not self.current_period_end:
            self.current_period_end = self._calculate_period_end(self.current_period_start)
            
        super().save(*args, **kwargs)
    
    def _calculate_period_end(self, start_date):
        """
        根据开始日期和计费周期计算结束日期
        
        Args:
            start_date: 开始日期
            
        Returns:
            datetime: 结束日期
        """
        if self.billing_cycle == self.BILLING_CYCLE_MONTHLY:
            return start_date + relativedelta(months=1)
        elif self.billing_cycle == self.BILLING_CYCLE_QUARTERLY:
            return start_date + relativedelta(months=3)
        elif self.billing_cycle == self.BILLING_CYCLE_YEARLY:
            return start_date + relativedelta(years=1)
        else:
            raise ValueError(_('无效的计费周期'))
    
    @property
    def is_active(self):
        """
        判断订阅是否处于活跃状态
        """
        return self.status in [self.STATUS_ACTIVE, self.STATUS_TRIAL] and self.end_date > timezone.now()
    
    @property
    def is_trial(self):
        """
        判断订阅是否处于试用期
        """
        return self.status == self.STATUS_TRIAL and (self.trial_end_date is None or self.trial_end_date > timezone.now())
    
    @property
    def days_until_expiration(self):
        """
        计算距离订阅过期还有多少天
        """
        if not self.is_active:
            return 0
        
        delta = self.end_date - timezone.now()
        return max(0, delta.days)
    
    def cancel(self, at_period_end=True):
        """
        取消订阅
        
        Args:
            at_period_end: 是否在当前计费周期结束时取消，True表示计费周期结束后取消，False表示立即取消
        """
        self.auto_renew = False
        self.canceled_at = timezone.now()
        
        if not at_period_end:
            # 立即取消
            self.status = self.STATUS_CANCELED
            self.end_date = timezone.now()
        
        self.save()
    
    def renew(self):
        """
        续订订阅，延长订阅周期
        """
        if not self.auto_renew:
            raise ValueError(_('已关闭自动续订的订阅不能续订'))
        
        # 更新计费周期
        self.current_period_start = self.current_period_end
        self.current_period_end = self._calculate_period_end(self.current_period_start)
        
        # 更新结束日期
        self.end_date = self.current_period_end
        
        # 确保状态为激活
        self.status = self.STATUS_ACTIVE
        
        self.save()
        
    def change_plan(self, new_plan, prorate=True):
        """
        更换订阅计划
        
        Args:
            new_plan: 新的订阅计划
            prorate: 是否按比例计算费用
        """
        old_plan = self.plan
        self.plan = new_plan
        
        # 更新价格
        self.price = new_plan.get_price_for_cycle(self.billing_cycle)
        
        # TODO: 实现按比例计算费用的逻辑
        
        self.save()
        
        return {
            'old_plan': old_plan,
            'new_plan': new_plan,
            'price_change': self.price - old_plan.get_price_for_cycle(self.billing_cycle)
        } 