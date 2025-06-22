"""
角色过滤器
"""

import django_filters
from django.db.models import Q
from apps.auth_service.models import Role


class RoleFilter(django_filters.FilterSet):
    """
    角色过滤器类
    
    提供对角色的高级过滤功能
    """
    # 按名称搜索
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    # 按属性过滤
    is_system = django_filters.BooleanFilter()
    is_default = django_filters.BooleanFilter()
    is_global = django_filters.BooleanFilter(method='filter_is_global')
    # 按租户过滤
    tenant_id = django_filters.UUIDFilter(field_name='tenant__id')
    tenant_name = django_filters.CharFilter(field_name='tenant__name', lookup_expr='icontains')
    # 按权限过滤
    has_permission = django_filters.CharFilter(method='filter_has_permission')
    # 按创建时间过滤
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    # 按更新时间过滤
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Role
        fields = {
            'name': ['exact', 'icontains'],
            'code': ['exact', 'icontains'],
            'is_system': ['exact'],
            'is_default': ['exact'],
            'tenant_id': ['exact'],
        }
    
    def filter_is_global(self, queryset, name, value):
        """
        过滤全局角色
        """
        if value is None:
            return queryset
            
        if value:
            return queryset.filter(tenant__isnull=True)
        else:
            return queryset.filter(tenant__isnull=False)
    
    def filter_has_permission(self, queryset, name, value):
        """
        过滤具有特定权限的角色
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(permissions__code__icontains=value) |
            Q(permissions__name__icontains=value)
        ).distinct()
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value) |
            Q(tenant__name__icontains=value)
        ).distinct() 