"""
统一响应格式工具类
"""
from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message=None, status_code=status.HTTP_200_OK):
    """
    统一的成功响应格式
    
    Args:
        data: 返回的数据内容
        message: 成功描述信息
        status_code: HTTP状态码
        
    Returns:
        Response: DRF响应对象
    """
    return Response({
        'success': True,
        'message': message,
        'results': data
    }, status=status_code)


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    """
    统一的错误响应格式
    
    Args:
        message: 错误描述信息
        status_code: HTTP状态码
        
    Returns:
        Response: DRF响应对象
    """
    return Response({
        'success': False,
        'message': message
    }, status=status_code) 