"""
响应格式混入类
"""

from core.utils.response import success_response, error_response


class ResponseMixin:
    """
    响应格式混入类
    
    提供统一的响应格式方法，可以被视图类继承使用
    基于core.utils.response中的工具函数实现
    """
    
    def get_success_response(self, data=None, message=None, status_code=None):
        """
        统一的成功响应格式
        
        Args:
            data: 返回的数据内容
            message: 成功描述信息
            status_code: HTTP状态码
            
        Returns:
            Response: DRF响应对象
        """
        return success_response(data, message, status_code)
    
    def get_error_response(self, message, status_code=None):
        """
        统一的错误响应格式
        
        Args:
            message: 错误描述信息
            status_code: HTTP状态码
            
        Returns:
            Response: DRF响应对象
        """
        return error_response(message, status_code)
        
    def get_paginated_response(self, data):
        """
        返回符合统一响应格式的分页响应
        
        Args:
            data: 分页后的数据内容
            
        Returns:
            Response: 包含分页信息的DRF响应对象
        """
        assert self.paginator is not None, '必须在视图中设置分页器'
        
        return success_response({
            'total': self.paginator.page.paginator.count,
            'page_size': self.paginator.get_page_size(self.request),
            'current_page': self.paginator.page.number,
            'total_pages': self.paginator.page.paginator.num_pages,
            'next': self.paginator.get_next_link(),
            'previous': self.paginator.get_previous_link(),
            'results': data
        }) 