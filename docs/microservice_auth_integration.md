# SciTigerCore微服务认证集成指南

本文档详细说明了其他微服务如何使用SciTigerCore提供的认证验证API来验证用户身份和权限。

## 1. 认证验证API概述

SciTigerCore提供了两个专门用于微服务的认证验证API：

1. **JWT令牌验证API**：验证JWT令牌的有效性和用户权限
2. **API密钥验证API**：验证API密钥的有效性和权限范围

这两个API都不需要认证即可调用，专门设计用于微服务间的认证验证。

## 2. JWT令牌验证

### 2.1 API端点

- **URL**：`/api/platform/auth/microservice/verify-token/`
- **方法**：POST
- **认证要求**：无（无需认证即可调用）

### 2.2 请求格式

```json
{
    "token": "JWT令牌",
    "service": "微服务名称（可选）",
    "resource": "资源类型（可选）",
    "action": "操作类型（可选）"
}
```

参数说明：
- `token`：要验证的JWT令牌（必需）
- `service`：微服务名称，用于权限检查（可选）
- `resource`：资源类型，用于权限检查（可选）
- `action`：操作类型，用于权限检查（可选）

当提供了`service`、`resource`和`action`时，API会检查用户是否有权限执行指定操作。

### 2.3 响应格式

成功响应：

```json
{
    "success": true,
    "message": "令牌验证成功",
    "results": {
        "id": "用户ID",
        "username": "用户名",
        "email": "用户邮箱",
        "is_active": true,
        "tenant_id": "租户ID",
        "roles": [
            {
                "id": "角色ID",
                "name": "角色名称"
            }
        ],
        "permissions": [
            {
                "id": "权限ID",
                "codename": "权限代码"
            }
        ]
    }
}
```

失败响应：

```json
{
    "success": false,
    "message": "失败原因"
}
```

### 2.4 集成示例

```python
import requests

def verify_token(token, service=None, resource=None, action=None):
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
        service: 服务名称（可选）
        resource: 资源类型（可选）
        action: 操作类型（可选）
        
    Returns:
        tuple: (is_valid, user_info, error_message)
            is_valid: 令牌是否有效
            user_info: 用户信息（令牌有效时）
            error_message: 错误信息（令牌无效时）
    """
    url = "https://core-service.example.com/api/platform/auth/microservice/verify-token/"
    
    # 准备请求数据
    data = {"token": token}
    
    # 添加可选参数
    if service:
        data["service"] = service
    if resource:
        data["resource"] = resource
    if action:
        data["action"] = action
    
    try:
        # 发送请求
        response = requests.post(url, json=data)
        
        # 解析响应
        result = response.json()
        
        if response.status_code == 200 and result.get("success"):
            # 令牌有效
            return True, result.get("results"), None
        else:
            # 令牌无效
            return False, None, result.get("message", "未知错误")
    
    except Exception as e:
        # 请求异常
        return False, None, str(e)
```

## 3. API密钥验证

### 3.1 API端点

- **URL**：`/api/platform/auth/microservice/verify-api-key/`
- **方法**：POST
- **认证要求**：无（无需认证即可调用）

### 3.2 请求格式

```json
{
    "key": "API密钥",
    "service": "微服务名称（可选）",
    "resource": "资源类型（可选）",
    "action": "操作类型（可选）"
}
```

参数说明：
- `key`：要验证的API密钥（必需）
- `service`：微服务名称，用于权限检查（可选）
- `resource`：资源类型，用于权限检查（可选）
- `action`：操作类型，用于权限检查（可选）

当提供了`service`、`resource`和`action`时，API会检查API密钥是否有权限执行指定操作。

### 3.3 响应格式

成功响应：

```json
{
    "success": true,
    "message": "API密钥验证成功",
    "results": {
        "id": "API密钥ID",
        "key_type": "system或user",
        "name": "API密钥名称",
        "prefix": "API密钥前缀",
        "is_active": true,
        "tenant_id": "租户ID",
        "user_id": "用户ID（用户级API密钥）",
        "application_name": "应用名称",
        "scopes": [
            {
                "id": "作用域ID",
                "service": "服务名称",
                "resource": "资源类型",
                "action": "操作类型"
            }
        ],
        "user": {  // 仅用户级API密钥
            "id": "用户ID",
            "username": "用户名",
            "email": "用户邮箱",
            "is_active": true,
            "roles": [...],
            "permissions": [...]
        }
    }
}
```

