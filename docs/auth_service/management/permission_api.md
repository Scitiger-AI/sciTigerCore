# 管理权限API文档

本文档描述了SciTigerCore平台的管理权限API，这些API专为系统管理员设计，提供权限的增删改查等功能。

## API基础信息

- **基础路径**: `/api/management/auth/permissions/`
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
        "next": "http://example.com/api/management/auth/permissions/?page=2",
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

### 1. 获取权限列表

获取系统中的权限列表。

- **URL**: `/api/management/auth/permissions/`
- **方法**: `GET`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 查询参数

| 参数名         | 类型    | 必填 | 描述           |
|---------------|---------|------|----------------|
| name          | string  | 否   | 按名称过滤      |
| code          | string  | 否   | 按代码过滤      |
| service       | string  | 否   | 按服务名过滤    |
| resource      | string  | 否   | 按资源类型过滤   |
| action        | string  | 否   | 按操作类型过滤   |
| is_system     | boolean | 否   | 是否系统权限     |
| is_tenant_level | boolean | 否 | 是否租户级权限   |
| tenant_id     | string  | 否   | 租户ID过滤      |
| search        | string  | 否   | 全局搜索        |
| page          | integer | 否   | 页码           |
| page_size     | integer | 否   | 每页条数        |
| ordering      | string  | 否   | 排序字段        |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "total": 30,
        "page_size": 10,
        "current_page": 1,
        "total_pages": 3,
        "next": "http://example.com/api/management/auth/permissions/?page=2",
        "previous": null,
        "results": [
            {
                "id": "650e8400-e29b-41d4-a716-446655440000",
                "code": "user:read:list",
                "name": "查看用户列表",
                "description": "允许查看用户列表",
                "service": "user",
                "resource": "read",
                "action": "list",
                "is_system": true,
                "is_tenant_level": false,
                "tenant": null,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            },
            {
                "id": "650e8400-e29b-41d4-a716-446655440001",
                "code": "user:write:create",
                "name": "创建用户",
                "description": "允许创建新用户",
                "service": "user",
                "resource": "write",
                "action": "create",
                "is_system": true,
                "is_tenant_level": true,
                "tenant": null,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        ]
    }
}
```

### 2. 获取权限详情

获取特定权限的详细信息。

- **URL**: `/api/management/auth/permissions/{permission_id}/`
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
        "id": "650e8400-e29b-41d4-a716-446655440000",
        "code": "user:read:list",
        "name": "查看用户列表",
        "description": "允许查看用户列表",
        "service": "user",
        "resource": "read",
        "action": "list",
        "is_system": true,
        "is_tenant_level": false,
        "tenant": null,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "权限不存在"
}
```

### 3. 创建权限

创建新权限。

- **URL**: `/api/management/auth/permissions/`
- **方法**: `POST`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名         | 类型    | 必填 | 描述           |
|---------------|---------|------|----------------|
| name          | string  | 是   | 权限名称       |
| service       | string  | 是   | 服务名称       |
| resource      | string  | 是   | 资源类型       |
| action        | string  | 是   | 操作类型       |
| description   | string  | 否   | 权限描述       |
| is_system     | boolean | 否   | 是否系统权限   |
| is_tenant_level | boolean | 否 | 是否租户级权限 |
| tenant_id     | string  | 否   | 所属租户ID     |

#### 请求示例

```json
{
    "name": "查看项目",
    "service": "project",
    "resource": "read",
    "action": "list",
    "description": "允许查看项目列表",
    "is_system": false,
    "is_tenant_level": true,
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "权限创建成功",
    "results": {
        "id": "650e8400-e29b-41d4-a716-446655440002",
        "code": "project:read:list",
        "name": "查看项目",
        "description": "允许查看项目列表",
        "service": "project",
        "resource": "read",
        "action": "list",
        "is_system": false,
        "is_tenant_level": true,
        "tenant": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2023-06-20T12:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z"
    }
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "具有相同服务、资源和操作的权限已存在"
}
```

### 4. 更新权限信息

更新特定权限的信息。

- **URL**: `/api/management/auth/permissions/{permission_id}/`
- **方法**: `PUT`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名         | 类型    | 必填 | 描述           |
|---------------|---------|------|----------------|
| name          | string  | 是   | 权限名称       |
| description   | string  | 否   | 权限描述       |
| is_system     | boolean | 否   | 是否系统权限   |
| is_tenant_level | boolean | 否 | 是否租户级权限 |

#### 请求示例

```json
{
    "name": "查看项目列表",
    "description": "允许查看所有项目列表",
    "is_system": false,
    "is_tenant_level": true
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "权限更新成功",
    "results": {
        "id": "650e8400-e29b-41d4-a716-446655440002",
        "code": "project:read:list",
        "name": "查看项目列表",
        "description": "允许查看所有项目列表",
        "service": "project",
        "resource": "read",
        "action": "list",
        "is_system": false,
        "is_tenant_level": true,
        "tenant": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2023-06-20T12:00:00Z",
        "updated_at": "2023-06-21T10:15:30Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "权限不存在"
}
```

### 5. 部分更新权限信息

部分更新特定权限的信息。

- **URL**: `/api/management/auth/permissions/{permission_id}/`
- **方法**: `PATCH`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

与更新权限信息接口相同，但所有字段均为可选。

#### 请求示例

```json
{
    "description": "更新后的权限描述"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "权限更新成功",
    "results": {
        "id": "650e8400-e29b-41d4-a716-446655440002",
        "code": "project:read:list",
        "name": "查看项目列表",
        "description": "更新后的权限描述",
        "service": "project",
        "resource": "read",
        "action": "list",
        "is_system": false,
        "is_tenant_level": true,
        "tenant": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2023-06-20T12:00:00Z",
        "updated_at": "2023-06-22T14:25:10Z"
    }
}
```

**失败响应与更新权限信息接口相同**

### 6. 删除权限

删除特定权限。

- **URL**: `/api/management/auth/permissions/{permission_id}/`
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
    "message": "权限删除成功"
}
```

**失败响应 (403 Forbidden)**

```json
{
    "success": false,
    "message": "系统权限不允许删除"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "权限删除失败"
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

1. 所有接口都需要超级管理员权限，普通管理员无法访问
2. 系统权限不允许删除
3. 权限代码由服务名称、资源类型和操作类型组合而成，格式为`service:resource:action`
4. 创建权限时，如果未提供代码，系统会自动根据服务名称、资源类型和操作类型生成
5. 服务名称、资源类型和操作类型的组合在全局范围内必须唯一 