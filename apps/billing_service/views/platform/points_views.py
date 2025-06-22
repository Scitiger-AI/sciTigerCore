"""
积分平台API视图
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticated

from apps.billing_service.models import UserPoints, PointsTransaction
from apps.billing_service.serializers import UserPointsSerializer, PointsTransactionSerializer
from apps.billing_service.services.points_service import PointsService
from core.mixins import ResponseMixin

logger = logging.getLogger('billing_service')


class PointsViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    积分视图集
    
    提供积分账户和交易记录的查询和管理功能
    """
    serializer_class = UserPointsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_success_response(self, data=None, message=None, status_code=status.HTTP_200_OK):
        """统一的成功响应格式"""
        return Response({
            'success': True,
            'message': message,
            'results': data
        }, status=status_code)
    
    def get_error_response(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        """统一的错误响应格式"""
        return Response({
            'success': False,
            'message': message
        }, status=status_code)
    
    def retrieve(self, request, *args, **kwargs):
        """
        获取用户积分账户
        """
        try:
            user_points = PointsService.get_user_points(
                tenant=request.tenant,
                user=request.user
            )
            
            serializer = UserPointsSerializer(user_points)
            return self.get_success_response(serializer.data)
            
        except Exception as e:
            logger.error(f"获取用户积分账户失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("获取积分账户失败: ") + str(e))
    
    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """
        获取用户积分交易记录
        """
        try:
            # 获取查询参数
            transaction_type = request.query_params.get('transaction_type')
            
            # 获取交易记录
            transactions = PointsService.get_user_points_transactions(
                tenant=request.tenant,
                user=request.user,
                transaction_type=transaction_type
            )
            
            # 分页
            page = self.paginate_queryset(transactions)
            if page is not None:
                serializer = PointsTransactionSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
                
            serializer = PointsTransactionSerializer(transactions, many=True)
            return self.get_success_response(serializer.data)
            
        except Exception as e:
            logger.error(f"获取用户积分交易记录失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("获取积分交易记录失败: ") + str(e))
    
    @action(detail=False, methods=['post'])
    def purchase(self, request):
        """
        购买积分
        """
        # 获取参数
        points = request.data.get('points')
        amount = request.data.get('amount')
        
        # 验证参数
        if not points or not amount:
            return self.get_error_response(_("请指定积分数量和金额"))
            
        try:
            # 创建积分购买订单
            order = PointsService.create_points_purchase_order(
                tenant=request.tenant,
                user=request.user,
                points=int(points),
                amount=float(amount),
                discount_amount=float(request.data.get('discount_amount', 0)),
                tax_amount=float(request.data.get('tax_amount', 0)),
                currency=request.data.get('currency', 'CNY')
            )
            
            return self.get_success_response({
                'order': {
                    'id': order.id,
                    'order_number': order.order_number,
                    'amount': order.amount,
                    'points': order.points,
                    'currency': order.currency,
                }
            }, _("积分购买订单创建成功，请完成支付"))
            
        except Exception as e:
            logger.error(f"创建积分购买订单失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("创建积分购买订单失败: ") + str(e))
    
    @action(detail=False, methods=['post'])
    def use_points(self, request):
        """
        使用积分
        """
        # 获取参数
        points = request.data.get('points')
        reason = request.data.get('reason')
        source = request.data.get('source', 'user_consumption')
        
        # 验证参数
        if not points:
            return self.get_error_response(_("请指定积分数量"))
            
        if not reason:
            return self.get_error_response(_("请提供使用原因"))
            
        try:
            # 扣除积分
            user_points, transaction = PointsService.deduct_points(
                tenant=request.tenant,
                user=request.user,
                points=int(points),
                reason=reason,
                source=source,
                created_by=request.user
            )
            
            return self.get_success_response({
                'points': {
                    'balance': user_points.balance,
                    'total_spent': user_points.total_spent
                },
                'transaction': PointsTransactionSerializer(transaction).data
            }, _("积分使用成功"))
            
        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception as e:
            logger.error(f"使用积分失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("使用积分失败: ") + str(e)) 