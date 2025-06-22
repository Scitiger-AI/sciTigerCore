# 管理角色API文档

本文档描述了SciTigerCore平台的管理角色API，这些API专为系统管理员设计，提供角色的增删改查、权限分配等功能。

## API基础信息

- **基础路径**: `/api/management/auth/roles/`
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
        "next": "http://example.com/api/management/auth/roles/?page=2",
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

### 1. 获取角色列表

获取系统中的角色列表。

- **URL**: `/api/management/auth/roles/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 查询参数

| 参数名          | 类型    | 必填 | 描述           |
|-----------------|---------|------|----------------|
| name            | string  | 否   | 按角色名称过滤  |
| code            | string  | 否   | 按角色代码过滤  |
| is_system       | boolean | 否   | 按系统角色过滤  |
| is_default      | boolean | 否   | 按默认角色过滤  |
| is_global       | boolean | 否   | 按全局角色过滤  |
| tenant_id       | string  | 否   | 按租户ID过滤    |
| has_permission  | string  | 否   | 按拥有权限过滤  |
| search          | string  | 否   | 全局搜索        |
| page            | integer | 否   | 页码           |
| page_size       | integer | 否   | 每页条数        |
| ordering        | string  | 否   | 排序字段        |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "total": 15,
        "page_size": 10,
        "current_page": 1,
        "total_pages": 2,
        "next": "http://example.com/api/management/auth/roles/?page=2",
        "previous": null,
        "results": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "系统管理员",
                "code": "system_admin",
                "description": "系统管理员角色，拥有所有权限",
                "is_system": true,
                "is_default": false,
                "tenant": null,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "普通用户",
                "code": "normal_user",
                "description": "普通用户角色，拥有基本权限",
                "is_system": true,
                "is_default": true,
                "tenant": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        ]
    }
}
```

### 2. 获取角色详情

获取特定角色的详细信息。

- **URL**: `/api/management/auth/roles/{role_id}/`
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
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "系统管理员",
        "code": "system_admin",
        "description": "系统管理员角色，拥有所有权限",
        "is_system": true,
        "is_default": false,
        "tenant": null,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "permissions": [
            {
                "id": "650e8400-e29b-41d4-a716-446655440000",
                "name": "查看用户",
                "code": "user:read:list",
                "service": "user",
                "resource": "read",
                "action": "list"
            },
            {
                "id": "650e8400-e29b-41d4-a716-446655440001",
                "name": "创建用户",
                "code": "user:write:create",
                "service": "user",
                "resource": "write",
                "action": "create"
            }
        ],
        "users_count": 5
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "角色不存在"
}
```

### 3. 创建角色

创建新角色。

- **URL**: `/api/management/auth/roles/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名        | 类型    | 必填 | 描述           |
|--------------|---------|------|----------------|
| name         | string  | 是   | 角色名称       |
| code         | string  | 是   | 角色代码       |
| description  | string  | 否   | 角色描述       |
| is_system    | boolean | 否   | 是否系统角色   |
| is_default   | boolean | 否   | 是否默认角色   |
| tenant_id    | string  | 否   | 所属租户ID     |
| permissions  | array   | 否   | 权限ID列表     |

#### 请求示例

```json
{
    "name": "项目管理员",
    "code": "project_admin",
    "description": "项目管理员角色，管理项目相关资源",
    "is_system": false,
    "is_default": false,
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "permissions": [
        "650e8400-e29b-41d4-a716-446655440002",
        "650e8400-e29b-41d4-a716-446655440003"
    ]
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "角色创建成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "项目管理员",
        "code": "project_admin",
        "description": "项目管理员角色，管理项目相关资源",
        "is_system": false,
        "is_default": false,
        "tenant": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2023-06-20T12:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z",
        "permissions": [
            {
                "id": "650e8400-e29b-41d4-a716-446655440002",
                "name": "查看项目",
                "code": "project:read:list",
                "service": "project",
                "resource": "read",
                "action": "list"
            },
            {
                "id": "650e8400-e29b-41d4-a716-446655440003",
                "name": "创建项目",
                "code": "project:write:create",
                "service": "project",
                "resource": "write",
                "action": "create"
            }
        ],
        "users_count": 0
    }
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "角色代码 'project_admin' 已存在"
}
```

### 4. 更新角色信息

更新特定角色的信息。

- **URL**: `/api/management/auth/roles/{role_id}/`
- **方法**: `PUT`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名        | 类型    | 必填 | 描述           |
|--------------|---------|------|----------------|
| name         | string  | 是   | 角色名称       |
| description  | string  | 否   | 角色描述       |
| is_default   | boolean | 否   | 是否默认角色   |
| permissions  | array   | 否   | 权限ID列表     |

#### 请求示例

