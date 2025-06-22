# 管理API密钥API文档

本文档描述了SciTigerCore平台的管理API密钥API，这些API专为系统管理员设计，提供API密钥的创建、查询、更新和删除等功能。

## API基础信息

- **基础路径**: `/api/management/auth/api-keys/`
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

### 分页响应

```json
{
    "success": true,
    "message": null,
    "results": {
        "total": 100,
        "page_size": 10,
        "current_page": 1,
        "total_pages": 10,
        "next": "http://example.com/api/management/auth/api-keys/?page=2",
        "previous": null,
        "results": [
            // 数据列表
        ]
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

### 1. 获取API密钥列表

获取系统中的API密钥列表。

- **URL**: `/api/management/auth/api-keys/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 查询参数

| 参数名      | 类型    | 必填 | 描述           |
|------------|---------|------|----------------|
| key_type   | string  | 否   | 密钥类型(system/user) |
| user_id    | string  | 否   | 用户ID过滤     |
| tenant_id  | string  | 否   | 租户ID过滤     |
| is_active  | boolean | 否   | 是否激活       |
| search     | string  | 否   | 全局搜索       |
| page       | integer | 否   | 页码           |
| page_size  | integer | 否   | 每页条数       |
| ordering   | string  | 否   | 排序字段       |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "total": 2,
        "page_size": 10,
        "current_page": 1,
        "total_pages": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": "750e8400-e29b-41d4-a716-446655440000",
                "key_type": "system",
                "prefix": "a1b2c3d4",
                "name": "系统API密钥",
                "tenant": "550e8400-e29b-41d4-a716-446655440000",
                "user": null,
                "is_active": true,
                "created_at": "2023-01-01T00:00:00Z",
                "expires_at": "2024-01-01T00:00:00Z",
                "last_used_at": "2023-06-15T08:30:45Z",
                "application_name": "外部系统集成"
            },
            {
                "id": "750e8400-e29b-41d4-a716-446655440001",
                "key_type": "user",
                "prefix": "e5f6g7h8",
                "name": "用户API密钥",
                "tenant": "550e8400-e29b-41d4-a716-446655440000",
                "user": "450e8400-e29b-41d4-a716-446655440000",
                "is_active": true,
                "created_at": "2023-01-01T00:00:00Z",
                "expires_at": null,
                "last_used_at": "2023-06-16T10:20:30Z",
                "application_name": "移动应用"
            }
        ]
    }
}
```

### 2. 获取API密钥详情

获取特定API密钥的详细信息。

- **URL**: `/api/management/auth/api-keys/{api_key_id}/`
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
        "id": "750e8400-e29b-41d4-a716-446655440000",
        "key_type": "system",
        "prefix": "a1b2c3d4",
        "name": "系统API密钥",
        "tenant": "550e8400-e29b-41d4-a716-446655440000",
        "user": null,
        "is_active": true,
        "created_at": "2023-01-01T00:00:00Z",
        "expires_at": "2024-01-01T00:00:00Z",
        "last_used_at": "2023-06-15T08:30:45Z",
        "application_name": "外部系统集成",
        "created_by_key_name": null,
        "metadata": {
            "description": "用于外部系统集成的API密钥",
            "created_by": "admin"
        },
        "scopes": [
            {
                "id": "850e8400-e29b-41d4-a716-446655440000",
                "service": "user",
                "resource": "read",
                "action": "list"
            },
            {
                "id": "850e8400-e29b-41d4-a716-446655440001",
                "service": "user",
                "resource": "write",
                "action": "create"
            }
        ]
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "API密钥不存在"
}
```

### 3. 创建系统级API密钥

创建新的系统级API密钥。

