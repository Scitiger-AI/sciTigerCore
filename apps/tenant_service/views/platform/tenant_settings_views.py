"""
租户设置平台视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.mixins import ResponseMixin
from apps.tenant_service.models import TenantSettings
from apps.tenant_service.services import TenantSettingsService
from apps.tenant_service.serializers import (
    TenantSettingsSerializer,
    TenantSettingsUpdateSerializer
)
from apps.tenant_service.permissions import IsTenantMember, IsTenantAdmin


class TenantSettingsViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    租户设置平台视图集
    
    提供租户设置的API接口
    """
    queryset = TenantSettings.objects.all()
    serializer_class = TenantSettingsSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def get_serializer_class(self):
        """
        根据操作选择序列化器
        """
        if self.action in ['update', 'partial_update']:
            return TenantSettingsUpdateSerializer
        return TenantSettingsSerializer
    
    def get_permissions(self):
        """
        根据操作选择权限类
        """
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsTenantAdmin]
        else:
            self.permission_classes = [IsAuthenticated, IsTenantMember]
        
        return super().get_permissions()
    
    def get_object(self):
        """
        获取当前租户的设置
        """
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            return None
            
        return TenantSettingsService.get_tenant_settings(self.request.tenant)
    
    def retrieve(self, request):
        """
        获取当前租户的设置
        """
        settings = self.get_object()
        if not settings:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = self.get_serializer(settings)
        return self.get_success_response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        更新租户设置
        """
        settings = self.get_object()
        if not settings:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = self.get_serializer(settings, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        # 更新租户设置
        settings = TenantSettingsService.update_tenant_settings(
            tenant=request.tenant,
            **serializer.validated_data
        )
        
        return self.get_success_response(
            TenantSettingsSerializer(settings).data,
            message="租户设置已更新"
        )
    
    def partial_update(self, request):
        """
        部分更新租户设置
        """
        return self.update(request, partial=True)
    
    @action(detail=False, methods=['get'])
    def theme(self, request):
        """
        获取租户主题设置
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        theme_settings = TenantSettingsService.get_tenant_theme(request.tenant)
        return self.get_success_response(theme_settings)
    
    @action(detail=False, methods=['get'])
    def localization(self, request):
        """
        获取租户本地化设置
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            return self.get_error_response("未找到当前租户", status_code=status.HTTP_404_NOT_FOUND)
            
        localization_settings = TenantSettingsService.get_tenant_localization(request.tenant)
        return self.get_success_response(localization_settings) 