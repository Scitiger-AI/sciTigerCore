"""
通知类型过滤器
"""

import django_filters
from django.db.models import Q
from apps.notification_service.models import NotificationType


class NotificationTypeFilter(django_filters.FilterSet):
    """
    通知类型过滤器类
    
    提供对通知类型的高级过滤功能
    """
    # 按名称和代码搜索
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    
    # 按分类过滤
    category = django_filters.ChoiceFilter(choices=NotificationType.CATEGORY_CHOICES)
    
    # 按优先级过滤
    priority = django_filters.ChoiceFilter(choices=NotificationType.PRIORITY_CHOICES)
    
    # 按状态过滤
    is_active = django_filters.BooleanFilter()
    
    # 按创建时间过滤
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # 按更新时间过滤
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = NotificationType
        fields = {
            'name': ['exact', 'icontains'],
            'code': ['exact', 'icontains'],
            'category': ['exact'],
            'priority': ['exact'],
            'is_active': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value)
        ) 