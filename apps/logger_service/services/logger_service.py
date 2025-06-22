"""
日志服务
"""

import uuid
import logging
import datetime
from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from django.utils import timezone
from apps.logger_service.models import LogCategory

logger = logging.getLogger('sciTigerCore')


class LoggerService:
    """
    日志服务类
    
    提供日志记录和查询功能，与MongoDB交互
    """
    
    @staticmethod
    def _get_mongo_client():
        """
        获取MongoDB客户端连接
        
        Returns:
            MongoClient: MongoDB客户端
        """
        try:
            # 检查MongoDB配置
            mongodb_uri = getattr(settings, 'MONGODB_URI', 'mongodb://localhost:27017/')
            logger.debug(f"连接MongoDB: {mongodb_uri}")
            return MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        except Exception as e:
            logger.error(f"MongoDB连接失败: {str(e)}")
            return None
    
    @staticmethod
    def _get_logs_collection():
        """
        获取日志集合
        
        Returns:
            Collection: MongoDB集合对象
        """
        client = LoggerService._get_mongo_client()
        if not client:
            logger.error("无法获取MongoDB客户端连接")
            return None
            
        try:
            # 验证连接
            client.admin.command('ping')
            
            mongodb_name = getattr(settings, 'MONGODB_NAME', 'sciTigerLogs')
            db = client[mongodb_name]
            collection_name = getattr(settings, 'MONGODB_COLLECTION', 'logs')
            return db[collection_name]
        except PyMongoError as e:
            logger.error(f"MongoDB集合获取失败: {str(e)}")
            return None
    
    @staticmethod
    def log(log_data):
        """
        记录单条日志
        
        Args:
            log_data: 日志数据
            
        Returns:
            dict: 创建的日志数据
        """
        # 添加时间戳
        if 'timestamp' not in log_data or not log_data['timestamp']:
            log_data['timestamp'] = timezone.now()
            
        # 获取日志集合
        collection = LoggerService._get_logs_collection()
        if not collection:
            logger.error("无法获取MongoDB日志集合")
            return log_data
            
        try:
            # 插入日志
            collection.insert_one(log_data)
            logger.debug(f"日志记录成功: {log_data['id']}")
            return log_data
        except PyMongoError as e:
            logger.error(f"日志记录失败: {str(e)}")
            return log_data
    
    @staticmethod
    def log_batch(logs_data):
        """
        批量记录日志
        
        Args:
            logs_data: 日志数据列表
            
        Returns:
            list: 创建的日志数据列表
        """
        if not logs_data:
            return []
            
        # 处理每条日志数据
        processed_logs = []
        now = timezone.now()
        
        for log_data in logs_data:
            # 构建日志数据
            entry_data = {
                'id': str(log_data.get('id', uuid.uuid4())),
                'message': log_data.get('message'),
                'level': log_data.get('level', 'info'),
                'timestamp': now,
                'source': log_data.get('source'),
                'ip_address': log_data.get('ip_address'),
                'user_agent': log_data.get('user_agent'),
                'request_id': log_data.get('request_id'),
                'metadata': log_data.get('metadata', {})
            }
            
            # 添加关联对象的ID
            if 'tenant' in log_data and log_data['tenant']:
                tenant = log_data['tenant']
                entry_data['tenant_id'] = str(tenant.id)
                entry_data['tenant_name'] = tenant.name
                
            if 'category' in log_data and log_data['category']:
                category = log_data['category']
                entry_data['category_id'] = str(category.id)
                entry_data['category_name'] = category.name
                entry_data['category_code'] = category.code
                
            if 'user' in log_data and log_data['user']:
                user = log_data['user']
                entry_data['user_id'] = str(user.id)
                entry_data['username'] = user.username
                
            processed_logs.append(entry_data)
        
        # 获取日志集合
        collection = LoggerService._get_logs_collection()
        if not collection:
            logger.error("无法获取MongoDB日志集合")
            return processed_logs
            
        try:
            # 批量插入日志
            if processed_logs:
                collection.insert_many(processed_logs)
                logger.debug(f"批量日志记录成功: {len(processed_logs)}条")
            return processed_logs
        except PyMongoError as e:
            logger.error(f"批量日志记录失败: {str(e)}")
            return processed_logs
    
    @staticmethod
    def get_logs(tenant_id=None, category_id=None, user_id=None, level=None, 
                start_time=None, end_time=None, source=None, search_text=None,
                page=1, page_size=20, sort_field='timestamp', sort_order=-1):
        """
        获取日志列表
        
        Args:
            tenant_id: 租户ID
            category_id: 分类ID
            user_id: 用户ID
            level: 日志级别
            start_time: 开始时间
            end_time: 结束时间
            source: 来源
            search_text: 搜索文本
            page: 页码
            page_size: 每页大小
            sort_field: 排序字段
            sort_order: 排序顺序(1: 升序, -1: 降序)
            
        Returns:
            tuple: (日志列表, 总数)
        """
        # 构建查询条件
        query = {}
        
        if tenant_id:
            query['tenant_id'] = tenant_id
            
        if category_id:
            query['category_id'] = category_id
            
        if user_id:
            query['user_id'] = user_id
            
        if level:
            query['level'] = level
            
        if source:
            query['source'] = source
            
        # 时间范围过滤
        if start_time or end_time:
            time_query = {}
            if start_time:
                time_query['$gte'] = start_time
            if end_time:
                time_query['$lte'] = end_time
            if time_query:
                query['timestamp'] = time_query
                
        # 文本搜索
        if search_text:
            query['$text'] = {'$search': search_text}
            
        # 获取日志集合
        collection = LoggerService._get_logs_collection()
        if not collection:
            logger.error("无法获取MongoDB日志集合")
            return [], 0
            
        try:
            # 计算总数
            total = collection.count_documents(query)
            
            # 分页查询
            skip = (page - 1) * page_size
            
            # 执行查询
            cursor = collection.find(query) \
                .sort(sort_field, sort_order) \
                .skip(skip) \
                .limit(page_size)
                
            # 转换为列表
            logs = list(cursor)
            
            return logs, total
        except PyMongoError as e:
            logger.error(f"日志查询失败: {str(e)}")
            return [], 0
    
    @staticmethod
    def get_log_by_id(log_id):
        """
        根据ID获取日志
        
        Args:
            log_id: 日志ID
            
        Returns:
            dict: 日志数据
        """
        # 获取日志集合
        collection = LoggerService._get_logs_collection()
        if not collection:
            logger.error("无法获取MongoDB日志集合")
            return None
            
        try:
            # 查询日志
            log = collection.find_one({'id': log_id})
            return log
        except PyMongoError as e:
            logger.error(f"日志查询失败: {str(e)}")
            return None
    
    @staticmethod
    def delete_logs(tenant_id=None, category_id=None, before_date=None):
        """
        删除日志
        
        Args:
            tenant_id: 租户ID
            category_id: 分类ID
            before_date: 删除此日期之前的日志
            
        Returns:
            int: 删除的日志数量
        """
        # 构建查询条件
        query = {}
        
        if tenant_id:
            query['tenant_id'] = tenant_id
            
        if category_id:
            query['category_id'] = category_id
            
        if before_date:
            query['timestamp'] = {'$lt': before_date}
            
        # 获取日志集合
        collection = LoggerService._get_logs_collection()
        if not collection:
            logger.error("无法获取MongoDB日志集合")
            return 0
            
        try:
            # 删除日志
            result = collection.delete_many(query)
            deleted_count = result.deleted_count
            logger.info(f"已删除{deleted_count}条日志")
            return deleted_count
        except PyMongoError as e:
            logger.error(f"日志删除失败: {str(e)}")
            return 0
    
    @staticmethod
    def apply_retention_policies():
        """
        应用日志保留策略，删除过期日志
        
        Returns:
            int: 删除的日志数量
        """
        from apps.logger_service.models import LogRetentionPolicy
        
        # 获取所有激活的保留策略
        policies = LogRetentionPolicy.objects.filter(is_active=True)
        
        total_deleted = 0
        for policy in policies:
            # 计算截止日期
            cutoff_date = timezone.now() - datetime.timedelta(days=policy.retention_days)
            
            # 删除过期日志
            tenant_id = str(policy.tenant.id) if policy.tenant else None
            category_id = str(policy.category.id)
            
            deleted = LoggerService.delete_logs(
                tenant_id=tenant_id,
                category_id=category_id,
                before_date=cutoff_date
            )
            
            total_deleted += deleted
            
        return total_deleted
    
    @staticmethod
    def get_log_stats(tenant_id=None, days=7):
        """
        获取日志统计信息
        
        Args:
            tenant_id: 租户ID
            days: 统计天数
            
        Returns:
            dict: 统计信息
        """
        # 计算开始日期
        start_date = timezone.now() - datetime.timedelta(days=days)
        
        # 获取日志集合
        collection = LoggerService._get_logs_collection()
        if not collection:
            logger.error("无法获取MongoDB日志集合")
            return {}
            
        try:
            # 基础查询条件
            match = {'timestamp': {'$gte': start_date}}
            if tenant_id:
                match['tenant_id'] = tenant_id
                
            # 按级别统计
            level_pipeline = [
                {'$match': match},
                {'$group': {'_id': '$level', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]
            
            level_stats = list(collection.aggregate(level_pipeline))
            
            # 按分类统计
            category_pipeline = [
                {'$match': match},
                {'$group': {'_id': '$category_name', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]
            
            category_stats = list(collection.aggregate(category_pipeline))
            
            # 按日期统计
            date_pipeline = [
                {'$match': match},
                {'$group': {
                    '_id': {
                        'year': {'$year': '$timestamp'},
                        'month': {'$month': '$timestamp'},
                        'day': {'$dayOfMonth': '$timestamp'}
                    },
                    'count': {'$sum': 1}
                }},
                {'$sort': {'_id.year': 1, '_id.month': 1, '_id.day': 1}}
            ]
            
            date_stats = list(collection.aggregate(date_pipeline))
            
            # 总数统计
            total_count = collection.count_documents(match)
            
            # 构建结果
            result = {
                'total_count': total_count,
                'level_stats': {item['_id']: item['count'] for item in level_stats},
                'category_stats': {item['_id'] or 'unknown': item['count'] for item in category_stats},
                'date_stats': [
                    {
                        'date': f"{item['_id']['year']}-{item['_id']['month']}-{item['_id']['day']}",
                        'count': item['count']
                    } for item in date_stats
                ]
            }
            
            return result
        except PyMongoError as e:
            logger.error(f"日志统计失败: {str(e)}")
            return {} 