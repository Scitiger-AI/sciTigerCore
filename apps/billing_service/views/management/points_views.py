"""
积分管理API视图
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAdminUser

from apps.billing_service.models import UserPoints, PointsTransaction
from apps.billing_service.serializers import UserPointsSerializer, PointsTransactionSerializer
from apps.billing_service.services.points_service import PointsService
from apps.auth_service.models import User
from core.mixins import ResponseMixin

logger = logging.getLogger('billing_service')


class PointsManagementViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    积分管理视图集
    
    提供积分账户和交易记录的管理功能
    """
    serializer_class = UserPointsSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """获取所有用户积分账户，支持筛选"""
        queryset = UserPoints.objects.filter(tenant=self.request.tenant)
        
        # 按用户筛选
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # 按余额范围筛选
        min_balance = self.request.query_params.get('min_balance')
        if min_balance:
            queryset = queryset.filter(balance__gte=min_balance)
            
        max_balance = self.request.query_params.get('max_balance')
        if max_balance:
            queryset = queryset.filter(balance__lte=max_balance)
            
        # 按是否激活筛选
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-updated_at')
    
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
    def adjust_points(self, request, pk=None):
        """
        调整用户积分
        """
        user_points = self.get_object()
        
        # 获取参数
        points_change = request.data.get('points_change')
        reason = request.data.get('reason')
        
        # 验证参数
        if points_change is None:
            return self.get_error_response(_("请指定积分变动量"))
            
        try:
            points_change = int(points_change)
        except ValueError:
            return self.get_error_response(_("积分变动量必须是整数"))
            
        if points_change == 0:
            return self.get_error_response(_("积分变动量不能为0"))
            
        if not reason:
            return self.get_error_response(_("请提供调整原因"))
            
        try:
            # 调整积分
            user_points, transaction = PointsService.adjust_points(
                tenant=self.request.tenant,
                user=user_points.user,
                points_change=points_change,
                reason=reason,
                created_by=request.user
            )
            
            if transaction:
                return self.get_success_response({
                    'points': UserPointsSerializer(user_points).data,
                    'transaction': PointsTransactionSerializer(transaction).data
                }, _("积分调整成功"))
            else:
                return self.get_success_response({
                    'points': UserPointsSerializer(user_points).data
                }, _("积分无变化"))
                
        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception as e:
            logger.error(f"调整积分失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("调整积分失败: ") + str(e))
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        启用或停用积分账户
        """
        user_points = self.get_object()
        
        user_points.is_active = not user_points.is_active
        user_points.save()
        
        status_text = _("启用") if user_points.is_active else _("停用")
        
        return self.get_success_response({
            'points': UserPointsSerializer(user_points).data
        }, _(f"积分账户已{status_text}"))
    
    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """
        获取积分交易记录，支持筛选
        """
        # 构建查询条件
        filters = {'tenant': self.request.tenant}
        
        # 按用户筛选
        user_id = self.request.query_params.get('user_id')
        if user_id:
            filters['user_id'] = user_id
            
        # 按交易类型筛选
        transaction_type = self.request.query_params.get('transaction_type')
        if transaction_type:
            filters['transaction_type'] = transaction_type
            
        # 按来源筛选
        source = self.request.query_params.get('source')
        if source:
            filters['source'] = source
            
        # 按积分范围筛选
        min_points = self.request.query_params.get('min_points')
        if min_points:
            filters['points__gte'] = min_points
            
        max_points = self.request.query_params.get('max_points')
        if max_points:
            filters['points__lte'] = max_points
            
        # 按日期范围筛选
        start_date = self.request.query_params.get('start_date')
        if start_date:
            filters['created_at__gte'] = start_date
            
        end_date = self.request.query_params.get('end_date')
        if end_date:
            filters['created_at__lte'] = end_date
        
        # 获取交易记录
        transactions = PointsTransaction.objects.filter(**filters).order_by('-created_at')
        
        # 分页
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = PointsTransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = PointsTransactionSerializer(transactions, many=True)
        return self.get_success_response(serializer.data) 