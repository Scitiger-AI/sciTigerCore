"""
日志保留策略平台视图
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
    日志保留策略视图集
    
    提供日志保留策略相关的API
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogRetentionPolicySerializer
    
    def get_queryset(self):
        """
        获取日志保留策略查询集
        """
        # 获取当前租户ID
        tenant_id = None
        if hasattr(self.request, 'tenant') and self.request.tenant:
            tenant_id = self.request.tenant.id
            
        # 平台API只能查看当前租户的策略和全局策略
        return LogRetentionPolicyService.get_policies(
            tenant_id=tenant_id,
            is_active=True
        ).union(
            LogRetentionPolicyService.get_policies(
                tenant_id=None,
                is_active=True
            )
        )
    
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
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        获取日志保留策略详情
        """
        policy = LogRetentionPolicyService.get_policy_by_id(pk)
        if not policy:
            return self.get_error_response("日志保留策略不存在", status_code=status.HTTP_404_NOT_FOUND)
            
        # 检查权限
        tenant_id = getattr(request.tenant, 'id', None) if hasattr(request, 'tenant') else None
        if policy.tenant_id and policy.tenant_id != tenant_id:
            return self.get_error_response("无权访问此日志保留策略", status_code=status.HTTP_403_FORBIDDEN)
            
        serializer = self.get_serializer(policy)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建日志保留策略
        
        平台API只能为当前租户创建策略
        """
        # 获取当前租户
        tenant = getattr(request, 'tenant', None) if hasattr(request, 'tenant') else None
        if not tenant:
            return self.get_error_response("无法确定当前租户", status_code=status.HTTP_400_BAD_REQUEST)
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 确保使用当前租户
        validated_data = serializer.validated_data.copy()
        validated_data['tenant'] = tenant
        
        # 创建策略
        policy = LogRetentionPolicyService.create_policy(
            category=validated_data['category'],
            tenant=tenant,
            retention_days=validated_data.get('retention_days', 30),
            is_active=validated_data.get('is_active', True)
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
        
        平台API只能更新当前租户的策略
        """
        policy = LogRetentionPolicyService.get_policy_by_id(pk)
        if not policy:
            return self.get_error_response("日志保留策略不存在", status_code=status.HTTP_404_NOT_FOUND)
            
        # 检查权限
        tenant_id = getattr(request.tenant, 'id', None) if hasattr(request, 'tenant') else None
        if not policy.tenant_id or policy.tenant_id != tenant_id:
            return self.get_error_response("无权修改此日志保留策略", status_code=status.HTTP_403_FORBIDDEN)
            
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
        
        平台API只能删除当前租户的策略
        """
        policy = LogRetentionPolicyService.get_policy_by_id(pk)
        if not policy:
            return self.get_error_response("日志保留策略不存在", status_code=status.HTTP_404_NOT_FOUND)
            
        # 检查权限
        tenant_id = getattr(request.tenant, 'id', None) if hasattr(request, 'tenant') else None
        if not policy.tenant_id or policy.tenant_id != tenant_id:
            return self.get_error_response("无权删除此日志保留策略", status_code=status.HTTP_403_FORBIDDEN)
            
        # 删除策略
        success = LogRetentionPolicyService.delete_policy(pk)
        if not success:
            return self.get_error_response("日志保留策略删除失败")
            
        return self.get_success_response(message="日志保留策略删除成功") 