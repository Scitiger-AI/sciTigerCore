# API密钥认证文档

本文档描述了SciTigerCore平台的API密钥认证机制，提供了如何创建、使用和验证API密钥的详细说明。

## API密钥概述

API密钥是一种简单而有效的认证方式，适用于服务器间通信、自动化脚本、第三方集成等场景。SciTigerCore平台支持两种类型的API密钥：

1. **系统级API密钥**：具有较高权限，用于系统级别的集成
2. **用户级API密钥**：与特定用户关联，权限受限于用户权限

## API密钥认证方式

系统支持多种方式提供API密钥：

1. **Authorization头**：`Authorization: ApiKey {your_api_key}` 或 `Authorization: Bearer {your_api_key}`
2. **自定义头**：`X-Api-Key: {your_api_key}`
3. **查询参数**：`?api_key={your_api_key}`

## API密钥管理接口

### 1. 获取API密钥列表

获取当前租户下的API密钥列表。

- **URL**: `/api/platform/auth/api-keys/`
- **方法**: `GET`
- **权限要求**: 已认证用户

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 租户上下文（必需）

需要提供租户信息，可通过以下方式：
- 请求头: `X-Tenant-ID: {tenant_id}`
- 查询参数: `?tenant_id={tenant_id}`
- 子域名: `https://tenant-name.yourdomain.com/api/platform/auth/api-keys/`

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "系统集成密钥",
            "key_type": "system",
            "created_at": "2023-06-15T08:30:45Z",
            "expires_at": "2024-06-15T08:30:45Z",
            "is_active": true,
            "last_used_at": "2023-06-16T10:20:30Z"
        }
    ]
}
```

### 2. 获取用户级API密钥列表

获取当前用户的API密钥列表。

- **URL**: `/api/platform/auth/api-keys/list_user_keys/`
- **方法**: `GET`
- **权限要求**: 已认证用户

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 租户上下文（必需）

需要提供租户信息，同上。

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "我的API密钥",
            "key_type": "user",
            "created_at": "2023-06-15T08:30:45Z",
            "expires_at": "2024-06-15T08:30:45Z",
            "is_active": true,
            "last_used_at": "2023-06-16T10:20:30Z"
        }
    ]
}
```

### 3. 创建系统级API密钥

创建新的系统级API密钥。

- **URL**: `/api/platform/auth/api-keys/create_system_key/`
- **方法**: `POST`
- **权限要求**: 已认证用户（需要管理员权限）

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 租户上下文（必需）

需要提供租户信息，同上。

#### 请求参数

| 参数名          | 类型    | 必填 | 描述                 |
|-----------------|---------|------|----------------------|
| name            | string  | 是   | API密钥名称          |
| expires_at      | string  | 否   | 过期时间 (ISO格式)   |
| is_active       | boolean | 否   | 是否激活             |
| scopes          | array   | 否   | 权限作用域列表       |

#### 请求示例

```json
{
    "name": "系统集成密钥",
    "expires_at": "2024-06-15T08:30:45Z",
    "is_active": true,
    "scopes": [
        {
            "service": "auth_service",
            "resource": "users",
            "action": "read"
        }
    ]
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "API密钥创建成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "系统集成密钥",
        "key": "sk_live_abcdefghijklmnopqrstuvwxyz123456",
        "key_type": "system",
        "created_at": "2023-06-15T08:30:45Z",
        "expires_at": "2024-06-15T08:30:45Z",
        "is_active": true,
        "scopes": [
            {
                "service": "auth_service",
                "resource": "users",
                "action": "read"
            }
        ]
    }
}
```

**注意**: API密钥值(`key`)只会在创建时返回一次，请妥善保存。

### 4. 创建用户级API密钥

创建新的用户级API密钥。

- **URL**: `/api/platform/auth/api-keys/create_user_key/`
- **方法**: `POST`
- **权限要求**: 已认证用户

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 租户上下文（必需）

需要提供租户信息，同上。

#### 请求参数

| 参数名          | 类型    | 必填 | 描述                 |
|-----------------|---------|------|----------------------|
| name            | string  | 是   | API密钥名称          |
| expires_at      | string  | 否   | 过期时间 (ISO格式)   |
| is_active       | boolean | 否   | 是否激活             |
| scopes          | array   | 否   | 权限作用域列表       |

#### 请求示例