```json
{
    "name": "项目高级管理员",
    "description": "项目高级管理员角色，拥有项目的所有权限",
    "is_default": false,
    "permissions": [
        "650e8400-e29b-41d4-a716-446655440002",
        "650e8400-e29b-41d4-a716-446655440003",
        "650e8400-e29b-41d4-a716-446655440004"
    ]
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "角色更新成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "项目高级管理员",
        "code": "project_admin",
        "description": "项目高级管理员角色，拥有项目的所有权限",
        "is_system": false,
        "is_default": false,
        "tenant": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2023-06-20T12:00:00Z",
        "updated_at": "2023-06-21T10:15:30Z",
        "permissions": [
            {
                "id": "650e8400-e29b-41d4-a716-446655440002",
                "name": "查看项目",
                "code": "project:read:list",
                "service": "project",
                "resource": "read",
                "action": "list"
            },
            {
                "id": "650e8400-e29b-41d4-a716-446655440003",
                "name": "创建项目",
                "code": "project:write:create",
                "service": "project",
                "resource": "write",
                "action": "create"
            },
            {
                "id": "650e8400-e29b-41d4-a716-446655440004",
                "name": "删除项目",
                "code": "project:write:delete",
                "service": "project",
                "resource": "write",
                "action": "delete"
            }
        ],
        "users_count": 0
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "角色不存在"
}
```

### 5. 部分更新角色信息

部分更新特定角色的信息。

- **URL**: `/api/management/auth/roles/{role_id}/`
- **方法**: `PATCH`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

与更新角色信息接口相同，但所有字段均为可选。

#### 请求示例

```json
{
    "description": "更新后的角色描述"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "角色更新成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "项目高级管理员",
        "code": "project_admin",
        "description": "更新后的角色描述",
        "is_system": false,
        "is_default": false,
        "tenant": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2023-06-20T12:00:00Z",
        "updated_at": "2023-06-22T14:25:10Z",
        "permissions": [
            {
                "id": "650e8400-e29b-41d4-a716-446655440002",
                "name": "查看项目",
                "code": "project:read:list",
                "service": "project",
                "resource": "read",
                "action": "list"
            },
            {
                "id": "650e8400-e29b-41d4-a716-446655440003",
                "name": "创建项目",
                "code": "project:write:create",
                "service": "project",
                "resource": "write",
                "action": "create"
            },
            {
                "id": "650e8400-e29b-41d4-a716-446655440004",
                "name": "删除项目",
                "code": "project:write:delete",
                "service": "project",
                "resource": "write",
                "action": "delete"
            }
        ],
        "users_count": 0
    }
}
```

**失败响应与更新角色信息接口相同**

### 6. 删除角色

删除特定角色。

- **URL**: `/api/management/auth/roles/{role_id}/`
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
    "message": "角色删除成功"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "角色删除失败，可能是系统角色或角色不存在"
}
```

### 7. 获取拥有此角色的用户列表

获取拥有特定角色的用户列表。

- **URL**: `/api/management/auth/roles/{role_id}/users/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 查询参数

| 参数名          | 类型    | 必填 | 描述           |
|-----------------|---------|------|----------------|
| page            | integer | 否   | 页码           |
| page_size       | integer | 否   | 每页条数        |
| ordering        | string  | 否   | 排序字段        |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "total": 8,
        "page_size": 10,
        "current_page": 1,
        "total_pages": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": "450e8400-e29b-41d4-a716-446655440000",
                "username": "user1",
                "email": "user1@example.com",
                "first_name": "First",
                "last_name": "User",
                "is_active": true
            },
            {
                "id": "450e8400-e29b-41d4-a716-446655440001",
                "username": "user2",
                "email": "user2@example.com",
                "first_name": "Second",
                "last_name": "User",
                "is_active": true
            }
        ]
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "角色不存在"
}
```

### 8. 为角色分配权限

为特定角色分配权限。

- **URL**: `/api/management/auth/roles/{role_id}/assign_permissions/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名          | 类型   | 必填 | 描述           |
|----------------|--------|------|----------------|
| permission_ids | array  | 是   | 权限ID列表     |

#### 请求示例

```json
{
    "permission_ids": [
        "650e8400-e29b-41d4-a716-446655440005",
        "650e8400-e29b-41d4-a716-446655440006"
    ]
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "权限分配成功"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "缺少权限ID列表"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "角色不存在"
}
```

### 9. 从角色中移除权限

从特定角色中移除权限。

- **URL**: `/api/management/auth/roles/{role_id}/remove_permissions/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名          | 类型   | 必填 | 描述           |
|----------------|--------|------|----------------|
| permission_ids | array  | 是   | 权限ID列表     |

#### 请求示例

```json
{
    "permission_ids": [
        "650e8400-e29b-41d4-a716-446655440005",
        "650e8400-e29b-41d4-a716-446655440006"
    ]
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "权限移除成功"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "缺少权限ID列表"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "角色不存在"
}
```

### 10. 设置为默认角色

将特定角色设置为默认角色。

- **URL**: `/api/management/auth/roles/{role_id}/set_default/`
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
    "message": "已设置为默认角色"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "角色不存在"
}
```

### 11. 取消默认角色设置

取消特定角色的默认角色设置。

- **URL**: `/api/management/auth/roles/{role_id}/unset_default/`
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
    "message": "已取消默认角色设置"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "角色不存在"
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
2. 系统角色不允许删除，也不允许修改其代码、系统角色标志和租户
3. 超级管理员可以查看和管理所有租户的角色，普通管理员只能管理自己租户的角色
4. 设置默认角色时，同一租户下的其他默认角色会被自动取消默认设置
5. 角色代码在同一租户内必须唯一 