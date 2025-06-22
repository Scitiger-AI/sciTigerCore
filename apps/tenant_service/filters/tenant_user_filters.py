"""
租户用户过滤器
"""

import django_filters
from django.db.models import Q
from apps.tenant_service.models import TenantUser


class TenantUserFilter(django_filters.FilterSet):
    """
    租户用户过滤器类
    
    提供对租户用户关联的高级过滤功能
    """
    # 按用户名或邮箱搜索用户
    user_search = django_filters.CharFilter(method='filter_user_search')
    # 按租户名称搜索
    tenant_name = django_filters.CharFilter(field_name='tenant__name', lookup_expr='icontains')
    # 按角色过滤
    role = django_filters.ChoiceFilter(choices=TenantUser.ROLE_CHOICES)
    # 按创建时间过滤
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    # 按更新时间过滤
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = TenantUser
        fields = {
            'tenant_id': ['exact'],
            'user_id': ['exact'],
            'role': ['exact'],
            'is_active': ['exact'],
        }
    
    def filter_user_search(self, queryset, name, value):
        """
        按用户名或邮箱搜索用户
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(user__email__icontains=value) |
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value)
        )
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(user__email__icontains=value) |
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(tenant__name__icontains=value) |
            Q(tenant__slug__icontains=value)
        ) 