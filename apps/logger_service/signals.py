"""
日志服务信号处理器
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger('sciTigerCore')

# 这里可以添加与日志相关的信号处理器
# 例如，当某些重要模型发生变化时自动记录日志 