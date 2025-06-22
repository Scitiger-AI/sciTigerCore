"""
用户通知偏好设置过滤器
"""

import django_filters
from django.db.models import Q
from apps.notification_service.models import UserNotificationPreference


class UserNotificationPreferenceFilter(django_filters.FilterSet):
    """
    用户通知偏好设置过滤器类
    
    提供对用户通知偏好设置的高级过滤功能
    """
    # 按用户过滤
    user_id = django_filters.UUIDFilter(field_name='user__id')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    
    # 按通知类型过滤
    notification_type_id = django_filters.UUIDFilter(field_name='notification_type__id')
    notification_type_code = django_filters.CharFilter(field_name='notification_type__code')
    notification_type_name = django_filters.CharFilter(field_name='notification_type__name', lookup_expr='icontains')
    notification_type_category = django_filters.CharFilter(field_name='notification_type__category')
    
    # 按渠道启用状态过滤
    email_enabled = django_filters.BooleanFilter()
    sms_enabled = django_filters.BooleanFilter()
    in_app_enabled = django_filters.BooleanFilter()
    push_enabled = django_filters.BooleanFilter()
    
    # 按免打扰设置过滤
    do_not_disturb_enabled = django_filters.BooleanFilter()
    urgent_bypass_dnd = django_filters.BooleanFilter()
    
    # 按租户过滤
    tenant_id = django_filters.UUIDFilter(field_name='tenant__id')
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
        model = UserNotificationPreference
        fields = {
            'user_id': ['exact'],
            'notification_type_id': ['exact'],
            'email_enabled': ['exact'],
            'sms_enabled': ['exact'],
            'in_app_enabled': ['exact'],
            'push_enabled': ['exact'],
            'do_not_disturb_enabled': ['exact'],
            'urgent_bypass_dnd': ['exact'],
            'tenant_id': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(user__email__icontains=value) |
            Q(notification_type__name__icontains=value) |
            Q(notification_type__code__icontains=value) |
            Q(tenant__name__icontains=value)
        ) 