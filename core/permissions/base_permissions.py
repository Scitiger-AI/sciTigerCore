"""
基础权限类
提供跨应用使用的通用权限检查类
"""

from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    检查用户是否为超级管理员
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsTenantMember(permissions.BasePermission):
    """
    检查用户是否为当前租户的成员
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if not hasattr(request, 'tenant') or not request.tenant:
            return False
            
        # 检查用户是否为租户成员
        return request.user.tenant_users.filter(
            tenant=request.tenant,
            is_active=True
        ).exists()


class IsTenantAdmin(permissions.BasePermission):
    """
    检查用户是否为当前租户的管理员
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if not hasattr(request, 'tenant') or not request.tenant:
            return False
            
        # 检查用户是否为租户管理员
        tenant_user = request.user.tenant_users.filter(
            tenant=request.tenant,
            is_active=True
        ).first()
        
        return tenant_user and tenant_user.is_admin


class IsTenantOwner(permissions.BasePermission):
    """
    检查用户是否为当前租户的所有者
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if not hasattr(request, 'tenant') or not request.tenant:
            return False
            
        # 检查用户是否为租户所有者
        tenant_user = request.user.tenant_users.filter(
            tenant=request.tenant,
            is_active=True
        ).first()
        
        return tenant_user and tenant_user.is_owner 