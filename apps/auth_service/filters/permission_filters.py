"""
权限过滤器
"""

import django_filters
from django.db.models import Q
from apps.auth_service.models import Permission


class PermissionFilter(django_filters.FilterSet):
    """
    权限过滤器类
    
    提供对权限的高级过滤功能
    
    权限分为两种类型：
    1. 系统全局权限 (is_system=True)：系统预设的权限，适用于所有租户，不关联特定租户
    2. 租户级权限 (is_tenant_level=True)：特定租户的自定义权限，必须关联到特定租户
    
    这两种类型互斥，一个权限不能同时是系统权限和租户级权限。
    """
    # 按名称搜索
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    # 按分类过滤
    service = django_filters.CharFilter(lookup_expr='icontains')
    resource = django_filters.CharFilter(lookup_expr='icontains')
    action = django_filters.CharFilter(lookup_expr='icontains')
    # 按属性过滤
    is_system = django_filters.BooleanFilter()
    is_tenant_level = django_filters.BooleanFilter()
    # 权限类型过滤（便捷过滤器）
    permission_type = django_filters.ChoiceFilter(
        choices=[('system', '系统权限'), ('tenant', '租户级权限')],
        method='filter_permission_type',
        label='权限类型'
    )
    # 按租户过滤
    # tenant_id = django_filters.UUIDFilter(field_name='tenant__id')
    tenant_name = django_filters.CharFilter(field_name='tenant__name', lookup_expr='icontains')
    # 按创建时间过滤
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    # 按更新时间过滤
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Permission
        fields = {
            'name': ['exact', 'icontains'],
            'code': ['exact', 'icontains'],
            'service': ['exact', 'icontains'],
            'resource': ['exact', 'icontains'],
            'action': ['exact', 'icontains'],
            'is_system': ['exact'],
            'is_tenant_level': ['exact'],
            # 'tenant_id': ['exact'],
        }
    
    def filter_permission_type(self, queryset, name, value):
        """
        按权限类型过滤
        
        Args:
            queryset: 查询集
            name: 字段名
            value: 权限类型值 ('system' 或 'tenant')
            
        Returns:
            过滤后的查询集
        """
        if value == 'system':
            return queryset.filter(is_system=True, is_tenant_level=False)
        elif value == 'tenant':
            return queryset.filter(is_system=False, is_tenant_level=True)
        return queryset
    
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
            Q(service__icontains=value) |
            Q(resource__icontains=value) |
            Q(action__icontains=value)
        ) 