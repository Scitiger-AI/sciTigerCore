"""
用户服务
"""

import logging
from django.db import transaction
from django.utils import timezone
from apps.auth_service.models import User

logger = logging.getLogger('sciTigerCore')


class UserService:
    """
    用户服务类
    
    提供用户相关的业务逻辑处理
    """
    
    @staticmethod
    def get_users(tenant_id=None, user_id=None, include_inactive=False, **filters):
        """
        获取用户列表
        
        Args:
            tenant_id: 租户ID，None表示所有租户
            user_id: 用户ID，None表示所有用户
            include_inactive: 是否包含非活跃用户
            filters: 其他过滤条件
            
        Returns:
            QuerySet: 用户查询集
        """
        # 获取基础查询集
        queryset = User.objects.all()
        
        # 租户过滤 - 通过TenantUser关联表过滤
        if tenant_id:
            queryset = queryset.filter(tenant_users__tenant_id=tenant_id)
        # 用户ID过滤
        if user_id:
            queryset = queryset.filter(id=user_id)
            
        # 活跃状态过滤
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            User: 用户对象，如果不存在则返回None
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_by_email(email):
        """
        根据邮箱获取用户
        
        Args:
            email: 用户邮箱
            
        Returns:
            User: 用户对象，如果不存在则返回None
        """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_by_username(username):
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            User: 用户对象，如果不存在则返回None
        """
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def update_user(user_id, **update_data):
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            update_data: 更新数据
            
        Returns:
            tuple: (user, error_message)
                user: 更新后的用户对象，更新失败时为None
                error_message: 错误信息，更新成功时为None
        """
        try:
            user = User.objects.get(id=user_id)
            
            # 如果尝试更新邮箱，需要检查是否已存在
            if 'email' in update_data and update_data['email'] != user.email:
                if User.objects.filter(email=update_data['email']).exists():
                    return None, "邮箱已被使用"
                # 更新邮箱时重置验证状态
                update_data['email_verified'] = False
                
            # 如果尝试更新用户名，需要检查是否已存在
            if 'username' in update_data and update_data['username'] != user.username:
                if User.objects.filter(username=update_data['username']).exists():
                    return None, "用户名已被使用"
            
            # 如果包含密码，需要特殊处理
            if 'password' in update_data:
                user.set_password(update_data.pop('password'))
                user.password_changed_at = timezone.now()
            
            # 更新其他字段
            for key, value in update_data.items():
                setattr(user, key, value)
            
            user.save()
            logger.info(f"Updated user: {user.username} (ID: {user.id})")
            
            return user, None
        except User.DoesNotExist:
            logger.warning(f"Attempted to update non-existent user: {user_id}")
            return None, "用户不存在"
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return None, f"更新用户失败: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def delete_user(user_id):
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            user = User.objects.get(id=user_id)
            username = user.username
            
            # 删除用户
            user.delete()
            logger.info(f"Deleted user: {username} (ID: {user_id})")
            
            return True
        except User.DoesNotExist:
            logger.warning(f"Attempted to delete non-existent user: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False
    
    @staticmethod
    def change_user_status(user_id, is_active):
        """
        修改用户状态
        
        Args:
            user_id: 用户ID
            is_active: 是否激活
            
        Returns:
            tuple: (user, error_message)
                user: 更新后的用户对象，更新失败时为None
                error_message: 错误信息，更新成功时为None
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_active = is_active
            user.save(update_fields=['is_active'])
            
            status_text = "激活" if is_active else "禁用"
            logger.info(f"{status_text}用户: {user.username} (ID: {user.id})")
            
            return user, None
        except User.DoesNotExist:
            return None, "用户不存在"
        except Exception as e:
            return None, f"修改用户状态失败: {str(e)}"
    
    @staticmethod
    def verify_user_email(user_id):
        """
        验证用户邮箱
        
        Args:
            user_id: 用户ID
            
        Returns:
            tuple: (user, error_message)
                user: 更新后的用户对象，更新失败时为None
                error_message: 错误信息，更新成功时为None
        """
        try:
            user = User.objects.get(id=user_id)
            user.email_verified = True
            user.save(update_fields=['email_verified'])
            
            logger.info(f"Verified email for user: {user.username} (ID: {user.id})")
            
            return user, None
        except User.DoesNotExist:
            return None, "用户不存在"
        except Exception as e:
            return None, f"验证用户邮箱失败: {str(e)}" 