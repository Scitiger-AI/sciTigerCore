"""
API密钥管理视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate

from core.mixins import ResponseMixin
from apps.auth_service.services import ApiKeyService
from apps.auth_service.filters import ApiKeyFilter, ApiKeyUsageLogFilter
from apps.auth_service.serializers import (
    ApiKeySerializer,
    ApiKeyDetailSerializer,
    SystemApiKeyCreateSerializer,
    UserApiKeyCreateSerializer,
    ApiKeyUpdateSerializer,
    ApiKeyUsageLogSerializer,
    ApiKeyHashSerializer
)


class ApiKeyManagementViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    API密钥管理视图集
    
    提供API密钥管理相关的API
    """
    permission_classes = [IsAdminUser]
    serializer_class = ApiKeySerializer
    filterset_class = ApiKeyFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'prefix', 'application_name', 'user__username', 'user__email', 'tenant__name']
    ordering_fields = ['name', 'created_at', 'expires_at', 'last_used_at', 'is_active', 'key_type']
    ordering = ['-created_at']  # 默认按创建时间降序排序
    
    def get_queryset(self):
        """
        获取API密钥查询集
        
        管理员可以查看所有API密钥
        """
         # 获取当前租户ID
        tenant_id = self.request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 超级管理员可以查看所有租户的API密钥
        if self.request.user.is_superuser:
            return ApiKeyService.get_api_keys(tenant_id=tenant_id)
        
        # 租户管理员只能查看自己租户的API密钥
        return ApiKeyService.get_api_keys(tenant_id=tenant_id)
    
    def get_serializer_class(self):
        """
        获取序列化器类
        
        根据不同的操作返回不同的序列化器
        """
        if self.action == 'retrieve':
            return ApiKeyDetailSerializer
        elif self.action == 'create_system_key':
            return SystemApiKeyCreateSerializer
        elif self.action == 'create_user_key':
            return UserApiKeyCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ApiKeyUpdateSerializer
        elif self.action == 'usage_logs':
            return ApiKeyUsageLogSerializer
        elif self.action == 'get_key_hash':
            return ApiKeyHashSerializer
        return self.serializer_class
    
    def get_serializer_context(self):
        """
        获取序列化器上下文
        
        为序列化器提供额外的上下文数据
        """
        context = super().get_serializer_context()
        
        # 添加租户查询集
        from apps.tenant_service.models import Tenant
        context['tenant_queryset'] = Tenant.objects.all()
        
        # 添加用户查询集
        from apps.auth_service.models import User
        context['user_queryset'] = User.objects.all()
        
        # 添加API密钥查询集
        from apps.auth_service.models import ApiKey
        context['api_key_queryset'] = ApiKey.objects.filter(key_type=ApiKey.TYPE_SYSTEM)
        
        return context
    
    def list(self, request):
        """
        获取API密钥列表，支持过滤、搜索和排序
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # 使用DRF的分页机制
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # 如果没有分页或分页被禁用，返回所有数据
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        获取API密钥详情
        """
        api_key = ApiKeyService.get_api_key_by_id(pk)
        if not api_key:
            return self.get_error_response("API密钥不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(api_key)
        return self.get_success_response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_system_key(self, request):
        """
        创建系统级API密钥
        """
        # 验证数据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 创建API密钥
        api_key, key, error_message = ApiKeyService.create_system_api_key(
            name=serializer.validated_data['name'],
            tenant=serializer.validated_data['tenant'],
            application_name=serializer.validated_data.get('application_name'),
            expires_in_days=serializer.validated_data.get('expires_in_days'),
            scopes=serializer.validated_data.get('scopes'),
            is_active=serializer.validated_data.get('is_active', True),
            metadata=serializer.validated_data.get('metadata', {})
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回创建的API密钥信息
        result_serializer = ApiKeyDetailSerializer(api_key)
        return self.get_success_response({
            'api_key': result_serializer.data,
            'key': key  # 明文密钥，只会在创建时返回一次
        }, message="系统级API密钥创建成功", status_code=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def create_user_key(self, request):
        """
        创建用户级API密钥
        """
        # 验证数据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 创建API密钥
        api_key, key, error_message = ApiKeyService.create_user_api_key(
            name=serializer.validated_data['name'],
            user=serializer.validated_data['user'],
            tenant=serializer.validated_data.get('tenant'),
            expires_in_days=serializer.validated_data.get('expires_in_days'),
            scopes=serializer.validated_data.get('scopes'),
            created_by_key=serializer.validated_data.get('created_by_key'),
            is_active=serializer.validated_data.get('is_active', True),
            metadata=serializer.validated_data.get('metadata', {})
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回创建的API密钥信息
        result_serializer = ApiKeyDetailSerializer(api_key)
        return self.get_success_response({
            'api_key': result_serializer.data,
            'key': key  # 明文密钥，只会在创建时返回一次
        }, message="用户级API密钥创建成功", status_code=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None, partial=False):
        """
        更新API密钥
        """
        # 获取API密钥
        api_key = ApiKeyService.get_api_key_by_id(pk)
        if not api_key:
            return self.get_error_response("API密钥不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 验证数据
        serializer = self.get_serializer(api_key, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 更新API密钥
        updated_api_key, error_message = ApiKeyService.update_api_key(
            api_key_id=pk,
            **serializer.validated_data
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回更新后的API密钥信息
        result_serializer = ApiKeyDetailSerializer(updated_api_key)
        return self.get_success_response(result_serializer.data, message="API密钥更新成功")
    
    def partial_update(self, request, pk=None):
        """
        部分更新API密钥
        """
        return self.update(request, pk, partial=True)
    
    def destroy(self, request, pk=None):
        """
        删除API密钥
        """
        # 删除API密钥
        success = ApiKeyService.delete_api_key(pk)
        
        if not success:
            return self.get_error_response("API密钥删除失败，可能是API密钥不存在")
        
        return self.get_success_response(message="API密钥删除成功")
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        激活API密钥
        """
        # 激活API密钥
        api_key, error_message = ApiKeyService.change_api_key_status(pk, True)
        
        if error_message:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="API密钥已激活")
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        禁用API密钥
        """
        # 禁用API密钥
        api_key, error_message = ApiKeyService.change_api_key_status(pk, False)
        
        if error_message:
            return self.get_error_response(error_message)
        
        return self.get_success_response(message="API密钥已禁用")
    
    @action(detail=True, methods=['get'])
    def usage_logs(self, request, pk=None):
        """
        获取API密钥使用日志，支持过滤、搜索和排序
        """
        # 获取API密钥
        api_key = ApiKeyService.get_api_key_by_id(pk)
        if not api_key:
            return self.get_error_response("API密钥不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 获取使用日志
        logs = ApiKeyService.get_api_key_usage_logs(api_key_id=pk)
        
        # 应用过滤器
        filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
        
        # 临时保存当前的filterset_class和ordering相关配置
        original_filterset_class = self.filterset_class
        original_ordering_fields = getattr(self, 'ordering_fields', None)
        original_ordering = getattr(self, 'ordering', None)
        
        try:
            # 设置正确的过滤器类和排序字段
            from apps.auth_service.filters import ApiKeyUsageLogFilter
            self.filterset_class = ApiKeyUsageLogFilter
            
            # 为ApiKeyUsageLog设置正确的排序字段
            self.ordering_fields = ['timestamp', 'response_status', 'request_method', 'request_path', 'client_ip']
            self.ordering = ['-timestamp']  # 默认按时间戳降序排序
            
            # 过滤查询集
            for backend in filter_backends:
                logs = backend().filter_queryset(request, logs, self)
            
            # 分页
            page = self.paginate_queryset(logs)
            if page is not None:
                serializer = ApiKeyUsageLogSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = ApiKeyUsageLogSerializer(logs, many=True)
            return self.get_success_response(serializer.data)
        finally:
            # 恢复原始配置
            self.filterset_class = original_filterset_class
            self.ordering_fields = original_ordering_fields
            self.ordering = original_ordering
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        获取API密钥统计信息
        """
        # 获取当前租户ID
        tenant_id = getattr(request, 'tenant', None)
        tenant_id = tenant_id.id if tenant_id else None
        
        # 获取统计信息
        stats = ApiKeyService.get_api_key_stats(tenant_id=tenant_id)
        
        return self.get_success_response(stats)
    
    @action(detail=False, methods=['post'])
    def get_key_hash(self, request):
        """
        获取API密钥哈希
        
        该接口需要验证用户密码才能返回API密钥的哈希值，增加安全性
        
        请求体格式：
        {
            "api_key_id": "API密钥ID",
            "password": "用户密码"
        }
        """
        # 验证数据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取当前用户
        user = request.user
        if not user.is_active:
            return self.get_error_response("用户未激活", status_code=status.HTTP_403_FORBIDDEN)
        
        # 验证用户密码
        if not authenticate(username=user.email, password=serializer.validated_data['password']):
            return self.get_error_response("密码不正确", status_code=status.HTTP_401_UNAUTHORIZED)
        
        # 获取API密钥
        api_key = ApiKeyService.get_api_key_by_id(serializer.validated_data['api_key_id'])
        if not api_key:
            return self.get_error_response("API密钥不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 检查权限（只有超级管理员或密钥所属租户的管理员可以查看）
        if not user.is_superuser:
            from apps.tenant_service.models import TenantUser
            tenant_user = TenantUser.objects.filter(user=user, tenant=api_key.tenant).first()
            if not tenant_user or not tenant_user.is_admin:
                return self.get_error_response("没有权限查看此API密钥的哈希", status_code=status.HTTP_403_FORBIDDEN)
        
        # 返回密钥哈希
        return self.get_success_response({
            'id': str(api_key.id),
            'name': api_key.name,
            'key_hash': api_key.key_hash,
            'prefix': api_key.prefix
        }, message="API密钥哈希获取成功") 