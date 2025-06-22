"""
订单平台API视图
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.billing_service.models import Order, Payment
from apps.billing_service.serializers import OrderSerializer, OrderDetailSerializer
from apps.billing_service.services.payment_service import PaymentService
from core.mixins import ResponseMixin

logger = logging.getLogger('billing_service')


class OrderViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    订单视图集
    
    提供订单的查询和管理功能
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的订单列表"""
        return Order.objects.filter(
            tenant=self.request.tenant,
            user=self.request.user
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer
    
    @action(detail=True, methods=['post'])
    def create_payment(self, request, pk=None):
        """
        为订单创建支付
        """
        order = self.get_object()
        
        # 检查订单状态
        if order.status != Order.STATUS_PENDING:
            return self.get_error_response(_("只有待支付状态的订单才能创建支付"))
            
        # 获取支付方式
        payment_method = request.data.get('payment_method')
        if not payment_method:
            return self.get_error_response(_("请指定支付方式"))
            
        # 检查支付方式是否支持
        if payment_method not in [Payment.METHOD_ALIPAY, Payment.METHOD_WECHAT]:
            return self.get_error_response(_("不支持的支付方式"))
            
        try:
            # 创建支付
            payment, payment_url = PaymentService.create_payment(
                order=order,
                payment_method=payment_method,
                payment_gateway=request.data.get('payment_gateway'),
                return_url=request.data.get('return_url'),
                notify_url=request.data.get('notify_url'),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            return self.get_success_response({
                'payment_id': payment.id,
                'payment_url': payment_url
            }, _("支付创建成功"))
            
        except Exception as e:
            logger.error(f"创建支付失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("创建支付失败: ") + str(e))
    
    @action(detail=True, methods=['get'])
    def payment_status(self, request, pk=None):
        """
        查询订单支付状态
        """
        order = self.get_object()
        
        # 查找最新的支付记录
        try:
            payment = Payment.objects.filter(order=order).latest('created_at')
        except Payment.DoesNotExist:
            return self.get_error_response(_("找不到支付记录"))
            
        # 查询支付状态
        result = PaymentService.query_payment_status(payment)
        
        return self.get_success_response({
            'order_status': order.status,
            'payment_status': payment.status,
            'result': result
        }) 