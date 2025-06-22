"""
日志保留策略服务
"""

import logging
from django.db import transaction
from apps.logger_service.models import LogRetentionPolicy, LogCategory

logger = logging.getLogger('sciTigerCore')


class LogRetentionPolicyService:
    """
    日志保留策略服务类
    
    提供日志保留策略的业务逻辑处理
    """
    
    @staticmethod
    def get_policies(tenant_id=None, category_id=None, is_active=None, **filters):
        """
        获取日志保留策略列表
        
        Args:
            tenant_id: 租户ID
            category_id: 分类ID
            is_active: 是否激活
            filters: 其他过滤条件
            
        Returns:
            QuerySet: 日志保留策略查询集
        """
        queryset = LogRetentionPolicy.objects.all()
        
        # 租户ID过滤
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
            
        # 分类ID过滤
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # 激活状态过滤
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_policy_by_id(policy_id):
        """
        根据ID获取日志保留策略
        
        Args:
            policy_id: 日志保留策略ID
            
        Returns:
            LogRetentionPolicy: 日志保留策略对象，如果不存在则返回None
        """
        try:
            return LogRetentionPolicy.objects.get(id=policy_id)
        except LogRetentionPolicy.DoesNotExist:
            return None
    
    @staticmethod
    def get_policy_by_tenant_and_category(tenant_id, category_id):
        """
        根据租户和分类获取日志保留策略
        
        Args:
            tenant_id: 租户ID
            category_id: 分类ID
            
        Returns:
            LogRetentionPolicy: 日志保留策略对象，如果不存在则返回None
        """
        try:
            return LogRetentionPolicy.objects.get(tenant_id=tenant_id, category_id=category_id)
        except LogRetentionPolicy.DoesNotExist:
            return None
    
    @staticmethod
    def create_policy(category, tenant=None, retention_days=30, is_active=True):
        """
        创建日志保留策略
        
        Args:
            category: 日志分类对象
            tenant: 租户对象
            retention_days: 保留天数
            is_active: 是否激活
            
        Returns:
            LogRetentionPolicy: 创建的日志保留策略对象
        """
        # 检查是否已存在相同的策略
        existing = LogRetentionPolicyService.get_policy_by_tenant_and_category(
            tenant_id=tenant.id if tenant else None,
            category_id=category.id
        )
        
        if existing:
            logger.warning(f"已存在相同的日志保留策略: {existing.id}")
            return existing
        
        # 创建策略
        policy = LogRetentionPolicy.objects.create(
            category=category,
            tenant=tenant,
            retention_days=retention_days,
            is_active=is_active
        )
        
        tenant_name = tenant.name if tenant else '全局'
        logger.info(f"创建日志保留策略: {tenant_name} - {category.name} ({policy.id})")
        
        return policy
    
    @staticmethod
    def update_policy(policy_id, **update_data):
        """
        更新日志保留策略
        
        Args:
            policy_id: 日志保留策略ID
            update_data: 更新数据
            
        Returns:
            LogRetentionPolicy: 更新后的日志保留策略对象，如果不存在则返回None
        """
        try:
            policy = LogRetentionPolicy.objects.get(id=policy_id)
            
            # 更新策略字段
            for key, value in update_data.items():
                setattr(policy, key, value)
                
            policy.save()
            tenant_name = policy.tenant.name if policy.tenant else '全局'
            logger.info(f"更新日志保留策略: {tenant_name} - {policy.category.name} ({policy.id})")
            
            return policy
        except LogRetentionPolicy.DoesNotExist:
            logger.warning(f"尝试更新不存在的日志保留策略: {policy_id}")
            return None
    
    @staticmethod
    def delete_policy(policy_id):
        """
        删除日志保留策略
        
        Args:
            policy_id: 日志保留策略ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            policy = LogRetentionPolicy.objects.get(id=policy_id)
            tenant_name = policy.tenant.name if policy.tenant else '全局'
            category_name = policy.category.name
            
            policy.delete()
            logger.info(f"删除日志保留策略: {tenant_name} - {category_name} ({policy_id})")
            
            return True
        except LogRetentionPolicy.DoesNotExist:
            logger.warning(f"尝试删除不存在的日志保留策略: {policy_id}")
            return False
    
    @staticmethod
    def init_default_policies():
        """
        初始化默认日志保留策略
        
        Returns:
            list: 创建的默认策略列表
        """
        # 获取所有系统分类
        categories = LogCategory.objects.filter(is_system=True)
        
        # 默认保留天数配置
        default_retention_days = {
            'system': 90,
            'auth': 180,
            'api': 30,
            'user': 90,
            'tenant': 180,
            'payment': 365,
            'notification': 30,
            'security': 365
        }
        
        # 创建全局默认策略
        created_policies = []
        for category in categories:
            retention_days = default_retention_days.get(category.code, 30)
            
            policy, created = LogRetentionPolicy.objects.get_or_create(
                category=category,
                tenant=None,
                defaults={
                    'retention_days': retention_days,
                    'is_active': True
                }
            )
            
            if created:
                logger.info(f"创建默认日志保留策略: 全局 - {category.name} ({policy.id})")
                created_policies.append(policy)
                
        return created_policies