"""
服务范围相关的服务类

处理服务、资源和操作的业务逻辑
"""

import logging
from uuid import UUID
from typing import List, Dict, Tuple, Optional, Any

from apps.auth_service.models.service_scope import Service, Resource, Action
from apps.tenant_service.models import Tenant

logger = logging.getLogger('sciTigerCore')


class ServiceScopeService:
    """
    服务范围服务类
    
    提供服务、资源和操作的相关操作
    """
    
    # 服务相关方法
    @classmethod
    def get_services(cls, tenant_id=None, is_system=None):
        """
        获取服务列表
        
        Args:
            tenant_id: 租户ID，如果提供，则返回该租户的服务
            is_system: 是否系统服务，如果提供，则筛选对应类型的服务
            
        Returns:
            QuerySet: 服务查询集
        """
        queryset = Service.objects.all()
        
        if is_system is not None:
            queryset = queryset.filter(is_system=is_system)
            
        if tenant_id is not None:
            # 如果指定了租户，返回系统服务和该租户的服务
            return queryset.filter(is_system=True) | queryset.filter(tenant_id=tenant_id, is_system=False)
            
        return queryset
    
    @classmethod
    def get_service_by_id(cls, service_id):
        """
        根据ID获取服务
        
        Args:
            service_id: 服务ID
            
        Returns:
            Service: 服务对象，如果不存在则返回None
        """
        try:
            return Service.objects.get(id=service_id)
        except (Service.DoesNotExist, ValueError):
            return None
    
    @classmethod
    def get_service_by_code(cls, code, tenant_id=None):
        """
        根据代码获取服务
        
        Args:
            code: 服务代码
            tenant_id: 租户ID，如果提供，则在该租户中查找
            
        Returns:
            Service: 服务对象，如果不存在则返回None
        """
        try:
            if tenant_id:
                # 先尝试查找租户级服务
                try:
                    return Service.objects.get(code=code, tenant_id=tenant_id)
                except Service.DoesNotExist:
                    # 再尝试查找系统服务
                    return Service.objects.get(code=code, is_system=True)
            else:
                # 只查找系统服务
                return Service.objects.get(code=code, is_system=True)
        except Service.DoesNotExist:
            return None
    
    @classmethod
    def create_service(cls, code, name, description=None, is_system=True, tenant_id=None):
        """
        创建服务
        
        Args:
            code: 服务代码
            name: 服务名称
            description: 服务描述
            is_system: 是否系统服务
            tenant_id: 租户ID，如果是租户级服务则必须提供
            
        Returns:
            Tuple[Service, str]: (创建的服务对象, 错误信息)，成功时错误信息为None
        """
        # 验证参数
        if not is_system and not tenant_id:
            return None, "租户级服务必须提供租户ID"
        
        if is_system and tenant_id:
            return None, "系统服务不能关联租户"
        
        # 检查代码是否已存在
        if is_system:
            if Service.objects.filter(code=code, is_system=True).exists():
                return None, f"系统服务代码 '{code}' 已存在"
        else:
            if Service.objects.filter(code=code, tenant_id=tenant_id).exists():
                return None, f"租户级服务代码 '{code}' 在当前租户中已存在"
        
        try:
            # 创建服务
            service = Service(
                code=code,
                name=name,
                description=description,
                is_system=is_system
            )
            
            # 如果是租户级服务，关联租户
            if not is_system:
                try:
                    tenant = Tenant.objects.get(id=tenant_id)
                    service.tenant = tenant
                except Tenant.DoesNotExist:
                    return None, f"租户ID '{tenant_id}' 不存在"
            
            service.save()
            return service, None
        except Exception as e:
            logger.error(f"创建服务失败: {e}")
            return None, f"创建服务失败: {str(e)}"
    
    @classmethod
    def update_service(cls, service_id, **kwargs):
        """
        更新服务
        
        Args:
            service_id: 服务ID
            **kwargs: 要更新的字段
            
        Returns:
            Tuple[Service, str]: (更新后的服务对象, 错误信息)，成功时错误信息为None
        """
        # 获取服务
        service = cls.get_service_by_id(service_id)
        if not service:
            return None, "服务不存在"
        
        # 不允许修改的字段
        not_allowed_fields = ['code', 'is_system', 'tenant']
        for field in not_allowed_fields:
            if field in kwargs:
                kwargs.pop(field)
        
        try:
            # 更新服务
            for key, value in kwargs.items():
                setattr(service, key, value)
            
            service.save()
            return service, None
        except Exception as e:
            logger.error(f"更新服务失败: {e}")
            return None, f"更新服务失败: {str(e)}"
    
    @classmethod
    def delete_service(cls, service_id):
        """
        删除服务
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 是否成功删除
        """
        service = cls.get_service_by_id(service_id)
        if not service:
            return False
        
        try:
            service.delete()
            return True
        except Exception as e:
            logger.error(f"删除服务失败: {e}")
            return False
    
    # 资源相关方法
    @classmethod
    def get_resources(cls, service_id=None, tenant_id=None, is_system=None):
        """
        获取资源列表
        
        Args:
            service_id: 服务ID，如果提供，则返回该服务的资源
            tenant_id: 租户ID，如果提供，则返回系统资源和该租户的资源
            is_system: 是否系统资源，如果提供，则筛选系统服务的资源
            
        Returns:
            QuerySet: 资源查询集
        """
        queryset = Resource.objects.all()
        
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        
        if is_system is not None:
            # 筛选系统服务的资源
            system_services = Service.objects.filter(is_system=is_system)
            queryset = queryset.filter(service__in=system_services)
        
        if tenant_id:
            # 返回系统资源和指定租户的资源
            system_services = Service.objects.filter(is_system=True)
            tenant_services = Service.objects.filter(tenant_id=tenant_id)
            queryset = queryset.filter(service__in=list(system_services) + list(tenant_services))
        
        return queryset
    
    @classmethod
    def get_resource_by_id(cls, resource_id):
        """
        根据ID获取资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            Resource: 资源对象，如果不存在则返回None
        """
        try:
            return Resource.objects.get(id=resource_id)
        except (Resource.DoesNotExist, ValueError):
            return None
    
    @classmethod
    def get_resources_by_service_code(cls, service_code, tenant_id=None):
        """
        根据服务代码获取资源
        
        Args:
            service_code: 服务代码
            tenant_id: 租户ID，如果提供，则在该租户和系统服务中查找
            
        Returns:
            QuerySet: 资源查询集
        """
        service = cls.get_service_by_code(service_code, tenant_id)
        if not service:
            return Resource.objects.none()
        
        return Resource.objects.filter(service=service)
    
    @classmethod
    def create_resource(cls, code, name, service_id, description=None):
        """
        创建资源
        
        Args:
            code: 资源代码
            name: 资源名称
            service_id: 服务ID
            description: 资源描述
            
        Returns:
            Tuple[Resource, str]: (创建的资源对象, 错误信息)，成功时错误信息为None
        """
        # 获取服务
        service = cls.get_service_by_id(service_id)
        if not service:
            return None, f"服务ID '{service_id}' 不存在"
        
        # 检查代码是否已存在
        if Resource.objects.filter(service=service, code=code).exists():
            return None, f"资源代码 '{code}' 在服务 '{service.name}' 中已存在"
        
        try:
            # 创建资源
            resource = Resource(
                code=code,
                name=name,
                description=description,
                service=service
            )
            resource.save()
            return resource, None
        except Exception as e:
            logger.error(f"创建资源失败: {e}")
            return None, f"创建资源失败: {str(e)}"
    
    @classmethod
    def update_resource(cls, resource_id, **kwargs):
        """
        更新资源
        
        Args:
            resource_id: 资源ID
            **kwargs: 要更新的字段
            
        Returns:
            Tuple[Resource, str]: (更新后的资源对象, 错误信息)，成功时错误信息为None
        """
        # 获取资源
        resource = cls.get_resource_by_id(resource_id)
        if not resource:
            return None, "资源不存在"
        
        # 不允许修改的字段
        not_allowed_fields = ['code', 'service']
        for field in not_allowed_fields:
            if field in kwargs:
                kwargs.pop(field)
        
        try:
            # 更新资源
            for key, value in kwargs.items():
                setattr(resource, key, value)
            
            resource.save()
            return resource, None
        except Exception as e:
            logger.error(f"更新资源失败: {e}")
            return None, f"更新资源失败: {str(e)}"
    
    @classmethod
    def delete_resource(cls, resource_id):
        """
        删除资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            bool: 是否成功删除
        """
        resource = cls.get_resource_by_id(resource_id)
        if not resource:
            return False
        
        try:
            resource.delete()
            return True
        except Exception as e:
            logger.error(f"删除资源失败: {e}")
            return False
    
    # 操作相关方法
    @classmethod
    def get_actions(cls, tenant_id=None, is_system=None):
        """
        获取操作列表
        
        Args:
            tenant_id: 租户ID，如果提供，则返回系统操作和该租户的操作
            is_system: 是否系统操作，如果提供，则筛选对应类型的操作
            
        Returns:
            QuerySet: 操作查询集
        """
        queryset = Action.objects.all()
        
        if is_system is not None:
            queryset = queryset.filter(is_system=is_system)
        
        if tenant_id:
            # 如果指定了租户，返回系统操作和该租户的操作
            return queryset.filter(is_system=True) | queryset.filter(tenant_id=tenant_id)
        
        return queryset
    
    @classmethod
    def get_action_by_id(cls, action_id):
        """
        根据ID获取操作
        
        Args:
            action_id: 操作ID
            
        Returns:
            Action: 操作对象，如果不存在则返回None
        """
        try:
            return Action.objects.get(id=action_id)
        except (Action.DoesNotExist, ValueError):
            return None
    
    @classmethod
    def get_action_by_code(cls, code, tenant_id=None):
        """
        根据代码获取操作
        
        Args:
            code: 操作代码
            tenant_id: 租户ID，如果提供，则在该租户中查找
            
        Returns:
            Action: 操作对象，如果不存在则返回None
        """
        try:
            if tenant_id:
                # 先尝试查找租户级操作
                try:
                    return Action.objects.get(code=code, tenant_id=tenant_id)
                except Action.DoesNotExist:
                    # 再尝试查找系统操作
                    return Action.objects.get(code=code, is_system=True)
            else:
                # 只查找系统操作
                return Action.objects.get(code=code, is_system=True)
        except Action.DoesNotExist:
            return None
    
    @classmethod
    def create_action(cls, code, name, description=None, is_system=True, tenant_id=None):
        """
        创建操作
        
        Args:
            code: 操作代码
            name: 操作名称
            description: 操作描述
            is_system: 是否系统操作
            tenant_id: 租户ID，如果是租户级操作则必须提供
            
        Returns:
            Tuple[Action, str]: (创建的操作对象, 错误信息)，成功时错误信息为None
        """
        # 验证参数
        if not is_system and not tenant_id:
            return None, "租户级操作必须提供租户ID"
        
        if is_system and tenant_id:
            return None, "系统操作不能关联租户"
        
        # 检查代码是否已存在
        if is_system:
            if Action.objects.filter(code=code, is_system=True).exists():
                return None, f"系统操作代码 '{code}' 已存在"
        else:
            if Action.objects.filter(code=code, tenant_id=tenant_id).exists():
                return None, f"租户级操作代码 '{code}' 在当前租户中已存在"
        
        try:
            # 创建操作
            action = Action(
                code=code,
                name=name,
                description=description,
                is_system=is_system
            )
            
            # 如果是租户级操作，关联租户
            if not is_system:
                try:
                    tenant = Tenant.objects.get(id=tenant_id)
                    action.tenant = tenant
                except Tenant.DoesNotExist:
                    return None, f"租户ID '{tenant_id}' 不存在"
            
            action.save()
            return action, None
        except Exception as e:
            logger.error(f"创建操作失败: {e}")
            return None, f"创建操作失败: {str(e)}"
    
    @classmethod
    def update_action(cls, action_id, **kwargs):
        """
        更新操作
        
        Args:
            action_id: 操作ID
            **kwargs: 要更新的字段
            
        Returns:
            Tuple[Action, str]: (更新后的操作对象, 错误信息)，成功时错误信息为None
        """
        # 获取操作
        action = cls.get_action_by_id(action_id)
        if not action:
            return None, "操作不存在"
        
        # 不允许修改的字段
        not_allowed_fields = ['code', 'is_system', 'tenant']
        for field in not_allowed_fields:
            if field in kwargs:
                kwargs.pop(field)
        
        try:
            # 更新操作
            for key, value in kwargs.items():
                setattr(action, key, value)
            
            action.save()
            return action, None
        except Exception as e:
            logger.error(f"更新操作失败: {e}")
            return None, f"更新操作失败: {str(e)}"
    
    @classmethod
    def delete_action(cls, action_id):
        """
        删除操作
        
        Args:
            action_id: 操作ID
            
        Returns:
            bool: 是否成功删除
        """
        action = cls.get_action_by_id(action_id)
        if not action:
            return False
        
        try:
            action.delete()
            return True
        except Exception as e:
            logger.error(f"删除操作失败: {e}")
            return False
            
    @classmethod
    def import_default_services(cls):
        """
        导入默认的系统服务、资源和操作
        
        Returns:
            Dict: 导入结果统计
        """
        # 默认服务列表
        default_services = [
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
        
        # 默认资源列表（按服务分组）
        default_resources = {
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
        
        # 默认操作列表
        default_actions = [
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
        
        # 导入统计
        stats = {
            "services": {"created": 0, "existed": 0, "failed": 0},
            "resources": {"created": 0, "existed": 0, "failed": 0},
            "actions": {"created": 0, "existed": 0, "failed": 0}
        }
        
        # 导入服务
        services_map = {}
        for service_data in default_services:
            service = cls.get_service_by_code(service_data["code"])
            if service:
                services_map[service_data["code"]] = service
                stats["services"]["existed"] += 1
                continue
            
            service, error = cls.create_service(
                code=service_data["code"],
                name=service_data["name"],
                description=service_data.get("description"),
                is_system=True
            )
            
            if service:
                services_map[service_data["code"]] = service
                stats["services"]["created"] += 1
            else:
                stats["services"]["failed"] += 1
                logger.error(f"导入系统服务失败: {error}")
        
        # 导入资源
        for service_code, resources in default_resources.items():
            service = services_map.get(service_code)
            if not service:
                continue
            
            for resource_data in resources:
                # 检查资源是否已存在
                existing_resources = Resource.objects.filter(service=service, code=resource_data["code"])
                if existing_resources.exists():
                    stats["resources"]["existed"] += 1
                    continue
                
                resource, error = cls.create_resource(
                    code=resource_data["code"],
                    name=resource_data["name"],
                    service_id=service.id,
                    description=resource_data.get("description")
                )
                
                if resource:
                    stats["resources"]["created"] += 1
                else:
                    stats["resources"]["failed"] += 1
                    logger.error(f"导入系统资源失败: {error}")
        
        # 导入操作
        for action_data in default_actions:
            action = cls.get_action_by_code(action_data["code"])
            if action:
                stats["actions"]["existed"] += 1
                continue
            
            action, error = cls.create_action(
                code=action_data["code"],
                name=action_data["name"],
                description=action_data.get("description"),
                is_system=True
            )
            
            if action:
                stats["actions"]["created"] += 1
            else:
                stats["actions"]["failed"] += 1
                logger.error(f"导入系统操作失败: {error}")
        
        return stats 