失败响应：

```json
{
    "success": false,
    "message": "失败原因"
}
```

### 3.4 集成示例

```python
import requests

def verify_api_key(key, service=None, resource=None, action=None):
    """
    验证API密钥
    
    Args:
        key: API密钥
        service: 服务名称（可选）
        resource: 资源类型（可选）
        action: 操作类型（可选）
        
    Returns:
        tuple: (is_valid, api_key_info, error_message)
            is_valid: API密钥是否有效
            api_key_info: API密钥信息（API密钥有效时）
            error_message: 错误信息（API密钥无效时）
    """
    url = "https://core-service.example.com/api/platform/auth/microservice/verify-api-key/"
    
    # 准备请求数据
    data = {"key": key}
    
    # 添加可选参数
    if service:
        data["service"] = service
    if resource:
        data["resource"] = resource
    if action:
        data["action"] = action
    
    try:
        # 发送请求
        response = requests.post(url, json=data)
        
        # 解析响应
        result = response.json()
        
        if response.status_code == 200 and result.get("success"):
            # API密钥有效
            return True, result.get("results"), None
        else:
            # API密钥无效
            return False, None, result.get("message", "未知错误")
    
    except Exception as e:
        # 请求异常
        return False, None, str(e)
```

## 4. 在微服务中使用认证验证

### 4.1 创建认证中间件

您可以在微服务中创建认证中间件，在每个请求处理前验证认证信息：

```python
from django.http import JsonResponse

class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 从请求中提取令牌
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # 验证令牌
            is_valid, user_info, error = verify_token(
                token,
                service='your-service-name'
            )
            
            if is_valid:
                # 令牌有效，将用户信息附加到请求
                request.user_info = user_info
                request.is_authenticated = True
            else:
                # 令牌无效
                request.is_authenticated = False
                request.auth_error = error
        else:
            # 没有提供令牌
            request.is_authenticated = False
        
        # 继续处理请求
        response = self.get_response(request)
        return response


class ApiKeyAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 从请求中提取API密钥
        key = None
        
        # 尝试从Authorization头获取
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('ApiKey ') or auth_header.startswith('Bearer '):
            key = auth_header.split(' ')[1]
        
        # 尝试从X-Api-Key头获取
        if not key:
            key = request.headers.get('X-Api-Key')
        
        # 尝试从查询参数获取
        if not key and 'api_key' in request.GET:
            key = request.GET.get('api_key')
        
        if key:
            # 验证API密钥
            is_valid, api_key_info, error = verify_api_key(
                key,
                service='your-service-name'
            )
            
            if is_valid:
                # API密钥有效，将API密钥信息附加到请求
                request.api_key_info = api_key_info
                request.is_authenticated = True
                
                # 保存API密钥的作用域信息
                request.api_key_scopes = api_key_info.get('scopes', [])
                
                # 如果是用户级API密钥，也附加用户信息
                if 'user' in api_key_info:
                    request.user_info = api_key_info['user']
            else:
                # API密钥无效
                request.is_authenticated = False
                request.auth_error = error
        else:
            # 没有提供API密钥
            request.is_authenticated = False
        
        # 继续处理请求
        response = self.get_response(request)
        return response
```

### 4.2 注册中间件

在您的微服务配置中注册中间件：

```python
# settings.py

MIDDLEWARE = [
    # ...其他中间件...
    'your_app.middleware.TokenAuthMiddleware',
    'your_app.middleware.ApiKeyAuthMiddleware',
]
```

### 4.3 创建权限装饰器

创建一个装饰器，用于检查请求是否已通过认证：

```python
from functools import wraps
from django.http import JsonResponse

def authenticated_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, 'is_authenticated', False):
            return JsonResponse({
                'success': False,
                'message': getattr(request, 'auth_error', '认证失败')
            }, status=401)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
```

