"""
通知中心平台API视图初始化
"""

from apps.notification_service.views.platform.notification_type_views import NotificationTypeViewSet
from apps.notification_service.views.platform.notification_channel_views import NotificationChannelViewSet
from apps.notification_service.views.platform.notification_template_views import NotificationTemplateViewSet
from apps.notification_service.views.platform.notification_views import NotificationViewSet
from apps.notification_service.views.platform.user_notification_preference_views import UserNotificationPreferenceViewSet

__all__ = [
    'NotificationTypeViewSet',
    'NotificationChannelViewSet',
    'NotificationTemplateViewSet',
    'NotificationViewSet',
    'UserNotificationPreferenceViewSet',
]
