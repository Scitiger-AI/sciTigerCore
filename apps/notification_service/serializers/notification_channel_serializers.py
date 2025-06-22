"""
通知渠道序列化器
"""

from rest_framework import serializers
from apps.notification_service.models import NotificationChannel


class NotificationChannelSerializer(serializers.ModelSerializer):
    """通知渠道序列化器"""
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = NotificationChannel
        fields = [
            'id', 'code', 'name', 'channel_type', 'description',
            'config', 'is_active', 'tenant', 'tenant_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationChannelCreateSerializer(serializers.ModelSerializer):
    """通知渠道创建序列化器"""
    
    class Meta:
        model = NotificationChannel
        fields = [
            'code', 'name', 'channel_type', 'description',
            'config', 'is_active', 'tenant'
        ]
    
    def validate(self, attrs):
        """验证通知渠道代码的唯一性"""
        code = attrs.get('code')
        tenant = attrs.get('tenant')
        
        # 检查相同租户下是否已存在相同代码的渠道
        if NotificationChannel.objects.filter(code=code, tenant=tenant).exists():
            raise serializers.ValidationError({"code": "该租户下已存在相同代码的通知渠道"})
        
        return attrs


class NotificationChannelUpdateSerializer(serializers.ModelSerializer):
    """通知渠道更新序列化器"""
    
    class Meta:
        model = NotificationChannel
        fields = [
            'name', 'description', 'config', 'is_active'
        ] 