### 4.4 在视图中使用

在您的视图中使用装饰器：

```python
@authenticated_required
def your_api_view(request):
    # 获取用户信息或API密钥信息
    user_info = getattr(request, 'user_info', None)
    api_key_info = getattr(request, 'api_key_info', None)
    
    # 处理请求
    # ...
    
    return JsonResponse({
        'success': True,
        'message': '操作成功',
        'data': {...}
    })
```

### 4.5 使用API密钥作用域进行权限检查

当使用API密钥认证时，您可以利用API密钥的作用域信息进行更细粒度的权限控制：

```python
from functools import wraps
from django.http import JsonResponse

def scope_required(service, resource, action):
    """
    检查API密钥是否具有特定作用域的装饰器
    
    Args:
        service: 服务名称
        resource: 资源类型
        action: 操作类型
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 检查是否已通过认证
            if not getattr(request, 'is_authenticated', False):
                return JsonResponse({
                    'success': False,
                    'message': getattr(request, 'auth_error', '认证失败')
                }, status=401)
            
            # 获取API密钥作用域
            api_key_scopes = getattr(request, 'api_key_scopes', [])
            
            # 检查是否有所需作用域
            has_scope = False
            for scope in api_key_scopes:
                if (scope.get('service') == service and 
                    scope.get('resource') == resource and 
                    scope.get('action') == action):
                    has_scope = True
                    break
            
            if not has_scope:
                return JsonResponse({
                    'success': False,
                    'message': '权限不足，API密钥没有所需的作用域'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

在视图中使用作用域检查装饰器：

```python
@authenticated_required
@scope_required(service='user-service', resource='user', action='read')
def get_user_info(request, user_id):
    # 此视图只有在API密钥具有'user-service.read_user'作用域时才能访问
    # ...
    
    return JsonResponse({
        'success': True,
        'message': '获取用户信息成功',
        'data': {...}
    })
```

## 5. 缓存优化（可选）

为了提高性能，您可以在微服务中实现认证信息的缓存：

```python
import time
from functools import lru_cache

# 使用LRU缓存来缓存令牌验证结果，最多缓存1000个结果，缓存时间1分钟
@lru_cache(maxsize=1000)
def cached_verify_token(token, service=None, resource=None, action=None, timestamp=None):
    """
    带缓存的令牌验证
    
    Args:
        token: JWT令牌
        service: 服务名称
        resource: 资源类型
        action: 操作类型
        timestamp: 时间戳，用于控制缓存过期
        
    Returns:
        tuple: (is_valid, user_info, error_message)
    """
    # 忽略timestamp参数，它只用于控制缓存
    return verify_token(token, service, resource, action)

def verify_token_with_cache(token, service=None, resource=None, action=None, cache_ttl=60):
    """
    带缓存控制的令牌验证
    
    Args:
        token: JWT令牌
        service: 服务名称
        resource: 资源类型
        action: 操作类型
        cache_ttl: 缓存时间（秒）
        
    Returns:
        tuple: (is_valid, user_info, error_message)
    """
    # 计算时间戳，控制缓存过期
    timestamp = int(time.time() / cache_ttl)
    
    # 调用缓存版本的验证函数
    return cached_verify_token(token, service, resource, action, timestamp)
