"""
订阅服务
实现订阅相关的业务逻辑
"""

import logging
from django.utils import timezone
from django.db import transaction

from apps.billing_service.models import Subscription, SubscriptionPlan, Order
from apps.billing_service.services.payment_service import PaymentService

logger = logging.getLogger('billing_service')


class SubscriptionService:
    """
    订阅服务类
    
    提供订阅相关的业务逻辑
    """
    
    @staticmethod
    def get_available_plans(tenant, is_public=True):
        """
        获取可用的订阅计划
        
        Args:
            tenant: 租户对象
            is_public: 是否只返回公开的计划
            
        Returns:
            QuerySet: 订阅计划查询集
        """
        plans = SubscriptionPlan.objects.filter(tenant=tenant, is_active=True)
        
        if is_public:
            plans = plans.filter(is_public=True)
            
        return plans.order_by('sort_order', 'name')
    
    @staticmethod
    def create_subscription(tenant, user, plan, billing_cycle, auto_renew=True, trial_days=0):
        """
        创建订阅
        
        Args:
            tenant: 租户对象
            user: 用户对象
            plan: 订阅计划对象
            billing_cycle: 计费周期，如 'monthly', 'quarterly', 'yearly'
            auto_renew: 是否自动续订
            trial_days: 试用期天数
            
        Returns:
            tuple: (Subscription, Order)，订阅对象和订单对象
        """
        try:
            with transaction.atomic():
                # 计算订阅开始和结束日期
                start_date = timezone.now()
                
                # 创建订阅对象
                subscription = Subscription(
                    tenant=tenant,
                    user=user,
                    plan=plan,
                    billing_cycle=billing_cycle,
                    auto_renew=auto_renew,
                    start_date=start_date,
                    current_period_start=start_date,
                    price=plan.get_price_for_cycle(billing_cycle)
                )
                
                # 如果有试用期
                if trial_days > 0:
                    subscription.status = Subscription.STATUS_TRIAL
                    subscription.trial_end_date = start_date + timezone.timedelta(days=trial_days)
                    subscription.end_date = subscription.trial_end_date
                    subscription.current_period_end = subscription.trial_end_date
                    subscription.save()
                    
                    logger.info(f"创建试用期订阅: subscription_id={subscription.id}, plan={plan.name}, trial_days={trial_days}")
                    
                    # 试用期不需要创建订单
                    return subscription, None
                    
                else:
                    # 无试用期，需要支付
                    subscription.status = Subscription.STATUS_UNPAID
                    
                    # 计算结束日期
                    if billing_cycle == Subscription.BILLING_CYCLE_MONTHLY:
                        subscription.end_date = start_date + timezone.timedelta(days=30)
                        subscription.current_period_end = subscription.end_date
                    elif billing_cycle == Subscription.BILLING_CYCLE_QUARTERLY:
                        subscription.end_date = start_date + timezone.timedelta(days=90)
                        subscription.current_period_end = subscription.end_date
                    elif billing_cycle == Subscription.BILLING_CYCLE_YEARLY:
                        subscription.end_date = start_date + timezone.timedelta(days=365)
                        subscription.current_period_end = subscription.end_date
                    else:
                        raise ValueError(f"无效的计费周期: {billing_cycle}")
                        
                    subscription.save()
                    
                    # 创建订单
                    order = PaymentService.create_order(
                        tenant=tenant,
                        user=user,
                        order_type=Order.TYPE_SUBSCRIPTION,
                        amount=subscription.price,
                        title=f"{plan.name} {dict(Subscription.BILLING_CYCLE_CHOICES).get(billing_cycle)}订阅",
                        description=f"{plan.name} {dict(Subscription.BILLING_CYCLE_CHOICES).get(billing_cycle)}订阅",
                        callback_data={'subscription_id': str(subscription.id)},
                        created_by=user
                    )
                    
                    logger.info(f"创建订阅: subscription_id={subscription.id}, plan={plan.name}, order_id={order.id}")
                    
                    return subscription, order
                    
        except Exception as e:
            logger.error(f"创建订阅失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def renew_subscription(subscription):
        """
        续订订阅
        
        Args:
            subscription: 订阅对象
            
        Returns:
            tuple: (Subscription, Order)，更新后的订阅对象和新创建的订单对象
        """
        try:
            with transaction.atomic():
                # 检查订阅是否可以续订
                if not subscription.auto_renew:
                    raise ValueError("该订阅已关闭自动续订")
                    
                if subscription.status not in [Subscription.STATUS_ACTIVE, Subscription.STATUS_PAST_DUE]:
                    raise ValueError(f"订阅状态不允许续订: {subscription.get_status_display()}")
                    
                # 计算新的计费周期
                new_period_start = subscription.current_period_end
                
                # 更新订阅对象
                subscription.current_period_start = new_period_start
                
                # 计算新的计费周期结束日期
                if subscription.billing_cycle == Subscription.BILLING_CYCLE_MONTHLY:
                    subscription.current_period_end = new_period_start + timezone.timedelta(days=30)
                elif subscription.billing_cycle == Subscription.BILLING_CYCLE_QUARTERLY:
                    subscription.current_period_end = new_period_start + timezone.timedelta(days=90)
                elif subscription.billing_cycle == Subscription.BILLING_CYCLE_YEARLY:
                    subscription.current_period_end = new_period_start + timezone.timedelta(days=365)
                    
                subscription.end_date = subscription.current_period_end
                subscription.status = Subscription.STATUS_UNPAID
                subscription.save()
                
                # 创建订单
                order = PaymentService.create_order(
                    tenant=subscription.tenant,
                    user=subscription.user,
                    order_type=Order.TYPE_SUBSCRIPTION,
                    amount=subscription.price,
                    title=f"{subscription.plan.name} {dict(Subscription.BILLING_CYCLE_CHOICES).get(subscription.billing_cycle)}续订",
                    description=f"{subscription.plan.name} {dict(Subscription.BILLING_CYCLE_CHOICES).get(subscription.billing_cycle)}续订",
                    callback_data={'subscription_id': str(subscription.id)},
                    created_by=subscription.user
                )
                
                logger.info(f"续订订阅: subscription_id={subscription.id}, order_id={order.id}")
                
                return subscription, order
                
        except Exception as e:
            logger.error(f"续订订阅失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def cancel_subscription(subscription, at_period_end=True, reason=None):
        """
        取消订阅
        
        Args:
            subscription: 订阅对象
            at_period_end: 是否在当前计费周期结束时取消
            reason: 取消原因
            
        Returns:
            Subscription: 更新后的订阅对象
        """
        try:
            # 取消订阅
            subscription.cancel(at_period_end=at_period_end)
            
            # 记录取消原因
            if reason:
                metadata = subscription.metadata or {}
                metadata['cancel_reason'] = reason
                metadata['canceled_at'] = timezone.now().isoformat()
                subscription.metadata = metadata
                subscription.save()
                
            logger.info(f"取消订阅: subscription_id={subscription.id}, at_period_end={at_period_end}")
            
            return subscription
            
        except Exception as e:
            logger.error(f"取消订阅失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def change_plan(subscription, new_plan, prorate=True):
        """
        更换订阅计划
        
        Args:
            subscription: 订阅对象
            new_plan: 新的订阅计划对象
            prorate: 是否按比例计算费用
            
        Returns:
            tuple: (Subscription, Order)，更新后的订阅对象和新创建的订单对象（如果需要补差价）
        """
        try:
            with transaction.atomic():
                # 检查订阅状态
                if subscription.status not in [Subscription.STATUS_ACTIVE, Subscription.STATUS_TRIAL]:
                    raise ValueError(f"订阅状态不允许更换计划: {subscription.get_status_display()}")
                    
                # 如果是相同的计划，无需更换
                if subscription.plan.id == new_plan.id:
                    return subscription, None
                    
                # 记录旧计划信息
                old_plan = subscription.plan
                old_price = subscription.price
                
                # 更换计划
                result = subscription.change_plan(new_plan, prorate=prorate)
                
                # 计算价格差异
                price_diff = result['price_change']
                
                # 如果需要补差价且差价大于0
                if prorate and price_diff > 0:
                    # 创建补差价订单
                    order = PaymentService.create_order(
                        tenant=subscription.tenant,
                        user=subscription.user,
                        order_type=Order.TYPE_SUBSCRIPTION,
                        amount=price_diff,
                        title=f"升级到 {new_plan.name} 计划",
                        description=f"从 {old_plan.name} 升级到 {new_plan.name} 的差价",
                        callback_data={'subscription_id': str(subscription.id), 'plan_change': True},
                        created_by=subscription.user
                    )
                    
                    logger.info(f"更换订阅计划: subscription_id={subscription.id}, old_plan={old_plan.name}, new_plan={new_plan.name}, price_diff={price_diff}")
                    
                    return subscription, order
                else:
                    # 无需补差价或差价小于等于0
                    logger.info(f"更换订阅计划: subscription_id={subscription.id}, old_plan={old_plan.name}, new_plan={new_plan.name}, no_payment_needed")
                    
                    return subscription, None
                    
        except Exception as e:
            logger.error(f"更换订阅计划失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def check_expired_subscriptions():
        """
        检查过期的订阅
        
        将过期但状态不是已过期的订阅标记为已过期
        """
        try:
            # 查找已过期但状态不是已过期的订阅
            now = timezone.now()
            expired_subscriptions = Subscription.objects.filter(
                end_date__lt=now,
                status__in=[
                    Subscription.STATUS_ACTIVE, 
                    Subscription.STATUS_TRIAL, 
                    Subscription.STATUS_PAST_DUE
                ]
            )
            
            count = 0
            for subscription in expired_subscriptions:
                subscription.status = Subscription.STATUS_EXPIRED
                subscription.save()
                count += 1
                
            if count > 0:
                logger.info(f"标记过期订阅: count={count}")
                
            return count
            
        except Exception as e:
            logger.error(f"检查过期订阅失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def get_user_subscriptions(user, active_only=False):
        """
        获取用户的订阅
        
        Args:
            user: 用户对象
            active_only: 是否只返回活跃的订阅
            
        Returns:
            QuerySet: 订阅查询集
        """
        subscriptions = Subscription.objects.filter(user=user)
        
        if active_only:
            subscriptions = subscriptions.filter(
                status__in=[Subscription.STATUS_ACTIVE, Subscription.STATUS_TRIAL],
                end_date__gt=timezone.now()
            )
            
        return subscriptions.order_by('-created_at') 