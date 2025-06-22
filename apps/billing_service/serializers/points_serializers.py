"""
积分序列化器
"""

from rest_framework import serializers
from apps.billing_service.models import UserPoints, PointsTransaction


class UserPointsSerializer(serializers.ModelSerializer):
    """
    用户积分账户序列化器
    """
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserPoints
        fields = [
            'id', 'user', 'username', 'balance', 'total_earned', 
            'total_spent', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'username', 'balance', 'total_earned', 
                           'total_spent', 'created_at', 'updated_at']


class PointsTransactionSerializer(serializers.ModelSerializer):
    """
    积分交易记录序列化器
    """
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PointsTransaction
        fields = [
            'id', 'user', 'username', 'points', 'balance_after', 
            'transaction_type', 'transaction_type_display', 'source',
            'description', 'order', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'username', 'points', 'balance_after',
                           'transaction_type', 'transaction_type_display', 'created_at'] 