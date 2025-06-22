"""
自定义异常处理器
"""
import logging
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework.views import exception_handler
from rest_framework import exceptions, status
from .response import error_response

logger = logging.getLogger('sciTigerCore')


def custom_exception_handler(exc, context):
    """
    自定义异常处理器，将各种异常转换为统一的错误响应格式
    
    Args:
        exc: 异常对象
        context: 异常上下文
        
    Returns:
        Response: 统一格式的错误响应
    """
    # 首先调用REST framework默认的异常处理器
    response = exception_handler(exc, context)
    
    # 记录异常信息
    logger.error(f"Exception occurred: {exc}", exc_info=True)
    
    # 如果是DRF已处理的异常，转换为统一格式
    if response is not None:
        error_message = "发生错误"
        
        # 处理验证错误，提取详细信息
        if isinstance(exc, exceptions.ValidationError):
            if isinstance(response.data, dict):
                error_message = "数据验证失败"
                # 将嵌套的验证错误展平为单个消息
                errors = []
                for field, field_errors in response.data.items():
                    if isinstance(field_errors, list):
                        for error in field_errors:
                            errors.append(f"{field}: {error}")
                    else:
                        errors.append(f"{field}: {field_errors}")
                error_message = ", ".join(errors)
            else:
                error_message = str(response.data)
        # 处理权限错误
        elif isinstance(exc, exceptions.PermissionDenied):
            error_message = "您没有执行此操作的权限"
        # 处理认证错误
        elif isinstance(exc, exceptions.AuthenticationFailed):
            error_message = "认证失败"
        # 处理未认证错误
        elif isinstance(exc, exceptions.NotAuthenticated):
            error_message = "您需要登录后才能执行此操作"
        # 处理方法不允许错误
        elif isinstance(exc, exceptions.MethodNotAllowed):
            error_message = f"方法 {context['request'].method} 不被允许"
        # 处理不可接受的内容类型错误
        elif isinstance(exc, exceptions.UnsupportedMediaType):
            error_message = "不支持的媒体类型"
        # 处理解析错误
        elif isinstance(exc, exceptions.ParseError):
            error_message = "请求数据解析错误"
        # 处理限流错误
        elif isinstance(exc, exceptions.Throttled):
            error_message = f"请求过于频繁，请 {exc.wait} 秒后再试"
        # 处理404错误
        elif isinstance(exc, Http404):
            error_message = "未找到请求的资源"
        # 其他错误
        else:
            error_message = str(exc)
        
        return error_response(error_message, response.status_code)
    
    # 处理Django验证错误
    if isinstance(exc, DjangoValidationError):
        return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
    
    # 处理未捕获的异常
    return error_response("服务器内部错误", status.HTTP_500_INTERNAL_SERVER_ERROR) 