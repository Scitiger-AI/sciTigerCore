"""
服务作用域视图

提供获取service、resource、action的管理接口
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import ResponseMixin
from apps.auth_service.models.service_scope import Service, Resource, Action
from apps.auth_service.services import ServiceScopeService
from apps.auth_service.filters import ServiceFilter, ResourceFilter, ActionFilter
from apps.auth_service.serializers import (
    ServiceSerializer, 
    ServiceDetailSerializer, 
    ServiceCreateSerializer, 
    ServiceUpdateSerializer,
    ResourceSerializer, 
    ResourceDetailSerializer, 
    ResourceCreateSerializer, 
    ResourceUpdateSerializer,
    ActionSerializer, 
    ActionDetailSerializer, 
    ActionCreateSerializer, 
    ActionUpdateSerializer
)

logger = logging.getLogger('sciTigerCore')


class ServiceViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    服务管理视图集
    
    提供服务的增删改查接口
    """
    permission_classes = [IsAdminUser]
    serializer_class = ServiceSerializer
    filterset_class = ServiceFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'is_system', 'created_at', 'updated_at']
    ordering = ['-created_at', 'code']  # 默认按服务代码排序
    
    def get_queryset(self):
        """
        获取服务查询集
        
        超级管理员可以查看所有服务，包括所有租户的服务
        普通管理员只能查看系统服务和自己租户的服务
        """
        # 获取当前租户ID
        tenant_id = self.request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        if tenant_id:   
             # 获取系统权限
            system_services = ServiceScopeService.get_services(is_system=True)
            # 获取当前租户的权限
            tenant_services = ServiceScopeService.get_services(tenant_id=tenant_id)
            # 合并查询集
            return system_services | tenant_services
        else:
            return Service.objects.all()
    
    def get_serializer_class(self):
        """
        根据不同的操作返回不同的序列化器
        """
        if self.action == 'retrieve':
            return ServiceDetailSerializer
        elif self.action == 'create':
            return ServiceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ServiceUpdateSerializer
        return self.serializer_class
    
    def list(self, request):
        """
        获取服务列表，支持过滤、搜索和排序
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # 使用DRF的分页机制
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # 如果没有分页或分页被禁用，返回所有数据
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        获取服务详情
        """
        service = ServiceScopeService.get_service_by_id(pk)
        if not service:
            return self.get_error_response("服务不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(service)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建服务
        """
        # 验证数据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 创建服务
        service, error_message = ServiceScopeService.create_service(
            code=serializer.validated_data['code'],
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description'),
            is_system=serializer.validated_data.get('is_system', True),
            tenant_id=serializer.validated_data.get('tenant_id')
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回创建的服务信息
        result_serializer = ServiceDetailSerializer(service)
        return self.get_success_response(
            result_serializer.data,
            message="服务创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None, partial=False):
        """
        更新服务
        """
        # 获取服务
        service = ServiceScopeService.get_service_by_id(pk)
        if not service:
            return self.get_error_response("服务不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 验证数据
        serializer = self.get_serializer(service, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 更新服务
        updated_service, error_message = ServiceScopeService.update_service(
            service_id=pk,
            **serializer.validated_data
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回更新后的服务信息
        result_serializer = ServiceDetailSerializer(updated_service)
        return self.get_success_response(result_serializer.data, message="服务更新成功")
    
    def partial_update(self, request, pk=None):
        """
        部分更新服务
        """
        return self.update(request, pk, partial=True)
    
    def destroy(self, request, pk=None):
        """
        删除服务
        """
        # 删除服务
        success = ServiceScopeService.delete_service(pk)
        
        if not success:
            return self.get_error_response("服务删除失败，可能是服务不存在或已被使用")
        
        return self.get_success_response(message="服务删除成功")
    
    @action(detail=False, methods=['post'])
    def import_default(self, request):
        """
        导入默认的系统服务、资源和操作
        """
        # 只允许超级管理员执行此操作
        if not request.user.is_superuser:
            return self.get_error_response("只有超级管理员可以导入默认服务", status_code=status.HTTP_403_FORBIDDEN)
        
        # 导入默认数据
        stats = ServiceScopeService.import_default_services()
        
        return self.get_success_response(stats, message="默认服务数据导入完成")


class ResourceViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    资源管理视图集
    
    提供资源的增删改查接口
    """
    permission_classes = [IsAdminUser]
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['code', 'name', 'description', 'service__code', 'service__name']
    ordering_fields = ['code', 'name', 'service__code', 'created_at', 'updated_at']
    ordering = ['-created_at', 'service__code', 'code']  # 默认按服务代码和资源代码排序
    
    def get_queryset(self):
        """
        获取资源查询集
        
        超级管理员可以查看所有资源，包括所有租户的资源
        普通管理员只能查看系统资源和自己租户的资源
        """
        # 获取当前租户ID
        tenant_id = self.request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        if tenant_id:   
             # 获取系统权限
            system_resources = ServiceScopeService.get_resources(is_system=True)
            # 获取当前租户的权限
            tenant_resources = ServiceScopeService.get_resources(tenant_id=tenant_id)
            # 合并查询集
            return system_resources | tenant_resources
        else:
            return Resource.objects.all()
    
    def get_serializer_class(self):
        """
        根据不同的操作返回不同的序列化器
        """
        if self.action == 'retrieve':
            return ResourceDetailSerializer
        elif self.action == 'create':
            return ResourceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ResourceUpdateSerializer
        return self.serializer_class
    
    def list(self, request):
        """
        获取资源列表，支持过滤、搜索和排序
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # 使用DRF的分页机制
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # 如果没有分页或分页被禁用，返回所有数据
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        获取资源详情
        """
        resource = ServiceScopeService.get_resource_by_id(pk)
        if not resource:
            return self.get_error_response("资源不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(resource)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建资源
        """
        # 验证数据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 创建资源
        resource, error_message = ServiceScopeService.create_resource(
            code=serializer.validated_data['code'],
            name=serializer.validated_data['name'],
            service_id=serializer.validated_data['service_id'],
            description=serializer.validated_data.get('description')
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回创建的资源信息
        result_serializer = ResourceDetailSerializer(resource)
        return self.get_success_response(
            result_serializer.data,
            message="资源创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None, partial=False):
        """
        更新资源
        """
        # 获取资源
        resource = ServiceScopeService.get_resource_by_id(pk)
        if not resource:
            return self.get_error_response("资源不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 验证数据
        serializer = self.get_serializer(resource, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 更新资源
        updated_resource, error_message = ServiceScopeService.update_resource(
            resource_id=pk,
            **serializer.validated_data
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回更新后的资源信息
        result_serializer = ResourceDetailSerializer(updated_resource)
        return self.get_success_response(result_serializer.data, message="资源更新成功")
    
    def partial_update(self, request, pk=None):
        """
        部分更新资源
        """
        return self.update(request, pk, partial=True)
    
    def destroy(self, request, pk=None):
        """
        删除资源
        """
        # 删除资源
        success = ServiceScopeService.delete_resource(pk)
        
        if not success:
            return self.get_error_response("资源删除失败，可能是资源不存在或已被使用")
        
        return self.get_success_response(message="资源删除成功")
    
    @action(detail=False, methods=['get'])
    def by_service(self, request):
        """
        按服务代码获取资源
        """
        service_code = request.query_params.get('service_code')
        if not service_code:
            return self.get_error_response("缺少service_code参数")
        
        # 获取当前租户ID
        tenant_id = request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 获取指定服务的资源
        resources = ServiceScopeService.get_resources_by_service_code(service_code, tenant_id)
        
        # 序列化并返回
        serializer = self.get_serializer(resources, many=True)
        return self.get_success_response(serializer.data)


class ActionViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    操作管理视图集
    
    提供操作的增删改查接口
    """
    permission_classes = [IsAdminUser]
    serializer_class = ActionSerializer
    filterset_class = ActionFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'is_system', 'created_at', 'updated_at']
    ordering = ['-created_at', 'code']  # 默认按操作代码排序
    
    def get_queryset(self):
        """
        获取操作查询集
        
        超级管理员可以查看所有操作，包括所有租户的操作
        普通管理员只能查看系统操作和自己租户的操作
        """
        # 获取当前租户ID
        tenant_id = self.request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(self.request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        if tenant_id:   
             # 获取系统权限
            system_actions = ServiceScopeService.get_actions(is_system=True)
            # 获取当前租户的权限
            tenant_actions = ServiceScopeService.get_actions(tenant_id=tenant_id)
            # 合并查询集
            return system_actions | tenant_actions
        else:
            return Action.objects.all()
    
    def get_serializer_class(self):
        """
        根据不同的操作返回不同的序列化器
        """
        if self.action == 'retrieve':
            return ActionDetailSerializer
        elif self.action == 'create':
            return ActionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ActionUpdateSerializer
        return self.serializer_class
    
    def list(self, request):
        """
        获取操作列表，支持过滤、搜索和排序
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # 使用DRF的分页机制
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # 如果没有分页或分页被禁用，返回所有数据
        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        获取操作详情
        """
        action = ServiceScopeService.get_action_by_id(pk)
        if not action:
            return self.get_error_response("操作不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(action)
        return self.get_success_response(serializer.data)
    
    def create(self, request):
        """
        创建操作
        """
        # 验证数据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 创建操作
        action, error_message = ServiceScopeService.create_action(
            code=serializer.validated_data['code'],
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description'),
            is_system=serializer.validated_data.get('is_system', True),
            tenant_id=serializer.validated_data.get('tenant_id')
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回创建的操作信息
        result_serializer = ActionDetailSerializer(action)
        return self.get_success_response(
            result_serializer.data,
            message="操作创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None, partial=False):
        """
        更新操作
        """
        # 获取操作
        action = ServiceScopeService.get_action_by_id(pk)
        if not action:
            return self.get_error_response("操作不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        # 验证数据
        serializer = self.get_serializer(action, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 更新操作
        updated_action, error_message = ServiceScopeService.update_action(
            action_id=pk,
            **serializer.validated_data
        )
        
        if error_message:
            return self.get_error_response(error_message)
        
        # 返回更新后的操作信息
        result_serializer = ActionDetailSerializer(updated_action)
        return self.get_success_response(result_serializer.data, message="操作更新成功")
    
    def partial_update(self, request, pk=None):
        """
        部分更新操作
        """
        return self.update(request, pk, partial=True)
    
    def destroy(self, request, pk=None):
        """
        删除操作
        """
        # 删除操作
        success = ServiceScopeService.delete_action(pk)
        
        if not success:
            return self.get_error_response("操作删除失败，可能是操作不存在或已被使用")
        
        return self.get_success_response(message="操作删除成功")


class ServiceScopeViewSet(ResponseMixin, viewsets.GenericViewSet):
    """
    服务作用域视图集
    
    提供获取service、resource、action的选项信息的兼容接口
    """
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def services(self, request):
        """
        获取服务选项列表
        """
        # 获取当前租户ID
        tenant_id = request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 获取服务列表
        if not tenant_id:
            # 如果没有指定tenant_id，返回系统服务
            services = ServiceScopeService.get_services()  # management 中不区分系统服务和租户服务
        else:
            # 返回系统服务和租户服务
            system_services = ServiceScopeService.get_services(is_system=True)
            tenant_services = ServiceScopeService.get_services(tenant_id=tenant_id)
            services = system_services | tenant_services
        
        # 转换为原有的格式
        result = []
        for service in services:
            result.append({
                "code": service.code,
                "name": service.name,
                "description": service.description or ""
            })
        
        return self.get_success_response(result)
    
    @action(detail=False, methods=['get'])
    def resources(self, request):
        """
        获取资源选项列表，可按服务过滤
        """
        # 获取当前租户ID
        tenant_id = request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 获取服务代码
        service_id = request.query_params.get('service')
        
        if service_id:
            # 获取特定服务的资源
            service = ServiceScopeService.get_service_by_code(service_id, tenant_id)
            if not service:
                return self.get_error_response(
                    f"服务 '{service_id}' 不存在", 
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            resources = Resource.objects.filter(service=service)
            
            # 转换为原有的格式
            result = []
            for resource in resources:
                result.append({
                    "code": resource.code,
                    "name": resource.name
                })
            
            return self.get_success_response(result)
        else:
            # 返回所有资源（按服务分组）
            result = {}
            
            # 获取系统服务和租户级服务
            if not tenant_id:
                # 如果没有指定tenant_id，返回系统服务
                services = ServiceScopeService.get_services()  # management 中不区分系统服务和租户服务
            else:
                # 返回系统服务和租户服务
                system_services = ServiceScopeService.get_services(is_system=True)
                tenant_services = ServiceScopeService.get_services(tenant_id=tenant_id)
                services = system_services | tenant_services
            
            # 按服务分组资源
            for service in services:
                resources = Resource.objects.filter(service=service)
                result[service.code] = []
                
                for resource in resources:
                    result[service.code].append({
                        "code": resource.code,
                        "name": resource.name
                    })
            
            return self.get_success_response(result)
    
    @action(detail=False, methods=['get'])
    def actions(self, request):
        """
        获取操作选项列表
        """
        # 获取当前租户ID
        tenant_id = request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 获取操作列表（系统操作和租户操作）
        if not tenant_id:
            # 如果没有指定tenant_id，返回系统操作
            actions = ServiceScopeService.get_actions()  # management 中不区分系统操作和租户操作
        else:
            # 返回系统操作和租户操作
            system_actions = ServiceScopeService.get_actions(is_system=True)
            tenant_actions = ServiceScopeService.get_actions(tenant_id=tenant_id)
            actions = system_actions | tenant_actions
        
        # 转换为原有的格式
        result = []
        for action in actions:
            result.append({
                "code": action.code,
                "name": action.name
            })
        
        return self.get_success_response(result)
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """
        获取所有选项信息（服务、资源、操作）
        """
        # 获取当前租户ID
        tenant_id = request.query_params.get('tenant_id')
        if not tenant_id:
            tenant_id = getattr(request, 'tenant_id', None)
            tenant_id = tenant_id.id if tenant_id else None
        
        # 获取服务列表
        if not tenant_id:
            # 如果没有指定tenant_id，返回系统服务
            services = ServiceScopeService.get_services()  # management 中不区分系统服务和租户服务
        else:
            # 返回系统服务和租户服务
            system_services = ServiceScopeService.get_services(is_system=True)
            tenant_services = ServiceScopeService.get_services(tenant_id=tenant_id)
            services = system_services | tenant_services
        
        services_data = []
        for service in services:
            services_data.append({
                "code": service.code,
                "name": service.name,
                "description": service.description or ""
            })
        
        # 获取资源列表（按服务分组）
        resources_data = {}
        for service in services:
            resources = Resource.objects.filter(service=service)
            resources_data[service.code] = []
            
            for resource in resources:
                resources_data[service.code].append({
                    "code": resource.code,
                    "name": resource.name
                })
        
        # 获取操作列表
        if not tenant_id:
            # 如果没有指定tenant_id，返回系统操作
            actions = ServiceScopeService.get_actions()  # management 中不区分系统操作和租户操作
        else:
            # 返回系统操作和租户操作
            system_actions = ServiceScopeService.get_actions(is_system=True)
            tenant_actions = ServiceScopeService.get_actions(tenant_id=tenant_id)
            actions = system_actions | tenant_actions
        
        actions_data = []
        for action in actions:
            actions_data.append({
                "code": action.code,
                "name": action.name
            })
        
        return self.get_success_response({
            "services": services_data,
            "resources": resources_data,
            "actions": actions_data
        }) 