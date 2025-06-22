"""
日志分类平台视图
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from core.mixins import ResponseMixin
from apps.logger_service.models import LogCategory
from apps.logger_service.services import LogCategoryService
from apps.logger_service.serializers import (
    LogCategorySerializer,
    LogCategoryDetailSerializer,
    LogCategoryCreateSerializer,
    LogCategoryUpdateSerializer
)


class LogCategoryViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    日志分类视图集
    
    提供日志分类相关的API
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogCategorySerializer
    
    def get_queryset(self):
        """
        获取日志分类查询集
        """
        # 平台API只能查看激活的分类
        return LogCategoryService.get_categories(is_active=True)
    
    def get_serializer_class(self):
        """
        获取序列化器类
        """
        if self.action == 'retrieve':
            return LogCategoryDetailSerializer
        elif self.action == 'create':
            return LogCategoryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LogCategoryUpdateSerializer
        return self.serializer_class
    
    def list(self, request):
        """
        获取日志分类列表
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        获取日志分类详情
        """
        category = LogCategoryService.get_category_by_id(pk)
        if not category:
            return self.get_error_response("日志分类不存在", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = self.get_serializer(category)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建日志分类
        
        平台API只能创建非系统分类
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 确保不能创建系统分类
        validated_data = serializer.validated_data.copy()
        validated_data['is_system'] = False
        
        # 创建分类
        category = LogCategoryService.create_category(
            name=validated_data['name'],
            code=validated_data['code'],
            description=validated_data.get('description'),
            is_system=False,
            is_active=validated_data.get('is_active', True)
        )
        
        result_serializer = LogCategoryDetailSerializer(category)
        return self.get_success_response(
            result_serializer.data, 
            message="日志分类创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None, partial=False):
        """
        更新日志分类
        
        平台API只能更新非系统分类
        """
        category = LogCategoryService.get_category_by_id(pk)
        if not category:
            return self.get_error_response("日志分类不存在", status_code=status.HTTP_404_NOT_FOUND)
            
        # 不允许更新系统分类
        if category.is_system:
            return self.get_error_response("不能修改系统分类", status_code=status.HTTP_403_FORBIDDEN)
            
        serializer = self.get_serializer(category, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 更新分类
        updated_category = LogCategoryService.update_category(
            category_id=pk,
            **serializer.validated_data
        )
        
        result_serializer = LogCategoryDetailSerializer(updated_category)
        return self.get_success_response(
            result_serializer.data, 
            message="日志分类更新成功"
        )
    
    def partial_update(self, request, pk=None):
        """
        部分更新日志分类
        """
        return self.update(request, pk, partial=True)
    
    def destroy(self, request, pk=None):
        """
        删除日志分类
        
        平台API只能删除非系统分类
        """
        category = LogCategoryService.get_category_by_id(pk)
        if not category:
            return self.get_error_response("日志分类不存在", status_code=status.HTTP_404_NOT_FOUND)
            
        # 不允许删除系统分类
        if category.is_system:
            return self.get_error_response("不能删除系统分类", status_code=status.HTTP_403_FORBIDDEN)
            
        # 删除分类
        success = LogCategoryService.delete_category(pk)
        if not success:
            return self.get_error_response("日志分类删除失败")
            
        return self.get_success_response(message="日志分类删除成功") 