"""
发票管理API视图
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAdminUser

from apps.billing_service.models import Invoice
from apps.billing_service.serializers import InvoiceSerializer, InvoiceDetailSerializer
from apps.billing_service.services.invoice_service import InvoiceService
from core.mixins import ResponseMixin

logger = logging.getLogger('billing_service')


class InvoiceManagementViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    发票管理视图集
    
    提供发票的管理功能
    """
    serializer_class = InvoiceDetailSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """获取所有发票，支持筛选"""
        queryset = Invoice.objects.filter(tenant=self.request.tenant)
        
        # 按用户筛选
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # 按订单筛选
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
            
        # 按发票状态筛选
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # 按发票类型筛选
        invoice_type = self.request.query_params.get('invoice_type')
        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)
            
        # 按发票号搜索
        invoice_number = self.request.query_params.get('invoice_number')
        if invoice_number:
            queryset = queryset.filter(invoice_number__icontains=invoice_number)
            
        # 按发票抬头搜索
        title = self.request.query_params.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)
            
        # 按金额范围筛选
        min_amount = self.request.query_params.get('min_amount')
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
            
        max_amount = self.request.query_params.get('max_amount')
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
            
        # 按开具日期范围筛选
        start_issue_date = self.request.query_params.get('start_issue_date')
        if start_issue_date:
            queryset = queryset.filter(issue_date__gte=start_issue_date)
            
        end_issue_date = self.request.query_params.get('end_issue_date')
        if end_issue_date:
            queryset = queryset.filter(issue_date__lte=end_issue_date)
        
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
    def issue(self, request, pk=None):
        """
        开具发票
        """
        invoice = self.get_object()
        
        try:
            # 开具发票
            invoice = InvoiceService.issue_invoice(invoice)
            
            return self.get_success_response({
                'invoice': InvoiceDetailSerializer(invoice).data
            }, _("发票已开具"))
            
        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception as e:
            logger.error(f"开具发票失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("开具发票失败: ") + str(e))
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """
        将发票标记为已支付
        """
        invoice = self.get_object()
        
        try:
            # 标记为已支付
            invoice = InvoiceService.mark_invoice_as_paid(invoice)
            
            return self.get_success_response({
                'invoice': InvoiceDetailSerializer(invoice).data
            }, _("发票已标记为已支付"))
            
        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception as e:
            logger.error(f"标记发票为已支付失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("标记发票为已支付失败: ") + str(e))
    
    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        """
        作废发票
        """
        invoice = self.get_object()
        
        # 获取作废原因
        reason = request.data.get('reason')
        
        if not reason:
            return self.get_error_response(_("请提供作废原因"))
            
        try:
            # 作废发票
            invoice = InvoiceService.void_invoice(invoice, reason)
            
            return self.get_success_response({
                'invoice': InvoiceDetailSerializer(invoice).data
            }, _("发票已作废"))
            
        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception as e:
            logger.error(f"作废发票失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("作废发票失败: ") + str(e))
    
    @action(detail=True, methods=['post'])
    def update_pdf(self, request, pk=None):
        """
        更新发票PDF链接
        """
        invoice = self.get_object()
        
        # 获取PDF链接
        pdf_url = request.data.get('pdf_url')
        download_url = request.data.get('download_url')
        
        if not pdf_url and not download_url:
            return self.get_error_response(_("请提供PDF链接或下载链接"))
            
        try:
            # 更新PDF链接
            if pdf_url:
                invoice.pdf_url = pdf_url
                
            if download_url:
                invoice.download_url = download_url
                
            invoice.save()
            
            return self.get_success_response({
                'invoice': InvoiceDetailSerializer(invoice).data
            }, _("发票PDF链接已更新"))
            
        except Exception as e:
            logger.error(f"更新发票PDF链接失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("更新发票PDF链接失败: ") + str(e)) 