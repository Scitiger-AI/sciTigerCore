"""
订阅序列化器
"""

from rest_framework import serializers
from apps.billing_service.models import Subscription, SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """
    订阅计划序列化器
    """
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'code', 'description', 'is_active', 'is_public',
            'monthly_price', 'quarterly_price', 'yearly_price', 'currency',
            'features', 'sort_order', 'highlight', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    订阅序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    billing_cycle_display = serializers.CharField(source='get_billing_cycle_display', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_trial = serializers.BooleanField(read_only=True)
    days_until_expiration = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'plan_name', 'status', 'status_display', 'billing_cycle',
            'billing_cycle_display', 'auto_renew', 'start_date', 'end_date',
            'price', 'currency', 'is_active', 'is_trial', 'days_until_expiration',
            'created_at'
        ]
        read_only_fields = [
            'id', 'plan', 'plan_name', 'status', 'start_date', 'end_date',
            'price', 'currency', 'created_at'
        ]


class SubscriptionDetailSerializer(SubscriptionSerializer):
    """
    订阅详细信息序列化器
    """
    plan = SubscriptionPlanSerializer(read_only=True)
    
    class Meta(SubscriptionSerializer.Meta):
        fields = SubscriptionSerializer.Meta.fields + [
            'trial_end_date', 'canceled_at', 'current_period_start',
            'current_period_end', 'metadata', 'updated_at'
        ]
        read_only_fields = SubscriptionSerializer.Meta.read_only_fields + [
            'trial_end_date', 'canceled_at', 'current_period_start',
            'current_period_end', 'updated_at'
        ] 