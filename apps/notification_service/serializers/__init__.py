"""
通知中心服务序列化器初始化
"""

from apps.notification_service.serializers.notification_type_serializers import (
    NotificationTypeSerializer, NotificationTypeCreateSerializer, NotificationTypeUpdateSerializer
)
from apps.notification_service.serializers.notification_channel_serializers import (
    NotificationChannelSerializer, NotificationChannelCreateSerializer, NotificationChannelUpdateSerializer
)
from apps.notification_service.serializers.notification_template_serializers import (
    NotificationTemplateSerializer, NotificationTemplateCreateSerializer, NotificationTemplateUpdateSerializer
)
from apps.notification_service.serializers.notification_serializers import (
    NotificationSerializer, NotificationCreateSerializer, NotificationListSerializer, 
    NotificationMarkReadSerializer
)
from apps.notification_service.serializers.user_notification_preference_serializers import (
    UserNotificationPreferenceSerializer, UserNotificationPreferenceCreateSerializer,
    UserNotificationPreferenceUpdateSerializer
)

__all__ = [
    'NotificationTypeSerializer',
    'NotificationTypeCreateSerializer',
    'NotificationTypeUpdateSerializer',
    'NotificationChannelSerializer',
    'NotificationChannelCreateSerializer',
    'NotificationChannelUpdateSerializer',
    'NotificationTemplateSerializer',
    'NotificationTemplateCreateSerializer',
    'NotificationTemplateUpdateSerializer',
    'NotificationSerializer',
    'NotificationCreateSerializer',
    'NotificationListSerializer',
    'NotificationMarkReadSerializer',
    'UserNotificationPreferenceSerializer',
    'UserNotificationPreferenceCreateSerializer',
    'UserNotificationPreferenceUpdateSerializer',
]
