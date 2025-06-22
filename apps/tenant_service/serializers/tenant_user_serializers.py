"""
租户用户关联序列化器
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.serializers import (
    BaseModelSerializer, 
    TimestampedFieldsMixin,
    TenantFieldMixin
)
from apps.tenant_service.models import TenantUser

User = get_user_model()


class TenantUserSerializer(TimestampedFieldsMixin, TenantFieldMixin, BaseModelSerializer):
    """
    租户用户关联序列化器
    """
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    last_login = serializers.DateTimeField(source='user.last_login', read_only=True)
    
    class Meta:
        model = TenantUser
        fields = [
            'id', 'user_id', 'avatar', 'username', 'email', 'full_name',
            'role', 'role_display', 'is_active', 'tenant', 'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']


class TenantUserCreateSerializer(TenantFieldMixin, BaseModelSerializer):
    """
    租户用户创建序列化器
    """
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = TenantUser
        fields = ['user_id', 'role', 'is_active', 'tenant']
        read_only_fields = ['tenant']
        
    def validate_user_id(self, value):
        """
        验证用户ID是否存在
        """
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("用户不存在")
            
        # 检查用户是否已经是租户成员
        tenant = self.tenant
        if TenantUser.objects.filter(tenant=tenant, user=user).exists():
            raise serializers.ValidationError("该用户已经是租户成员")
            
        return value
        
    def create(self, validated_data):
        """
        创建租户用户关联
        """
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        
        # BaseModelSerializer会自动处理tenant字段
        return TenantUser.objects.create(
            user=user,
            **validated_data
        )


class TenantUserUpdateSerializer(TenantFieldMixin, BaseModelSerializer):
    """
    租户用户更新序列化器
    """
    
    class Meta:
        model = TenantUser
        fields = ['role', 'is_active', 'tenant']
        read_only_fields = ['tenant']
        
    def validate_role(self, value):
        """
        验证角色变更
        """
        # 如果是更新为所有者角色，需要特殊处理
        if value == TenantUser.ROLE_OWNER:
            tenant = self.instance.tenant
            # 检查是否已有所有者
            if TenantUser.objects.filter(
                tenant=tenant, 
                role=TenantUser.ROLE_OWNER
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("租户已有所有者，请先移除现有所有者")
                
        return value 