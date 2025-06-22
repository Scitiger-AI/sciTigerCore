"""
基础序列化器类
提供跨应用使用的通用序列化器基类
"""

from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    """
    基础模型序列化器
    
    提供通用的序列化器功能，如租户过滤、自动设置当前用户等
    """
    
    def __init__(self, *args, **kwargs):
        """
        初始化序列化器，设置上下文相关的属性
        """
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.tenant = getattr(self.request, 'tenant_id', None) if self.request else None
        self.user = getattr(self.request, 'user', None) if self.request else None
    
    def validate(self, attrs):
        """
        通用验证逻辑
        """
        attrs = super().validate(attrs)
        return attrs
    
    def create(self, validated_data):
        """
        创建实例时自动设置租户
        """
        # 如果模型有tenant字段且未设置，则自动设置当前租户
        if hasattr(self.Meta.model, 'tenant') and 'tenant' not in validated_data and self.tenant:
            validated_data['tenant'] = self.tenant
            
        # 如果模型有created_by字段且未设置，则自动设置当前用户
        if hasattr(self.Meta.model, 'created_by') and 'created_by' not in validated_data and self.user:
            validated_data['created_by'] = self.user
            
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        更新实例时自动设置更新者
        """
        # 如果模型有updated_by字段且未设置，则自动设置当前用户
        if hasattr(self.Meta.model, 'updated_by') and 'updated_by' not in validated_data and self.user:
            validated_data['updated_by'] = self.user
            
        return super().update(instance, validated_data) 