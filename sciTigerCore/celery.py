"""
Celery configuration for sciTigerCore project.
"""

import os
from celery import Celery

# 设置Django设置模块的默认值
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sciTigerCore.settings.development')

# 创建Celery实例
app = Celery('sciTigerCore')

# 使用Django的settings配置Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的Django应用中加载任务
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """测试任务，用于调试"""
    print(f'Request: {self.request!r}')
