"""
用户序列化器
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from core.serializers import (
    BaseModelSerializer, 
    TimestampedFieldsMixin,
    ReadOnlyFieldsMixin
)
from apps.auth_service.models import User, Role
from apps.tenant_service.models import TenantUser
from apps.auth_service.serializers.role_serializers import SimpleRoleSerializer


class SimpleUserSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    用户基础序列化器
    """
    class Meta:
        model = User
        fields = ['id', 'avatar', 'username', 'email', 'first_name', 'last_name', 'is_superuser']


class UserSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    用户基础序列化器
    """

    tenants = serializers.SerializerMethodField()
    current_tenant = serializers.SerializerMethodField()
    roles = SimpleRoleSerializer(many=True)
    class Meta:
        model = User
        fields = [
            'id', 'avatar', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'phone', 'email_verified', 'phone_verified',
            'last_login', 'date_joined', 'is_superuser', 'tenants', 'current_tenant', 'roles'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'email_verified', 'phone_verified']

    def get_tenants(self, obj):
        """获取用户所属租户"""
        tenant_users = TenantUser.objects.filter(user=obj)
        return [
            {
                'id': str(tenant_user.tenant.id),
                'name': tenant_user.tenant.name,
                'slug': tenant_user.tenant.slug,
                'role': tenant_user.role,
                'role_display': tenant_user.get_role_display()
            }
            for tenant_user in tenant_users
        ]
        
    def get_current_tenant(self, obj):
        """获取用户在当前租户中的信息"""
        # 从上下文中获取当前租户ID
        tenant_id = self.context.get('current_tenant_id')
        if not tenant_id:
            return None
            
        # 查找用户在当前租户中的关联
        try:
            tenant_user = TenantUser.objects.get(user=obj, tenant_id=tenant_id)
            return {
                'id': str(tenant_user.tenant.id),
                'name': tenant_user.tenant.name,
                'slug': tenant_user.tenant.slug,
                'role': tenant_user.role,
                'role_display': tenant_user.get_role_display()
            }
        except TenantUser.DoesNotExist:
            return None


class UserDetailSerializer(UserSerializer):
    """
    用户详情序列化器
    """
    roles = serializers.SerializerMethodField()
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['roles', 'bio', 'avatar']
    
    def get_roles(self, obj):
        """获取用户角色"""
        return [
            {
                'id': str(role.id),
                'name': role.name,
                'code': role.code
            }
            for role in obj.roles.all()
        ]


class UserCreateSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    用户创建序列化器
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    roles = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        required=False
    )
    tenant_id = serializers.UUIDField(required=False, write_only=True)
    tenant_role = serializers.ChoiceField(
        choices=['owner', 'admin', 'member'],
        default='member',
        required=False,
        write_only=True
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'is_active',
            'bio', 'avatar', 'roles', 'tenant_id', 'tenant_role'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False},
            'is_active': {'required': False},
            'bio': {'required': False},
            'avatar': {'required': False}
        }
    
    def validate(self, attrs):
        """
        验证两次密码输入是否一致
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "两次密码输入不一致"})
        return attrs


class UserUpdateSerializer(TimestampedFieldsMixin, BaseModelSerializer):
    """
    用户更新序列化器
    """
    roles = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'is_active', 'bio', 'avatar', 'roles'
        ]
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False},
            'is_active': {'required': False},
            'bio': {'required': False},
            'avatar': {'required': False}
        }


class ChangePasswordSerializer(serializers.Serializer):
    """
    修改密码序列化器
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """
        验证两次密码输入是否一致
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "两次密码输入不一致"})
        return attrs 