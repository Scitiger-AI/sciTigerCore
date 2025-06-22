"""
通知模板过滤器
"""

import django_filters
from django.db.models import Q
from apps.notification_service.models import NotificationTemplate


class NotificationTemplateFilter(django_filters.FilterSet):
    """
    通知模板过滤器类
    
    提供对通知模板的高级过滤功能
    """
    # 按名称和代码搜索
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    subject_template = django_filters.CharFilter(lookup_expr='icontains')
    
    # 按通知类型过滤
    notification_type_id = django_filters.UUIDFilter(field_name='notification_type__id')
    notification_type_code = django_filters.CharFilter(field_name='notification_type__code')
    notification_type_name = django_filters.CharFilter(field_name='notification_type__name', lookup_expr='icontains')
    
    # 按通知渠道过滤
    channel_id = django_filters.UUIDFilter(field_name='channel__id')
    channel_code = django_filters.CharFilter(field_name='channel__code')
    channel_type = django_filters.CharFilter(field_name='channel__channel_type')
    
    # 按语言过滤
    language = django_filters.CharFilter()
    
    # 按状态过滤
    is_active = django_filters.BooleanFilter()
    
    # 按租户过滤
    tenant_id = django_filters.UUIDFilter(field_name='tenant__id')
    tenant_name = django_filters.CharFilter(field_name='tenant__name', lookup_expr='icontains')
    is_system = django_filters.BooleanFilter(method='filter_is_system')
    
    # 按创建时间过滤
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # 按更新时间过滤
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = NotificationTemplate
        fields = {
            'name': ['exact', 'icontains'],
            'code': ['exact', 'icontains'],
            'language': ['exact'],
            'is_active': ['exact'],
            'tenant_id': ['exact'],
        }
    
    def filter_is_system(self, queryset, name, value):
        """
        过滤系统级模板（租户为空的模板）
        """
        if value is None:
            return queryset
            
        if value:
            return queryset.filter(tenant__isnull=True)
        else:
            return queryset.filter(tenant__isnull=False)
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(subject_template__icontains=value) |
            Q(notification_type__name__icontains=value) |
            Q(channel__name__icontains=value) |
            Q(tenant__name__icontains=value)
        ) 