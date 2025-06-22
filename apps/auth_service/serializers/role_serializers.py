"""
角色序列化器
"""

from rest_framework import serializers
from core.serializers import (
    BaseModelSerializer, 
    TimestampedFieldsMixin,
    UniqueInTenantValidator
)
from apps.auth_service.models import Role, Permission
from apps.tenant_service.serializers import TenantSerializer


class SimpleRoleSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    角色基础序列化器
    """
    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description']

class RoleSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    角色基础序列化器
    """

    tenant = TenantSerializer()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'description',
            'is_system', 'is_default', 'tenant_id', 'tenant',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_tenant_id(self, obj):
        """获取租户"""
        if obj.tenant:  
            return obj.tenant.id
        else:
            return None


class RoleDetailSerializer(RoleSerializer):
    """
    角色详情序列化器
    """
    permissions = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    class Meta(RoleSerializer.Meta):
        fields = RoleSerializer.Meta.fields + ['permissions', 'users_count']
    
    def get_permissions(self, obj):
        """获取角色权限"""
        return [
            {
                'id': str(permission.id),
                'name': permission.name,
                'code': permission.code,
                'service': permission.service,
                'resource': permission.resource,
                'action': permission.action
            }
            for permission in obj.permissions.all()
        ]
    
    def get_users_count(self, obj):
        """获取拥有此角色的用户数量"""
        return obj.users.count()


class RoleCreateSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    角色创建序列化器
    """
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = [
            'name', 'code', 'description', 'is_system',
            'is_default', 'tenant', 'permissions'
        ]
        validators = [
            UniqueInTenantValidator(
                queryset=Role.objects.all(),
                fields=('code',),
                message='具有相同代码的角色已存在'
            )
        ]


class RoleUpdateSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    角色更新序列化器
    """
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = [
            'name', 'description', 'is_default',
            'permissions'
        ] 