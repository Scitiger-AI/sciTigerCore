"""
服务范围过滤器
"""

import django_filters
from apps.auth_service.models.service_scope import Service, Resource, Action


class ServiceFilter(django_filters.FilterSet):
    """
    服务过滤器
    """
    code = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    is_system = django_filters.BooleanFilter()
    # tenant_id = django_filters.UUIDFilter(field_name='tenant__id')
    
    class Meta:
        model = Service
        fields = ['code', 'name', 'description', 'is_system']


class ResourceFilter(django_filters.FilterSet):
    """
    资源过滤器
    """
    code = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    service_id = django_filters.UUIDFilter(field_name='service__id')
    service_code = django_filters.CharFilter(field_name='service__code')
    is_system = django_filters.BooleanFilter(field_name='service__is_system')
    # tenant_id = django_filters.UUIDFilter(field_name='service__tenant__id')
    
    class Meta:
        model = Resource
        fields = ['code', 'name', 'description', 'service_id', 'service_code', 'is_system']


class ActionFilter(django_filters.FilterSet):
    """
    操作过滤器
    """
    code = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    is_system = django_filters.BooleanFilter()
    # tenant_id = django_filters.UUIDFilter(field_name='tenant__id')
    
    class Meta:
        model = Action
        fields = ['code', 'name', 'description', 'is_system'] 