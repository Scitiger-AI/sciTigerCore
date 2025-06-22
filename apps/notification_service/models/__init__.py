"""
通知中心服务模型初始化
"""

from apps.notification_service.models.notification_type import NotificationType
from apps.notification_service.models.notification_channel import NotificationChannel
from apps.notification_service.models.notification_template import NotificationTemplate
from apps.notification_service.models.notification import Notification
from apps.notification_service.models.user_notification_preference import UserNotificationPreference

__all__ = [
    'NotificationType',
    'NotificationChannel',
    'NotificationTemplate',
    'Notification',
    'UserNotificationPreference',
]
