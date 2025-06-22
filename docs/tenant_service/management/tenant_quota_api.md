# 租户配额管理API文档

本文档描述了SciTigerCore平台的租户配额管理API，这些API专为系统管理员设计，提供租户资源配额的查询和修改功能。

## API基础信息

- **基础路径**: `/api/management/tenants/quotas/`
- **认证方式**: JWT令牌认证（需要超级管理员权限）
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

### 1. 获取租户配额列表

获取系统中的租户配额列表。

- **URL**: `/api/management/tenants/quotas/`
- **方法**: `GET`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名    | 类型   | 必填 | 描述           |
|-----------|--------|------|----------------|
| tenant_id | string | 否   | 筛选特定租户   |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "tenant": {
                "id": "650e8400-e29b-41d4-a716-446655440000",
                "name": "租户1",
                "slug": "tenant1"
            },
            "max_users": 50,
            "max_storage_gb": 100,
            "max_api_keys": 20,
            "max_api_requests_per_day": 10000,
            "current_api_calls_today": 2500,
            "current_api_calls_this_month": 45000,
            "max_log_retention_days": 30,
            "max_notifications_per_day": 1000,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "tenant": {
                "id": "650e8400-e29b-41d4-a716-446655440001",
                "name": "租户2",
                "slug": "tenant2"
            },
            "max_users": 100,
            "max_storage_gb": 500,
            "max_api_keys": 50,
            "max_api_requests_per_day": 50000,
            "current_api_calls_today": 12000,
            "current_api_calls_this_month": 230000,
            "max_log_retention_days": 90,
            "max_notifications_per_day": 5000,
            "created_at": "2023-01-02T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z"
        }
    ]
}
```

### 2. 获取租户配额详情

获取特定租户配额的详细信息。

- **URL**: `/api/management/tenants/quotas/{quota_id}/`
- **方法**: `GET`
- **权限要求**: 超级管理员权限

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
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "name": "租户1",
            "slug": "tenant1",
            "subdomain": "tenant1"
        },
        "max_users": 50,
        "current_users": 32,
        "max_storage_gb": 100,
        "current_storage_gb": 45.6,
        "max_api_keys": 20,
        "current_api_keys": 8,
        "max_api_requests_per_day": 10000,
        "current_api_calls_today": 2500,
        "current_api_calls_this_month": 45000,
        "max_log_retention_days": 30,
        "max_notifications_per_day": 1000,
        "current_notifications_today": 250,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "租户配额不存在"
}
```

### 3. 根据租户ID获取配额

根据租户ID获取对应的租户配额。

- **URL**: `/api/management/tenants/quotas/by_tenant/`
- **方法**: `GET`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名    | 类型   | 必填 | 描述       |
|-----------|--------|------|------------|
| tenant_id | string | 是   | 租户ID     |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "name": "租户1",
            "slug": "tenant1"
        },
        "max_users": 50,
        "current_users": 32,
        "max_storage_gb": 100,
        "current_storage_gb": 45.6,
        "max_api_keys": 20,
        "current_api_keys": 8,
        "max_api_requests_per_day": 10000,
        "current_api_calls_today": 2500,
        "current_api_calls_this_month": 45000,
        "max_log_retention_days": 30,
        "max_notifications_per_day": 1000,
        "current_notifications_today": 250,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "必须指定租户ID"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "指定的租户不存在"
}
```

### 4. 更新租户配额

更新特定租户配额的信息。

- **URL**: `/api/management/tenants/quotas/{quota_id}/`
- **方法**: `PUT` 或 `PATCH`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名                   | 类型    | 必填 | 描述                   |
|--------------------------|---------|------|----------------------|
| max_users                | integer | 否   | 最大用户数             |
| max_storage_gb           | integer | 否   | 最大存储空间(GB)       |
| max_api_keys             | integer | 否   | 最大API密钥数量        |
| max_api_requests_per_day | integer | 否   | 每日最大API请求数      |
| max_log_retention_days   | integer | 否   | 日志保留天数           |
| max_notifications_per_day| integer | 否   | 每日最大通知数量       |

#### 请求示例

```json
{
    "max_users": 100,
    "max_storage_gb": 200,
    "max_api_keys": 30,
    "max_api_requests_per_day": 20000,
    "max_log_retention_days": 60,
    "max_notifications_per_day": 2000
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "租户配额已更新",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "name": "租户1",
            "slug": "tenant1"
        },
        "max_users": 100,
        "current_users": 32,
        "max_storage_gb": 200,
        "current_storage_gb": 45.6,
        "max_api_keys": 30,
        "current_api_keys": 8,
        "max_api_requests_per_day": 20000,
        "current_api_calls_today": 2500,
        "current_api_calls_this_month": 45000,
        "max_log_retention_days": 60,
        "max_notifications_per_day": 2000,
        "current_notifications_today": 250,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "租户配额不存在"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "配额值必须为正整数"
}
```

### 5. 重置API调用计数

重置特定租户的API调用计数。

- **URL**: `/api/management/tenants/quotas/{quota_id}/reset_api_calls/`
- **方法**: `POST`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "API调用计数已重置",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "name": "租户1",
            "slug": "tenant1"
        },
        "max_users": 50,
        "max_storage_gb": 100,
        "max_api_keys": 20,
        "max_api_requests_per_day": 10000,
        "current_api_calls_today": 0,
        "current_api_calls_this_month": 0,
        "max_log_retention_days": 30,
        "max_notifications_per_day": 1000,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "租户配额不存在"
}
```

## 错误码说明

| 状态码 | 描述                                 |
|--------|------------------------------------|
| 200    | 请求成功                             |
| 400    | 请求参数错误                         |
| 401    | 未授权（未提供认证凭据或凭据无效）     |
| 403    | 禁止访问（权限不足）                 |
| 404    | 资源不存在                           |
| 500    | 服务器内部错误                       |

## 注意事项

1. 所有接口都需要超级管理员权限，非超级管理员用户无法访问
2. 租户配额在创建租户时会自动生成默认配置
3. 配额限制会影响租户的资源使用，超过配额限制后相应功能可能会受限
4. API调用计数每日自动重置，也可以通过专门的接口手动重置
5. 配额调整会立即生效，但不会影响已经使用的资源（如已创建的用户） 