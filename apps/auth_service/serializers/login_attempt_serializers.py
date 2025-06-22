"""
登录尝试序列化器
"""

from rest_framework import serializers
from core.serializers import (
    BaseModelSerializer, 
    TimestampedFieldsMixin
)
from apps.auth_service.models import LoginAttempt
from apps.auth_service.serializers.user_serializers import UserSerializer
from apps.tenant_service.serializers import TenantSerializer


class LoginAttemptSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    登录尝试基础序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LoginAttempt
        fields = [
            'id', 'email', 'ip_address', 'status', 'status_display',
            'reason', 'is_admin_login', 'timestamp',
            'user_id', 'tenant_id'
        ]
        read_only_fields = fields


class LoginAttemptDetailSerializer(LoginAttemptSerializer):
    """
    登录尝试详情序列化器
    """
    user = UserSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)
    
    class Meta:
        model = LoginAttempt
        fields = [
            'id', 'email', 'ip_address', 'user_agent', 'status', 'status_display',
            'reason', 'is_admin_login', 'timestamp', 'failure_reason',
            'user', 'user_id', 'tenant', 'tenant_id'
        ]
        read_only_fields = fields 