"""
通知中心权限类
"""

from rest_framework import permissions


class NotificationTypePermission(permissions.BasePermission):
    """通知类型权限"""
    
    def has_permission(self, request, view):
        """检查请求权限"""
        # 管理API需要管理员权限
        if 'management' in request.path:
            return request.user.is_authenticated and request.user.is_staff
        
        # 平台API需要认证
        return request.user.is_authenticated


class NotificationChannelPermission(permissions.BasePermission):
    """通知渠道权限"""
    
    def has_permission(self, request, view):
        """检查请求权限"""
        # 管理API需要管理员权限
        if 'management' in request.path:
            return request.user.is_authenticated and request.user.is_staff
        
        # 平台API需要认证和租户管理员权限
        if request.user.is_authenticated:
            return request.user.is_tenant_admin
        
        return False


class NotificationTemplatePermission(permissions.BasePermission):
    """通知模板权限"""
    
    def has_permission(self, request, view):
        """检查请求权限"""
        # 管理API需要管理员权限
        if 'management' in request.path:
            return request.user.is_authenticated and request.user.is_staff
        
        # 平台API需要认证和租户管理员权限
        if request.user.is_authenticated:
            return request.user.is_tenant_admin
        
        return False


class NotificationPermission(permissions.BasePermission):
    """通知记录权限"""
    
    def has_permission(self, request, view):
        """检查请求权限"""
        # 管理API需要管理员权限
        if 'management' in request.path:
            return request.user.is_authenticated and request.user.is_staff
        
        # 平台API需要认证
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """检查对象权限"""
        # 管理API需要管理员权限
        if 'management' in request.path:
            return request.user.is_authenticated and request.user.is_staff
        
        # 平台API只能访问自己的通知或者租户管理员可以访问租户内所有通知
        return (obj.user == request.user or 
                (request.user.is_tenant_admin and obj.tenant == request.tenant))


class UserNotificationPreferencePermission(permissions.BasePermission):
    """用户通知偏好设置权限"""
    
    def has_permission(self, request, view):
        """检查请求权限"""
        # 管理API需要管理员权限
        if 'management' in request.path:
            return request.user.is_authenticated and request.user.is_staff
        
        # 平台API需要认证
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """检查对象权限"""
        # 管理API需要管理员权限
        if 'management' in request.path:
            return request.user.is_authenticated and request.user.is_staff
        
        # 平台API只能访问自己的偏好设置或者租户管理员可以访问租户内所有偏好设置
        return (obj.user == request.user or 
                (request.user.is_tenant_admin and obj.tenant == request.tenant)) 