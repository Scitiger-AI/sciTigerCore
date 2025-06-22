"""
租户序列化器
"""

from rest_framework import serializers
from core.serializers import (
    BaseModelSerializer, 
    TimestampedFieldsMixin,
    UniqueInTenantValidator
)
from apps.tenant_service.models import Tenant


class TenantSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    租户基础序列化器
    """
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'subdomain', 
            'description', 'logo', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantDetailSerializer(TenantSerializer):
    """
    租户详情序列化器
    """
    
    class Meta(TenantSerializer.Meta):
        fields = TenantSerializer.Meta.fields + [
            'contact_email', 'contact_phone', 'address', 'expires_at'
        ]


class TenantCreateSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    租户创建序列化器
    """
    
    class Meta:
        model = Tenant
        fields = [
            'name', 'slug', 'subdomain', 'description', 
            'logo', 'contact_email', 'contact_phone', 
            'address', 'is_active', 'expires_at'
        ]
        
    def validate_slug(self, value):
        """
        验证租户标识符的唯一性
        """
        if Tenant.objects.filter(slug=value).exists():
            raise serializers.ValidationError("租户标识符已存在")
        return value
        
    def validate_subdomain(self, value):
        """
        验证子域名的唯一性
        """
        if Tenant.objects.filter(subdomain=value).exists():
            raise serializers.ValidationError("子域名已存在")
        return value


class TenantUpdateSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    租户更新序列化器
    """
    
    class Meta:
        model = Tenant
        fields = [
            'name', 'description', 'logo', 
            'contact_email', 'contact_phone', 'address',
            'is_active', 'expires_at'
        ]
        
    def validate_slug(self, value):
        """
        验证租户标识符的唯一性
        """
        instance = self.instance
        if Tenant.objects.filter(slug=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError("租户标识符已存在")
        return value
        
    def validate_subdomain(self, value):
        """
        验证子域名的唯一性
        """
        instance = self.instance
        if Tenant.objects.filter(subdomain=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError("子域名已存在")
        return value 