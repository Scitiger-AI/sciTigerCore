"""
序列化器混入类
提供可重用的序列化器功能
"""

from rest_framework import serializers


class TimestampedFieldsMixin:
    """
    时间戳字段混入类
    
    为序列化器添加创建时间和更新时间字段的处理
    """
    
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')


class AuditFieldsMixin:
    """
    审计字段混入类
    
    为序列化器添加创建者和更新者字段的处理
    """
    
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    
    def get_created_by(self, obj):
        """获取创建者用户名"""
        if obj.created_by:
            return obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        """获取更新者用户名"""
        if obj.updated_by:
            return obj.updated_by.username
        return None


class TenantFieldMixin:
    """
    租户字段混入类
    
    为序列化器添加租户字段的处理
    """
    
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    
    def get_tenant(self, obj):
        """获取租户名称"""
        if obj.tenant:
            return obj.tenant.name
        return None


class ReadOnlyFieldsMixin:
    """
    只读字段混入类
    
    根据请求方法动态设置字段为只读
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        
        # 根据请求方法设置只读字段
        if request and request.method in ['PUT', 'PATCH']:
            for field_name in getattr(self.Meta, 'read_only_on_update', []):
                if field_name in self.fields:
                    self.fields[field_name].read_only = True 