"""
权限服务
"""

import logging
from django.db import transaction
from apps.auth_service.models import Permission, User

logger = logging.getLogger('sciTigerCore')


class PermissionService:
    """
    权限服务类
    
    提供权限相关的业务逻辑处理
    
    权限分为两种类型：
    1. 系统全局权限 (is_system=True)：系统预设的权限，适用于所有租户，不关联特定租户
    2. 租户级权限 (is_tenant_level=True)：特定租户的自定义权限，必须关联到特定租户
    
    这两种类型互斥，一个权限不能同时是系统权限和租户级权限。
    """
    
    @staticmethod
    def get_permissions(tenant_id=None, is_system=None, is_tenant_level=None, **filters):
        """
        获取权限列表
        
        Args:
            tenant_id: 租户ID，None表示所有租户
            is_system: 是否系统权限，None表示所有类型
            is_tenant_level: 是否租户级权限，None表示所有级别
            filters: 其他过滤条件
            
        Returns:
            QuerySet: 权限查询集
        """
        queryset = Permission.objects.all()
        
        # 租户ID过滤
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
            
        # 系统权限过滤
        if is_system is not None:
            queryset = queryset.filter(is_system=is_system)
            
        # 租户级权限过滤
        if is_tenant_level is not None:
            queryset = queryset.filter(is_tenant_level=is_tenant_level)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_permission_by_id(permission_id):
        """
        根据ID获取权限
        
        Args:
            permission_id: 权限ID
            
        Returns:
            Permission: 权限对象，如果不存在则返回None
        """
        try:
            return Permission.objects.get(id=permission_id)
        except Permission.DoesNotExist:
            return None
    
    @staticmethod
    def get_permission_by_code(code):
        """
        根据代码获取权限
        
        Args:
            code: 权限代码
            
        Returns:
            Permission: 权限对象，如果不存在则返回None
        """
        try:
            return Permission.objects.get(code=code)
        except Permission.DoesNotExist:
            return None
    
    @staticmethod
    def get_permissions_by_service(service, tenant_id=None):
        """
        根据服务名称获取权限列表
        
        Args:
            service: 服务名称
            tenant_id: 租户ID，None表示仅系统权限，有值表示系统权限和指定租户的权限
            
        Returns:
            QuerySet: 权限查询集
        """
        if tenant_id:
            # 获取系统权限和指定租户的权限
            system_permissions = Permission.objects.filter(service=service, is_system=True)
            tenant_permissions = Permission.objects.filter(service=service, tenant_id=tenant_id)
            return system_permissions | tenant_permissions
        else:
            # 仅获取系统权限
            return Permission.objects.filter(service=service, is_system=True)
    
    @staticmethod
    @transaction.atomic
    def create_permission(name, service, resource, action, **permission_data):
        """
        创建权限
        
        Args:
            name: 权限名称
            service: 服务名称
            resource: 资源类型
            action: 操作类型
            permission_data: 其他权限数据，可包含：
                - is_system: 是否系统权限，默认为True
                - is_tenant_level: 是否租户级权限，默认为False
                - tenant: 所属租户，租户级权限必须提供
                - description: 权限描述
            
        Returns:
            Permission: 创建的权限对象
            
        Notes:
            - 系统权限(is_system=True)和租户级权限(is_tenant_level=True)是互斥的
            - 租户级权限必须关联租户，系统权限不应关联租户
        """
        # 确保权限类型一致性
        is_system = permission_data.get('is_system', True)
        is_tenant_level = permission_data.get('is_tenant_level', False)
        tenant = permission_data.get('tenant')
        
        # 验证权限类型互斥
        if is_system and is_tenant_level:
            logger.error("Cannot create permission: system permission and tenant-level permission are mutually exclusive")
            raise ValueError("系统权限和租户级权限不能同时为真")
        
        # 验证租户级权限必须关联租户
        if is_tenant_level and tenant is None:
            logger.error("Cannot create permission: tenant-level permission must be associated with a tenant")
            raise ValueError("租户级权限必须关联租户")
        
        # 验证系统权限不应关联租户
        if is_system and tenant is not None:
            logger.error("Cannot create permission: system permission should not be associated with a specific tenant")
            raise ValueError("系统权限不应关联到特定租户")
        
        # 创建权限
        permission = Permission.objects.create(
            name=name,
            service=service,
            resource=resource,
            action=action,
            **permission_data
        )
        
        logger.info(f"Created permission: {permission.name} (ID: {permission.id}), Type: {'System' if is_system else 'Tenant-level'}")
        
        return permission
    
    @staticmethod
    def update_permission(permission_id, **update_data):
        """
        更新权限
        
        Args:
            permission_id: 权限ID
            update_data: 更新数据，可包含：
                - name: 权限名称
                - description: 权限描述
                - is_system: 是否系统权限
                - is_tenant_level: 是否租户级权限
                - tenant: 所属租户
            
        Returns:
            Permission: 更新后的权限对象，如果不存在则返回None
            
        Notes:
            - 系统权限(is_system=True)和租户级权限(is_tenant_level=True)是互斥的
            - 租户级权限必须关联租户，系统权限不应关联租户
            - 不允许更新服务、资源和操作字段，因为这些字段决定了权限的唯一性
        """
        try:
            permission = Permission.objects.get(id=permission_id)
            
            # 不允许更新服务、资源和操作字段，因为这些字段决定了权限的唯一性
            update_data.pop('service', None)
            update_data.pop('resource', None)
            update_data.pop('action', None)
            
            # 获取更新后的值（如果未提供，则使用现有值）
            is_system = update_data.get('is_system', permission.is_system)
            is_tenant_level = update_data.get('is_tenant_level', permission.is_tenant_level)
            tenant = update_data.get('tenant', permission.tenant)
            
            # 验证权限类型互斥
            if is_system and is_tenant_level:
                logger.error(f"Cannot update permission {permission_id}: system permission and tenant-level permission are mutually exclusive")
                raise ValueError("系统权限和租户级权限不能同时为真")
            
            # 验证租户级权限必须关联租户
            if is_tenant_level and tenant is None:
                logger.error(f"Cannot update permission {permission_id}: tenant-level permission must be associated with a tenant")
                raise ValueError("租户级权限必须关联租户")
            
            # 验证系统权限不应关联租户
            if is_system and tenant is not None:
                logger.error(f"Cannot update permission {permission_id}: system permission should not be associated with a specific tenant")
                raise ValueError("系统权限不应关联到特定租户")
            
            # 更新权限字段
            for key, value in update_data.items():
                setattr(permission, key, value)
                
            permission.save()
            logger.info(f"Updated permission: {permission.name} (ID: {permission.id})")
            
            return permission
        except Permission.DoesNotExist:
            logger.warning(f"Attempted to update non-existent permission: {permission_id}")
            return None
    
    @staticmethod
    @transaction.atomic
    def delete_permission(permission_id):
        """
        删除权限
        
        Args:
            permission_id: 权限ID
            
        Returns:
            bool: 是否成功删除
            
        Notes:
            - 系统权限不允许删除
        """
        try:
            permission = Permission.objects.get(id=permission_id)
            
            # # 系统权限不允许删除
            # if permission.is_system:
            #     logger.warning(f"Attempted to delete system permission: {permission.name} (ID: {permission.id})")
            #     return False
            
            permission_name = permission.name
            
            # 删除权限
            permission.delete()
            logger.info(f"Deleted permission: {permission_name} (ID: {permission_id})")
            
            return True
        except Permission.DoesNotExist:
            logger.warning(f"Attempted to delete non-existent permission: {permission_id}")
            return False
    
    @staticmethod
    def get_user_permissions(user_id):
        """
        获取用户的所有权限
        
        Args:
            user_id: 用户ID
            
        Returns:
            QuerySet: 权限查询集，如果用户不存在则返回None
        """
        try:
            user = User.objects.get(id=user_id)
            
            # 获取用户所有角色的权限
            return Permission.objects.filter(roles__in=user.roles.all()).distinct()
        except User.DoesNotExist:
            logger.warning(f"Attempted to get permissions for non-existent user: {user_id}")
            return None 