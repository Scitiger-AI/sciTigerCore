"""
URL configuration for sciTigerCore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    
    # 平台API
    path('api/platform/auth/', include('apps.auth_service.urls.platform')),
    path('api/platform/tenants/', include('apps.tenant_service.urls.platform')),
    path('api/platform/notifications/', include('apps.notification_service.urls.platform')),
    path('api/platform/logs/', include('apps.logger_service.urls.platform')),
    path('api/platform/payments/', include('apps.billing_service.urls.platform')),
    
    # 管理API
    path('api/management/auth/', include('apps.auth_service.urls.management')),
    path('api/management/tenants/', include('apps.tenant_service.urls.management')),
    path('api/management/notifications/', include('apps.notification_service.urls.management')),
    path('api/management/logs/', include('apps.logger_service.urls.management')),
    path('api/management/payments/', include('apps.billing_service.urls.management')),
]

# 添加静态文件和媒体文件的URL配置
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
