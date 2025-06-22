"""
日志保留策略管理视图
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from core.mixins import ResponseMixin
from apps.logger_service.services import LogRetentionPolicyService
from apps.logger_service.serializers import (
    LogRetentionPolicySerializer,
    LogRetentionPolicyDetailSerializer,
    LogRetentionPolicyCreateSerializer,
    LogRetentionPolicyUpdateSerializer
)


class LogRetentionPolicyViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    日志保留策略管理视图集
    
    提供日志保留策略相关的管理API
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogRetentionPolicySerializer
    
    def get_queryset(self):
        """
        获取日志保留策略查询集
        """
        # 管理API可以查看所有策略
        return LogRetentionPolicyService.get_policies()
    
    def get_serializer_class(self):
        """
        获取序列化器类
        """
        if self.action == 'retrieve':
            return LogRetentionPolicyDetailSerializer
        elif self.action == 'create':
            return LogRetentionPolicyCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LogRetentionPolicyUpdateSerializer
        return self.serializer_class
    
    def list(self, request):
        """
        获取日志保留策略列表
        """
        # 获取查询参数
        tenant_id = request.query_params.get('tenant_id')
        category_id = request.query_params.get('category_id')
        is_active = request.query_params.get('is_active')
        
        # 转换布尔值
        if is_active is not None:
            is_active = is_active.lower() == 'true'
        
        # 获取查询集
        queryset = LogRetentionPolicyService.get_policies(
            tenant_id=tenant_id,
            category_id=category_id,
            is_active=is_active
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        获取日志保留策略详情
        """
        policy = LogRetentionPolicyService.get_policy_by_id(pk)
        if not policy:
            return self.get_error_response("日志保留策略不存在", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = self.get_serializer(policy)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建日志保留策略
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 创建策略
        policy = LogRetentionPolicyService.create_policy(
            category=serializer.validated_data['category'],
            tenant=serializer.validated_data.get('tenant'),
            retention_days=serializer.validated_data.get('retention_days', 30),
            is_active=serializer.validated_data.get('is_active', True)
        )
        
        result_serializer = LogRetentionPolicyDetailSerializer(policy)
        return self.get_success_response(
            result_serializer.data, 
            message="日志保留策略创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None, partial=False):
        """
        更新日志保留策略
        """
        policy = LogRetentionPolicyService.get_policy_by_id(pk)
        if not policy:
            return self.get_error_response("日志保留策略不存在", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = self.get_serializer(policy, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 更新策略
        updated_policy = LogRetentionPolicyService.update_policy(
            policy_id=pk,
            **serializer.validated_data
        )
        
        result_serializer = LogRetentionPolicyDetailSerializer(updated_policy)
        return self.get_success_response(
            result_serializer.data, 
            message="日志保留策略更新成功"
        )
    
    def partial_update(self, request, pk=None):
        """
        部分更新日志保留策略
        """
        return self.update(request, pk, partial=True)
    
    def destroy(self, request, pk=None):
        """
        删除日志保留策略
        """
        policy = LogRetentionPolicyService.get_policy_by_id(pk)
        if not policy:
            return self.get_error_response("日志保留策略不存在", status_code=status.HTTP_404_NOT_FOUND)
            
        # 删除策略
        success = LogRetentionPolicyService.delete_policy(pk)
        if not success:
            return self.get_error_response("日志保留策略删除失败")
            
        return self.get_success_response(message="日志保留策略删除成功")
    
    @action(detail=False, methods=['post'])
    def init_default_policies(self, request):
        """
        初始化默认日志保留策略
        """
        created_policies = LogRetentionPolicyService.init_default_policies()
        
        return self.get_success_response({
            'created_count': len(created_policies),
            'policies': LogRetentionPolicySerializer(created_policies, many=True).data
        }, message="默认日志保留策略初始化成功") 