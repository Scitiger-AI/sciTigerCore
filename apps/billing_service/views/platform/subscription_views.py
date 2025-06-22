"""
订阅平台API视图
"""

import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticated

from apps.billing_service.models import Subscription, SubscriptionPlan
from apps.billing_service.serializers import (
    SubscriptionSerializer, SubscriptionDetailSerializer, SubscriptionPlanSerializer
)
from apps.billing_service.services.subscription_service import SubscriptionService
from core.mixins import ResponseMixin

logger = logging.getLogger('billing_service')


class SubscriptionPlanViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    订阅计划视图集
    
    提供订阅计划的查询功能
    """
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """获取可用的订阅计划列表"""
        return SubscriptionService.get_available_plans(
            tenant=self.request.tenant,
            is_public=True
        )
    
    # 不需要这些方法，因为现在继承了ResponseMixin
    # def get_success_response(self, data=None, message=None, status_code=status.HTTP_200_OK):
    #     """统一的成功响应格式"""
    #     return Response({
    #         'success': True,
    #         'message': message,
    #         'results': data
    #     }, status=status_code)
    
    # def get_error_response(self, message, status_code=status.HTTP_400_BAD_REQUEST):
    #     """统一的错误响应格式"""
    #     return Response({
    #         'success': False,
    #         'message': message
    #     }, status=status_code)


class SubscriptionViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    订阅视图集
    
    提供订阅的查询和管理功能
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的订阅列表"""
        return Subscription.objects.filter(
            tenant=self.request.tenant,
            user=self.request.user
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action == 'retrieve':
            return SubscriptionDetailSerializer
        return SubscriptionSerializer
    
    # 不需要这些方法，因为现在继承了ResponseMixin
    # def get_success_response(self, data=None, message=None, status_code=status.HTTP_200_OK):
    #     """统一的成功响应格式"""
    #     return Response({
    #         'success': True,
    #         'message': message,
    #         'results': data
    #     }, status=status_code)
    
    # def get_error_response(self, message, status_code=status.HTTP_400_BAD_REQUEST):
    #     """统一的错误响应格式"""
    #     return Response({
    #         'success': False,
    #         'message': message
    #     }, status=status_code)
    
    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """
        创建订阅
        """
        # 获取参数
        plan_id = request.data.get('plan_id')
        billing_cycle = request.data.get('billing_cycle', Subscription.BILLING_CYCLE_MONTHLY)
        auto_renew = request.data.get('auto_renew', True)
        
        # 验证参数
        if not plan_id:
            return self.get_error_response(_("请指定订阅计划"))
            
        try:
            # 获取订阅计划
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True, tenant=request.tenant)
            
            # 创建订阅
            subscription, order = SubscriptionService.create_subscription(
                tenant=request.tenant,
                user=request.user,
                plan=plan,
                billing_cycle=billing_cycle,
                auto_renew=auto_renew
            )
            
            # 返回结果
            if order:
                # 需要支付
                return self.get_success_response({
                    'subscription': SubscriptionSerializer(subscription).data,
                    'order': {
                        'id': order.id,
                        'order_number': order.order_number,
                        'amount': order.amount,
                        'currency': order.currency,
                    }
                }, _("订阅创建成功，请完成支付"))
            else:
                # 免费试用
                return self.get_success_response({
                    'subscription': SubscriptionSerializer(subscription).data
                }, _("订阅创建成功"))
                
        except SubscriptionPlan.DoesNotExist:
            return self.get_error_response(_("找不到指定的订阅计划"))
        except Exception as e:
            logger.error(f"创建订阅失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("创建订阅失败: ") + str(e))
    
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
                'subscription': SubscriptionSerializer(subscription).data
            }, _("订阅已取消"))
            
        except Exception as e:
            logger.error(f"取消订阅失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("取消订阅失败: ") + str(e))
    
    @action(detail=True, methods=['post'])
    def change_plan(self, request, pk=None):
        """
        更换订阅计划
        """
        subscription = self.get_object()
        
        # 获取参数
        new_plan_id = request.data.get('new_plan_id')
        prorate = request.data.get('prorate', True)
        
        # 验证参数
        if not new_plan_id:
            return self.get_error_response(_("请指定新的订阅计划"))
            
        try:
            # 获取新的订阅计划
            new_plan = SubscriptionPlan.objects.get(id=new_plan_id, is_active=True, tenant=request.tenant)
            
            # 更换计划
            subscription, order = SubscriptionService.change_plan(
                subscription=subscription,
                new_plan=new_plan,
                prorate=prorate
            )
            
            # 返回结果
            if order:
                # 需要支付差价
                return self.get_success_response({
                    'subscription': SubscriptionSerializer(subscription).data,
                    'order': {
                        'id': order.id,
                        'order_number': order.order_number,
                        'amount': order.amount,
                        'currency': order.currency,
                    }
                }, _("订阅计划更换成功，请完成差价支付"))
            else:
                # 无需支付
                return self.get_success_response({
                    'subscription': SubscriptionSerializer(subscription).data
                }, _("订阅计划更换成功"))
                
        except SubscriptionPlan.DoesNotExist:
            return self.get_error_response(_("找不到指定的订阅计划"))
        except Exception as e:
            logger.error(f"更换订阅计划失败: {str(e)}", exc_info=True)
            return self.get_error_response(_("更换订阅计划失败: ") + str(e)) 