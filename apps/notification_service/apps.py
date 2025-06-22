"""
通知中心服务应用配置
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notification_service'
    verbose_name = _('通知中心服务')
    
    def ready(self):
        """
        应用就绪时执行的操作
        """
        try:
            # 导入信号处理器
            import apps.notification_service.signals
        except ImportError:
            pass
