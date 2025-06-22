"""
订单序列化器
"""

from rest_framework import serializers
from apps.billing_service.models import Order, Payment


class OrderSerializer(serializers.ModelSerializer):
    """
    订单序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_type', 'order_type_display', 'status', 'status_display',
            'title', 'description', 'amount', 'discount_amount', 'tax_amount', 'total_amount',
            'points', 'currency', 'payment_method', 'payment_url', 'transaction_id',
            'paid_at', 'expires_at', 'is_expired', 'created_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'status', 'payment_url', 'transaction_id',
            'paid_at', 'expires_at', 'created_at'
        ]


class OrderDetailSerializer(OrderSerializer):
    """
    订单详细信息序列化器
    """
    payments = serializers.SerializerMethodField()
    
    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + [
            'refunded_amount', 'refunded_at', 'payments', 'ip_address',
            'user_agent', 'notes', 'updated_at'
        ]
        read_only_fields = OrderSerializer.Meta.read_only_fields + [
            'refunded_amount', 'refunded_at', 'payments', 'updated_at'
        ]
    
    def get_payments(self, obj):
        """获取订单相关的支付记录"""
        from apps.billing_service.serializers.payment_serializers import PaymentSerializer
        payments = obj.payments.all().order_by('-created_at')
        return PaymentSerializer(payments, many=True).data 