```json
{
    "name": "我的API密钥",
    "expires_at": "2024-06-15T08:30:45Z",
    "is_active": true,
    "scopes": [
        {
            "service": "auth_service",
            "resource": "users",
            "action": "read"
        }
    ]
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "API密钥创建成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "我的API密钥",
        "key": "uk_live_abcdefghijklmnopqrstuvwxyz123456",
        "key_type": "user",
        "created_at": "2023-06-15T08:30:45Z",
        "expires_at": "2024-06-15T08:30:45Z",
        "is_active": true,
        "scopes": [
            {
                "service": "auth_service",
                "resource": "users",
                "action": "read"
            }
        ]
    }
}
```

### 5. 验证API密钥

验证API密钥的有效性。

- **URL**: `/api/platform/auth/api-keys/verify/`
- **方法**: `POST`
- **权限要求**: 无（公开接口）

#### 请求参数

| 参数名          | 类型    | 必填 | 描述                 |
|-----------------|---------|------|----------------------|
| key             | string  | 是   | API密钥              |
| service         | string  | 否   | 服务名称             |
| resource        | string  | 否   | 资源类型             |
| action          | string  | 否   | 操作类型             |

#### 请求示例

```json
{
    "key": "sk_live_abcdefghijklmnopqrstuvwxyz123456",
    "service": "auth_service",
    "resource": "users",
    "action": "read"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "API密钥有效",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "系统集成密钥",
        "key_type": "system",
        "tenant_id": "450e8400-e29b-41d4-a716-446655440000",
        "is_active": true,
        "expires_at": "2024-06-15T08:30:45Z"
    }
}
```

**失败响应 (401 Unauthorized)**

```json
{
    "success": false,
    "message": "API密钥无效或已过期"
}
```

### 6. 获取API密钥哈希

获取API密钥的哈希值，需要验证用户密码，增加安全性。

- **URL**: `/api/platform/auth/api-keys/get_key_hash/`
- **方法**: `POST`
- **权限要求**: 已认证用户

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
    "api_key_id": "550e8400-e29b-41d4-a716-446655440001",
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
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "我的API密钥",
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
    "message": "API密钥不属于当前用户"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "API密钥不存在"
}
```

### 7. 吊销API密钥

吊销API密钥。

- **URL**: `/api/platform/auth/api-keys/revoke/`
- **方法**: `POST`
- **权限要求**: 已认证用户

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名          | 类型    | 必填 | 描述                 |
|-----------------|---------|------|----------------------|
| api_key_id      | string  | 是   | API密钥ID             |

#### 请求示例

```json
{
    "api_key_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "API密钥吊销成功"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "请求参数错误"
}
```

## 使用API密钥进行认证

要使用API密钥进行API调用，可以通过以下任一方式提供API密钥：

### 1. 通过Authorization头

```
Authorization: ApiKey sk_live_abcdefghijklmnopqrstuvwxyz123456
```

或

```
Authorization: Bearer sk_live_abcdefghijklmnopqrstuvwxyz123456
```

### 2. 通过自定义头

```
X-Api-Key: sk_live_abcdefghijklmnopqrstuvwxyz123456
```

### 3. 通过查询参数

```
/api/platform/your-endpoint/?api_key=sk_live_abcdefghijklmnopqrstuvwxyz123456
```

## API密钥权限作用域

API密钥可以配置特定的权限作用域，限制其访问范围。作用域由三个部分组成：

1. **服务(service)**: 表示API所属的服务，如 `auth_service`
2. **资源(resource)**: 表示操作的资源类型，如 `users`
3. **操作(action)**: 表示对资源的操作类型，如 `read`、`write`、`delete`

例如，要允许API密钥只能读取用户信息，可以设置作用域为：
```json
{
    "service": "auth_service",
    "resource": "users",
    "action": "read"
}
```

## 最佳实践

1. **安全存储**: 妥善保管API密钥，不要在客户端代码中硬编码
2. **最小权限**: 只授予API密钥完成任务所需的最小权限
3. **设置过期时间**: 为API密钥设置合理的过期时间，定期轮换
4. **监控使用**: 定期检查API密钥的使用情况，发现异常及时处理
5. **系统级与用户级分离**: 根据需求选择合适类型的API密钥

## 错误码说明

| 状态码 | 描述                                 |
|--------|------------------------------------|
| 200    | 请求成功                             |
| 201    | 创建成功                             |
| 400    | 请求参数错误                         |
| 401    | 未授权（API密钥无效或已过期）         |
| 403    | 禁止访问（API密钥权限不足）           |
| 500    | 服务器内部错误                       | 