"""
API密钥序列化器
"""

from rest_framework import serializers
from core.serializers import (
    BaseModelSerializer, 
    TimestampedFieldsMixin
)
from apps.auth_service.models import ApiKey, ApiKeyScope, ApiKeyUsageLog
from apps.auth_service.models import User
from django.apps import apps
from apps.tenant_service.serializers import TenantSerializer
from apps.auth_service.serializers import SimpleUserSerializer

class ApiKeyScopeSerializer(BaseModelSerializer):
    """
    API密钥作用域序列化器
    """
    
    class Meta:
        model = ApiKeyScope
        fields = ['id', 'service', 'resource', 'action']
        read_only_fields = ['id']


class ApiKeySerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    API密钥基础序列化器
    """

    tenant = TenantSerializer()
    user = SimpleUserSerializer()
    
    class Meta:
        model = ApiKey
        fields = [
            'id', 'key_type', 'prefix', 'name',
            'tenant', 'user', 'is_active',
            'created_at', 'expires_at', 'last_used_at',
            'application_name'
        ]
        read_only_fields = [
            'id', 'key_type', 'prefix', 'created_at',
            'last_used_at'
        ]


class ApiKeyDetailSerializer(ApiKeySerializer):
    """
    API密钥详情序列化器
    """
    scopes = ApiKeyScopeSerializer(many=True, read_only=True)
    created_by_key_name = serializers.SerializerMethodField()
    
    class Meta(ApiKeySerializer.Meta):
        fields = ApiKeySerializer.Meta.fields + ['scopes', 'created_by_key_name', 'metadata']
    
    def get_created_by_key_name(self, obj):
        """获取创建此密钥的密钥名称"""
        if obj.created_by_key:
            return obj.created_by_key.name
        return None


class ApiKeyCreateSerializer(BaseModelSerializer):
    """
    API密钥创建序列化器基类
    """
    scopes = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True
    )
    expires_in_days = serializers.IntegerField(
        required=False,
        write_only=True
    )
    
    class Meta:
        model = ApiKey
        fields = [
            'name', 'is_active', 'expires_in_days',
            'scopes', 'application_name', 'metadata'
        ]
        extra_kwargs = {
            'application_name': {'required': False},
            'metadata': {'required': False}
        }


class SystemApiKeyCreateSerializer(ApiKeyCreateSerializer):
    """
    系统级API密钥创建序列化器
    """
    # 使用空查询集初始化，在__init__中重新设置
    tenant = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=apps.get_model('tenant_service', 'Tenant').objects.none()
    )
    
    class Meta(ApiKeyCreateSerializer.Meta):
        fields = ApiKeyCreateSerializer.Meta.fields + ['tenant']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态设置租户查询集，在视图中会传入
        if 'tenant_queryset' in self.context:
            self.fields['tenant'].queryset = self.context['tenant_queryset']


class UserApiKeyCreateSerializer(ApiKeyCreateSerializer):
    """
    用户级API密钥创建序列化器
    """
    # 使用空查询集初始化，在__init__中重新设置
    user = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=User.objects.none()
    )
    tenant = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=apps.get_model('tenant_service', 'Tenant').objects.none()
    )
    created_by_key = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=ApiKey.objects.none()
    )
    
    class Meta(ApiKeyCreateSerializer.Meta):
        fields = ApiKeyCreateSerializer.Meta.fields + ['user', 'tenant', 'created_by_key']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态设置查询集，在视图中会传入
        if 'user_queryset' in self.context:
            self.fields['user'].queryset = self.context['user_queryset']
        if 'tenant_queryset' in self.context:
            self.fields['tenant'].queryset = self.context['tenant_queryset']
        if 'api_key_queryset' in self.context:
            self.fields['created_by_key'].queryset = self.context['api_key_queryset']


class ApiKeyUpdateSerializer(BaseModelSerializer):
    """
    API密钥更新序列化器
    """
    scopes = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = ApiKey
        fields = [
            'name', 'is_active', 'expires_at',
            'scopes', 'application_name', 'metadata'
        ]
        extra_kwargs = {
            'name': {'required': False},
            'is_active': {'required': False},
            'expires_at': {'required': False},
            'application_name': {'required': False},
            'metadata': {'required': False}
        }


class ApiKeyUsageLogSerializer(BaseModelSerializer):
    """
    API密钥使用日志序列化器
    """
    api_key_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ApiKeyUsageLog
        fields = [
            'id', 'api_key', 'api_key_name', 'tenant',
            'request_path', 'request_method', 'response_status',
            'timestamp', 'client_ip', 'request_id'
        ]
        read_only_fields = fields
    
    def get_api_key_name(self, obj):
        """获取API密钥名称"""
        return obj.api_key.name if obj.api_key else None


class ApiKeyVerifySerializer(serializers.Serializer):
    """
    API密钥验证序列化器
    """
    key = serializers.CharField(required=True)
    service = serializers.CharField(required=False)
    resource = serializers.CharField(required=False)
    action = serializers.CharField(required=False)


class ApiKeyHashSerializer(serializers.Serializer):
    """
    获取API密钥哈希的序列化器
    
    用于提供额外安全验证来获取API密钥哈希
    """
    password = serializers.CharField(required=True, write_only=True)
    api_key_id = serializers.UUIDField(required=True) 