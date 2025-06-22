"""
用户授权认证服务信号处理器
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.utils import timezone

from .models import User, ApiKey, ApiKeyScope

logger = logging.getLogger('sciTigerCore')


@receiver(post_save, sender=User)
def create_user_related_models(sender, instance, created, **kwargs):
    """
    创建用户时的相关操作
    
    Args:
        sender: 发送信号的模型类
        instance: 用户实例
        created: 是否为新创建的实例
    """
    if created:
        logger.info(f"New user created: {instance.email} (ID: {instance.id})")


@receiver(post_save, sender=ApiKey)
def update_tenant_api_key_count(sender, instance, **kwargs):
    """
    更新租户API密钥数量
    
    Args:
        sender: 发送信号的模型类
        instance: API密钥实例
    """
    if instance.tenant and hasattr(instance.tenant, 'quota'):
        instance.tenant.quota.update_api_key_count()
        logger.debug(f"Updated API key count for tenant: {instance.tenant.name}")


@receiver(post_delete, sender=ApiKey)
def update_tenant_api_key_count_on_delete(sender, instance, **kwargs):
    """
    删除API密钥时更新租户API密钥数量
    
    Args:
        sender: 发送信号的模型类
        instance: API密钥实例
    """
    try:
        if instance.tenant and hasattr(instance.tenant, 'quota'):
            instance.tenant.quota.update_api_key_count()
            logger.debug(f"Updated API key count after deletion for tenant: {instance.tenant.name}")
    except Exception as e:
        logger.error(f"Error updating API key count after deletion: {e}")


@receiver(user_logged_in)
def update_user_login_info(sender, request, user, **kwargs):
    """
    用户登录成功后更新登录信息
    
    Args:
        sender: 发送信号的对象
        request: 请求对象
        user: 用户对象
    """
    # 更新最后登录IP
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            user.last_login_ip = x_forwarded_for.split(',')[0].strip()
        else:
            user.last_login_ip = request.META.get('REMOTE_ADDR')
    
    # 更新最后活跃时间
    user.last_active = timezone.now()
    user.save(update_fields=['last_login_ip', 'last_active'])
    
    # 记录登录尝试
    from .models import LoginAttempt
    if request:
        LoginAttempt.record_attempt(
            email=user.email,
            ip_address=user.last_login_ip,
            status=LoginAttempt.STATUS_SUCCESS,
            user=user,
            tenant=getattr(request, 'tenant', None),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
    
    logger.info(f"User logged in: {user.email} (ID: {user.id})")


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """
    记录登录失败
    
    Args:
        sender: 发送信号的对象
        credentials: 登录凭证
        request: 请求对象
    """
    # 记录登录尝试
    from .models import LoginAttempt
    
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        email = credentials.get('username', '')
        
        # 检查是否超过最大尝试次数
        if not LoginAttempt.check_login_attempts(email, ip_address):
            status = LoginAttempt.STATUS_BLOCKED
            reason = "超过最大尝试次数"
        else:
            status = LoginAttempt.STATUS_FAILED
            reason = "用户名或密码错误"
        
        LoginAttempt.record_attempt(
            email=email,
            ip_address=ip_address,
            status=status,
            tenant=getattr(request, 'tenant', None),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            reason=reason
        )
    
    logger.warning(f"Failed login attempt for: {credentials.get('username', 'unknown')}") 