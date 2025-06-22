"""
支付序列化器
"""

from rest_framework import serializers
from apps.billing_service.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    支付记录序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'payment_method', 'payment_method_display', 
            'payment_gateway', 'amount', 'currency', 'status', 'status_display',
            'transaction_id', 'payment_url', 'paid_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'order', 'order_number', 'payment_url', 'transaction_id',
            'status', 'paid_at', 'created_at'
        ]


class PaymentDetailSerializer(PaymentSerializer):
    """
    支付记录详细信息序列化器
    """
    class Meta(PaymentSerializer.Meta):
        fields = PaymentSerializer.Meta.fields + [
            'callback_url', 'return_url', 'notify_url', 'error_message',
            'refunded_amount', 'refunded_at', 'ip_address', 'user_agent',
            'notes', 'updated_at'
        ]
        read_only_fields = PaymentSerializer.Meta.read_only_fields + [
            'callback_url', 'return_url', 'notify_url', 'refunded_amount', 
            'refunded_at', 'updated_at'
        ] 