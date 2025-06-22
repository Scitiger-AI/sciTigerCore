# 租户管理API文档

本文档描述了SciTigerCore平台的租户管理API，这些API专为系统管理员设计，提供租户的增删改查等功能。

## API基础信息

- **基础路径**: `/api/management/tenants/`
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

### 1. 获取租户列表

获取系统中的租户列表。

- **URL**: `/api/management/tenants/`
- **方法**: `GET`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名    | 类型    | 必填 | 描述           |
|-----------|---------|------|----------------|
| is_active | boolean | 否   | 筛选活跃状态   |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "租户1",
            "slug": "tenant1",
            "subdomain": "tenant1",
            "is_active": true,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "租户2",
            "slug": "tenant2",
            "subdomain": "tenant2",
            "is_active": true,
            "created_at": "2023-01-02T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z"
        }
    ]
}
```

### 2. 获取租户详情

获取特定租户的详细信息。

- **URL**: `/api/management/tenants/{tenant_id}/`
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
        "name": "租户1",
        "slug": "tenant1",
        "subdomain": "tenant1",
        "description": "这是租户1的描述",
        "logo_url": "https://example.com/logos/tenant1.png",
        "primary_color": "#3498db",
        "secondary_color": "#2ecc71",
        "owner_user": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "username": "owner",
            "email": "owner@example.com"
        },
        "is_active": true,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "user_count": 10,
        "subscription_plan": "enterprise",
        "subscription_status": "active",
        "subscription_end_date": "2024-01-01T00:00:00Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "租户不存在"
}
```

### 3. 创建租户

创建新租户。

- **URL**: `/api/management/tenants/`
- **方法**: `POST`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名          | 类型    | 必填 | 描述                   |
|-----------------|---------|------|----------------------|
| name            | string  | 是   | 租户名称               |
| slug            | string  | 是   | 租户标识（URL友好）    |
| subdomain       | string  | 是   | 子域名                 |
| owner_user_id   | string  | 是   | 所有者用户ID           |
| description     | string  | 否   | 租户描述               |
| logo_url        | string  | 否   | 租户logo URL          |
| primary_color   | string  | 否   | 主色调                 |
| secondary_color | string  | 否   | 辅助色调               |
| is_active       | boolean | 否   | 是否激活（默认true）   |

#### 请求示例

```json
{
    "name": "新租户",
    "slug": "new-tenant",
    "subdomain": "newtenant",
    "owner_user_id": "650e8400-e29b-41d4-a716-446655440000",
    "description": "这是新租户的描述",
    "logo_url": "https://example.com/logos/newtenant.png",
    "primary_color": "#3498db",
    "secondary_color": "#2ecc71",
    "is_active": true
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "租户创建成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "新租户",
        "slug": "new-tenant",
        "subdomain": "newtenant",
        "description": "这是新租户的描述",
        "logo_url": "https://example.com/logos/newtenant.png",
        "primary_color": "#3498db",
        "secondary_color": "#2ecc71",
        "owner_user": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "username": "owner",
            "email": "owner@example.com"
        },
        "is_active": true,
        "created_at": "2023-06-20T12:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z",
        "user_count": 1,
        "subscription_plan": "free",
        "subscription_status": "active",
        "subscription_end_date": null
    }
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "租户标识已存在"
}
```

```json
{
    "success": false,
    "message": "必须指定租户所有者"
}
```

```json
{
    "success": false,
    "message": "指定的所有者用户不存在"
}
```

### 4. 更新租户信息

更新特定租户的信息。

- **URL**: `/api/management/tenants/{tenant_id}/`
- **方法**: `PUT`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名          | 类型    | 必填 | 描述                   |
|-----------------|---------|------|----------------------|
| name            | string  | 是   | 租户名称               |
| description     | string  | 否   | 租户描述               |
| logo_url        | string  | 否   | 租户logo URL          |
| primary_color   | string  | 否   | 主色调                 |
| secondary_color | string  | 否   | 辅助色调               |
| is_active       | boolean | 否   | 是否激活               |

#### 请求示例

```json
{
    "name": "更新的租户名称",
    "description": "更新后的租户描述",
    "logo_url": "https://example.com/logos/updated.png",
    "primary_color": "#9b59b6",
    "secondary_color": "#f1c40f",
    "is_active": true
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "租户信息已更新",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "更新的租户名称",
        "slug": "tenant1",
        "subdomain": "tenant1",
        "description": "更新后的租户描述",
        "logo_url": "https://example.com/logos/updated.png",
        "primary_color": "#9b59b6",
        "secondary_color": "#f1c40f",
        "owner_user": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "username": "owner",
            "email": "owner@example.com"
        },
        "is_active": true,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z",
        "user_count": 10,
        "subscription_plan": "enterprise",
        "subscription_status": "active",
        "subscription_end_date": "2024-01-01T00:00:00Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "租户不存在"
}
```

### 5. 部分更新租户信息

部分更新特定租户的信息。

- **URL**: `/api/management/tenants/{tenant_id}/`
- **方法**: `PATCH`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

与更新租户信息接口相同，但所有字段均为可选。

#### 请求示例

```json
{
    "description": "部分更新的租户描述",
    "is_active": false
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "租户信息已更新",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "租户1",
        "slug": "tenant1",
        "subdomain": "tenant1",
        "description": "部分更新的租户描述",
        "logo_url": "https://example.com/logos/tenant1.png",
        "primary_color": "#3498db",
        "secondary_color": "#2ecc71",
        "owner_user": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "username": "owner",
            "email": "owner@example.com"
        },
        "is_active": false,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z",
        "user_count": 10,
        "subscription_plan": "enterprise",
        "subscription_status": "active",
        "subscription_end_date": "2024-01-01T00:00:00Z"
    }
}
```

**失败响应与更新租户信息接口相同**

### 6. 删除租户

删除特定租户。

- **URL**: `/api/management/tenants/{tenant_id}/`
- **方法**: `DELETE`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 响应示例

**成功响应 (204 No Content)**

```json
{
    "success": true,
    "message": "租户已删除"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "租户删除失败"
}
```

## 错误码说明

| 状态码 | 描述                                 |
|--------|------------------------------------|
| 200    | 请求成功                             |
| 201    | 创建成功                             |
| 204    | 删除成功                             |
| 400    | 请求参数错误                         |
| 401    | 未授权（未提供认证凭据或凭据无效）     |
| 403    | 禁止访问（权限不足）                 |
| 404    | 资源不存在                           |
| 500    | 服务器内部错误                       |

## 注意事项

1. 所有接口都需要超级管理员权限，非超级管理员用户无法访问
2. 创建租户时必须指定有效的所有者用户
3. 租户标识（slug）和子域名（subdomain）在创建后不可修改
4. 删除租户操作不可逆，会同时删除与该租户关联的所有数据，请谨慎使用 