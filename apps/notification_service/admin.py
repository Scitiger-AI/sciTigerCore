"""
通知中心管理界面配置
"""

from django.contrib import admin
from apps.notification_service.models import (
    NotificationType, NotificationChannel, NotificationTemplate,
    Notification, UserNotificationPreference
)


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    """通知类型管理"""
    list_display = ('name', 'code', 'category', 'priority', 'is_active', 'created_at')
    list_filter = ('category', 'priority', 'is_active')
    search_fields = ('name', 'code', 'description')
    ordering = ('category', 'priority', 'name')


@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    """通知渠道管理"""
    list_display = ('name', 'code', 'channel_type', 'tenant', 'is_active', 'created_at')
    list_filter = ('channel_type', 'is_active', 'tenant')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """通知模板管理"""
    list_display = ('name', 'code', 'notification_type', 'channel', 'language', 'tenant', 'is_active')
    list_filter = ('notification_type', 'channel', 'language', 'is_active', 'tenant')
    search_fields = ('name', 'code', 'subject_template')
    ordering = ('notification_type', 'channel', 'language')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """通知记录管理"""
    list_display = ('subject', 'user', 'notification_type', 'channel', 'status', 'is_read', 'created_at')
    list_filter = ('status', 'is_read', 'notification_type', 'channel', 'tenant')
    search_fields = ('subject', 'content', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'sent_at', 'read_at')


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    """用户通知偏好设置管理"""
    list_display = ('user', 'notification_type', 'email_enabled', 'sms_enabled', 
                    'in_app_enabled', 'push_enabled', 'do_not_disturb_enabled')
    list_filter = ('email_enabled', 'sms_enabled', 'in_app_enabled', 'push_enabled', 
                   'do_not_disturb_enabled', 'notification_type', 'tenant')
    search_fields = ('user__username', 'notification_type__name')
    ordering = ('user', 'notification_type')
