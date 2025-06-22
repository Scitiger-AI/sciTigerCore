"""
通知记录序列化器
"""

from rest_framework import serializers
from apps.notification_service.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """通知记录序列化器"""
    
    notification_type_name = serializers.CharField(source='notification_type.name', read_only=True)
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'tenant', 'user', 'user_name', 'notification_type', 
            'notification_type_name', 'channel', 'channel_name', 'template',
            'subject', 'content', 'html_content', 'data', 'status',
            'is_read', 'read_at', 'recipient_address', 'error_message',
            'external_id', 'scheduled_at', 'sent_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationCreateSerializer(serializers.Serializer):
    """通知创建序列化器"""
    
    user_id = serializers.UUIDField(required=True)
    notification_type_code = serializers.CharField(required=True)
    channel_code = serializers.CharField(required=False, default='in_app')
    data = serializers.JSONField(required=False)
    scheduled_at = serializers.DateTimeField(required=False)
    
    def create(self, validated_data):
        """创建通知"""
        from apps.notification_service.services import NotificationService
        
        tenant_id = self.context['request'].tenant.id
        user_id = validated_data.pop('user_id')
        notification_type_code = validated_data.pop('notification_type_code')
        channel_code = validated_data.pop('channel_code', 'in_app')
        data = validated_data.pop('data', None)
        scheduled_at = validated_data.pop('scheduled_at', None)
        
        notification = NotificationService.create_notification(
            tenant_id=tenant_id,
            user_id=user_id,
            notification_type_code=notification_type_code,
            channel_code=channel_code,
            data=data,
            scheduled_at=scheduled_at
        )
        
        return notification


class NotificationListSerializer(serializers.ModelSerializer):
    """通知列表序列化器"""
    
    notification_type_name = serializers.CharField(source='notification_type.name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'subject', 'notification_type_name', 'status',
            'is_read', 'created_at'
        ]


class NotificationMarkReadSerializer(serializers.Serializer):
    """通知标记已读序列化器"""
    
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    mark_all = serializers.BooleanField(default=False)
    
    def validate(self, attrs):
        """验证参数"""
        notification_ids = attrs.get('notification_ids')
        mark_all = attrs.get('mark_all')
        
        if not notification_ids and not mark_all:
            raise serializers.ValidationError(
                "必须提供notification_ids或设置mark_all为true"
            )
        
        return attrs 