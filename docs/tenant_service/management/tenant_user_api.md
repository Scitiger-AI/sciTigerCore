# 租户用户管理API文档

本文档描述了SciTigerCore平台的租户用户管理API，这些API专为系统管理员设计，提供租户用户关联的增删改查等功能。

## API基础信息

- **基础路径**: `/api/management/tenants/users/`
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

### 1. 获取租户用户列表

获取系统中的租户用户关联列表。

- **URL**: `/api/management/tenants/users/`
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
            "user": {
                "id": "750e8400-e29b-41d4-a716-446655440000",
                "username": "user1",
                "email": "user1@example.com"
            },
            "role": "owner",
            "is_active": true,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "tenant": {
                "id": "650e8400-e29b-41d4-a716-446655440000",
                "name": "租户1",
                "slug": "tenant1"
            },
            "user": {
                "id": "750e8400-e29b-41d4-a716-446655440001",
                "username": "user2",
                "email": "user2@example.com"
            },
            "role": "member",
            "is_active": true,
            "created_at": "2023-01-02T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z"
        }
    ]
}
```

### 2. 获取租户用户详情

获取特定租户用户关联的详细信息。

- **URL**: `/api/management/tenants/users/{tenant_user_id}/`
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
        "user": {
            "id": "750e8400-e29b-41d4-a716-446655440000",
            "username": "user1",
            "email": "user1@example.com",
            "first_name": "First",
            "last_name": "User"
        },
        "role": "owner",
        "is_active": true,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "last_login_at": "2023-06-15T08:30:45Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "租户用户关联不存在"
}
```

### 3. 创建租户用户关联

创建新的租户用户关联。

- **URL**: `/api/management/tenants/users/`
- **方法**: `POST`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名    | 类型    | 必填 | 描述                   |
|-----------|---------|------|----------------------|
| tenant_id | string  | 是   | 租户ID                |
| user_id   | string  | 是   | 用户ID                |
| role      | string  | 否   | 用户角色（默认member）|
| is_active | boolean | 否   | 是否激活（默认true）  |

#### 请求示例

```json
{
    "tenant_id": "650e8400-e29b-41d4-a716-446655440000",
    "user_id": "750e8400-e29b-41d4-a716-446655440002",
    "role": "admin",
    "is_active": true
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "租户用户关联创建成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "tenant": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "name": "租户1",
            "slug": "tenant1"
        },
        "user": {
            "id": "750e8400-e29b-41d4-a716-446655440002",
            "username": "user3",
            "email": "user3@example.com"
        },
        "role": "admin",
        "is_active": true,
        "created_at": "2023-06-20T12:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z"
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

```json
{
    "success": false,
    "message": "指定的租户不存在"
}
```

```json
{
    "success": false,
    "message": "用户已经是该租户的成员"
}
```

### 4. 更新租户用户关联

更新特定租户用户关联的信息。

- **URL**: `/api/management/tenants/users/{tenant_user_id}/`
- **方法**: `PUT`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名    | 类型    | 必填 | 描述           |
|-----------|---------|------|----------------|
| role      | string  | 是   | 用户角色       |
| is_active | boolean | 是   | 是否激活       |

#### 请求示例

```json
{
    "role": "admin",
    "is_active": true
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "租户用户关联已更新",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "name": "租户1",
            "slug": "tenant1"
        },
        "user": {
            "id": "750e8400-e29b-41d4-a716-446655440000",
            "username": "user1",
            "email": "user1@example.com"
        },
        "role": "admin",
        "is_active": true,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "租户用户关联不存在"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "无法修改租户所有者的角色"
}
```

### 5. 部分更新租户用户关联

部分更新特定租户用户关联的信息。

- **URL**: `/api/management/tenants/users/{tenant_user_id}/`
- **方法**: `PATCH`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

与更新租户用户关联接口相同，但所有字段均为可选。

#### 请求示例

```json
{
    "is_active": false
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "租户用户关联已更新",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "name": "租户1",
            "slug": "tenant1"
        },
        "user": {
            "id": "750e8400-e29b-41d4-a716-446655440000",
            "username": "user1",
            "email": "user1@example.com"
        },
        "role": "owner",
        "is_active": false,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z"
    }
}
```

**失败响应与更新租户用户关联接口相同**

### 6. 删除租户用户关联

删除特定租户用户关联。

- **URL**: `/api/management/tenants/users/{tenant_user_id}/`
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
    "message": "租户用户关联已删除"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "租户用户关联删除失败"
}
```

```json
{
    "success": false,
    "message": "无法删除租户所有者的关联"
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
2. 每个租户必须有且仅有一个所有者（owner）角色的用户
3. 不能修改或删除租户所有者的关联，必须先转移所有权
4. 用户可以同时属于多个租户，但在每个租户中只能有一个角色
5. 禁用租户用户关联后，用户将无法访问该租户的资源 