"""
API密钥平台视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate

from core.mixins import ResponseMixin
from apps.auth_service.services import ApiKeyService
from apps.auth_service.models import ApiKey
from apps.auth_service.filters import ApiKeyFilter, ApiKeyUsageLogFilter
from apps.auth_service.serializers import (
    ApiKeySerializer,
    ApiKeyDetailSerializer,
    SystemApiKeyCreateSerializer,
    UserApiKeyCreateSerializer,
    ApiKeyUpdateSerializer,
    ApiKeyUsageLogSerializer,
    ApiKeyVerifySerializer,
    ApiKeyHashSerializer
)


class ApiKeyViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    API密钥视图集
    
    提供API密钥相关的API
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ApiKeySerializer
    filterset_class = ApiKeyFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'prefix', 'application_name']
    ordering_fields = ['name', 'created_at', 'expires_at', 'last_used_at', 'is_active']
    ordering = ['-created_at']  # 默认按创建时间降序排序
    
    def get_queryset(self):
        """
        获取API密钥查询集
        
        根据当前用户的权限和租户过滤API密钥列表
        """
        # 获取当前租户ID
        tenant_id = self.request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 获取API密钥列表
        if self.action == 'list_user_keys':
            # 用户级API密钥
            return ApiKeyService.get_api_keys(
                tenant_id=tenant_id,
                user_id=self.request.user.id,
                key_type=ApiKey.TYPE_USER
            )
        else:
            # 系统级API密钥
            return ApiKeyService.get_api_keys(
                tenant_id=tenant_id,
                key_type=ApiKey.TYPE_SYSTEM
            )
    
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
        获取系统级API密钥列表，支持过滤、搜索和排序
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
    
    @action(detail=False, methods=['get'])
    def list_user_keys(self, request):
        """
        获取用户级API密钥列表，支持过滤、搜索和排序
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
        
        # 获取当前租户
        current_tenant = getattr(request, 'tenant', None)
        
        # 确定要使用的租户对象
        tenant = serializer.validated_data.get('tenant')
        if not tenant and current_tenant:
            # 使用当前租户
            tenant_to_use = current_tenant
        else:
            # 使用请求中指定的租户
            tenant_to_use = tenant
        
        # 创建API密钥
        api_key, key, error_message = ApiKeyService.create_system_api_key(
            name=serializer.validated_data['name'],
            tenant=tenant_to_use,  # 直接传递租户对象
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
        
        # 获取当前租户和用户
        current_tenant = getattr(request, 'tenant', None)
        current_user = request.user
        
        # 确定要使用的租户对象
        tenant = serializer.validated_data.get('tenant')
        if not tenant and current_tenant:
            tenant_to_use = current_tenant
        else:
            tenant_to_use = tenant
        
        # 确定要使用的用户对象
        user = serializer.validated_data.get('user')
        if not user:
            user_to_use = current_user
        else:
            user_to_use = user
        
        # 获取创建此密钥的系统级密钥对象
        created_by_key = serializer.validated_data.get('created_by_key')
        
        # 创建API密钥
        api_key, key, error_message = ApiKeyService.create_user_api_key(
            name=serializer.validated_data['name'],
            tenant=tenant_to_use,  # 直接传递租户对象
            user=user_to_use,  # 直接传递用户对象
            created_by_key=created_by_key,  # 可能为None
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
        获取API密钥使用日志
        """
        # 获取API密钥
        api_key = ApiKeyService.get_api_key_by_id(pk)
        if not api_key:
            return self.get_error_response("API密钥不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 获取使用日志
        logs = ApiKeyService.get_api_key_usage_logs(api_key_id=pk)
        
        # 应用过滤器
        filterset = ApiKeyUsageLogFilter(request.query_params, queryset=logs)
        filtered_logs = filterset.qs
        
        # 应用排序
        ordering = request.query_params.get('ordering', '-timestamp')
        if ordering:
            if ordering.startswith('-'):
                field = ordering[1:]
                filtered_logs = filtered_logs.order_by(f'-{field}')
            else:
                filtered_logs = filtered_logs.order_by(ordering)
        
        # 使用DRF的分页机制
        page = self.paginate_queryset(filtered_logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # 如果没有分页或分页被禁用，返回所有数据
        serializer = self.get_serializer(filtered_logs, many=True)
        return self.get_success_response(serializer.data)

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
        
        # 检查是否是当前用户的API密钥
        if api_key.user != user:
            return self.get_error_response("API密钥不属于当前用户", status_code=status.HTTP_403_FORBIDDEN)
        
        # 返回密钥哈希
        return self.get_success_response({
            'id': str(api_key.id),
            'name': api_key.name,
            'key_hash': api_key.key_hash,
            'prefix': api_key.prefix
        }, message="API密钥哈希获取成功")


class VerifyApiKeyView(ResponseMixin, APIView):
    """
    API密钥验证视图
    
    提供API密钥验证功能
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        验证API密钥
        """
        # 验证数据
        serializer = ApiKeyVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 验证API密钥
        api_key = ApiKeyService.verify_api_key(
            key=serializer.validated_data['key'],
            service=serializer.validated_data.get('service'),
            resource=serializer.validated_data.get('resource'),
            action=serializer.validated_data.get('action')
        )
        
        if not api_key:
            return self.get_error_response("API密钥无效或不具有所需权限", status_code=status.HTTP_403_FORBIDDEN)
        
        # 返回API密钥信息
        result_serializer = ApiKeyDetailSerializer(api_key)
        return self.get_success_response(result_serializer.data, message="API密钥验证成功") 