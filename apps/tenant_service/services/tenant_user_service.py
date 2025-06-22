"""
租户用户服务
"""

import logging
from django.db import transaction
from apps.tenant_service.models import TenantUser

logger = logging.getLogger('sciTigerCore')


class TenantUserService:
    """
    租户用户服务类
    
    提供租户用户关联的业务逻辑处理
    """
    
    @staticmethod
    def get_tenant_users(tenant, user_id=None, role=None, is_active=None, **filters):
        """
        获取租户用户列表
        
        Args:
            tenant: 租户对象
            user_id: 用户ID，None表示所有用户
            role: 角色，None表示所有角色
            is_active: 是否激活，None表示所有状态
            filters: 其他过滤条件
            
        Returns:
            QuerySet: 租户用户查询集
        """
        queryset = TenantUser.objects.filter(tenant=tenant)
        
        # 用户ID过滤
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # 角色过滤
        if role:
            queryset = queryset.filter(role=role)
            
        # 激活状态过滤
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_tenant_user(tenant, user):
        """
        获取特定租户用户关联
        
        Args:
            tenant: 租户对象
            user: 用户对象
            
        Returns:
            TenantUser: 租户用户关联对象，如果不存在则返回None
        """
        try:
            return TenantUser.objects.get(tenant=tenant, user=user)
        except TenantUser.DoesNotExist:
            return None
    
    @staticmethod
    def create_tenant_user(tenant, user, role=TenantUser.ROLE_MEMBER, is_active=True):
        """
        创建租户用户关联
        
        Args:
            tenant: 租户对象
            user: 用户对象
            role: 角色，默认为成员
            is_active: 是否激活，默认为True
            
        Returns:
            TenantUser: 创建的租户用户关联对象
        """
        # 检查是否已存在关联
        existing = TenantUserService.get_tenant_user(tenant, user)
        if existing:
            logger.warning(f"User {user.username} already associated with tenant {tenant.name}")
            return existing
            
        # 如果角色是所有者，检查是否已有所有者
        if role == TenantUser.ROLE_OWNER and TenantUser.objects.filter(
            tenant=tenant, 
            role=TenantUser.ROLE_OWNER
        ).exists():
            logger.warning(f"Tenant {tenant.name} already has an owner")
            raise ValueError("租户已有所有者，请先移除现有所有者")
            
        # 创建关联
        tenant_user = TenantUser.objects.create(
            tenant=tenant,
            user=user,
            role=role,
            is_active=is_active
        )
        
        logger.info(f"Created tenant user: {user.username} for tenant {tenant.name} with role {role}")
        
        return tenant_user
    
    @staticmethod
    def update_tenant_user(tenant_user_id, **update_data):
        """
        更新租户用户关联
        
        Args:
            tenant_user_id: 租户用户关联ID
            update_data: 更新数据
            
        Returns:
            TenantUser: 更新后的租户用户关联对象，如果不存在则返回None
        """
        try:
            tenant_user = TenantUser.objects.get(id=tenant_user_id)
            
            # 如果要更新为所有者角色，检查是否已有所有者
            if 'role' in update_data and update_data['role'] == TenantUser.ROLE_OWNER:
                if TenantUser.objects.filter(
                    tenant=tenant_user.tenant, 
                    role=TenantUser.ROLE_OWNER
                ).exclude(id=tenant_user_id).exists():
                    logger.warning(f"Tenant {tenant_user.tenant.name} already has an owner")
                    raise ValueError("租户已有所有者，请先移除现有所有者")
            
            # 更新字段
            for key, value in update_data.items():
                setattr(tenant_user, key, value)
                
            tenant_user.save()
            logger.info(f"Updated tenant user: {tenant_user.user.username} for tenant {tenant_user.tenant.name}")
            
            return tenant_user
        except TenantUser.DoesNotExist:
            logger.warning(f"Attempted to update non-existent tenant user: {tenant_user_id}")
            return None
    
    @staticmethod
    def delete_tenant_user(tenant_user_id):
        """
        删除租户用户关联
        
        Args:
            tenant_user_id: 租户用户关联ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            tenant_user = TenantUser.objects.get(id=tenant_user_id)
            
            # 检查是否为所有者，不允许删除所有者
            if tenant_user.role == TenantUser.ROLE_OWNER:
                logger.warning(f"Cannot delete owner of tenant {tenant_user.tenant.name}")
                raise ValueError("不能删除租户所有者，请先转移所有权")
                
            user_name = tenant_user.user.username
            tenant_name = tenant_user.tenant.name
            
            # 删除关联
            tenant_user.delete()
            logger.info(f"Deleted tenant user: {user_name} from tenant {tenant_name}")
            
            return True
        except TenantUser.DoesNotExist:
            logger.warning(f"Attempted to delete non-existent tenant user: {tenant_user_id}")
            return False
    
    @staticmethod
    @transaction.atomic
    def transfer_ownership(tenant, from_user, to_user):
        """
        转移租户所有权
        
        Args:
            tenant: 租户对象
            from_user: 原所有者用户对象
            to_user: 新所有者用户对象
            
        Returns:
            bool: 是否成功转移
        """
        # 获取原所有者关联
        try:
            from_tenant_user = TenantUser.objects.get(
                tenant=tenant,
                user=from_user,
                role=TenantUser.ROLE_OWNER
            )
        except TenantUser.DoesNotExist:
            logger.warning(f"User {from_user.username} is not the owner of tenant {tenant.name}")
            return False
            
        # 获取或创建新所有者关联
        to_tenant_user, created = TenantUser.objects.get_or_create(
            tenant=tenant,
            user=to_user,
            defaults={'role': TenantUser.ROLE_OWNER, 'is_active': True}
        )
        
        if not created:
            # 如果已存在关联，更新为所有者角色
            to_tenant_user.role = TenantUser.ROLE_OWNER
            to_tenant_user.is_active = True
            to_tenant_user.save()
            
        # 将原所有者降级为管理员
        from_tenant_user.role = TenantUser.ROLE_ADMIN
        from_tenant_user.save()
        
        logger.info(f"Transferred ownership of tenant {tenant.name} from {from_user.username} to {to_user.username}")
        
        return True 