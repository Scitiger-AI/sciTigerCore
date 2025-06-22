"""
积分服务
实现积分相关的业务逻辑
"""

import logging
from django.utils import timezone
from django.db import transaction

from apps.billing_service.models import UserPoints, PointsTransaction, Order
from apps.billing_service.services.payment_service import PaymentService

logger = logging.getLogger('billing_service')


class PointsService:
    """
    积分服务类
    
    提供积分相关的业务逻辑
    """
    
    @staticmethod
    def get_user_points(tenant, user):
        """
        获取用户积分账户
        
        Args:
            tenant: 租户对象
            user: 用户对象
            
        Returns:
            UserPoints: 用户积分账户对象
        """
        try:
            # 获取或创建用户积分账户
            user_points, created = UserPoints.objects.get_or_create(
                tenant=tenant,
                user=user,
                defaults={'balance': 0, 'total_earned': 0, 'total_spent': 0}
            )
            
            if created:
                logger.info(f"创建用户积分账户: user_id={user.id}")
                
            return user_points
            
        except Exception as e:
            logger.error(f"获取用户积分账户失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def add_points(tenant, user, points, reason=None, source=None, transaction_type=None, created_by=None):
        """
        为用户添加积分
        
        Args:
            tenant: 租户对象
            user: 用户对象
            points: 积分数量（正整数）
            reason: 添加原因
            source: 积分来源
            transaction_type: 交易类型
            created_by: 创建者
            
        Returns:
            tuple: (UserPoints, PointsTransaction)，用户积分账户对象和积分交易记录对象
        """
        try:
            if points <= 0:
                raise ValueError("添加的积分必须为正数")
                
            with transaction.atomic():
                # 获取或创建用户积分账户
                user_points = PointsService.get_user_points(tenant, user)
                
                # 添加积分
                transaction = user_points.add_points(
                    points=points,
                    reason=reason,
                    source=source,
                    transaction_type=transaction_type or PointsTransaction.TYPE_EARN
                )
                
                # 设置创建者
                if created_by:
                    transaction.created_by = created_by
                    transaction.save()
                
                logger.info(f"添加积分: user_id={user.id}, points={points}, source={source}, transaction_id={transaction.id}")
                
                return user_points, transaction
                
        except Exception as e:
            logger.error(f"添加积分失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def deduct_points(tenant, user, points, reason=None, source=None, transaction_type=None, created_by=None):
        """
        扣除用户积分
        
        Args:
            tenant: 租户对象
            user: 用户对象
            points: 积分数量（正整数）
            reason: 扣除原因
            source: 积分去向
            transaction_type: 交易类型
            created_by: 创建者
            
        Returns:
            tuple: (UserPoints, PointsTransaction)，用户积分账户对象和积分交易记录对象
            
        Raises:
            ValueError: 积分不足
        """
        try:
            if points <= 0:
                raise ValueError("扣除的积分必须为正数")
                
            with transaction.atomic():
                # 获取用户积分账户
                user_points = PointsService.get_user_points(tenant, user)
                
                # 检查积分是否足够
                if user_points.balance < points:
                    raise ValueError(f"积分余额不足，当前余额: {user_points.balance}, 需要扣除: {points}")
                
                # 扣除积分
                transaction = user_points.deduct_points(
                    points=points,
                    reason=reason,
                    source=source,
                    transaction_type=transaction_type or PointsTransaction.TYPE_SPEND
                )
                
                # 设置创建者
                if created_by:
                    transaction.created_by = created_by
                    transaction.save()
                
                logger.info(f"扣除积分: user_id={user.id}, points={points}, source={source}, transaction_id={transaction.id}")
                
                return user_points, transaction
                
        except ValueError as e:
            logger.warning(f"扣除积分失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"扣除积分失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def create_points_purchase_order(tenant, user, points, amount, discount_amount=0, tax_amount=0, currency='CNY'):
        """
        创建积分购买订单
        
        Args:
            tenant: 租户对象
            user: 用户对象
            points: 积分数量
            amount: 订单金额
            discount_amount: 折扣金额
            tax_amount: 税费
            currency: 货币
            
        Returns:
            Order: 创建的订单对象
        """
        try:
            # 创建订单
            order = PaymentService.create_order(
                tenant=tenant,
                user=user,
                order_type=Order.TYPE_POINTS,
                amount=amount,
                title=f"购买 {points} 积分",
                description=f"购买 {points} 积分",
                points=points,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                currency=currency,
                created_by=user
            )
            
            logger.info(f"创建积分购买订单: user_id={user.id}, points={points}, amount={amount}, order_id={order.id}")
            
            return order
            
        except Exception as e:
            logger.error(f"创建积分购买订单失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def get_user_points_transactions(tenant, user, transaction_type=None, start_date=None, end_date=None):
        """
        获取用户积分交易记录
        
        Args:
            tenant: 租户对象
            user: 用户对象
            transaction_type: 交易类型
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            QuerySet: 积分交易记录查询集
        """
        try:
            # 构建查询条件
            filters = {
                'tenant': tenant,
                'user': user
            }
            
            if transaction_type:
                filters['transaction_type'] = transaction_type
                
            if start_date:
                filters['created_at__gte'] = start_date
                
            if end_date:
                filters['created_at__lte'] = end_date
                
            # 查询交易记录
            transactions = PointsTransaction.objects.filter(**filters).order_by('-created_at')
            
            return transactions
            
        except Exception as e:
            logger.error(f"获取用户积分交易记录失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def adjust_points(tenant, user, points_change, reason, created_by=None):
        """
        调整用户积分（管理员操作）
        
        Args:
            tenant: 租户对象
            user: 用户对象
            points_change: 积分变动（正数为增加，负数为减少）
            reason: 调整原因
            created_by: 创建者
            
        Returns:
            tuple: (UserPoints, PointsTransaction)，用户积分账户对象和积分交易记录对象
        """
        try:
            with transaction.atomic():
                # 获取用户积分账户
                user_points = PointsService.get_user_points(tenant, user)
                
                if points_change > 0:
                    # 增加积分
                    transaction = user_points.add_points(
                        points=points_change,
                        reason=reason,
                        source='admin_adjustment',
                        transaction_type=PointsTransaction.TYPE_ADJUST
                    )
                elif points_change < 0:
                    # 减少积分
                    # 检查积分是否足够
                    if user_points.balance < abs(points_change):
                        raise ValueError(f"积分余额不足，当前余额: {user_points.balance}, 需要扣除: {abs(points_change)}")
                    
                    # 扣除积分
                    transaction = user_points.deduct_points(
                        points=abs(points_change),
                        reason=reason,
                        source='admin_adjustment',
                        transaction_type=PointsTransaction.TYPE_ADJUST
                    )
                else:
                    # 积分变动为0，无需操作
                    return user_points, None
                
                # 设置创建者
                if created_by:
                    transaction.created_by = created_by
                    transaction.save()
                
                logger.info(f"调整积分: user_id={user.id}, points_change={points_change}, reason={reason}, transaction_id={transaction.id}")
                
                return user_points, transaction
                
        except ValueError as e:
            logger.warning(f"调整积分失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"调整积分失败: {str(e)}", exc_info=True)
            raise 