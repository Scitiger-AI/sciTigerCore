"""
租户配额序列化器
"""

from rest_framework import serializers
from core.serializers import (
    BaseModelSerializer, 
    TimestampedFieldsMixin,
    TenantFieldMixin
)
from apps.tenant_service.models import TenantQuota


class TenantQuotaSerializer(TimestampedFieldsMixin, TenantFieldMixin, BaseModelSerializer):
    """
    租户配额序列化器
    """
    
    class Meta:
        model = TenantQuota
        fields = [
            'id', 'tenant', 'max_users', 'current_user_count',
            'max_storage_gb', 'current_storage_used_gb', 'max_api_keys',
            'current_api_key_count', 'max_api_requests_per_day',
            'max_log_retention_days', 'max_notifications_per_day',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'tenant', 'current_user_count', 'current_storage_used_gb',
            'current_api_key_count', 'created_at', 'updated_at'
        ]


class TenantQuotaUpdateSerializer(TenantFieldMixin, BaseModelSerializer):
    """
    租户配额更新序列化器
    """
    
    class Meta:
        model = TenantQuota
        fields = [
            'max_users', 'max_storage_gb', 'max_api_keys',
            'max_api_requests_per_day', 'max_log_retention_days',
            'max_notifications_per_day', 'tenant'
        ]
        read_only_fields = ['tenant']
        
    def validate_max_users(self, value):
        """
        验证最大用户数
        """
        if value < self.instance.current_user_count:
            raise serializers.ValidationError(
                f"最大用户数不能小于当前用户数 ({self.instance.current_user_count})"
            )
        return value
        
    def validate_max_storage_gb(self, value):
        """
        验证最大存储空间
        """
        if value < self.instance.current_storage_used_gb:
            raise serializers.ValidationError(
                f"最大存储空间不能小于当前使用空间 ({self.instance.current_storage_used_gb})"
            )
        return value
        
    def validate_max_api_keys(self, value):
        """
        验证最大API密钥数
        """
        if value < self.instance.current_api_key_count:
            raise serializers.ValidationError(
                f"最大API密钥数不能小于当前API密钥数 ({self.instance.current_api_key_count})"
            )
        return value 