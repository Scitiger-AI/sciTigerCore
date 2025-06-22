"""
租户过滤器
"""

import django_filters
from django.db.models import Q
from apps.tenant_service.models import Tenant


class TenantFilter(django_filters.FilterSet):
    """
    租户过滤器类
    
    提供对租户的高级过滤功能
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    slug = django_filters.CharFilter(lookup_expr='icontains')
    subdomain = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    contact_email = django_filters.CharFilter(lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    expires_after = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='gte')
    expires_before = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='lte')
    is_expired = django_filters.BooleanFilter(method='filter_is_expired')
    
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Tenant
        fields = {
            'name': ['exact', 'icontains'],
            'slug': ['exact', 'icontains'],
            'subdomain': ['exact', 'icontains'],
            'is_active': ['exact'],
            'contact_email': ['exact', 'icontains'],
            'contact_phone': ['exact', 'icontains'],
        }
    
    def filter_is_expired(self, queryset, name, value):
        """
        过滤已过期的租户
        """
        from django.utils import timezone
        now = timezone.now()
        
        if value:  # 过滤已过期的租户
            return queryset.filter(
                Q(expires_at__isnull=False) & Q(expires_at__lt=now)
            )
        else:  # 过滤未过期的租户
            return queryset.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            )
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(subdomain__icontains=value) |
            Q(description__icontains=value) |
            Q(contact_email__icontains=value) |
            Q(contact_phone__icontains=value) |
            Q(address__icontains=value)
        ) 