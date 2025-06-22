"""
日志分类序列化器
"""

from rest_framework import serializers
from apps.logger_service.models import LogCategory


class LogCategorySerializer(serializers.ModelSerializer):
    """
    日志分类序列化器
    """
    class Meta:
        model = LogCategory
        fields = ['id', 'name', 'code', 'description', 'is_system', 'is_active']
        read_only_fields = ['id', 'is_system']


class LogCategoryDetailSerializer(serializers.ModelSerializer):
    """
    日志分类详情序列化器
    """
    class Meta:
        model = LogCategory
        fields = ['id', 'name', 'code', 'description', 'is_system', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_system', 'created_at', 'updated_at']


class LogCategoryCreateSerializer(serializers.ModelSerializer):
    """
    日志分类创建序列化器
    """
    class Meta:
        model = LogCategory
        fields = ['name', 'code', 'description', 'is_active']
        
    def validate_code(self, value):
        """
        验证分类代码的唯一性
        """
        if LogCategory.objects.filter(code=value).exists():
            raise serializers.ValidationError("分类代码已存在")
        return value


class LogCategoryUpdateSerializer(serializers.ModelSerializer):
    """
    日志分类更新序列化器
    """
    class Meta:
        model = LogCategory
        fields = ['name', 'description', 'is_active']
        
    def validate(self, data):
        """
        验证系统分类是否可以修改
        """
        if self.instance and self.instance.is_system:
            if 'name' in data and data['name'] != self.instance.name:
                raise serializers.ValidationError("系统分类名称不能修改")
        return data 