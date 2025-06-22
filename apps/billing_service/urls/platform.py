"""
支付订单服务平台 API URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.billing_service.views.platform import (
    OrderViewSet, 
    PaymentViewSet, 
    SubscriptionViewSet, 
    SubscriptionPlanViewSet, 
    PointsViewSet, 
    InvoiceViewSet
)

# 创建路由器
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='platform-order')
router.register(r'payments', PaymentViewSet, basename='platform-payment')
router.register(r'subscriptions', SubscriptionViewSet, basename='platform-subscription')
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='platform-subscription-plan')
router.register(r'points', PointsViewSet, basename='platform-points')
router.register(r'invoices', InvoiceViewSet, basename='platform-invoice')

# URL 模式
urlpatterns = [
    # 支付回调特殊URL
    path('payments/alipay-notify/', PaymentViewSet.as_view({'post': 'alipay_notify'}), name='alipay-notify'),
    path('payments/wechat-notify/', PaymentViewSet.as_view({'post': 'wechat_notify'}), name='wechat-notify'),
    
    # 注册路由器URL
    path('', include(router.urls)),
]
