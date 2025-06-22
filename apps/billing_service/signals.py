"""
账单服务信号处理器
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from apps.billing_service.models import Order, Payment, Subscription

logger = logging.getLogger('billing_service')


@receiver(post_save, sender=Payment)
def handle_payment_success(sender, instance, created, **kwargs):
    """
    处理支付成功事件
    
    当支付记录状态变为成功时，更新相关订单状态并触发后续操作
    """
    if not created and instance.status == Payment.STATUS_SUCCESS:
        logger.info(f"支付成功处理: payment_id={instance.id}, order_id={instance.order_id if instance.order else None}")
        
        # 订单状态已在 Payment.mark_as_success 方法中更新
        
        # 如果是订阅订单，处理订阅相关逻辑
        if instance.order and instance.order.order_type == Order.TYPE_SUBSCRIPTION:
            try:
                # 获取订阅ID
                subscription_id = instance.order.callback_data.get('subscription_id')
                if subscription_id:
                    subscription = Subscription.objects.get(id=subscription_id)
                    
                    # 如果是新订阅的首次支付
                    if subscription.status == Subscription.STATUS_UNPAID:
                        subscription.status = Subscription.STATUS_ACTIVE
                        subscription.save()
                        logger.info(f"激活订阅: subscription_id={subscription.id}")
                    
                    # 如果是续订支付
                    elif subscription.status in [Subscription.STATUS_ACTIVE, Subscription.STATUS_PAST_DUE]:
                        # 更新订阅周期
                        subscription.renew()
                        logger.info(f"续订订阅: subscription_id={subscription.id}")
                        
            except Subscription.DoesNotExist:
                logger.error(f"找不到订阅: subscription_id={subscription_id}")
            except Exception as e:
                logger.error(f"处理订阅支付时出错: {str(e)}", exc_info=True)
                
        # 如果是积分订单，处理积分发放
        elif instance.order and instance.order.order_type == Order.TYPE_POINTS:
            from apps.billing_service.models import UserPoints
            
            try:
                # 获取或创建用户积分账户
                user_points, created = UserPoints.objects.get_or_create(
                    tenant=instance.order.tenant,
                    user=instance.order.user,
                    defaults={'balance': 0, 'total_earned': 0, 'total_spent': 0}
                )
                
                # 添加积分
                points_to_add = instance.order.points
                if points_to_add > 0:
                    user_points.add_points(
                        points=points_to_add,
                        reason=f"购买积分 (订单: {instance.order.order_number})",
                        source="points_purchase",
                        transaction_type="purchase"
                    )
                    logger.info(f"积分购买成功: user_id={instance.order.user.id}, points={points_to_add}")
                    
            except Exception as e:
                logger.error(f"处理积分购买时出错: {str(e)}", exc_info=True)


@receiver(pre_save, sender=Subscription)
def handle_subscription_status_change(sender, instance, **kwargs):
    """
    处理订阅状态变更
    
    当订阅状态变更时，执行相应的操作
    """
    if not instance.pk:
        # 新创建的订阅，无需处理
        return
        
    try:
        # 获取订阅的原始状态
        old_instance = Subscription.objects.get(pk=instance.pk)
        old_status = old_instance.status
        
        # 如果状态发生变化
        if old_status != instance.status:
            logger.info(f"订阅状态变更: subscription_id={instance.id}, old_status={old_status}, new_status={instance.status}")
            
            # 如果状态变为已取消
            if instance.status == Subscription.STATUS_CANCELED and old_status != Subscription.STATUS_CANCELED:
                # 记录取消时间
                if not instance.canceled_at:
                    instance.canceled_at = timezone.now()
                    
            # 如果状态变为已过期
            elif instance.status == Subscription.STATUS_EXPIRED and old_status != Subscription.STATUS_EXPIRED:
                # 可以在这里执行一些清理操作
                pass
                
    except Subscription.DoesNotExist:
        # 订阅不存在，可能是新创建的
        pass
    except Exception as e:
        logger.error(f"处理订阅状态变更时出错: {str(e)}", exc_info=True)


@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):
    """
    处理订单状态变更
    
    当订单状态变更时，执行相应的操作
    """
    if created:
        # 新创建的订单，记录日志
        logger.info(f"新订单创建: order_id={instance.id}, order_number={instance.order_number}, type={instance.order_type}")
        return
        
    # 订单状态变更的处理逻辑可以在这里添加 