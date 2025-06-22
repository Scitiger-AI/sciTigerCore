"""
API密钥过滤器
"""

import django_filters
from django.db.models import Q
from apps.auth_service.models import ApiKey, ApiKeyScope, ApiKeyUsageLog


class ApiKeyFilter(django_filters.FilterSet):
    """
    API密钥过滤器类
    
    提供对API密钥的高级过滤功能
    """
    # 按名称搜索
    name = django_filters.CharFilter(lookup_expr='icontains')
    prefix = django_filters.CharFilter(lookup_expr='icontains')
    # 按类型过滤
    key_type = django_filters.ChoiceFilter(choices=ApiKey.TYPE_CHOICES)
    # 按状态过滤
    is_active = django_filters.BooleanFilter()
    is_expired = django_filters.BooleanFilter(method='filter_is_expired')
    # 按租户过滤
    tenant_id = django_filters.UUIDFilter(field_name='tenant__id')
    tenant_name = django_filters.CharFilter(field_name='tenant__name', lookup_expr='icontains')
    # 按用户过滤
    user_id = django_filters.UUIDFilter(field_name='user__id')
    user_email = django_filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    user_username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    # 按应用名称过滤
    application_name = django_filters.CharFilter(lookup_expr='icontains')
    # 按时间过滤
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    expires_after = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='gte')
    expires_before = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='lte')
    last_used_after = django_filters.DateTimeFilter(field_name='last_used_at', lookup_expr='gte')
    last_used_before = django_filters.DateTimeFilter(field_name='last_used_at', lookup_expr='lte')
    # 按作用域过滤
    has_scope = django_filters.CharFilter(method='filter_has_scope')
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = ApiKey
        fields = {
            'name': ['exact', 'icontains'],
            'prefix': ['exact', 'icontains'],
            'key_type': ['exact'],
            'is_active': ['exact'],
            'tenant_id': ['exact'],
            'user_id': ['exact'],
            'application_name': ['exact', 'icontains'],
        }
    
    def filter_is_expired(self, queryset, name, value):
        """
        过滤已过期的API密钥
        """
        from django.utils import timezone
        now = timezone.now()
        
        if value:  # 过滤已过期的API密钥
            return queryset.filter(
                Q(expires_at__isnull=False) & Q(expires_at__lt=now)
            )
        else:  # 过滤未过期的API密钥
            return queryset.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            )
    
    def filter_has_scope(self, queryset, name, value):
        """
        过滤具有特定作用域的API密钥
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(scopes__service__icontains=value) |
            Q(scopes__resource__icontains=value) |
            Q(scopes__action__icontains=value)
        ).distinct()
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(name__icontains=value) |
            Q(prefix__icontains=value) |
            Q(application_name__icontains=value) |
            Q(tenant__name__icontains=value) |
            Q(user__username__icontains=value) |
            Q(user__email__icontains=value)
        ).distinct()


class ApiKeyScopeFilter(django_filters.FilterSet):
    """
    API密钥作用域过滤器类
    
    提供对API密钥作用域的高级过滤功能
    """
    # 按API密钥过滤
    api_key_id = django_filters.UUIDFilter(field_name='api_key__id')
    api_key_name = django_filters.CharFilter(field_name='api_key__name', lookup_expr='icontains')
    api_key_prefix = django_filters.CharFilter(field_name='api_key__prefix', lookup_expr='icontains')
    # 按作用域过滤
    service = django_filters.CharFilter(lookup_expr='icontains')
    resource = django_filters.CharFilter(lookup_expr='icontains')
    action = django_filters.CharFilter(lookup_expr='icontains')
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = ApiKeyScope
        fields = {
            'api_key_id': ['exact'],
            'service': ['exact', 'icontains'],
            'resource': ['exact', 'icontains'],
            'action': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(service__icontains=value) |
            Q(resource__icontains=value) |
            Q(action__icontains=value) |
            Q(api_key__name__icontains=value)
        ).distinct()


class ApiKeyUsageLogFilter(django_filters.FilterSet):
    """
    API密钥使用日志过滤器类
    
    提供对API密钥使用日志的高级过滤功能
    """
    # 按API密钥过滤
    api_key_id = django_filters.UUIDFilter(field_name='api_key__id')
    api_key_name = django_filters.CharFilter(field_name='api_key__name', lookup_expr='icontains')
    api_key_prefix = django_filters.CharFilter(field_name='api_key__prefix', lookup_expr='icontains')
    # 按租户过滤
    tenant_id = django_filters.UUIDFilter(field_name='tenant__id')
    tenant_name = django_filters.CharFilter(field_name='tenant__name', lookup_expr='icontains')
    # 按请求过滤
    request_path = django_filters.CharFilter(lookup_expr='icontains')
    request_method = django_filters.CharFilter(lookup_expr='icontains')
    response_status = django_filters.NumberFilter()
    response_status_gte = django_filters.NumberFilter(field_name='response_status', lookup_expr='gte')
    response_status_lte = django_filters.NumberFilter(field_name='response_status', lookup_expr='lte')
    client_ip = django_filters.CharFilter(lookup_expr='icontains')
    request_id = django_filters.CharFilter(lookup_expr='icontains')
    # 按时间过滤
    timestamp_after = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    timestamp_before = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = ApiKeyUsageLog
        fields = {
            'api_key_id': ['exact'],
            'tenant_id': ['exact'],
            'request_path': ['exact', 'icontains'],
            'request_method': ['exact', 'icontains'],
            'response_status': ['exact'],
            'client_ip': ['exact', 'icontains'],
            'request_id': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(request_path__icontains=value) |
            Q(client_ip__icontains=value) |
            Q(request_id__icontains=value) |
            Q(api_key__name__icontains=value) |
            Q(tenant__name__icontains=value)
        ).distinct() 