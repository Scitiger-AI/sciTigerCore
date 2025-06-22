"""
租户配额过滤器
"""

import django_filters
from django.db.models import Q
from apps.tenant_service.models import TenantQuota


class TenantQuotaFilter(django_filters.FilterSet):
    """
    租户配额过滤器类
    
    提供对租户配额的高级过滤功能
    """
    # 按租户名称搜索
    tenant_name = django_filters.CharFilter(field_name='tenant__name', lookup_expr='icontains')
    # 按租户标识符搜索
    tenant_slug = django_filters.CharFilter(field_name='tenant__slug', lookup_expr='icontains')
    # 按用户配额过滤
    max_users_min = django_filters.NumberFilter(field_name='max_users', lookup_expr='gte')
    max_users_max = django_filters.NumberFilter(field_name='max_users', lookup_expr='lte')
    # 按API配额过滤
    max_api_keys_min = django_filters.NumberFilter(field_name='max_api_keys', lookup_expr='gte')
    max_api_keys_max = django_filters.NumberFilter(field_name='max_api_keys', lookup_expr='lte')
    max_api_requests_min = django_filters.NumberFilter(field_name='max_api_requests_per_day', lookup_expr='gte')
    max_api_requests_max = django_filters.NumberFilter(field_name='max_api_requests_per_day', lookup_expr='lte')
    # 按存储配额过滤
    max_storage_min = django_filters.NumberFilter(field_name='max_storage_gb', lookup_expr='gte')
    max_storage_max = django_filters.NumberFilter(field_name='max_storage_gb', lookup_expr='lte')
    # 按使用统计过滤
    current_user_count_min = django_filters.NumberFilter(field_name='current_user_count', lookup_expr='gte')
    current_user_count_max = django_filters.NumberFilter(field_name='current_user_count', lookup_expr='lte')
    current_storage_used_min = django_filters.NumberFilter(field_name='current_storage_used_gb', lookup_expr='gte')
    current_storage_used_max = django_filters.NumberFilter(field_name='current_storage_used_gb', lookup_expr='lte')
    # 按资源使用率过滤（自定义过滤器）
    user_quota_usage = django_filters.NumberFilter(method='filter_user_quota_usage')
    storage_quota_usage = django_filters.NumberFilter(method='filter_storage_quota_usage')
    # 按创建时间过滤
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    # 按更新时间过滤
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = TenantQuota
        fields = {
            'tenant_id': ['exact'],
            'max_users': ['exact', 'gt', 'lt'],
            'max_api_keys': ['exact', 'gt', 'lt'],
            'max_api_requests_per_day': ['exact', 'gt', 'lt'],
            'max_storage_gb': ['exact', 'gt', 'lt'],
            'max_log_retention_days': ['exact', 'gt', 'lt'],
            'max_notifications_per_day': ['exact', 'gt', 'lt'],
        }
    
    def filter_user_quota_usage(self, queryset, name, value):
        """
        按用户配额使用率过滤
        
        value: 使用率百分比（0-100）
        """
        if value is None:
            return queryset
            
        # 计算使用率为指定百分比的记录
        # 使用率 = (current_user_count / max_users) * 100
        from django.db.models.expressions import ExpressionWrapper, F
        from django.db.models import FloatField
        
        usage_expr = ExpressionWrapper(
            (F('current_user_count') * 100.0) / F('max_users'),
            output_field=FloatField()
        )
        
        # 添加使用率作为注解
        queryset = queryset.annotate(user_quota_usage=usage_expr)
        
        # 过滤使用率大于等于指定值的记录
        return queryset.filter(user_quota_usage__gte=value)
    
    def filter_storage_quota_usage(self, queryset, name, value):
        """
        按存储配额使用率过滤
        
        value: 使用率百分比（0-100）
        """
        if value is None:
            return queryset
            
        # 计算使用率为指定百分比的记录
        # 使用率 = (current_storage_used_gb / max_storage_gb) * 100
        from django.db.models.expressions import ExpressionWrapper, F
        from django.db.models import FloatField
        
        usage_expr = ExpressionWrapper(
            (F('current_storage_used_gb') * 100.0) / F('max_storage_gb'),
            output_field=FloatField()
        )
        
        # 添加使用率作为注解
        queryset = queryset.annotate(storage_quota_usage=usage_expr)
        
        # 过滤使用率大于等于指定值的记录
        return queryset.filter(storage_quota_usage__gte=value)
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(tenant__name__icontains=value) |
            Q(tenant__slug__icontains=value)
        ) 