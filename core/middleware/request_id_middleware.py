"""
请求ID中间件

为每个请求生成唯一的请求ID，用于跟踪和日志记录
"""
import uuid
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('sciTigerCore')


class RequestIdMiddleware(MiddlewareMixin):
    """
    为每个请求生成唯一的请求ID
    
    请求ID会被添加到请求对象和响应头中
    """
    
    def process_request(self, request):
        """
        处理请求，生成请求ID
        
        Args:
            request: HTTP请求对象
        """
        # 首先尝试从请求头中获取请求ID
        request_id = request.headers.get('X-Request-ID')
        
        # 如果请求头中没有请求ID，则生成一个新的
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # 将请求ID添加到请求对象中
        request.request_id = request_id
        
        # 记录请求信息
        logger.info(f"Request received: {request.method} {request.path} [ID: {request_id}]")
    
    def process_response(self, request, response):
        """
        处理响应，添加请求ID到响应头
        
        Args:
            request: HTTP请求对象
            response: HTTP响应对象
            
        Returns:
            response: 添加了请求ID的HTTP响应对象
        """
        # 获取请求ID（如果process_request没有被调用，可能没有request_id属性）
        request_id = getattr(request, 'request_id', None)
        
        # 如果有请求ID，添加到响应头
        if request_id:
            response['X-Request-ID'] = request_id
            
        return response 