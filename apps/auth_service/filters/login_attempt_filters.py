"""
登录尝试过滤器
"""

import django_filters
from django.db.models import Q
from apps.auth_service.models import LoginAttempt


class LoginAttemptFilter(django_filters.FilterSet):
    """
    登录尝试过滤器类
    
    提供对登录尝试记录的高级过滤功能
    """
    # 按邮箱搜索
    email = django_filters.CharFilter(lookup_expr='icontains')
    # 按IP地址搜索
    ip_address = django_filters.CharFilter(lookup_expr='icontains')
    # 按状态过滤
    status = django_filters.ChoiceFilter(choices=LoginAttempt.STATUS_CHOICES)
    # 按时间过滤
    timestamp_after = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    timestamp_before = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    # 按类型过滤
    is_admin_login = django_filters.BooleanFilter()
    # 按用户过滤
    user_id = django_filters.UUIDFilter(field_name='user__id')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    # 按租户过滤
    tenant_id = django_filters.UUIDFilter(field_name='tenant__id')
    tenant_name = django_filters.CharFilter(field_name='tenant__name', lookup_expr='icontains')
    # 按失败原因过滤
    reason = django_filters.CharFilter(lookup_expr='icontains')
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = LoginAttempt
        fields = {
            'email': ['exact', 'icontains'],
            'ip_address': ['exact', 'icontains'],
            'status': ['exact'],
            'is_admin_login': ['exact'],
            'user_id': ['exact'],
            'tenant_id': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(email__icontains=value) |
            Q(ip_address__icontains=value) |
            Q(user_agent__icontains=value) |
            Q(reason__icontains=value) |
            Q(user__username__icontains=value) |
            Q(tenant__name__icontains=value)
        ) 