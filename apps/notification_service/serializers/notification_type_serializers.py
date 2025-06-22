"""
通知类型序列化器
"""

from rest_framework import serializers
from apps.notification_service.models import NotificationType


class NotificationTypeSerializer(serializers.ModelSerializer):
    """通知类型序列化器"""
    
    class Meta:
        model = NotificationType
        fields = [
            'id', 'code', 'name', 'description', 'category', 
            'priority', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationTypeCreateSerializer(serializers.ModelSerializer):
    """通知类型创建序列化器"""
    
    class Meta:
        model = NotificationType
        fields = [
            'code', 'name', 'description', 'category', 
            'priority', 'is_active'
        ]
    
    def validate_code(self, value):
        """验证通知类型代码的唯一性"""
        if NotificationType.objects.filter(code=value).exists():
            raise serializers.ValidationError("该通知类型代码已存在")
        return value


class NotificationTypeUpdateSerializer(serializers.ModelSerializer):
    """通知类型更新序列化器"""
    
    class Meta:
        model = NotificationType
        fields = [
            'name', 'description', 'category', 
            'priority', 'is_active'
        ] 