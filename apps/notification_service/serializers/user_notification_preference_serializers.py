"""
用户通知偏好设置序列化器
"""

from rest_framework import serializers
from apps.notification_service.models import UserNotificationPreference, NotificationType


class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    """用户通知偏好设置序列化器"""
    
    notification_type_name = serializers.CharField(source='notification_type.name', read_only=True)
    notification_type_code = serializers.CharField(source='notification_type.code', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserNotificationPreference
        fields = [
            'id', 'tenant', 'user', 'user_name', 'notification_type', 
            'notification_type_name', 'notification_type_code',
            'email_enabled', 'sms_enabled', 'in_app_enabled', 'push_enabled',
            'do_not_disturb_enabled', 'do_not_disturb_start', 'do_not_disturb_end',
            'urgent_bypass_dnd', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'user', 'notification_type', 'created_at', 'updated_at']


class UserNotificationPreferenceCreateSerializer(serializers.ModelSerializer):
    """用户通知偏好设置创建序列化器"""
    
    notification_type_code = serializers.CharField(write_only=True)
    
    class Meta:
        model = UserNotificationPreference
        fields = [
            'user', 'notification_type_code', 'email_enabled', 'sms_enabled',
            'in_app_enabled', 'push_enabled', 'do_not_disturb_enabled',
            'do_not_disturb_start', 'do_not_disturb_end', 'urgent_bypass_dnd'
        ]
    
    def validate(self, attrs):
        """验证参数"""
        user = attrs.get('user')
        notification_type_code = attrs.pop('notification_type_code')
        tenant = self.context['request'].tenant
        
        try:
            notification_type = NotificationType.objects.get(code=notification_type_code)
        except NotificationType.DoesNotExist:
            raise serializers.ValidationError({"notification_type_code": "通知类型不存在"})
        
        # 检查是否已存在相同用户和通知类型的偏好设置
        if UserNotificationPreference.objects.filter(
            tenant=tenant,
            user=user,
            notification_type=notification_type
        ).exists():
            raise serializers.ValidationError("该用户已存在相同通知类型的偏好设置")
        
        attrs['tenant'] = tenant
        attrs['notification_type'] = notification_type
        
        return attrs


class UserNotificationPreferenceUpdateSerializer(serializers.ModelSerializer):
    """用户通知偏好设置更新序列化器"""
    
    class Meta:
        model = UserNotificationPreference
        fields = [
            'email_enabled', 'sms_enabled', 'in_app_enabled', 'push_enabled',
            'do_not_disturb_enabled', 'do_not_disturb_start', 'do_not_disturb_end',
            'urgent_bypass_dnd'
        ] 