- **URL**: `/api/management/auth/api-keys/create_system_key/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名           | 类型    | 必填 | 描述           |
|-----------------|---------|------|----------------|
| name            | string  | 是   | 密钥名称       |
| tenant_id       | string  | 是   | 所属租户ID     |
| application_name| string  | 否   | 应用名称       |
| expires_in_days | integer | 否   | 过期天数       |
| is_active       | boolean | 否   | 是否激活       |
| metadata        | object  | 否   | 元数据         |
| scopes          | array   | 否   | 作用域列表     |

#### 请求示例

```json
{
    "name": "新系统API密钥",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "application_name": "数据分析系统",
    "expires_in_days": 365,
    "is_active": true,
    "metadata": {
        "description": "用于数据分析系统的API密钥",
        "created_by": "admin"
    },
    "scopes": [
        {
            "service": "analytics",
            "resource": "read",
            "action": "list"
        },
        {
            "service": "analytics",
            "resource": "read",
            "action": "export"
        }
    ]
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "系统级API密钥创建成功",
    "results": {
        "api_key": {
            "id": "750e8400-e29b-41d4-a716-446655440002",
            "key_type": "system",
            "prefix": "i9j0k1l2",
            "name": "新系统API密钥",
            "tenant": "550e8400-e29b-41d4-a716-446655440000",
            "user": null,
            "is_active": true,
            "created_at": "2023-06-20T12:00:00Z",
            "expires_at": "2024-06-19T12:00:00Z",
            "last_used_at": null,
            "application_name": "数据分析系统",
            "created_by_key_name": null,
            "metadata": {
                "description": "用于数据分析系统的API密钥",
                "created_by": "admin"
            },
            "scopes": [
                {
                    "id": "850e8400-e29b-41d4-a716-446655440002",
                    "service": "analytics",
                    "resource": "read",
                    "action": "list"
                },
                {
                    "id": "850e8400-e29b-41d4-a716-446655440003",
                    "service": "analytics",
                    "resource": "read",
                    "action": "export"
                }
            ]
        },
        "key": "i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6" // 明文密钥，只会在创建时返回一次
    }
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "系统级API密钥必须关联租户"
}
```

### 4. 创建用户级API密钥

创建新的用户级API密钥。

- **URL**: `/api/management/auth/api-keys/create_user_key/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名           | 类型    | 必填 | 描述           |
|-----------------|---------|------|----------------|
| name            | string  | 是   | 密钥名称       |
| user_id         | string  | 是   | 所属用户ID     |
| tenant_id       | string  | 否   | 所属租户ID     |
| created_by_key_id| string  | 否   | 创建此密钥的系统级密钥ID |
| expires_in_days | integer | 否   | 过期天数       |
| is_active       | boolean | 否   | 是否激活       |
| metadata        | object  | 否   | 元数据         |
| scopes          | array   | 否   | 作用域列表     |

#### 请求示例

```json
{
    "name": "新用户API密钥",
    "user_id": "450e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "expires_in_days": 180,
    "is_active": true,
    "metadata": {
        "description": "用于移动应用的API密钥",
        "device": "iPhone"
    },
    "scopes": [
        {
            "service": "profile",
            "resource": "read",
            "action": "view"
        },
        {
            "service": "profile",
            "resource": "write",
            "action": "update"
        }
    ]
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "用户级API密钥创建成功",
    "results": {
        "api_key": {
            "id": "750e8400-e29b-41d4-a716-446655440003",
            "key_type": "user",
            "prefix": "m3n4o5p6",
            "name": "新用户API密钥",
            "tenant": "550e8400-e29b-41d4-a716-446655440000",
            "user": "450e8400-e29b-41d4-a716-446655440000",
            "is_active": true,
            "created_at": "2023-06-20T12:00:00Z",
            "expires_at": "2023-12-17T12:00:00Z",
            "last_used_at": null,
            "application_name": null,
            "created_by_key_name": null,
            "metadata": {
                "description": "用于移动应用的API密钥",
                "device": "iPhone"
            },
            "scopes": [
                {
                    "id": "850e8400-e29b-41d4-a716-446655440004",
                    "service": "profile",
                    "resource": "read",
                    "action": "view"
                },
                {
                    "id": "850e8400-e29b-41d4-a716-446655440005",
                    "service": "profile",
                    "resource": "write",
                    "action": "update"
                }
            ]
        },
        "key": "m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0" // 明文密钥，只会在创建时返回一次
    }
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "用户级API密钥必须关联用户"
}
```

### 5. 更新API密钥信息

更新特定API密钥的信息。

