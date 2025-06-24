"""
服务范围相关序列化器

包含服务、资源和操作的序列化器
"""

from rest_framework import serializers
from apps.auth_service.models.service_scope import Service, Resource, Action
from apps.tenant_service.models import Tenant
from apps.tenant_service.serializers import TenantSerializer


# 服务序列化器
class ServiceSerializer(serializers.ModelSerializer):
    """
    服务基本序列化器
    """
    tenant = TenantSerializer(read_only=True)
    class Meta:
        model = Service
        fields = ['id', 'code', 'name', 'description', 'is_system', 'tenant', 'created_at', 'updated_at']


class ServiceDetailSerializer(serializers.ModelSerializer):
    """
    服务详情序列化器
    """
    tenant = TenantSerializer(read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'code', 'name', 'description', 'is_system', 'tenant', 
                 'created_at', 'updated_at']


class ServiceCreateSerializer(serializers.ModelSerializer):
    """
    服务创建序列化器
    """
    tenant_id = serializers.UUIDField(required=False, write_only=True)
    
    class Meta:
        model = Service
        fields = ['code', 'name', 'description', 'is_system', 'tenant_id']
    
    def validate(self, data):
        """
        验证服务创建数据
        """
        is_system = data.get('is_system', True)
        tenant_id = data.get('tenant_id')
        
        # 验证租户级服务必须提供租户
        if not is_system and not tenant_id:
            raise serializers.ValidationError({"tenant_id": "租户级服务必须提供租户ID"})
            
        # 验证系统服务不能关联租户
        if is_system and tenant_id:
            raise serializers.ValidationError({"tenant_id": "系统服务不能关联租户"})
            
        return data
    
    def create(self, validated_data):
        """
        创建服务
        """
        tenant_id = validated_data.pop('tenant_id', None)
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id)
                validated_data['tenant'] = tenant
            except Tenant.DoesNotExist:
                raise serializers.ValidationError({"tenant_id": f"租户ID {tenant_id} 不存在"})
        
        return Service.objects.create(**validated_data)


class ServiceUpdateSerializer(serializers.ModelSerializer):
    """
    服务更新序列化器
    """
    class Meta:
        model = Service
        fields = ['name', 'description']
        # 不允许修改code、is_system和tenant等关键属性


# 资源序列化器
class ResourceSerializer(serializers.ModelSerializer):
    """
    资源基本序列化器
    """
    service = ServiceSerializer(read_only=True)
    service_code = serializers.CharField(source='service.code', read_only=True)
    is_system = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Resource
        fields = ['id', 'code', 'name', 'description', 'service', 'service_code', 'is_system', 'created_at', 'updated_at']


class ResourceDetailSerializer(serializers.ModelSerializer):
    """
    资源详情序列化器
    """
    service = ServiceSerializer(read_only=True)
    is_system = serializers.BooleanField(read_only=True)
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Resource
        fields = ['id', 'code', 'name', 'description', 'service', 'is_system', 
                 'tenant_id', 'tenant_name', 'created_at', 'updated_at']


class ResourceCreateSerializer(serializers.ModelSerializer):
    """
    资源创建序列化器
    """
    service_id = serializers.UUIDField(required=True, write_only=True)
    
    class Meta:
        model = Resource
        fields = ['code', 'name', 'description', 'service_id',]
    
    def validate(self, data):
        """
        验证资源创建数据
        """
        service_id = data.get('service_id')
        
        # 验证服务存在
        try:
            service = Service.objects.get(id=service_id)
            data['service'] = service
        except Service.DoesNotExist:
            raise serializers.ValidationError({"service_id": f"服务ID {service_id} 不存在"})
            
        return data
    
    def create(self, validated_data):
        """
        创建资源
        """
        service = validated_data.pop('service')
        return Resource.objects.create(service=service, **validated_data)


class ResourceUpdateSerializer(serializers.ModelSerializer):
    """
    资源更新序列化器
    """
    class Meta:
        model = Resource
        fields = ['name', 'description']
        # 不允许修改code和service等关键属性


# 操作序列化器
class ActionSerializer(serializers.ModelSerializer):
    """
    操作基本序列化器
    """
    class Meta:
        model = Action
        fields = ['id', 'code', 'name', 'description', 'is_system', 'created_at', 'updated_at']


class ActionDetailSerializer(serializers.ModelSerializer):
    """
    操作详情序列化器
    """
    tenant = TenantSerializer(read_only=True)
    
    class Meta:
        model = Action
        fields = ['id', 'code', 'name', 'description', 'is_system', 'tenant', 
                 'created_at', 'updated_at']


class ActionCreateSerializer(serializers.ModelSerializer):
    """
    操作创建序列化器
    """
    tenant_id = serializers.UUIDField(required=False, write_only=True)
    
    class Meta:
        model = Action
        fields = ['code', 'name', 'description', 'is_system', 'tenant_id']
    
    def validate(self, data):
        """
        验证操作创建数据
        """
        is_system = data.get('is_system', True)
        tenant_id = data.get('tenant_id')
        
        # 验证租户级操作必须提供租户
        if not is_system and not tenant_id:
            raise serializers.ValidationError({"tenant_id": "租户级操作必须提供租户ID"})
            
        # 验证系统操作不能关联租户
        if is_system and tenant_id:
            raise serializers.ValidationError({"tenant_id": "系统操作不能关联租户"})
            
        return data
    
    def create(self, validated_data):
        """
        创建操作
        """
        tenant_id = validated_data.pop('tenant_id', None)
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id)
                validated_data['tenant'] = tenant
            except Tenant.DoesNotExist:
                raise serializers.ValidationError({"tenant_id": f"租户ID {tenant_id} 不存在"})
        
        return Action.objects.create(**validated_data)


class ActionUpdateSerializer(serializers.ModelSerializer):
    """
    操作更新序列化器
    """
    class Meta:
        model = Action
        fields = ['name', 'description']
        # 不允许修改code、is_system和tenant等关键属性 