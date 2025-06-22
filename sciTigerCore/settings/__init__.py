"""
Default settings import for sciTigerCore project.
By default, we use the development settings.
To use production settings, set DJANGO_SETTINGS_MODULE=sciTigerCore.settings.production
"""

import os

# 根据环境变量选择配置
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'sciTigerCore.settings.development')

if settings_module == 'sciTigerCore.settings':
    from .development import *
else:
    # 当明确指定了配置模块时，不做任何导入，让Django自己处理
    pass
