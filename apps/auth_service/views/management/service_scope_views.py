"""
服务作用域视图

提供获取service、resource、action的选项信息
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core.mixins import ResponseMixin


class ServiceScopeViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    服务作用域视图集
    
    提供获取service、resource、action的选项信息
    """
    permission_classes = [IsAdminUser]
    
    # 硬编码的服务作用域选项
    SERVICE_OPTIONS = [
        {
            "code": "auth_service",
            "name": "认证服务",
            "description": "提供用户认证、授权、权限管理等功能"
        },
        {
            "code": "tenant_service",
            "name": "租户服务",
            "description": "提供租户管理、租户配置等功能"
        },
        {
            "code": "payment_service",
            "name": "支付服务",
            "description": "提供订单管理、支付处理等功能"
        },
        {
            "code": "notification_service",
            "name": "通知服务",
            "description": "提供消息通知、邮件发送等功能"
        },
        {
            "code": "log_service",
            "name": "日志服务",
            "description": "提供系统日志、操作日志等功能"
        },
        {
            "code": "text_service",
            "name": "文本模型调用服务",
            "description": "提供文本生成、文本摘要、情感分析等能力，支持多种文本处理模型：DeepSeek、Qwen、智谱AI、Kimi等"
        },
         {
            "code": "image_service",
            "name": "图像模型调用服务",
            "description": "提供图片生成、图片编辑、图片风格转换等能力，支持多种图片处理模型：wan2.2、liblib等"
        },
         {
            "code": "video_service",
            "name": "视频模型调用服务",
            "description": "提供视频生成、视频编辑、视频风格转换等能力，支持多种视频处理模型：wan2.2、zhipu等"
        },
        {
            "code": "video_edit_service",
            "name": "视频编辑服务",
            "description": "提供视频编辑、视频剪辑、视频拼接等能力"
        },
    ]
    
    # 硬编码的资源选项（按服务分组）
    RESOURCE_OPTIONS = {
        "auth_service": [
            {"code": "users", "name": "用户"},
            {"code": "roles", "name": "角色"},
            {"code": "permissions", "name": "权限"},
            {"code": "api_keys", "name": "API密钥"}
        ],
        "tenant_service": [
            {"code": "tenants", "name": "租户"},
            {"code": "tenant_configs", "name": "租户配置"},
            {"code": "tenant_domains", "name": "租户域名"}
        ],
        "payment_service": [
            {"code": "orders", "name": "订单"},
            {"code": "payments", "name": "支付"},
            {"code": "refunds", "name": "退款"},
            {"code": "subscriptions", "name": "订阅"}
        ],
        "notification_service": [
            {"code": "messages", "name": "消息"},
            {"code": "templates", "name": "模板"},
            {"code": "channels", "name": "渠道"}
        ],
        "log_service": [
            {"code": "system_logs", "name": "系统日志"},
            {"code": "operation_logs", "name": "操作日志"},
            {"code": "audit_logs", "name": "审计日志"}
        ],
        "text_service": [
            {"code": "tasks", "name": "任务"},
            {"code": "models", "name": "模型"},
        ],
        "image_service": [
            {"code": "tasks", "name": "任务"},
            {"code": "models", "name": "模型"},
        ],
        "video_service": [
            {"code": "tasks", "name": "任务"},
            {"code": "models", "name": "模型"},
        ],
        "video_edit_service": [
            {"code": "tasks", "name": "任务"},
            {"code": "models", "name": "模型"},
        ],
    }
    
    # 硬编码的操作选项
    ACTION_OPTIONS = [
        {"code": "create", "name": "创建"},
        {"code": "read", "name": "读取"},
        {"code": "update", "name": "更新"},
        {"code": "delete", "name": "删除"},
        {"code": "list", "name": "列表"},
        {"code": "cancel", "name": "取消"},
        {"code": "export", "name": "导出"},
        {"code": "import", "name": "导入"},
        {"code": "approve", "name": "审批"},
        {"code": "reject", "name": "拒绝"},
        {"code": "execute", "name": "执行"}
    ]
    
    @action(detail=False, methods=['get'])
    def services(self, request):
        """
        获取服务选项列表
        """
        return self.get_success_response(self.SERVICE_OPTIONS)
    
    @action(detail=False, methods=['get'])
    def resources(self, request):
        """
        获取资源选项列表，可按服务过滤
        """
        service_id = request.query_params.get('service')
        
        if service_id and service_id in self.RESOURCE_OPTIONS:
            # 返回特定服务的资源选项
            return self.get_success_response(self.RESOURCE_OPTIONS[service_id])
        elif service_id:
            # 请求的服务不存在
            return self.get_error_response(
                f"服务 '{service_id}' 不存在", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        else:
            # 返回所有资源选项（按服务分组）
            return self.get_success_response(self.RESOURCE_OPTIONS)
    
    @action(detail=False, methods=['get'])
    def actions(self, request):
        """
        获取操作选项列表
        """
        return self.get_success_response(self.ACTION_OPTIONS)
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """
        获取所有选项信息（服务、资源、操作）
        """
        return self.get_success_response({
            "services": self.SERVICE_OPTIONS,
            "resources": self.RESOURCE_OPTIONS,
            "actions": self.ACTION_OPTIONS
        }) 