"""
账单服务应用配置
"""
from django.apps import AppConfig


class BillingServiceConfig(AppConfig):
    """
    账单服务应用配置类
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.billing_service'
    verbose_name = '账单服务'
    
    def ready(self):
        """
        应用就绪时执行的操作
        """
        try:
            # 导入信号处理器
            import apps.billing_service.signals
        except ImportError:
            pass
