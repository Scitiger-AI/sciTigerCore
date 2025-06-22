"""
账单服务平台API视图包
"""

from apps.billing_service.views.platform.order_views import OrderViewSet
from apps.billing_service.views.platform.payment_views import PaymentViewSet
from apps.billing_service.views.platform.subscription_views import SubscriptionViewSet, SubscriptionPlanViewSet
from apps.billing_service.views.platform.points_views import PointsViewSet
from apps.billing_service.views.platform.invoice_views import InvoiceViewSet

__all__ = [
    'OrderViewSet',
    'PaymentViewSet',
    'SubscriptionViewSet',
    'SubscriptionPlanViewSet',
    'PointsViewSet',
    'InvoiceViewSet',
]
