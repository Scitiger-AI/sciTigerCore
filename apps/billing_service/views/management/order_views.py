"""
订单管理API视图
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAdminUser

from apps.billing_service.models import Order, Payment
from apps.billing_service.serializers import OrderSerializer, OrderDetailSerializer
from apps.billing_service.services.payment_service import PaymentService
from core.mixins import ResponseMixin

logger = logging.getLogger('billing_service')


class OrderManagementViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    订单管理视图集
    
    提供订单的管理功能
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """获取所有订单，支持筛选"""
        queryset = Order.objects.filter(tenant=self.request.tenant)
        
        # 按用户筛选
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # 按订单状态筛选
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # 按订单类型筛选
        order_type = self.request.query_params.get('order_type')
        if order_type:
            queryset = queryset.filter(order_type=order_type)
            
        # 按订单号搜索
        order_number = self.request.query_params.get('order_number')
        if order_number:
            queryset = queryset.filter(order_number__icontains=order_number)
            
        # 按金额范围筛选
        min_amount = self.request.query_params.get('min_amount')
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
            
        max_amount = self.request.query_params.get('max_amount')
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
            
        # 按创建时间范围筛选
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
            
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')
    
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
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        取消订单
        """
        order = self.get_object()
        
        # 检查订单状态
        if order.status != Order.STATUS_PENDING:
            return self.get_error_response(_("只有待支付状态的订单才能取消"))
            
        # 获取取消原因
        reason = request.data.get('reason')
        
        try:
            # 取消订单
            order.cancel(reason=reason)
            
            return self.get_success_response({
                'order': OrderDetailSerializer(order).data
            }, _("订单已取消"))
            
        except Exception as e:
            logger.error(f"取消订单失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("取消订单失败: ") + str(e))
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """
        退款
        """
        order = self.get_object()
        
        # 检查订单状态
        if order.status != Order.STATUS_PAID:
            return self.get_error_response(_("只有已支付状态的订单才能退款"))
            
        # 获取退款金额和原因
        amount = request.data.get('amount')
        reason = request.data.get('reason')
        
        if amount:
            try:
                amount = float(amount)
            except ValueError:
                return self.get_error_response(_("无效的退款金额"))
        
        try:
            # 退款
            order.refund(amount=amount, reason=reason)
            
            return self.get_success_response({
                'order': OrderDetailSerializer(order).data
            }, _("退款成功"))
            
        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception as e:
            logger.error(f"退款失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("退款失败: ") + str(e)) 