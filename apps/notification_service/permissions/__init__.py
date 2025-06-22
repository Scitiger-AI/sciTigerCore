"""
通知中心权限类初始化
"""

from apps.notification_service.permissions.notification_permissions import (
    NotificationTypePermission, NotificationChannelPermission,
    NotificationTemplatePermission, NotificationPermission,
    UserNotificationPreferencePermission
)

__all__ = [
    'NotificationTypePermission',
    'NotificationChannelPermission',
    'NotificationTemplatePermission',
    'NotificationPermission',
    'UserNotificationPreferencePermission',
]
