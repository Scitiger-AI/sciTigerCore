"""
发票序列化器
"""

from rest_framework import serializers
from apps.billing_service.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    """
    发票序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    invoice_type_display = serializers.CharField(source='get_invoice_type_display', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'order', 'order_number', 'invoice_type', 
            'invoice_type_display', 'status', 'status_display', 'amount', 
            'tax_amount', 'total_amount', 'currency', 'title', 'issue_date', 
            'due_date', 'paid_date', 'created_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'order', 'order_number', 'status', 
            'status_display', 'issue_date', 'paid_date', 'created_at'
        ]


class InvoiceDetailSerializer(InvoiceSerializer):
    """
    发票详细信息序列化器
    """
    class Meta(InvoiceSerializer.Meta):
        fields = InvoiceSerializer.Meta.fields + [
            'tax_number', 'address', 'phone', 'bank_name', 'bank_account', 
            'items', 'notes', 'terms', 'pdf_url', 'download_url', 'metadata',
            'updated_at'
        ]
        read_only_fields = InvoiceSerializer.Meta.read_only_fields + [
            'pdf_url', 'download_url', 'updated_at'
        ] 