- **URL**: `/api/management/auth/api-keys/{api_key_id}/`
- **方法**: `PUT`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名           | 类型    | 必填 | 描述           |
|-----------------|---------|------|----------------|
| name            | string  | 是   | 密钥名称       |
| is_active       | boolean | 是   | 是否激活       |
| expires_at      | string  | 否   | 过期时间       |
| application_name| string  | 否   | 应用名称       |
| metadata        | object  | 否   | 元数据         |
| scopes          | array   | 否   | 作用域列表     |

#### 请求示例

```json
{
    "name": "更新后的API密钥",
    "is_active": true,
    "expires_at": "2024-12-31T23:59:59Z",
    "application_name": "更新后的应用名称",
    "metadata": {
        "description": "更新后的描述",
        "updated_by": "admin"
    },
    "scopes": [
        {
            "service": "user",
            "resource": "read",
            "action": "list"
        },
        {
            "service": "user",
            "resource": "read",
            "action": "view"
        }
    ]
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "API密钥更新成功",
    "results": {
        "id": "750e8400-e29b-41d4-a716-446655440000",
        "key_type": "system",
        "prefix": "a1b2c3d4",
        "name": "更新后的API密钥",
        "tenant": "550e8400-e29b-41d4-a716-446655440000",
        "user": null,
        "is_active": true,
        "created_at": "2023-01-01T00:00:00Z",
        "expires_at": "2024-12-31T23:59:59Z",
        "last_used_at": "2023-06-15T08:30:45Z",
        "application_name": "更新后的应用名称",
        "created_by_key_name": null,
        "metadata": {
            "description": "更新后的描述",
            "updated_by": "admin"
        },
        "scopes": [
            {
                "id": "850e8400-e29b-41d4-a716-446655440006",
                "service": "user",
                "resource": "read",
                "action": "list"
            },
            {
                "id": "850e8400-e29b-41d4-a716-446655440007",
                "service": "user",
                "resource": "read",
                "action": "view"
            }
        ]
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "API密钥不存在"
}
```

### 6. 部分更新API密钥信息

部分更新特定API密钥的信息。

- **URL**: `/api/management/auth/api-keys/{api_key_id}/`
- **方法**: `PATCH`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

与更新API密钥信息接口相同，但所有字段均为可选。

#### 请求示例

```json
{
    "name": "部分更新的API密钥",
    "metadata": {
        "note": "添加的备注信息"
    }
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "API密钥更新成功",
    "results": {
        "id": "750e8400-e29b-41d4-a716-446655440000",
        "key_type": "system",
        "prefix": "a1b2c3d4",
        "name": "部分更新的API密钥",
        "tenant": "550e8400-e29b-41d4-a716-446655440000",
        "user": null,
        "is_active": true,
        "created_at": "2023-01-01T00:00:00Z",
        "expires_at": "2024-12-31T23:59:59Z",
        "last_used_at": "2023-06-15T08:30:45Z",
        "application_name": "更新后的应用名称",
        "created_by_key_name": null,
        "metadata": {
            "description": "更新后的描述",
            "updated_by": "admin",
            "note": "添加的备注信息"
        },
        "scopes": [
            {
                "id": "850e8400-e29b-41d4-a716-446655440006",
                "service": "user",
                "resource": "read",
                "action": "list"
            },
            {
                "id": "850e8400-e29b-41d4-a716-446655440007",
                "service": "user",
                "resource": "read",
                "action": "view"
            }
        ]
    }
}
```

**失败响应与更新API密钥信息接口相同**

### 7. 删除API密钥

删除特定API密钥。

- **URL**: `/api/management/auth/api-keys/{api_key_id}/`
- **方法**: `DELETE`
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
    "message": "API密钥删除成功"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "API密钥删除失败，可能是API密钥不存在"
}
```

### 8. 激活API密钥

激活特定API密钥。

- **URL**: `/api/management/auth/api-keys/{api_key_id}/activate/`
- **方法**: `POST`
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
    "message": "API密钥已激活"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "API密钥不存在"
}
```

### 9. 禁用API密钥

禁用特定API密钥。

