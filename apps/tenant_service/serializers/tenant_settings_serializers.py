"""
租户设置序列化器
"""

from rest_framework import serializers
from core.serializers import (
    BaseModelSerializer, 
    TimestampedFieldsMixin,
    TenantFieldMixin
)
from apps.tenant_service.models import TenantSettings


class TenantSettingsSerializer(TimestampedFieldsMixin, TenantFieldMixin, BaseModelSerializer):
    """
    租户设置序列化器
    """
    
    class Meta:
        model = TenantSettings
        fields = [
            'id', 'tenant', 'theme_primary_color', 'theme_secondary_color',
            'enable_notifications', 'enable_api_keys', 'enable_two_factor_auth',
            'password_expiry_days', 'max_login_attempts', 'session_timeout_minutes',
            'default_notification_email', 'timezone', 'date_format', 'time_format',
            'settings_json', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']


class TenantSettingsUpdateSerializer(TenantFieldMixin, BaseModelSerializer):
    """
    租户设置更新序列化器
    """
    
    class Meta:
        model = TenantSettings
        fields = [
            'theme_primary_color', 'theme_secondary_color',
            'enable_notifications', 'enable_api_keys', 'enable_two_factor_auth',
            'password_expiry_days', 'max_login_attempts', 'session_timeout_minutes',
            'default_notification_email', 'timezone', 'date_format', 'time_format',
            'settings_json', 'tenant'
        ]
        read_only_fields = ['tenant']
        
    def validate_custom_css(self, value):
        """
        验证自定义CSS
        """
        # 这里可以添加CSS验证逻辑
        if value and len(value) > 50000:  # 限制CSS大小
            raise serializers.ValidationError("自定义CSS过大，请保持在50KB以内")
        return value
        
    def validate_custom_js(self, value):
        """
        验证自定义JavaScript
        """
        # 这里可以添加JavaScript验证逻辑
        if value and len(value) > 50000:  # 限制JS大小
            raise serializers.ValidationError("自定义JavaScript过大，请保持在50KB以内")
        return value 