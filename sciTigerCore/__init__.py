"""
sciTigerCore package initialization.
"""

# 确保在Django启动时导入Celery应用
from .celery import app as celery_app

__all__ = ('celery_app',)
