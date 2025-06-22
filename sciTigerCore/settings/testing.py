"""
Testing settings for sciTigerCore project.
"""

from .base import *

# 测试环境调试模式
DEBUG = False

# 允许的主机配置
ALLOWED_HOSTS = ['*']

# 测试数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 测试缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# 测试邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 测试密码哈希器（加速测试）
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 测试文件存储
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# 禁用Celery（在测试中使用同步任务）
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 测试日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': False,
        },
        'sciTigerCore': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}
