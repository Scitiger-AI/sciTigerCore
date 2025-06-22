"""
权限序列化器
"""

from rest_framework import serializers
from core.serializers import (
    BaseModelSerializer, 
    TimestampedFieldsMixin,
    UniqueInTenantValidator
)
from apps.auth_service.models import Permission
from apps.tenant_service.serializers import TenantSerializer

class PermissionSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    权限基础序列化器
    """
    tenant = TenantSerializer()
    class Meta:
        model = Permission
        fields = [
            'id', 'code', 'name', 'description',
            'service', 'resource', 'action',
            'is_system', 'is_tenant_level', 'tenant',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class PermissionDetailSerializer(PermissionSerializer):
    """
    权限详情序列化器
    """
    
    class Meta(PermissionSerializer.Meta):
        fields = PermissionSerializer.Meta.fields


class PermissionCreateSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    权限创建序列化器
    
    权限分为两种类型：
    1. 系统全局权限 (is_system=True)：系统预设的权限，适用于所有租户，不关联特定租户
    2. 租户级权限 (is_tenant_level=True)：特定租户的自定义权限，必须关联到特定租户
    
    这两种类型互斥，一个权限不能同时是系统权限和租户级权限。
    """
    
    class Meta:
        model = Permission
        fields = [
            'name', 'description', 'service', 
            'resource', 'action', 'is_system', 
            'is_tenant_level', 'tenant'
        ]
        validators = [
            UniqueInTenantValidator(
                queryset=Permission.objects.all(),
                fields=('service', 'resource', 'action'),
                message='具有相同服务、资源和操作的权限已存在'
            )
        ]
    
    def validate(self, data):
        """
        验证权限数据
        """
        # 生成权限代码
        service = data.get('service', '').strip().lower()
        resource = data.get('resource', '').strip().lower()
        action = data.get('action', '').strip().lower()
        
        if service and resource and action:
            data['code'] = f"{service}:{resource}:{action}"
        
        # 验证权限类型互斥
        is_system = data.get('is_system', True)  # 默认为系统权限
        is_tenant_level = data.get('is_tenant_level', False)
        tenant = data.get('tenant')
        
        if is_system and is_tenant_level:
            raise serializers.ValidationError({
                'is_system': '系统权限和租户级权限不能同时为真',
                'is_tenant_level': '系统权限和租户级权限不能同时为真'
            })
        
        # 验证租户级权限必须关联租户
        if is_tenant_level and tenant is None:
            raise serializers.ValidationError({
                'tenant': '租户级权限必须关联租户'
            })
        
        # 验证系统权限不应关联租户
        if is_system and tenant is not None:
            raise serializers.ValidationError({
                'tenant': '系统权限不应关联到特定租户'
            })
        
        return data


class PermissionUpdateSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    权限更新序列化器
    
    权限分为两种类型：
    1. 系统全局权限 (is_system=True)：系统预设的权限，适用于所有租户，不关联特定租户
    2. 租户级权限 (is_tenant_level=True)：特定租户的自定义权限，必须关联到特定租户
    
    这两种类型互斥，一个权限不能同时是系统权限和租户级权限。
    """
    
    class Meta:
        model = Permission
        fields = [
            'name', 'description', 'is_system', 
            'is_tenant_level', 'tenant'
        ]
    
    def validate(self, data):
        """
        验证更新的权限数据
        """
        # 获取当前实例的值，如果没有提供新值则使用当前值
        instance = self.instance
        is_system = data.get('is_system', instance.is_system if instance else True)
        is_tenant_level = data.get('is_tenant_level', instance.is_tenant_level if instance else False)
        tenant = data.get('tenant', instance.tenant if instance else None)
        
        # 验证权限类型互斥
        if is_system and is_tenant_level:
            raise serializers.ValidationError({
                'is_system': '系统权限和租户级权限不能同时为真',
                'is_tenant_level': '系统权限和租户级权限不能同时为真'
            })
        
        # 验证租户级权限必须关联租户
        if is_tenant_level and tenant is None:
            raise serializers.ValidationError({
                'tenant': '租户级权限必须关联租户'
            })
        
        # 验证系统权限不应关联租户
        if is_system and tenant is not None:
            raise serializers.ValidationError({
                'tenant': '系统权限不应关联到特定租户'
            })
        
        return data 