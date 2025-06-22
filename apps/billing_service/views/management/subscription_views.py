"""
订阅管理API视图
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAdminUser

from apps.billing_service.models import Subscription, SubscriptionPlan
from apps.billing_service.serializers import (
    SubscriptionSerializer, SubscriptionDetailSerializer, SubscriptionPlanSerializer
)
from apps.billing_service.services.subscription_service import SubscriptionService
from core.mixins import ResponseMixin

logger = logging.getLogger('billing_service')


class SubscriptionPlanManagementViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    订阅计划管理视图集
    
    提供订阅计划的管理功能
    """
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """获取所有订阅计划，包括非公开和非激活的"""
        return SubscriptionPlan.objects.filter(tenant=self.request.tenant).order_by('sort_order', 'name')
    
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
    
    def create(self, request, *args, **kwargs):
        """创建订阅计划"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 设置租户
        serializer.validated_data['tenant'] = request.tenant
        
        self.perform_create(serializer)
        
        return self.get_success_response(
            serializer.data,
            _("订阅计划创建成功"),
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """更新订阅计划"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return self.get_success_response(
            serializer.data,
            _("订阅计划更新成功")
        )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        激活订阅计划
        """
        plan = self.get_object()
        plan.is_active = True
        plan.save()
        
        return self.get_success_response({
            'plan': SubscriptionPlanSerializer(plan).data
        }, _("订阅计划已激活"))
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        停用订阅计划
        """
        plan = self.get_object()
        plan.is_active = False
        plan.save()
        
        return self.get_success_response({
            'plan': SubscriptionPlanSerializer(plan).data
        }, _("订阅计划已停用"))


class SubscriptionManagementViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    订阅管理视图集
    
    提供订阅的管理功能
    """
    serializer_class = SubscriptionDetailSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """获取所有订阅，支持筛选"""
        queryset = Subscription.objects.filter(tenant=self.request.tenant)
        
        # 按用户筛选
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # 按计划筛选
        plan_id = self.request.query_params.get('plan_id')
        if plan_id:
            queryset = queryset.filter(plan_id=plan_id)
            
        # 按状态筛选
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # 按计费周期筛选
        billing_cycle = self.request.query_params.get('billing_cycle')
        if billing_cycle:
            queryset = queryset.filter(billing_cycle=billing_cycle)
            
        # 按是否自动续订筛选
        auto_renew = self.request.query_params.get('auto_renew')
        if auto_renew is not None:
            auto_renew = auto_renew.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(auto_renew=auto_renew)
            
        # 按过期日期范围筛选
        min_end_date = self.request.query_params.get('min_end_date')
        if min_end_date:
            queryset = queryset.filter(end_date__gte=min_end_date)
            
        max_end_date = self.request.query_params.get('max_end_date')
        if max_end_date:
            queryset = queryset.filter(end_date__lte=max_end_date)
        
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
        取消订阅
        """
        subscription = self.get_object()
        
        # 获取参数
        at_period_end = request.data.get('at_period_end', True)
        reason = request.data.get('reason')
        
        try:
            # 取消订阅
            subscription = SubscriptionService.cancel_subscription(
                subscription=subscription,
                at_period_end=at_period_end,
                reason=reason
            )
            
            return self.get_success_response({
                'subscription': SubscriptionDetailSerializer(subscription).data
            }, _("订阅已取消"))
            
        except Exception as e:
            logger.error(f"取消订阅失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("取消订阅失败: ") + str(e))
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """
        手动续订订阅
        """
        subscription = self.get_object()
        
        try:
            # 续订订阅
            subscription, order = SubscriptionService.renew_subscription(
                subscription=subscription
            )
            
            if order:
                return self.get_success_response({
                    'subscription': SubscriptionDetailSerializer(subscription).data,
                    'order': {
                        'id': order.id,
                        'order_number': order.order_number,
                        'amount': order.amount
                    }
                }, _("订阅续订成功，已创建订单"))
            else:
                return self.get_success_response({
                    'subscription': SubscriptionDetailSerializer(subscription).data
                }, _("订阅续订成功"))
                
        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception as e:
            logger.error(f"续订订阅失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("续订订阅失败: ") + str(e))
    
    @action(detail=False, methods=['post'])
    def check_expired(self, request):
        """
        检查并处理过期的订阅
        """
        try:
            # 检查过期的订阅
            count = SubscriptionService.check_expired_subscriptions()
            
            return self.get_success_response({
                'count': count
            }, _("成功处理 {0} 个过期订阅").format(count))
            
        except Exception as e:
            logger.error(f"检查过期订阅失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("检查过期订阅失败: ") + str(e)) 