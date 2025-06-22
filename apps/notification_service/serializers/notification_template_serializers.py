"""
通知模板序列化器
"""

from rest_framework import serializers
from apps.notification_service.models import NotificationTemplate


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """通知模板序列化器"""
    
    notification_type_name = serializers.CharField(source='notification_type.name', read_only=True)
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'code', 'name', 'notification_type', 'notification_type_name',
            'channel', 'channel_name', 'subject_template', 'content_template',
            'html_template', 'language', 'tenant', 'tenant_name', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationTemplateCreateSerializer(serializers.ModelSerializer):
    """通知模板创建序列化器"""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'code', 'name', 'notification_type', 'channel',
            'subject_template', 'content_template', 'html_template',
            'language', 'tenant', 'is_active'
        ]
    
    def validate(self, attrs):
        """验证通知模板的唯一性"""
        code = attrs.get('code')
        channel = attrs.get('channel')
        language = attrs.get('language')
        tenant = attrs.get('tenant')
        
        # 检查相同租户、渠道和语言下是否已存在相同代码的模板
        if NotificationTemplate.objects.filter(
            code=code,
            channel=channel,
            language=language,
            tenant=tenant
        ).exists():
            raise serializers.ValidationError({"code": "该租户下已存在相同代码、渠道和语言的通知模板"})
        
        return attrs


class NotificationTemplateUpdateSerializer(serializers.ModelSerializer):
    """通知模板更新序列化器"""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'name', 'subject_template', 'content_template',
            'html_template', 'is_active'
        ] 