```

## 6. 健壮性和错误处理

为了提高微服务认证的健壮性，您应该：

1. 实现重试机制
2. 添加超时控制
3. 实现熔断机制
4. 添加适当的日志记录

示例：

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retry():
    """创建带有重试机制的会话"""
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        method_whitelist=["POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def verify_token_robust(token, service=None, resource=None, action=None):
    """带有健壮性的令牌验证"""
    url = "https://core-service.example.com/api/platform/auth/microservice/verify-token/"
    
    # 准备请求数据
    data = {"token": token}
    if service:
        data["service"] = service
    if resource:
        data["resource"] = resource
    if action:
        data["action"] = action
    
    try:
        # 使用带重试的会话发送请求
        session = create_session_with_retry()
        response = session.post(url, json=data, timeout=3)
        
        # 解析响应
        result = response.json()
        
        if response.status_code == 200 and result.get("success"):
            return True, result.get("results"), None
        else:
            return False, None, result.get("message", "未知错误")
    
    except requests.exceptions.Timeout:
        # 请求超时
        return False, None, "认证服务请求超时"
    
    except requests.exceptions.RequestException as e:
        # 请求异常
        return False, None, f"认证服务请求异常: {str(e)}"
    
    except Exception as e:
        # 其他异常
        return False, None, f"认证验证异常: {str(e)}"


def verify_api_key_robust(key, service=None, resource=None, action=None):
    """带有健壮性的API密钥验证"""
    url = "https://core-service.example.com/api/platform/auth/microservice/verify-api-key/"
    
    # 准备请求数据
    data = {"key": key}
    if service:
        data["service"] = service
    if resource:
        data["resource"] = resource
    if action:
        data["action"] = action
    
    try:
        # 使用带重试的会话发送请求
        session = create_session_with_retry()
        response = session.post(url, json=data, timeout=3)
        
        # 解析响应
        result = response.json()
        
        if response.status_code == 200 and result.get("success"):
            return True, result.get("results"), None
        else:
            return False, None, result.get("message", "未知错误")
    
    except requests.exceptions.Timeout:
        # 请求超时
        return False, None, "API密钥验证服务请求超时"
    
    except requests.exceptions.RequestException as e:
        # 请求异常
        return False, None, f"API密钥验证服务请求异常: {str(e)}"
    
    except Exception as e:
        # 其他异常
        return False, None, f"API密钥验证异常: {str(e)}"
```

## 7. 安全建议

1. 始终使用HTTPS进行认证验证请求
2. 不要在客户端代码中存储API密钥
3. 考虑使用API网关或服务网格来统一处理认证
4. 定期轮换API密钥
5. 监控认证失败事件，并设置告警
6. 实现适当的访问控制和权限检查

## 8. 故障排查

如果遇到认证问题，可以尝试以下步骤：

1. 检查令牌或API密钥是否正确
2. 确认令牌未过期
3. 验证权限设置是否正确
4. 检查网络连接
5. 查看认证服务和微服务的日志
6. 使用工具直接调用认证API进行测试

### 8.1 API密钥作用域问题排查

如果使用API密钥时遇到权限问题，请特别检查以下几点：

1. 确认API密钥是否有效且处于激活状态
2. 检查API密钥是否具有所需的作用域
   - 在验证响应中查看`scopes`字段
   - 确认作用域包含所需的`service`、`resource`和`action`组合
3. 如果是用户级API密钥，检查关联用户是否有所需权限
4. 使用以下工具脚本直接测试API密钥的作用域：

```python
import requests
import json

def test_api_key_scope(key, service, resource, action):
    """测试API密钥是否具有特定作用域"""
    url = "https://core-service.example.com/api/platform/auth/microservice/verify-api-key/"
    
    data = {
        "key": key,
        "service": service,
        "resource": resource,
        "action": action
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and result.get("success"):
            print("\n✅ API密钥验证成功")
            
            # 检查作用域
            scopes = result.get("results", {}).get("scopes", [])
            has_scope = False
            for scope in scopes:
                if (scope.get("service") == service and 
                    scope.get("resource") == resource and 
                    scope.get("action") == action):
                    has_scope = True
                    break
            
            if has_scope:
                print(f"✅ API密钥具有所需作用域: {service}.{action}_{resource}")
            else:
                print(f"❌ API密钥缺少所需作用域: {service}.{action}_{resource}")
                print("可用作用域:")
                for scope in scopes:
                    print(f"  - {scope.get('service')}.{scope.get('action')}_{scope.get('resource')}")
        else:
            print(f"\n❌ API密钥验证失败: {result.get('message', '未知错误')}")
    
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 使用示例
if __name__ == "__main__":
    test_api_key_scope(
        key="your-api-key",
        service="user-service",
        resource="user",
        action="read"
    )
``` 