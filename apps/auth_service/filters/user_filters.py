"""
用户过滤器
"""

import django_filters
from django.db.models import Q
from apps.auth_service.models import User


class UserFilter(django_filters.FilterSet):
    """
    用户过滤器类
    
    提供对用户的高级过滤功能
    """
    # 按用户名或邮箱搜索
    username = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    # 按名字搜索
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    # 按状态过滤
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()
    is_superuser = django_filters.BooleanFilter()
    email_verified = django_filters.BooleanFilter()
    # 按注册时间过滤
    date_joined_after = django_filters.DateTimeFilter(field_name='date_joined', lookup_expr='gte')
    date_joined_before = django_filters.DateTimeFilter(field_name='date_joined', lookup_expr='lte')
    # 按最后登录时间过滤
    last_login_after = django_filters.DateTimeFilter(field_name='last_login', lookup_expr='gte')
    last_login_before = django_filters.DateTimeFilter(field_name='last_login', lookup_expr='lte')
    # 按角色过滤
    role = django_filters.CharFilter(method='filter_by_role')
    # 全局搜索
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = User
        fields = {
            'username': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'is_active': ['exact'],
            'is_staff': ['exact'],
            'is_superuser': ['exact'],
            'email_verified': ['exact'],
        }
    
    def filter_by_role(self, queryset, name, value):
        """
        按角色过滤用户
        """
        if not value:
            return queryset
        
        return queryset.filter(roles__name__icontains=value)
    
    def filter_search(self, queryset, name, value):
        """
        全局搜索，匹配多个字段
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(username__icontains=value) |
            Q(email__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(phone__icontains=value)
        ) 