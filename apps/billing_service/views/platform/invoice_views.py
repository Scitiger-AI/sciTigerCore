"""
发票平台API视图
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticated

from apps.billing_service.models import Invoice, Order
from apps.billing_service.serializers import InvoiceSerializer, InvoiceDetailSerializer
from apps.billing_service.services.invoice_service import InvoiceService
from core.mixins import ResponseMixin

logger = logging.getLogger('billing_service')


class InvoiceViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    发票视图集
    
    提供发票的查询和管理功能
    """
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的发票列表"""
        return Invoice.objects.filter(
            tenant=self.request.tenant,
            user=self.request.user
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action == 'retrieve':
            return InvoiceDetailSerializer
        return InvoiceSerializer
    
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
    
    @action(detail=False, methods=['post'])
    def request_invoice(self, request):
        """
        申请开具发票
        """
        # 获取参数
        order_id = request.data.get('order_id')
        invoice_type = request.data.get('invoice_type', Invoice.TYPE_REGULAR)
        title = request.data.get('title')
        tax_number = request.data.get('tax_number')
        address = request.data.get('address')
        phone = request.data.get('phone')
        bank_name = request.data.get('bank_name')
        bank_account = request.data.get('bank_account')
        notes = request.data.get('notes')
        
        # 验证参数
        if not order_id:
            return self.get_error_response(_("请指定订单ID"))
            
        if not title:
            return self.get_error_response(_("请提供发票抬头"))
            
        try:
            # 获取订单
            order = Order.objects.get(id=order_id, tenant=request.tenant, user=request.user)
            
            # 检查订单状态
            if order.status != Order.STATUS_PAID:
                return self.get_error_response(_("只有已支付的订单才能开具发票"))
                
            # 创建发票
            invoice = InvoiceService.create_invoice_from_order(
                order=order,
                invoice_type=invoice_type,
                title=title,
                tax_number=tax_number,
                address=address,
                phone=phone,
                bank_name=bank_name,
                bank_account=bank_account,
                notes=notes,
                created_by=request.user
            )
            
            return self.get_success_response({
                'invoice': InvoiceDetailSerializer(invoice).data
            }, _("发票申请成功，我们将尽快处理"))
            
        except Order.DoesNotExist:
            return self.get_error_response(_("找不到指定的订单"))
        except Exception as e:
            logger.error(f"申请开具发票失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("申请开具发票失败: ") + str(e))
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        下载发票
        """
        invoice = self.get_object()
        
        # 检查发票状态
        if invoice.status not in [Invoice.STATUS_ISSUED, Invoice.STATUS_PAID]:
            return self.get_error_response(_("只有已开具或已支付的发票才能下载"))
            
        # 检查是否有下载链接
        if not invoice.download_url:
            return self.get_error_response(_("发票尚未生成，请稍后再试"))
            
        return self.get_success_response({
            'download_url': invoice.download_url
        }) 