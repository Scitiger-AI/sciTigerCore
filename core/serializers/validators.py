"""
序列化器验证器
提供跨应用使用的通用验证器
"""

import logging
from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueValidator, qs_exists
from rest_framework.exceptions import ValidationError

logger = logging.getLogger('sciTigerCore')

class UniqueInTenantValidator(UniqueValidator):
    """
    租户内唯一性验证器
    
    验证字段在当前租户范围内是否唯一，支持单字段或多字段唯一性验证
    """
    
    message = _('该值在当前租户中已存在。')
    
    def __init__(self, queryset, message=None, lookup='exact', fields=None, **kwargs):
        self.fields = fields
        super().__init__(queryset, message, lookup, **kwargs)
    
    def filter_queryset(self, value, queryset, field_name):
        """
        在验证唯一性时，将查询限制在当前租户范围内
        """
        # 获取当前请求和租户
        request = self.context.get('request')
        tenant = getattr(request, 'tenant', None) if request else None
        tenant_id = None
        
        # 尝试从多个来源获取数据
        data = None
        
        # 1. 从context中的serializer获取
        serializer = self.context.get('serializer')
        logger.debug(f"UniqueInTenantValidator serializer: {serializer}")
        
        if serializer and hasattr(serializer, 'initial_data'):
            data = serializer.initial_data
        
        # 2. 如果上面失败，从保存的serializer_field中获取
        if data is None and hasattr(self, 'serializer_field') and hasattr(self.serializer_field, 'parent'):
            parent = self.serializer_field.parent
            if parent and hasattr(parent, 'initial_data'):
                data = parent.initial_data
                logger.debug(f"UniqueInTenantValidator got data from serializer_field.parent")
        
        # 3. 如果上面都失败，从request.data获取
        if data is None and request and hasattr(request, 'data'):
            data = request.data
            logger.debug(f"UniqueInTenantValidator got data from request.data")
        
        logger.debug(f"UniqueInTenantValidator data: {data}")
        
        # 从请求和序列化器数据中尝试获取租户ID
        if not tenant and data:
            # 尝试从 tenant_id 字段获取
            if 'tenant_id' in data:
                tenant_id = data.get('tenant_id')
                logger.debug(f"UniqueInTenantValidator using tenant_id from data: {tenant_id}")
            # 尝试从 tenant 字段获取
            elif 'tenant' in data:
                tenant_data = data.get('tenant')
                # tenant 可能是 ID 字符串或包含 ID 的字典
                if isinstance(tenant_data, dict) and 'id' in tenant_data:
                    tenant_id = tenant_data['id']
                else:
                    tenant_id = tenant_data
                logger.debug(f"UniqueInTenantValidator using tenant from data: {tenant_id}")
        elif tenant:
            tenant_id = tenant.id
            logger.debug(f"UniqueInTenantValidator using tenant from request: {tenant_id}")
        else:
            # 尝试从请求参数中获取租户ID
            tenant_id_param = request.query_params.get('tenant_id') if request and hasattr(request, 'query_params') else None
            tenant_param = request.query_params.get('tenant') if request and hasattr(request, 'query_params') else None
            tenant_id = tenant_id_param or tenant_param
            logger.debug(f"UniqueInTenantValidator using tenant_id from query params: {tenant_id}")
        
        # 如果是多字段唯一性验证
        if self.fields:
            # 获取序列化器数据
            if data:
                filter_kwargs = {}
                for field in self.fields:
                    if field in data:
                        filter_kwargs[f'{field}__{self.lookup}'] = data[field]
                
                if filter_kwargs:
                    # 添加调试日志
                    logger.debug(f"UniqueInTenantValidator filter_kwargs: {filter_kwargs}")
                    queryset = queryset.filter(**filter_kwargs)
        else:
            # 单字段唯一性验证
            filter_kwargs = {f'{field_name}__{self.lookup}': value}
            queryset = queryset.filter(**filter_kwargs)
        
        # 如果有租户ID，则添加租户过滤条件
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        # 添加调试日志
        logger.debug(f"UniqueInTenantValidator queryset count: {queryset.count()}")
        if queryset.count() > 0:
            # 获取模型的基本字段，避免尝试访问不存在的字段
            try:
                # 获取查询集的第一个元素的模型类
                model = queryset.model
                # 获取模型的一些基本字段
                fields = [field.name for field in model._meta.fields[:3]]  # 只取前几个字段用于日志
                logger.debug(f"UniqueInTenantValidator existing records: {list(queryset.values(*fields))}")
            except Exception as e:
                logger.debug(f"UniqueInTenantValidator failed to log existing records: {str(e)}")
            
        return queryset
    
    def __call__(self, value, serializer_field):
        # 保存serializer_field以便后续使用
        self.serializer_field = serializer_field
        # 设置上下文
        self.context = {
            'request': serializer_field.context.get('request'),
            'serializer': serializer_field.parent
        }
        
        # 如果是多字段唯一性验证，直接在这里验证
        if self.fields:
            # 获取查询集
            queryset = self.queryset
            queryset = self.filter_queryset(None, queryset, None)
            
            # 检查排除当前实例
            instance = getattr(serializer_field.parent, 'instance', None)
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            # 检查是否存在
            if queryset.exists():
                # 修复：直接使用ValidationError而不是调用raise_error方法
                raise ValidationError(self.message, code='unique')
        else:
            # 单字段唯一性验证，使用父类逻辑
            queryset = self.queryset
            queryset = self.filter_queryset(value, queryset, serializer_field.source_attrs[-1])
            
            # 检查是否存在
            if qs_exists(queryset, serializer_field):
                # 使用字段对象的raise_error方法
                raise serializer_field.error_messages['unique']


class FutureOnlyValidator:
    """
    仅允许未来日期的验证器
    """
    
    message = _('日期必须是未来日期。')
    
    def __init__(self, message=None):
        self.message = message or self.message
    
    def __call__(self, value, serializer_field):
        from django.utils import timezone
        
        if value <= timezone.now():
            raise ValidationError(self.message, code='future_only')


class GreaterThanValidator:
    """
    大于指定字段值的验证器
    """
    
    message = _('该值必须大于 {field_name}。')
    
    def __init__(self, field_name, message=None):
        self.field_name = field_name
        self.message = message or self.message
    
    def __call__(self, value, serializer_field):
        data = serializer_field.parent.initial_data
        
        if self.field_name not in data:
            return
        
        compare_value = data[self.field_name]
        
        if value <= compare_value:
            message = self.message.format(field_name=self.field_name)
            raise ValidationError(message, code='greater_than') 