- **URL**: `/api/management/auth/api-keys/{api_key_id}/deactivate/`
- **方法**: `POST`
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
    "message": "API密钥已禁用"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "API密钥不存在"
}
```

### 10. 获取API密钥使用日志

获取特定API密钥的使用日志。

- **URL**: `/api/management/auth/api-keys/{api_key_id}/usage_logs/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 查询参数

| 参数名      | 类型    | 必填 | 描述           |
|------------|---------|------|----------------|
| page       | integer | 否   | 页码           |
| page_size  | integer | 否   | 每页条数       |
| ordering   | string  | 否   | 排序字段       |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "total": 2,
        "page_size": 10,
        "current_page": 1,
        "total_pages": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": "950e8400-e29b-41d4-a716-446655440000",
                "api_key": "750e8400-e29b-41d4-a716-446655440000",
                "api_key_name": "系统API密钥",
                "tenant": "550e8400-e29b-41d4-a716-446655440000",
                "request_path": "/api/platform/users/",
                "request_method": "GET",
                "response_status": 200,
                "timestamp": "2023-06-15T08:30:45Z",
                "client_ip": "192.168.1.1",
                "request_id": "req-123456789"
            },
            {
                "id": "950e8400-e29b-41d4-a716-446655440001",
                "api_key": "750e8400-e29b-41d4-a716-446655440000",
                "api_key_name": "系统API密钥",
                "tenant": "550e8400-e29b-41d4-a716-446655440000",
                "request_path": "/api/platform/users/",
                "request_method": "POST",
                "response_status": 201,
                "timestamp": "2023-06-15T09:45:30Z",
                "client_ip": "192.168.1.1",
                "request_id": "req-987654321"
            }
        ]
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "API密钥不存在"
}
```

### 11. 获取API密钥统计信息

获取API密钥的统计信息。

- **URL**: `/api/management/auth/api-keys/stats/`
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
        "total_keys": 10,
        "system_keys": 3,
        "user_keys": 7,
        "active_keys": 8,
        "inactive_keys": 2,
        "expired_keys": 1,
        "recent_keys": 5,
        "recent_usage": 150,
        "status_stats": {
            "200": 120,
            "201": 15,
            "400": 10,
            "401": 5
        }
    }
}
```

### 12. 获取API密钥哈希

获取API密钥的哈希值，需要验证用户密码，增加安全性。

- **URL**: `/api/management/auth/api-keys/get_key_hash/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名           | 类型    | 必填 | 描述           |
|-----------------|---------|------|----------------|
| api_key_id      | string  | 是   | API密钥ID      |
| password        | string  | 是   | 用户密码       |

#### 请求示例

```json
{
    "api_key_id": "750e8400-e29b-41d4-a716-446655440000",
    "password": "your_secure_password"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "API密钥哈希获取成功",
    "results": {
        "id": "750e8400-e29b-41d4-a716-446655440000",
        "name": "系统API密钥",
        "key_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
        "prefix": "a1b2c3d4"
    }
}
```

**失败响应 (401 Unauthorized)**

```json
{
    "success": false,
    "message": "密码不正确"
}
```

**失败响应 (403 Forbidden)**

```json
{
    "success": false,
    "message": "没有权限查看此API密钥的哈希"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "API密钥不存在"
}
```

## 错误码说明

| 状态码 | 描述                                 |
|--------|------------------------------------|
| 200    | 请求成功                             |
| 201    | 创建成功                             |
| 400    | 请求参数错误                         |
| 401    | 未授权（未提供认证凭据或凭据无效）     |
| 403    | 禁止访问（权限不足）                 |
| 404    | 资源不存在                           |
| 500    | 服务器内部错误                       |

## 注意事项

1. 所有接口都需要管理员权限，非管理员用户无法访问
2. 超级管理员可以查看和管理所有租户的API密钥，普通管理员只能管理自己租户的API密钥
3. API密钥创建后，明文密钥只会在创建时返回一次，请妥善保存
4. 系统级API密钥必须关联租户，用户级API密钥必须关联用户
5. API密钥可以设置过期时间，过期后将无法使用
6. 可以通过激活/禁用功能临时控制API密钥的可用性 