"""
租户配额平台视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.mixins import ResponseMixin
from apps.tenant_service.models import TenantQuota
from apps.tenant_service.services import TenantQuotaService
from apps.tenant_service.serializers import TenantQuotaSerializer
from apps.tenant_service.permissions import IsTenantMember, IsTenantAdmin


class TenantQuotaViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    租户配额平台视图集
    
    提供租户配额的API接口
    """
    queryset = TenantQuota.objects.all()
    serializer_class = TenantQuotaSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def get_object(self):
        """
        获取当前租户的配额
        """
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            return None
            
        return TenantQuotaService.get_tenant_quota(self.request.tenant)
    
    def retrieve(self, request):
        """
        获取当前租户的配额
        """
        quota = self.get_object()
        if not quota:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = self.get_serializer(quota)
        return self.get_success_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def check_user_quota(self, request):
        """
        检查用户配额是否已满
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        has_quota = TenantQuotaService.check_user_quota(request.tenant)
        return self.get_success_response({
            'has_quota': has_quota
        })
    
    @action(detail=False, methods=['get'])
    def check_storage_quota(self, request):
        """
        检查存储配额是否足够
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        required_space = int(request.query_params.get('required_space', 0))
        has_quota = TenantQuotaService.check_storage_quota(request.tenant, required_space)
        return self.get_success_response({
            'has_quota': has_quota
        })
    
    @action(detail=False, methods=['get'])
    def check_project_quota(self, request):
        """
        检查项目配额是否已满
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        has_quota = TenantQuotaService.check_project_quota(request.tenant)
        return self.get_success_response({
            'has_quota': has_quota
        })
    
    @action(detail=False, methods=['get'])
    def check_api_call_quota(self, request):
        """
        检查API调用配额是否已满
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        has_quota = TenantQuotaService.check_api_call_quota(request.tenant)
        return self.get_success_response({
            'has_quota': has_quota
        }) 