"""
日志保留策略序列化器
"""

from rest_framework import serializers
from apps.logger_service.models import LogRetentionPolicy, LogCategory


class LogRetentionPolicySerializer(serializers.ModelSerializer):
    """
    日志保留策略序列化器
    """
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = LogRetentionPolicy
        fields = ['id', 'tenant', 'category', 'category_name', 'retention_days', 'is_active']
        read_only_fields = ['id']


class LogRetentionPolicyDetailSerializer(serializers.ModelSerializer):
    """
    日志保留策略详情序列化器
    """
    category_name = serializers.ReadOnlyField(source='category.name')
    category_code = serializers.ReadOnlyField(source='category.code')
    tenant_name = serializers.ReadOnlyField(source='tenant.name', default=None)
    
    class Meta:
        model = LogRetentionPolicy
        fields = [
            'id', 'tenant', 'tenant_name', 'category', 'category_name', 'category_code',
            'retention_days', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LogRetentionPolicyCreateSerializer(serializers.ModelSerializer):
    """
    日志保留策略创建序列化器
    """
    category_code = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = LogRetentionPolicy
        fields = ['category', 'category_code', 'tenant', 'retention_days', 'is_active']
        
    def validate(self, data):
        """
        验证分类和租户
        """
        category = data.get('category')
        category_code = data.get('category_code')
        tenant = data.get('tenant')
        
        # 如果提供了分类代码，则根据代码获取分类
        if not category and category_code:
            try:
                category = LogCategory.objects.get(code=category_code)
                data['category'] = category
            except LogCategory.DoesNotExist:
                raise serializers.ValidationError({"category_code": f"分类代码 '{category_code}' 不存在"})
                
        # 验证分类是否存在
        if not category:
            raise serializers.ValidationError({"category": "必须提供分类"})
            
        # 验证是否已存在相同的策略
        if LogRetentionPolicy.objects.filter(category=category, tenant=tenant).exists():
            raise serializers.ValidationError("该租户下已存在此分类的保留策略")
            
        return data


class LogRetentionPolicyUpdateSerializer(serializers.ModelSerializer):
    """
    日志保留策略更新序列化器
    """
    class Meta:
        model = LogRetentionPolicy
        fields = ['retention_days', 'is_active'] 