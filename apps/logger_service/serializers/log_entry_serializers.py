"""
日志条目序列化器
"""

from rest_framework import serializers
from apps.logger_service.models import LogEntry, LogCategory


class LogEntrySerializer(serializers.Serializer):
    """
    日志条目序列化器
    """
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    tenant_name = serializers.CharField(read_only=True, required=False)
    category_id = serializers.CharField(read_only=True, required=False)
    category_name = serializers.CharField(read_only=True, required=False)
    category_code = serializers.CharField(read_only=True, required=False)
    level = serializers.ChoiceField(choices=LogEntry.LEVEL_CHOICES, read_only=True)
    message = serializers.CharField(read_only=True)
    source = serializers.CharField(read_only=True, required=False)
    user_id = serializers.CharField(read_only=True, required=False)
    username = serializers.CharField(read_only=True, required=False)
    ip_address = serializers.IPAddressField(read_only=True, required=False)
    user_agent = serializers.CharField(read_only=True, required=False)
    request_id = serializers.CharField(read_only=True, required=False)
    metadata = serializers.JSONField(read_only=True, required=False)
    timestamp = serializers.DateTimeField(read_only=True)


class LogEntryDetailSerializer(LogEntrySerializer):
    """
    日志条目详情序列化器
    """
    pass


class LogEntryCreateSerializer(serializers.Serializer):
    """
    日志条目创建序列化器
    """
    message = serializers.CharField(required=True)
    level = serializers.ChoiceField(choices=LogEntry.LEVEL_CHOICES, default=LogEntry.LEVEL_INFO)
    category_code = serializers.CharField(required=False)
    source = serializers.CharField(required=False)
    ip_address = serializers.IPAddressField(required=False)
    user_agent = serializers.CharField(required=False)
    request_id = serializers.CharField(required=False)
    metadata = serializers.JSONField(required=False)
    
    def validate_category_code(self, value):
        """
        验证分类代码是否存在
        """
        if value and not LogCategory.objects.filter(code=value).exists():
            raise serializers.ValidationError(f"分类代码 '{value}' 不存在")
        return value
    
    def create(self, validated_data):
        """
        创建日志条目
        """
        # 获取当前请求上下文
        request = self.context.get('request')
        
        # 获取分类
        category = None
        category_code = validated_data.pop('category_code', None)
        if category_code:
            try:
                category = LogCategory.objects.get(code=category_code)
            except LogCategory.DoesNotExist:
                pass
        
        # 获取租户和用户
        tenant = getattr(request, 'tenant', None) if request else None
        user = request.user if request and request.user.is_authenticated else None
        
        # 创建日志
        return LogEntry.create_log(
            message=validated_data['message'],
            level=validated_data.get('level', LogEntry.LEVEL_INFO),
            category=category,
            tenant=tenant,
            user=user,
            source=validated_data.get('source'),
            ip_address=validated_data.get('ip_address'),
            user_agent=validated_data.get('user_agent'),
            request_id=validated_data.get('request_id'),
            metadata=validated_data.get('metadata')
        )


class LogEntryBatchCreateSerializer(serializers.Serializer):
    """
    日志条目批量创建序列化器
    """
    logs = LogEntryCreateSerializer(many=True)
    
    def create(self, validated_data):
        """
        批量创建日志条目
        """
        logs_data = validated_data.get('logs', [])
        results = []
        
        # 获取当前请求上下文
        request = self.context.get('request')
        tenant = getattr(request, 'tenant', None) if request else None
        user = request.user if request and request.user.is_authenticated else None
        
        # 批量创建日志
        from apps.logger_service.services import LoggerService
        return LoggerService.log_batch([
            self._prepare_log_data(log_data, tenant, user) for log_data in logs_data
        ])
    
    def _prepare_log_data(self, log_data, tenant, user):
        """
        准备日志数据
        """
        # 获取分类
        category = None
        category_code = log_data.pop('category_code', None)
        if category_code:
            try:
                category = LogCategory.objects.get(code=category_code)
            except LogCategory.DoesNotExist:
                pass
                
        # 构建日志数据
        log_entry_data = {
            'message': log_data['message'],
            'level': log_data.get('level', LogEntry.LEVEL_INFO),
            'source': log_data.get('source'),
            'ip_address': log_data.get('ip_address'),
            'user_agent': log_data.get('user_agent'),
            'request_id': log_data.get('request_id'),
            'metadata': log_data.get('metadata', {})
        }
        
        # 添加关联对象
        if category:
            log_entry_data['category'] = category
        if tenant:
            log_entry_data['tenant'] = tenant
        if user:
            log_entry_data['user'] = user
            
        return log_entry_data 