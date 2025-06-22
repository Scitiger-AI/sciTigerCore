"""
分页工具类
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    标准分页器
    
    支持通过page和page_size参数控制分页
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        重写返回格式，符合统一响应格式
        """
        return Response({
            'success': True,
            'message': None,
            'results': {
                'total': self.page.paginator.count,
                'page_size': self.get_page_size(self.request),
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            }
        })


class LargeResultsSetPagination(PageNumberPagination):
    """
    大数据量分页器
    
    用于处理大量数据的场景
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500
    
    def get_paginated_response(self, data):
        """
        重写返回格式，符合统一响应格式
        """
        return Response({
            'success': True,
            'message': None,
            'results': {
                'total': self.page.paginator.count,
                'page_size': self.get_page_size(self.request),
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            }
        }) 