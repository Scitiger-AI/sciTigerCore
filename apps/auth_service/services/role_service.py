"""
角色服务
"""

import logging
from django.db import transaction
from apps.auth_service.models import Role, Permission, User

logger = logging.getLogger('sciTigerCore')


class RoleService:
    """
    角色服务类
    
    提供角色相关的业务逻辑处理
    """
    
    @staticmethod
    def get_roles(tenant_id=None, is_system=None, **filters):
        """
        获取角色列表
        
        Args:
            tenant_id: 租户ID，None表示所有租户
            is_system: 是否系统角色，None表示所有类型
            filters: 其他过滤条件
            
        Returns:
            QuerySet: 角色查询集
        """
        queryset = Role.objects.all()
        
        # 租户ID过滤
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        # 系统角色过滤
        if is_system is not None:
            queryset = queryset.filter(is_system=is_system)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_role_by_id(role_id):
        """
        根据ID获取角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            Role: 角色对象，如果不存在则返回None
        """
        try:
            return Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return None
    
    @staticmethod
    def get_role_by_code(code, tenant_id=None):
        """
        根据代码获取角色
        
        Args:
            code: 角色代码
            tenant_id: 租户ID，None表示全局角色
            
        Returns:
            Role: 角色对象，如果不存在则返回None
        """
        try:
            return Role.objects.get(code=code, tenant_id=tenant_id)
        except Role.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def create_role(name, code, tenant_id=None, permissions=None, **role_data):
        """
        创建角色
        
        Args:
            name: 角色名称
            code: 角色代码
            tenant_id: 租户ID，None表示全局角色
            permissions: 权限ID列表
            role_data: 其他角色数据
            
        Returns:
            tuple: (role, error_message)
                role: 创建的角色对象，创建失败时为None
                error_message: 错误信息，创建成功时为None
        """
        # 检查角色代码是否已存在
        if Role.objects.filter(code=code, tenant_id=tenant_id).exists():
            return None, f"角色代码 '{code}' 已存在"
        logger.debug(f"RoleService create_role: {name}, {code}, {tenant_id}, {permissions}, {role_data}")
        try:
            # 创建角色
            role = Role.objects.create(
                name=name,
                code=code,
                tenant_id=tenant_id,
                **role_data
            )

            logger.warning(f"RoleService create_role: {role}，{role.tenant}")
            
            # 添加权限
            if permissions:
                role.permissions.set(Permission.objects.filter(id__in=permissions))
            
            logger.info(f"Created role: {role.name} (ID: {role.id})")
            
            return role, None
        except Exception as e:
            logger.error(f"Error creating role: {str(e)}")
            return None, f"创建角色失败: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def update_role(role_id, **update_data):
        """
        更新角色
        
        Args:
            role_id: 角色ID
            update_data: 更新数据
            
        Returns:
            tuple: (role, error_message)
                role: 更新后的角色对象，更新失败时为None
                error_message: 错误信息，更新成功时为None
        """
        try:
            role = Role.objects.get(id=role_id)
            
            # 系统角色不允许修改某些字段
            if role.is_system:
                update_data.pop('code', None)
                update_data.pop('is_system', None)
                update_data.pop('tenant_id', None)
            
            # 如果尝试更新代码，需要检查是否已存在
            if 'code' in update_data and update_data['code'] != role.code:
                if Role.objects.filter(code=update_data['code'], tenant_id=role.tenant_id).exists():
                    return None, f"角色代码 '{update_data['code']}' 已存在"
            
            # 处理权限更新
            permissions = update_data.pop('permissions', None)
            if permissions is not None:
                role.permissions.set(Permission.objects.filter(id__in=permissions))
            
            # 更新其他字段
            for key, value in update_data.items():
                setattr(role, key, value)
            
            role.save()
            logger.info(f"Updated role: {role.name} (ID: {role.id})")
            
            return role, None
        except Role.DoesNotExist:
            logger.warning(f"Attempted to update non-existent role: {role_id}")
            return None, "角色不存在"
        except Exception as e:
            logger.error(f"Error updating role: {str(e)}")
            return None, f"更新角色失败: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def delete_role(role_id):
        """
        删除角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            role = Role.objects.get(id=role_id)
            
            # 系统角色不允许删除
            if role.is_system:
                logger.warning(f"Attempted to delete system role: {role.name} (ID: {role.id})")
                return False
            
            role_name = role.name
            
            # 删除角色
            role.delete()
            logger.info(f"Deleted role: {role_name} (ID: {role_id})")
            
            return True
        except Role.DoesNotExist:
            logger.warning(f"Attempted to delete non-existent role: {role_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting role: {str(e)}")
            return False
    
    @staticmethod
    @transaction.atomic
    def assign_role_to_user(role_id, user_id):
        """
        将角色分配给用户
        
        Args:
            role_id: 角色ID
            user_id: 用户ID
            
        Returns:
            tuple: (success, error_message)
                success: 是否成功分配
                error_message: 错误信息，成功时为None
        """
        try:
            role = Role.objects.get(id=role_id)
            user = User.objects.get(id=user_id)
            
            # 检查用户是否已有此角色
            if role in user.roles.all():
                return True, None
            
            # 分配角色
            user.roles.add(role)
            logger.info(f"Assigned role {role.name} to user {user.username}")
            
            return True, None
        except Role.DoesNotExist:
            return False, "角色不存在"
        except User.DoesNotExist:
            return False, "用户不存在"
        except Exception as e:
            logger.error(f"Error assigning role to user: {str(e)}")
            return False, f"分配角色失败: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def remove_role_from_user(role_id, user_id):
        """
        从用户中移除角色
        
        Args:
            role_id: 角色ID
            user_id: 用户ID
            
        Returns:
            tuple: (success, error_message)
                success: 是否成功移除
                error_message: 错误信息，成功时为None
        """
        try:
            role = Role.objects.get(id=role_id)
            user = User.objects.get(id=user_id)
            
            # 检查用户是否有此角色
            if role not in user.roles.all():
                return True, None
            
            # 移除角色
            user.roles.remove(role)
            logger.info(f"Removed role {role.name} from user {user.username}")
            
            return True, None
        except Role.DoesNotExist:
            return False, "角色不存在"
        except User.DoesNotExist:
            return False, "用户不存在"
        except Exception as e:
            logger.error(f"Error removing role from user: {str(e)}")
            return False, f"移除角色失败: {str(e)}"
    
    @staticmethod
    def get_user_roles(user_id):
        """
        获取用户的所有角色
        
        Args:
            user_id: 用户ID
            
        Returns:
            QuerySet: 角色查询集，如果用户不存在则返回None
        """
        try:
            user = User.objects.get(id=user_id)
            return user.roles.all()
        except User.DoesNotExist:
            return None
            
    @staticmethod
    @transaction.atomic
    def set_role_as_default(role_id):
        """
        设置角色为默认角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            tuple: (role, error_message)
                role: 更新后的角色对象，更新失败时为None
                error_message: 错误信息，更新成功时为None
        """
        try:
            role = Role.objects.get(id=role_id)
            
            # 如果角色已经是默认角色，则不需要操作
            if role.is_default:
                return role, None
            
            # 获取租户ID
            tenant_id = role.tenant_id
            
            # 将同一租户下的其他默认角色设置为非默认
            if tenant_id:
                Role.objects.filter(tenant_id=tenant_id, is_default=True).update(is_default=False)
            else:
                # 全局角色
                Role.objects.filter(tenant__isnull=True, is_default=True).update(is_default=False)
            
            # 设置当前角色为默认
            role.is_default = True
            role.save()
            
            logger.info(f"设置角色 {role.name} (ID: {role.id}) 为默认角色")
            
            return role, None
        except Role.DoesNotExist:
            logger.warning(f"尝试设置不存在的角色 {role_id} 为默认角色")
            return None, "角色不存在"
        except Exception as e:
            logger.error(f"设置默认角色失败: {str(e)}")
            return None, f"设置默认角色失败: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def unset_role_as_default(role_id):
        """
        取消角色的默认设置
        
        Args:
            role_id: 角色ID
            
        Returns:
            tuple: (role, error_message)
                role: 更新后的角色对象，更新失败时为None
                error_message: 错误信息，更新成功时为None
        """
        try:
            role = Role.objects.get(id=role_id)
            
            # 如果角色不是默认角色，则不需要操作
            if not role.is_default:
                return role, None
            
            # 取消默认设置
            role.is_default = False
            role.save()
            
            logger.info(f"取消角色 {role.name} (ID: {role.id}) 的默认设置")
            
            return role, None
        except Role.DoesNotExist:
            logger.warning(f"尝试取消不存在的角色 {role_id} 的默认设置")
            return None, "角色不存在"
        except Exception as e:
            logger.error(f"取消默认角色设置失败: {str(e)}")
            return None, f"取消默认角色设置失败: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def assign_permissions_to_role(role_id, permission_ids):
        """
        为角色分配权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表
            
        Returns:
            tuple: (success, error_message)
                success: 是否成功分配
                error_message: 错误信息，成功时为None
        """
        try:
            role = Role.objects.get(id=role_id)
            
            # 获取有效的权限对象
            permissions = Permission.objects.filter(id__in=permission_ids)
            
            # 检查权限是否存在
            if len(permissions) != len(permission_ids):
                return False, "部分权限不存在"
            
            # 添加权限到角色
            role.permissions.add(*permissions)
            
            logger.info(f"为角色 {role.name} (ID: {role.id}) 分配了 {len(permissions)} 个权限")
            
            return True, None
        except Role.DoesNotExist:
            logger.warning(f"尝试为不存在的角色 {role_id} 分配权限")
            return False, "角色不存在"
        except Exception as e:
            logger.error(f"为角色分配权限失败: {str(e)}")
            return False, f"为角色分配权限失败: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def remove_permissions_from_role(role_id, permission_ids):
        """
        从角色中移除权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表
            
        Returns:
            tuple: (success, error_message)
                success: 是否成功移除
                error_message: 错误信息，成功时为None
        """
        try:
            role = Role.objects.get(id=role_id)
            
            # 获取有效的权限对象
            permissions = Permission.objects.filter(id__in=permission_ids)
            
            # 从角色中移除权限
            role.permissions.remove(*permissions)
            
            logger.info(f"从角色 {role.name} (ID: {role.id}) 移除了 {len(permissions)} 个权限")
            
            return True, None
        except Role.DoesNotExist:
            logger.warning(f"尝试从不存在的角色 {role_id} 移除权限")
            return False, "角色不存在"
        except Exception as e:
            logger.error(f"从角色移除权限失败: {str(e)}")
            return False, f"从角色移除权限失败: {str(e)}" 