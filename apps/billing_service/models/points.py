"""
积分模型
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserPoints(models.Model):
    """
    用户积分账户模型
    
    记录用户的积分余额
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('ID'))
    tenant = models.ForeignKey('tenant_service.Tenant', on_delete=models.CASCADE, related_name='user_points', verbose_name=_('租户'))
    user = models.ForeignKey('auth_service.User', on_delete=models.CASCADE, related_name='points_account', verbose_name=_('用户'))
    balance = models.IntegerField(default=0, verbose_name=_('积分余额'))
    total_earned = models.IntegerField(default=0, verbose_name=_('总获得积分'))
    total_spent = models.IntegerField(default=0, verbose_name=_('总消费积分'))
    is_active = models.BooleanField(default=True, verbose_name=_('是否激活'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('用户积分账户')
        verbose_name_plural = _('用户积分账户')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['tenant', 'user']),
        ]
        unique_together = [('tenant', 'user')]
    
    def __str__(self):
        return f"{self.user} - {self.balance} 积分"
    
    def add_points(self, points, reason=None, source=None, transaction_type=None):
        """
        为用户添加积分
        
        Args:
            points: 积分数量（正整数）
            reason: 添加原因
            source: 积分来源
            transaction_type: 交易类型
            
        Returns:
            PointsTransaction: 积分交易记录
        """
        if points <= 0:
            raise ValueError(_('添加的积分必须为正数'))
            
        # 更新积分余额
        self.balance += points
        self.total_earned += points
        self.save()
        
        # 创建交易记录
        transaction = PointsTransaction.objects.create(
            tenant=self.tenant,
            user=self.user,
            user_points=self,
            points=points,
            balance_after=self.balance,
            transaction_type=transaction_type or PointsTransaction.TYPE_EARN,
            source=source,
            description=reason
        )
        
        return transaction
    
    def deduct_points(self, points, reason=None, source=None, transaction_type=None):
        """
        扣除用户积分
        
        Args:
            points: 积分数量（正整数）
            reason: 扣除原因
            source: 积分去向
            transaction_type: 交易类型
            
        Returns:
            PointsTransaction: 积分交易记录
            
        Raises:
            ValueError: 积分不足
        """
        if points <= 0:
            raise ValueError(_('扣除的积分必须为正数'))
            
        if self.balance < points:
            raise ValueError(_('积分余额不足'))
            
        # 更新积分余额
        self.balance -= points
        self.total_spent += points
        self.save()
        
        # 创建交易记录
        transaction = PointsTransaction.objects.create(
            tenant=self.tenant,
            user=self.user,
            user_points=self,
            points=-points,  # 负数表示支出
            balance_after=self.balance,
            transaction_type=transaction_type or PointsTransaction.TYPE_SPEND,
            source=source,
            description=reason
        )
        
        return transaction


class PointsTransaction(models.Model):
    """
    积分交易记录模型
    
    记录所有积分变动的详细信息
    """
    # 交易类型选项
    TYPE_EARN = 'earn'
    TYPE_SPEND = 'spend'
    TYPE_EXPIRE = 'expire'
    TYPE_ADJUST = 'adjust'
    TYPE_REFUND = 'refund'
    TYPE_PURCHASE = 'purchase'
    TYPE_REWARD = 'reward'
    TYPE_OTHER = 'other'
    
    TRANSACTION_TYPE_CHOICES = (
        (TYPE_EARN, _('获得')),
        (TYPE_SPEND, _('消费')),
        (TYPE_EXPIRE, _('过期')),
        (TYPE_ADJUST, _('调整')),
        (TYPE_REFUND, _('退款')),
        (TYPE_PURCHASE, _('购买')),
        (TYPE_REWARD, _('奖励')),
        (TYPE_OTHER, _('其他')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('ID'))
    tenant = models.ForeignKey('tenant_service.Tenant', on_delete=models.CASCADE, related_name='points_transactions', verbose_name=_('租户'))
    user = models.ForeignKey('auth_service.User', on_delete=models.CASCADE, related_name='points_transactions', verbose_name=_('用户'))
    user_points = models.ForeignKey('billing_service.UserPoints', on_delete=models.CASCADE, related_name='transactions', verbose_name=_('积分账户'))
    points = models.IntegerField(verbose_name=_('积分变动'), help_text=_('正数表示收入，负数表示支出'))
    balance_after = models.IntegerField(verbose_name=_('变动后余额'))
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, verbose_name=_('交易类型'))
    source = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('来源/去向'))
    description = models.TextField(blank=True, null=True, verbose_name=_('描述'))
    order = models.ForeignKey('billing_service.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='points_transactions', verbose_name=_('关联订单'))
    metadata = models.JSONField(default=dict, verbose_name=_('元数据'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    created_by = models.ForeignKey(
        'auth_service.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_points_transactions', 
        verbose_name=_('创建者')
    )
    
    class Meta:
        verbose_name = _('积分交易记录')
        verbose_name_plural = _('积分交易记录')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'user']),
            models.Index(fields=['tenant', 'transaction_type']),
            models.Index(fields=['tenant', 'created_at']),
        ]
    
    def __str__(self):
        if self.points > 0:
            return f"{self.user} 获得 {self.points} 积分 ({self.get_transaction_type_display()})"
        else:
            return f"{self.user} 消费 {abs(self.points)} 积分 ({self.get_transaction_type_display()})" 