"""
Development settings for sciTigerCore project.
"""

from .base import *

# 开发环境调试模式
DEBUG = True

# 允许所有主机访问
ALLOWED_HOSTS = ['*']

# 开发环境CORS配置
CORS_ALLOW_ALL_ORIGINS = True

# 开发环境数据库配置（可选择使用SQLite简化开发）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 开发环境邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 开发环境静态文件配置
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# 禁用密码验证（简化开发）
AUTH_PASSWORD_VALIDATORS = []

# 开发环境日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'sciTigerCore': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
