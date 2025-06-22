"""
通知记录过滤器
"""

import django_filters
from django.db.models import Q
from apps.notification_service.models import Notification


class NotificationFilter(django_filters.FilterSet):
    """
    通知记录过滤器类
    
    提供对通知记录的高级过滤功能
    """
    # 按主题和内容搜索
    subject = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    
    # 按用户过滤
    user_id = django_filters.UUIDFilter(field_name='user__id')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    
    # 按通知类型过滤
    notification_type_id = django_filters.UUIDFilter(field_name='notification_type__id')
    notification_type_code = django_filters.CharFilter(field_name='notification_type__code')
    notification_type_name = django_filters.CharFilter(field_name='notification_type__name', lookup_expr='icontains')
    notification_type_category = django_filters.CharFilter(field_name='notification_type__category')
    notification_type_priority = django_filters.CharFilter(field_name='notification_type__priority')
    
    # 按通知渠道过滤
    channel_id = django_filters.UUIDFilter(field_name='channel__id')
    channel_code = django_filters.CharFilter(field_name='channel__code')
    channel_type = django_filters.CharFilter(field_name='channel__channel_type')
    
    # 按状态过滤
    status = django_filters.CharFilter()
    is_read = django_filters.BooleanFilter()
    
    # 按时间过滤
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    scheduled_after = django_filters.DateTimeFilter(field_name='scheduled_at', lookup_expr='gte')
    scheduled_before = django_filters.DateTimeFilter(field_name='scheduled_at', lookup_expr='lte')
    sent_after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    read_after = django_filters.DateTimeFilter(field_name='read_at', lookup_expr='gte')
    read_before = django_filters.DateTimeFilter(field_name='read_at', lookup_expr='lte')
    
    # 按租户过滤
    tenant_id = django_filters.UUIDFilter(field_name='tenant__id')
    tenant_name = django_filters.CharFilter(field_name='tenant__name', lookup_expr='icontains')
    
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Notification
        fields = {
            'subject': ['exact', 'icontains'],
            'status': ['exact'],
            'is_read': ['exact'],
            'tenant_id': ['exact'],
            'user_id': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(subject__icontains=value) |
            Q(content__icontains=value) |
            Q(user__username__icontains=value) |
            Q(notification_type__name__icontains=value) |
            Q(channel__name__icontains=value)
        ) 