"""
用户授权认证服务应用配置
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth_service'
    verbose_name = _('用户授权认证服务')
    
    def ready(self):
        """
        应用就绪时执行的操作
        """
        # 导入信号处理器
        import apps.auth_service.signals
