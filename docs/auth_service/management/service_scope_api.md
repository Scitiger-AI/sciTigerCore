# 服务作用域API文档

本文档描述了SciTigerCore平台的服务作用域API，这些API用于获取系统中的服务、资源和操作选项信息，主要用于权限配置和API密钥作用域设置等场景。

## API基础信息

- **基础路径**: `/api/management/auth/service-scopes/`
- **认证方式**: JWT令牌认证（需要管理员权限）
- **响应格式**: 统一的JSON响应格式

## 统一响应格式

### 成功响应

```json
{
    "success": true,
    "message": "操作成功描述（可选）",
    "results": {
        // 返回的数据内容
    }
}
```

### 错误响应

```json
{
    "success": false,
    "message": "错误描述信息"
}
```

## 接口列表

### 1. 获取服务选项列表

获取系统中所有可用的服务选项。

- **URL**: `/api/management/auth/service-scopes/services/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": [
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
        }
    ]
}
```

### 2. 获取资源选项列表

获取系统中所有资源选项或特定服务的资源选项。

- **URL**: `/api/management/auth/service-scopes/resources/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 查询参数

| 参数名          | 类型    | 必填 | 描述               |
|-----------------|---------|------|-------------------|
| service         | string  | 否   | 服务代码，用于过滤特定服务的资源 |

#### 响应示例

**成功响应 - 所有资源 (200 OK)**

```json
{
    "success": true,
    "results": {
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
        ]
    }
}
```

**成功响应 - 特定服务的资源 (200 OK)**

```json
{
    "success": true,
    "results": [
        {"code": "users", "name": "用户"},
        {"code": "roles", "name": "角色"},
        {"code": "permissions", "name": "权限"},
        {"code": "api_keys", "name": "API密钥"}
    ]
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "服务 'unknown_service' 不存在"
}
```

### 3. 获取操作选项列表

获取系统中所有可用的操作选项。

- **URL**: `/api/management/auth/service-scopes/actions/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": [
        {"code": "create", "name": "创建"},
        {"code": "read", "name": "读取"},
        {"code": "update", "name": "更新"},
        {"code": "delete", "name": "删除"},
        {"code": "list", "name": "列表"},
        {"code": "export", "name": "导出"},
        {"code": "import", "name": "导入"},
        {"code": "approve", "name": "审批"},
        {"code": "reject", "name": "拒绝"},
        {"code": "execute", "name": "执行"}
    ]
}
```

### 4. 获取所有选项信息

获取系统中所有服务、资源和操作选项信息。

- **URL**: `/api/management/auth/service-scopes/all/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "services": [
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
            }
        ],
        "resources": {
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
            ]
        },
        "actions": [
            {"code": "create", "name": "创建"},
            {"code": "read", "name": "读取"},
            {"code": "update", "name": "更新"},
            {"code": "delete", "name": "删除"},
            {"code": "list", "name": "列表"},
            {"code": "export", "name": "导出"},
            {"code": "import", "name": "导入"},
            {"code": "approve", "name": "审批"},
            {"code": "reject", "name": "拒绝"},
            {"code": "execute", "name": "执行"}
        ]
    }
}
```

## 使用场景

服务作用域API主要用于以下场景：

1. **权限管理**：在创建或编辑权限时，提供服务、资源和操作的选项
2. **API密钥作用域设置**：在设置API密钥的作用域时，提供可选的服务、资源和操作
3. **权限配置界面**：为权限配置界面提供标准化的选项数据
4. **角色权限分配**：在为角色分配权限时，提供服务、资源和操作的选项
5. **自定义权限创建**：在创建自定义权限时，提供标准化的服务、资源和操作选项

## 实现说明

当前API采用硬编码方式实现，后续可能会改为数据库存储形式，以支持更灵活的服务作用域配置。 