"""
通知服务实现
"""

import logging
from django.utils import timezone
from django.template import Template, Context
from django.conf import settings
from django.db import models
from apps.notification_service.models import (
    NotificationType, NotificationChannel, NotificationTemplate, 
    Notification, UserNotificationPreference
)

logger = logging.getLogger(__name__)


class NotificationService:
    """
    通知服务类
    
    提供通知发送和管理的核心功能
    """
    
    @staticmethod
    def get_notification_types(tenant_id=None, is_active=True, **filters):
        """
        获取通知类型列表
        
        参数:
            tenant_id: 租户ID，None表示获取系统级通知类型
            is_active: 是否只获取活跃的通知类型
            filters: 其他过滤条件
        
        返回:
            QuerySet: 通知类型查询集
        """
        queryset = NotificationType.objects.all()
        
        if is_active:
            queryset = queryset.filter(is_active=True)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_notification_channels(tenant_id=None, is_active=True, **filters):
        """
        获取通知渠道列表
        
        参数:
            tenant_id: 租户ID，None表示获取系统级通知渠道
            is_active: 是否只获取活跃的通知渠道
            filters: 其他过滤条件
        
        返回:
            QuerySet: 通知渠道查询集
        """
        queryset = NotificationChannel.objects.all()
        
        # 根据租户过滤
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        else:
            queryset = queryset.filter(tenant__isnull=True)
        
        if is_active:
            queryset = queryset.filter(is_active=True)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_notification_templates(tenant_id=None, notification_type_id=None, 
                                   channel_id=None, is_active=True, **filters):
        """
        获取通知模板列表
        
        参数:
            tenant_id: 租户ID，None表示获取系统级通知模板
            notification_type_id: 通知类型ID
            channel_id: 通知渠道ID
            is_active: 是否只获取活跃的通知模板
            filters: 其他过滤条件
        
        返回:
            QuerySet: 通知模板查询集
        """
        queryset = NotificationTemplate.objects.all()
        
        # 根据租户过滤
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        else:
            queryset = queryset.filter(tenant__isnull=True)
        
        # 根据通知类型过滤
        if notification_type_id:
            queryset = queryset.filter(notification_type_id=notification_type_id)
        
        # 根据通知渠道过滤
        if channel_id:
            queryset = queryset.filter(channel_id=channel_id)
        
        if is_active:
            queryset = queryset.filter(is_active=True)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_notifications(tenant_id, user_id=None, is_read=None, status=None, **filters):
        """
        获取通知列表
        
        参数:
            tenant_id: 租户ID
            user_id: 用户ID
            is_read: 是否已读
            status: 通知状态
            filters: 其他过滤条件
        
        返回:
            QuerySet: 通知查询集
        """
        queryset = Notification.objects.filter(tenant_id=tenant_id)
        
        # 根据用户过滤
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # 根据已读状态过滤
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)
        
        # 根据通知状态过滤
        if status:
            queryset = queryset.filter(status=status)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_user_notification_preferences(tenant_id, user_id, notification_type_id=None):
        """
        获取用户通知偏好设置
        
        参数:
            tenant_id: 租户ID
            user_id: 用户ID
            notification_type_id: 通知类型ID
        
        返回:
            QuerySet: 用户通知偏好设置查询集
        """
        queryset = UserNotificationPreference.objects.filter(
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        # 根据通知类型过滤
        if notification_type_id:
            queryset = queryset.filter(notification_type_id=notification_type_id)
            
        return queryset
    
    @classmethod
    def create_notification(cls, tenant_id, user_id, notification_type_code, 
                          channel_code='in_app', data=None, scheduled_at=None):
        """
        创建通知
        
        参数:
            tenant_id: 租户ID
            user_id: 用户ID
            notification_type_code: 通知类型代码
            channel_code: 通知渠道代码，默认为系统内通知
            data: 通知数据，用于模板渲染
            scheduled_at: 计划发送时间，None表示立即发送
        
        返回:
            Notification: 创建的通知对象
        """
        try:
            # 获取通知类型
            notification_type = NotificationType.objects.get(code=notification_type_code, is_active=True)
            
            # 获取通知渠道
            channel = NotificationChannel.objects.filter(
                code=channel_code,
                is_active=True
            ).filter(
                # 优先使用租户特定渠道，如果没有则使用系统渠道
                models.Q(tenant_id=tenant_id) | models.Q(tenant__isnull=True)
            ).first()
            
            if not channel:
                raise ValueError(f"找不到有效的通知渠道: {channel_code}")
            
            # 获取通知模板
            template = NotificationTemplate.objects.filter(
                notification_type=notification_type,
                channel=channel,
                is_active=True
            ).filter(
                # 优先使用租户特定模板，如果没有则使用系统模板
                models.Q(tenant_id=tenant_id) | models.Q(tenant__isnull=True)
            ).first()
            
            if not template:
                raise ValueError(f"找不到有效的通知模板: {notification_type_code} - {channel_code}")
            
            # 检查用户通知偏好设置
            user_preference = UserNotificationPreference.objects.filter(
                tenant_id=tenant_id,
                user_id=user_id,
                notification_type=notification_type
            ).first()
            
            # 如果没有用户偏好设置，则创建默认设置
            if not user_preference:
                user_preference = UserNotificationPreference.objects.create(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    notification_type=notification_type
                )
            
            # 检查用户是否启用了该渠道的通知
            if not user_preference.is_channel_enabled(channel.channel_type):
                logger.info(f"用户 {user_id} 已禁用 {channel.channel_type} 渠道的通知")
                return None
            
            # 检查是否在免打扰时段内
            if (user_preference.is_in_do_not_disturb_period() and 
                not (notification_type.priority == 'urgent' and user_preference.urgent_bypass_dnd)):
                logger.info(f"用户 {user_id} 处于免打扰时段，通知已延迟")
                # 如果在免打扰时段内，设置为延迟发送
                if not scheduled_at:
                    # 计算免打扰结束时间
                    now = timezone.localtime()
                    end_time = user_preference.do_not_disturb_end
                    scheduled_at = timezone.make_aware(
                        timezone.datetime.combine(
                            now.date() + timezone.timedelta(days=1 if now.time() > end_time else 0),
                            end_time
                        )
                    )
            
            # 准备通知数据
            context_data = data or {}
            
            # 渲染模板
            subject = cls._render_template(template.subject_template, context_data)
            content = cls._render_template(template.content_template, context_data)
            html_content = cls._render_template(template.html_template, context_data) if template.html_template else None
            
            # 创建通知记录
            notification = Notification.objects.create(
                tenant_id=tenant_id,
                user_id=user_id,
                notification_type=notification_type,
                channel=channel,
                template=template,
                subject=subject,
                content=content,
                html_content=html_content,
                data=data or {},
                status='pending',
                scheduled_at=scheduled_at
            )
            
            # 如果没有设置计划发送时间，则立即发送
            if not scheduled_at:
                cls.send_notification(notification)
            
            return notification
            
        except Exception as e:
            logger.error(f"创建通知失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    def send_notification(cls, notification):
        """
        发送通知
        
        参数:
            notification: 通知对象
        
        返回:
            bool: 是否发送成功
        """
        try:
            # 更新通知状态为发送中
            notification.status = 'sending'
            notification.save(update_fields=['status', 'updated_at'])
            
            # 根据渠道类型调用不同的发送方法
            channel_type = notification.channel.channel_type
            
            if channel_type == 'email':
                success = cls._send_email_notification(notification)
            elif channel_type == 'sms':
                success = cls._send_sms_notification(notification)
            elif channel_type == 'in_app':
                success = cls._send_in_app_notification(notification)
            elif channel_type == 'push':
                success = cls._send_push_notification(notification)
            elif channel_type == 'webhook':
                success = cls._send_webhook_notification(notification)
            else:
                raise ValueError(f"不支持的通知渠道类型: {channel_type}")
            
            # 更新通知状态
            if success:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
            else:
                notification.status = 'failed'
                notification.error_message = "发送失败"
            
            notification.save(update_fields=['status', 'sent_at', 'error_message', 'updated_at'])
            
            return success
            
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}", exc_info=True)
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save(update_fields=['status', 'error_message', 'updated_at'])
            return False
    
    @staticmethod
    def _send_email_notification(notification):
        """发送邮件通知"""
        # TODO: 实现邮件发送逻辑
        logger.info(f"发送邮件通知: {notification.id}")
        return True
    
    @staticmethod
    def _send_sms_notification(notification):
        """发送短信通知"""
        # TODO: 实现短信发送逻辑
        logger.info(f"发送短信通知: {notification.id}")
        return True
    
    @staticmethod
    def _send_in_app_notification(notification):
        """发送系统内通知"""
        # 系统内通知不需要额外处理，已经保存到数据库
        logger.info(f"发送系统内通知: {notification.id}")
        return True
    
    @staticmethod
    def _send_push_notification(notification):
        """发送推送通知"""
        # TODO: 实现推送通知逻辑
        logger.info(f"发送推送通知: {notification.id}")
        return True
    
    @staticmethod
    def _send_webhook_notification(notification):
        """发送Webhook通知"""
        # TODO: 实现Webhook通知逻辑
        logger.info(f"发送Webhook通知: {notification.id}")
        return True
    
    @staticmethod
    def _render_template(template_string, context_data):
        """
        渲染模板
        
        参数:
            template_string: 模板字符串
            context_data: 上下文数据
        
        返回:
            str: 渲染后的内容
        """
        if not template_string:
            return ""
        
        template = Template(template_string)
        context = Context(context_data)
        return template.render(context)
    
    @staticmethod
    def mark_notification_as_read(notification_id):
        """
        将通知标记为已读
        
        参数:
            notification_id: 通知ID
        
        返回:
            bool: 是否成功
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            logger.error(f"通知不存在: {notification_id}")
            return False
        except Exception as e:
            logger.error(f"标记通知为已读失败: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def mark_notification_as_unread(notification_id):
        """
        将通知标记为未读
        
        参数:
            notification_id: 通知ID
        
        返回:
            bool: 是否成功
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.mark_as_unread()
            return True
        except Notification.DoesNotExist:
            logger.error(f"通知不存在: {notification_id}")
            return False
        except Exception as e:
            logger.error(f"标记通知为未读失败: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def mark_all_notifications_as_read(tenant_id, user_id):
        """
        将用户的所有通知标记为已读
        
        参数:
            tenant_id: 租户ID
            user_id: 用户ID
        
        返回:
            int: 更新的通知数量
        """
        try:
            from django.utils import timezone
            now = timezone.now()
            
            # 批量更新未读通知
            count = Notification.objects.filter(
                tenant_id=tenant_id,
                user_id=user_id,
                is_read=False
            ).update(
                is_read=True,
                read_at=now,
                updated_at=now
            )
            
            return count
        except Exception as e:
            logger.error(f"批量标记通知为已读失败: {str(e)}", exc_info=True)
            raise 