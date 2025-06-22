"""
租户设置过滤器
"""

import django_filters
from django.db.models import Q
from apps.tenant_service.models import TenantSettings


class TenantSettingsFilter(django_filters.FilterSet):
    """
    租户设置过滤器类
    
    提供对租户设置的高级过滤功能
    """
    # 按租户名称搜索
    tenant_name = django_filters.CharFilter(field_name='tenant__name', lookup_expr='icontains')
    # 按租户标识符搜索
    tenant_slug = django_filters.CharFilter(field_name='tenant__slug', lookup_expr='icontains')
    # 按功能开关过滤
    enable_notifications = django_filters.BooleanFilter()
    enable_api_keys = django_filters.BooleanFilter()
    enable_two_factor_auth = django_filters.BooleanFilter()
    # 按安全设置过滤
    password_expiry_days_min = django_filters.NumberFilter(field_name='password_expiry_days', lookup_expr='gte')
    password_expiry_days_max = django_filters.NumberFilter(field_name='password_expiry_days', lookup_expr='lte')
    max_login_attempts_min = django_filters.NumberFilter(field_name='max_login_attempts', lookup_expr='gte')
    max_login_attempts_max = django_filters.NumberFilter(field_name='max_login_attempts', lookup_expr='lte')
    # 按创建时间过滤
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    # 按更新时间过滤
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = TenantSettings
        fields = {
            'tenant_id': ['exact'],
            'timezone': ['exact', 'icontains'],
            'date_format': ['exact', 'icontains'],
            'time_format': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(tenant__name__icontains=value) |
            Q(tenant__slug__icontains=value) |
            Q(default_notification_email__icontains=value) |
            Q(timezone__icontains=value)
        ) 