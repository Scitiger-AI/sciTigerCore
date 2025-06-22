"""
日志条目平台视图
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from core.mixins import ResponseMixin
from apps.logger_service.services import LoggerService
from apps.logger_service.serializers import (
    LogEntrySerializer,
    LogEntryDetailSerializer,
    LogEntryCreateSerializer,
    LogEntryBatchCreateSerializer
)


class LogEntryViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    日志条目视图集
    
    提供日志条目相关的API
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogEntrySerializer
    
    def get_serializer_class(self):
        """
        获取序列化器类
        """
        if self.action == 'retrieve':
            return LogEntryDetailSerializer
        elif self.action == 'create':
            return LogEntryCreateSerializer
        elif self.action == 'batch_create':
            return LogEntryBatchCreateSerializer
        return self.serializer_class
    
    def list(self, request):
        """
        获取日志条目列表
        """
        # 获取当前租户ID
        tenant_id = None
        if hasattr(request, 'tenant') and request.tenant:
            tenant_id = str(request.tenant.id)
            
        # 获取查询参数
        category_id = request.query_params.get('category_id')
        level = request.query_params.get('level')
        source = request.query_params.get('source')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        search_text = request.query_params.get('search_text')
        
        # 分页参数
        try:
            page = int(request.query_params.get('page', 1))
            page_size = min(int(request.query_params.get('page_size', 20)), 100)
        except ValueError:
            page = 1
            page_size = 20
            
        # 排序参数
        sort_field = request.query_params.get('sort_field', 'timestamp')
        sort_order = -1 if request.query_params.get('sort_order', 'desc').lower() == 'desc' else 1
        
        # 查询日志
        logs, total = LoggerService.get_logs(
            tenant_id=tenant_id,
            category_id=category_id,
            user_id=None,  # 平台API不支持按用户过滤
            level=level,
            start_time=start_time,
            end_time=end_time,
            source=source,
            search_text=search_text,
            page=page,
            page_size=page_size,
            sort_field=sort_field,
            sort_order=sort_order
        )
        
        # 序列化结果
        serializer = self.get_serializer(logs, many=True)
        
        # 构建分页响应
        return self.get_success_response({
            'results': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        })
    
    def retrieve(self, request, pk=None):
        """
        获取日志条目详情
        """
        # 获取当前租户ID
        tenant_id = None
        if hasattr(request, 'tenant') and request.tenant:
            tenant_id = str(request.tenant.id)
            
        # 获取日志
        log = LoggerService.get_log_by_id(pk)
        
        if not log:
            return self.get_error_response("日志条目不存在", status_code=status.HTTP_404_NOT_FOUND)
            
        # 检查租户权限
        if tenant_id and log.get('tenant_id') != tenant_id:
            return self.get_error_response("无权访问此日志", status_code=status.HTTP_403_FORBIDDEN)
            
        serializer = self.get_serializer(log)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建日志条目
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        log_data = serializer.save()
        
        return self.get_success_response(
            log_data, 
            message="日志条目创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        """
        批量创建日志条目
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        logs_data = serializer.save()
        
        return self.get_success_response(
            logs_data, 
            message=f"成功创建{len(logs_data)}条日志",
            status_code=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        获取日志统计信息
        """
        # 获取当前租户ID
        tenant_id = None
        if hasattr(request, 'tenant') and request.tenant:
            tenant_id = str(request.tenant.id)
            
        # 获取统计天数
        try:
            days = int(request.query_params.get('days', 7))
            days = min(max(days, 1), 30)  # 限制范围1-30天
        except ValueError:
            days = 7
            
        # 获取统计信息
        stats = LoggerService.get_log_stats(tenant_id=tenant_id, days=days)
        
        return self.get_success_response(stats) 