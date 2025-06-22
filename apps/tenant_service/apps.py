"""
租户服务应用配置
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TenantServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tenant_service'
    verbose_name = _('租户服务')
    
    def ready(self):
        """
        应用就绪时执行的操作
        """
        # 导入信号处理器
        import apps.tenant_service.signals
