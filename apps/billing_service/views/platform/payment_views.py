"""
支付平台API视图
"""

import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.billing_service.models import Payment
from apps.billing_service.serializers import PaymentSerializer, PaymentDetailSerializer
from apps.billing_service.services.payment_service import PaymentService
from core.mixins import ResponseMixin

logger = logging.getLogger('billing_service')


class PaymentViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    支付视图集
    
    提供支付记录的查询和管理功能
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的支付记录列表"""
        return Payment.objects.filter(
            tenant=self.request.tenant,
            user=self.request.user
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action == 'retrieve':
            return PaymentDetailSerializer
        return PaymentSerializer
    
    @action(detail=True, methods=['get'])
    def query_status(self, request, pk=None):
        """
        查询支付状态
        """
        payment = self.get_object()
        
        # 查询支付状态
        result = PaymentService.query_payment_status(payment)
        
        return self.get_success_response({
            'payment_status': payment.status,
            'result': result
        })
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def alipay_notify(self, request):
        """
        支付宝异步通知
        """
        logger.info(f"收到支付宝回调: {request.data}")
        
        try:
            # 处理支付宝回调
            result = PaymentService.process_alipay_callback(
                post_data=request.data,
                signature=request.data.get('sign')
            )
            
            if result.get('success'):
                return Response("success")  # 支付宝要求返回success字符串
            else:
                logger.error(f"处理支付宝回调失败: {result.get('message')}")
                return Response("fail")
                
        except Exception as e:
            logger.error(f"处理支付宝回调异常: {str(e)}", exc_info=True)
            return Response("fail")
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def wechat_notify(self, request):
        """
        微信支付异步通知
        """
        logger.info(f"收到微信支付回调: {request.data}")
        
        try:
            # 处理微信支付回调
            result = PaymentService.process_wechat_callback(
                post_data=request.data,
                signature=request.data.get('sign')
            )
            
            if result.get('success'):
                return Response({"code": "SUCCESS", "message": "成功"})
            else:
                logger.error(f"处理微信支付回调失败: {result.get('message')}")
                return Response({"code": "FAIL", "message": result.get('message')})
                
        except Exception as e:
            logger.error(f"处理微信支付回调异常: {str(e)}", exc_info=True)
            return Response({"code": "FAIL", "message": str(e)})
    
    @action(detail=True, methods=['get'])
    def return_url(self, request, pk=None):
        """
        支付完成返回
        """
        payment = self.get_object()
        
        # 查询支付状态
        result = PaymentService.query_payment_status(payment)
        
        if payment.status == Payment.STATUS_SUCCESS:
            return self.get_success_response({
                'payment_status': payment.status,
                'order_number': payment.order.order_number if payment.order else None,
                'paid_at': payment.paid_at,
                'amount': payment.amount,
                'currency': payment.currency
            }, _("支付成功"))
        else:
            return self.get_error_response(_("支付未完成或处理中"), status_code=status.HTTP_202_ACCEPTED) 