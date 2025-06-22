"""
日志分类服务
"""

import logging
from django.db import transaction
from apps.logger_service.models import LogCategory

logger = logging.getLogger('sciTigerCore')


class LogCategoryService:
    """
    日志分类服务类
    
    提供日志分类的业务逻辑处理
    """
    
    @staticmethod
    def get_categories(is_system=None, is_active=None, **filters):
        """
        获取日志分类列表
        
        Args:
            is_system: 是否系统分类
            is_active: 是否激活
            filters: 其他过滤条件
            
        Returns:
            QuerySet: 日志分类查询集
        """
        queryset = LogCategory.objects.all()
        
        # 系统分类过滤
        if is_system is not None:
            queryset = queryset.filter(is_system=is_system)
            
        # 激活状态过滤
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def get_category_by_id(category_id):
        """
        根据ID获取日志分类
        
        Args:
            category_id: 日志分类ID
            
        Returns:
            LogCategory: 日志分类对象，如果不存在则返回None
        """
        try:
            return LogCategory.objects.get(id=category_id)
        except LogCategory.DoesNotExist:
            return None
    
    @staticmethod
    def get_category_by_code(code):
        """
        根据代码获取日志分类
        
        Args:
            code: 日志分类代码
            
        Returns:
            LogCategory: 日志分类对象，如果不存在则返回None
        """
        try:
            return LogCategory.objects.get(code=code)
        except LogCategory.DoesNotExist:
            return None
    
    @staticmethod
    def create_category(name, code, description=None, is_system=False, is_active=True):
        """
        创建日志分类
        
        Args:
            name: 分类名称
            code: 分类代码
            description: 分类描述
            is_system: 是否系统分类
            is_active: 是否激活
            
        Returns:
            LogCategory: 创建的日志分类对象
        """
        # 创建分类
        category = LogCategory.objects.create(
            name=name,
            code=code,
            description=description,
            is_system=is_system,
            is_active=is_active
        )
        
        logger.info(f"创建日志分类: {category.name} (ID: {category.id})")
        
        return category
    
    @staticmethod
    def update_category(category_id, **update_data):
        """
        更新日志分类
        
        Args:
            category_id: 日志分类ID
            update_data: 更新数据
            
        Returns:
            LogCategory: 更新后的日志分类对象，如果不存在则返回None
        """
        try:
            category = LogCategory.objects.get(id=category_id)
            
            # 系统分类的代码不能修改
            if category.is_system and 'code' in update_data:
                logger.warning(f"尝试修改系统分类的代码: {category.code}")
                update_data.pop('code')
            
            # 更新分类字段
            for key, value in update_data.items():
                setattr(category, key, value)
                
            category.save()
            logger.info(f"更新日志分类: {category.name} (ID: {category.id})")
            
            return category
        except LogCategory.DoesNotExist:
            logger.warning(f"尝试更新不存在的日志分类: {category_id}")
            return None
    
    @staticmethod
    def delete_category(category_id):
        """
        删除日志分类
        
        Args:
            category_id: 日志分类ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            category = LogCategory.objects.get(id=category_id)
            
            # 系统分类不能删除
            if category.is_system:
                logger.warning(f"尝试删除系统分类: {category.name} (ID: {category.id})")
                return False
                
            category_name = category.name
            category.delete()
            logger.info(f"删除日志分类: {category_name} (ID: {category_id})")
            
            return True
        except LogCategory.DoesNotExist:
            logger.warning(f"尝试删除不存在的日志分类: {category_id}")
            return False
    
    @staticmethod
    def init_system_categories():
        """
        初始化系统日志分类
        
        Returns:
            list: 创建的系统分类列表
        """
        # 系统分类定义
        system_categories = [
            {
                'code': 'system',
                'name': '系统日志',
                'description': '系统级别的日志记录'
            },
            {
                'code': 'auth',
                'name': '认证日志',
                'description': '用户认证相关的日志记录'
            },
            {
                'code': 'api',
                'name': 'API日志',
                'description': 'API调用相关的日志记录'
            },
            {
                'code': 'user',
                'name': '用户日志',
                'description': '用户操作相关的日志记录'
            },
            {
                'code': 'tenant',
                'name': '租户日志',
                'description': '租户相关的日志记录'
            },
            {
                'code': 'payment',
                'name': '支付日志',
                'description': '支付相关的日志记录'
            },
            {
                'code': 'notification',
                'name': '通知日志',
                'description': '通知相关的日志记录'
            },
            {
                'code': 'security',
                'name': '安全日志',
                'description': '安全相关的日志记录'
            }
        ]
        
        # 创建系统分类
        created_categories = []
        for cat_data in system_categories:
            category, created = LogCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'is_system': True,
                    'is_active': True
                }
            )
            
            if created:
                logger.info(f"创建系统日志分类: {category.name} (ID: {category.id})")
                created_categories.append(category)
                
        return created_categories 