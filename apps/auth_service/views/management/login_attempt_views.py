"""
登录尝试管理视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from core.mixins import ResponseMixin
from apps.auth_service.models import LoginAttempt
from apps.auth_service.filters import LoginAttemptFilter
from apps.auth_service.serializers.login_attempt_serializers import (
    LoginAttemptSerializer,
    LoginAttemptDetailSerializer
)


class LoginAttemptManagementViewSet(ResponseMixin, viewsets.ReadOnlyModelViewSet):
    """
    登录尝试管理视图集
    
    提供管理员查看登录尝试记录的功能
    """
    permission_classes = [IsAdminUser]
    serializer_class = LoginAttemptSerializer
    filterset_class = LoginAttemptFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['email', 'ip_address', 'user_agent', 'reason']
    ordering_fields = ['timestamp', 'email', 'status', 'is_admin_login']
    ordering = ['-timestamp']  # 默认按时间降序排序
    
    def get_queryset(self):
        """
        获取登录尝试记录查询集
        
        超级管理员可以查看所有记录，普通管理员只能查看自己租户的记录
        """
        # 获取当前租户ID
        tenant_id = self.request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 超级管理员可以查看所有租户的记录
        if self.request.user.is_superuser:
            return LoginAttempt.objects.filter(tenant_id=tenant_id)
        
        # 租户管理员只能查看自己租户的记录
        return LoginAttempt.objects.filter(tenant_id=tenant_id)
    
    def get_serializer_class(self):
        """
        根据不同的操作返回不同的序列化器
        """
        if self.action == 'retrieve':
            return LoginAttemptDetailSerializer
        return LoginAttemptSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        获取登录尝试统计信息
        """
        # 获取查询集
        queryset = self.filter_queryset(self.get_queryset())
        
        # 计算时间范围
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # 总体统计
        total_attempts = queryset.count()
        success_attempts = queryset.filter(status=LoginAttempt.STATUS_SUCCESS).count()
        failed_attempts = queryset.filter(status=LoginAttempt.STATUS_FAILED).count()
        blocked_attempts = queryset.filter(status=LoginAttempt.STATUS_BLOCKED).count()
        admin_attempts = queryset.filter(is_admin_login=True).count()
        user_attempts = queryset.filter(is_admin_login=False).count()
        
        # 时间范围统计
        last_24h_attempts = queryset.filter(timestamp__gte=last_24h).count()
        last_7d_attempts = queryset.filter(timestamp__gte=last_7d).count()
        last_30d_attempts = queryset.filter(timestamp__gte=last_30d).count()
        
        # 失败原因统计
        reason_stats = list(queryset.filter(
            status=LoginAttempt.STATUS_FAILED
        ).values('reason').annotate(
            count=Count('id')
        ).order_by('-count')[:10])
        
        # IP地址统计
        ip_stats = list(queryset.values('ip_address').annotate(
            count=Count('id')
        ).order_by('-count')[:10])
        
        # 返回统计结果
        return self.get_success_response({
            'total': total_attempts,
            'success': success_attempts,
            'failed': failed_attempts,
            'blocked': blocked_attempts,
            'admin_login': admin_attempts,
            'user_login': user_attempts,
            'time_ranges': {
                'last_24h': last_24h_attempts,
                'last_7d': last_7d_attempts,
                'last_30d': last_30d_attempts
            },
            'reasons': reason_stats,
            'ip_addresses': ip_stats
        })
    
    @action(detail=False, methods=['get'])
    def failed_login_stats(self, request):
        """
        获取失败登录尝试统计信息
        """
        # 获取查询集
        queryset = self.filter_queryset(self.get_queryset()).filter(
            status=LoginAttempt.STATUS_FAILED
        )
        
        # 计算时间范围
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # 失败登录统计
        total_failed = queryset.count()
        failed_24h = queryset.filter(timestamp__gte=last_24h).count()
        failed_7d = queryset.filter(timestamp__gte=last_7d).count()
        
        # 按IP地址统计
        ip_stats = list(queryset.values('ip_address').annotate(
            count=Count('id')
        ).order_by('-count')[:10])
        
        # 按邮箱统计
        email_stats = list(queryset.values('email').annotate(
            count=Count('id')
        ).order_by('-count')[:10])
        
        # 按失败原因统计
        reason_stats = list(queryset.values('reason').annotate(
            count=Count('id')
        ).order_by('-count')[:10])
        
        # 按时间分布统计
        hourly_stats = list(queryset.filter(
            timestamp__gte=last_24h
        ).extra(
            select={'hour': "EXTRACT(hour FROM timestamp)"}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour'))
        
        # 返回统计结果
        return self.get_success_response({
            'total_failed': total_failed,
            'failed_24h': failed_24h,
            'failed_7d': failed_7d,
            'ip_stats': ip_stats,
            'email_stats': email_stats,
            'reason_stats': reason_stats,
            'hourly_stats': hourly_stats
        }) 