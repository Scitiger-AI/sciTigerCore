"""
用户通知偏好设置模型定义
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserNotificationPreference(models.Model):
    """
    用户通知偏好设置模型
    
    存储用户对不同类型通知的接收偏好设置
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    tenant = models.ForeignKey(
        'tenant_service.Tenant',
        on_delete=models.CASCADE,
        related_name='user_notification_preferences',
        verbose_name=_('所属租户')
    )
    user = models.ForeignKey(
        'auth_service.User',
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name=_('用户')
    )
    notification_type = models.ForeignKey(
        'notification_service.NotificationType',
        on_delete=models.CASCADE,
        related_name='user_preferences',
        verbose_name=_('通知类型')
    )
    # 各渠道的启用状态
    email_enabled = models.BooleanField(
        default=True,
        verbose_name=_('启用邮件通知')
    )
    sms_enabled = models.BooleanField(
        default=False,
        verbose_name=_('启用短信通知')
    )
    in_app_enabled = models.BooleanField(
        default=True,
        verbose_name=_('启用系统内通知')
    )
    push_enabled = models.BooleanField(
        default=False,
        verbose_name=_('启用推送通知')
    )
    # 免打扰时段设置
    do_not_disturb_enabled = models.BooleanField(
        default=False,
        verbose_name=_('启用免打扰')
    )
    do_not_disturb_start = models.TimeField(
        default='22:00',
        verbose_name=_('免打扰开始时间')
    )
    do_not_disturb_end = models.TimeField(
        default='08:00',
        verbose_name=_('免打扰结束时间')
    )
    # 紧急通知例外设置
    urgent_bypass_dnd = models.BooleanField(
        default=True,
        verbose_name=_('紧急通知绕过免打扰'),
        help_text=_('设置为True时，紧急通知将不受免打扰时段限制')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('创建时间')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('更新时间')
    )
    
    class Meta:
        verbose_name = _('用户通知偏好')
        verbose_name_plural = _('用户通知偏好')
        unique_together = [['user', 'notification_type']]
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type.name}"
    
    def is_channel_enabled(self, channel_type):
        """
        检查指定渠道是否启用
        
        参数:
            channel_type: 渠道类型，如 'email', 'sms', 'in_app', 'push'
            
        返回:
            Boolean: 是否启用
        """
        if channel_type == 'email':
            return self.email_enabled
        elif channel_type == 'sms':
            return self.sms_enabled
        elif channel_type == 'in_app':
            return self.in_app_enabled
        elif channel_type == 'push':
            return self.push_enabled
        return False
    
    def is_in_do_not_disturb_period(self, current_time=None):
        """
        检查当前时间是否在免打扰时段内
        
        参数:
            current_time: 当前时间，默认为None，表示使用系统当前时间
            
        返回:
            Boolean: 是否在免打扰时段内
        """
        if not self.do_not_disturb_enabled:
            return False
            
        from django.utils import timezone
        
        if current_time is None:
            current_time = timezone.localtime()
        
        # 提取当前时间的时分
        current_time_obj = current_time.time()
        
        # 跨天情况处理（如22:00-08:00）
        if self.do_not_disturb_start > self.do_not_disturb_end:
            return current_time_obj >= self.do_not_disturb_start or current_time_obj < self.do_not_disturb_end
        
        # 同一天内的时间段
        return self.do_not_disturb_start <= current_time_obj < self.do_not_disturb_end 