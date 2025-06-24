# 服务范围管理API

本文档描述了服务范围管理相关的API接口，包括服务、资源和操作的管理。

## 基础信息

- 基础路径: `/api/management/`
- 认证方式: JWT认证
- 权限要求: 管理员权限

## 1. 服务管理API

### 1.1 获取服务列表

获取系统中所有服务的列表，支持过滤、搜索和分页。

- **请求方法**: `GET`
- **请求路径**: `/api/management/services/`
- **请求参数**:
  - `page`: 页码，默认为1
  - `page_size`: 每页记录数，默认为10
  - `search`: 搜索关键词，会匹配服务的代码、名称和描述
  - `ordering`: 排序字段，可选值包括 `code`, `name`, `is_system`, `created_at`, `updated_at`，前面加 `-` 表示降序
  - `code`: 按代码过滤
  - `name`: 按名称过滤
  - `description`: 按描述过滤
  - `is_system`: 按是否系统服务过滤，可选值为 `true` 或 `false`
  - `tenant_id`: 按租户ID过滤

- **响应示例**:
```json
{
    "success": true,
    "message": null,
    "results": {
        "count": 9,
        "next": "http://example.com/api/management/services/?page=2",
        "previous": null,
        "results": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "code": "auth_service",
                "name": "认证服务",
                "description": "提供用户认证、授权、权限管理等功能",
                "is_system": true,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            },
            // ... 更多服务
        ]
    }
}
```

### 1.2 获取服务详情

获取指定服务的详细信息。

- **请求方法**: `GET`
- **请求路径**: `/api/management/services/{id}/`
- **路径参数**:
  - `id`: 服务ID

- **响应示例**:
```json
{
    "success": true,
    "message": null,
    "results": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "code": "auth_service",
        "name": "认证服务",
        "description": "提供用户认证、授权、权限管理等功能",
        "is_system": true,
        "tenant": null,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

### 1.3 创建服务

创建新的服务。

- **请求方法**: `POST`
- **请求路径**: `/api/management/services/`
- **请求体**:
```json
{
    "code": "custom_service",
    "name": "自定义服务",
    "description": "这是一个自定义服务",
    "is_system": false,
    "tenant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

- **响应示例**:
```json
{
    "success": true,
    "message": "服务创建成功",
    "results": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "code": "custom_service",
        "name": "自定义服务",
        "description": "这是一个自定义服务",
        "is_system": false,
        "tenant": {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "测试租户",
            // ... 其他租户信息
        },
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

### 1.4 更新服务

更新指定服务的信息。

- **请求方法**: `PUT` 或 `PATCH`
- **请求路径**: `/api/management/services/{id}/`
- **路径参数**:
  - `id`: 服务ID
- **请求体**:
```json
{
    "name": "更新后的服务名称",
    "description": "更新后的服务描述"
}
```

- **响应示例**:
```json
{
    "success": true,
    "message": "服务更新成功",
    "results": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "code": "auth_service",
        "name": "更新后的服务名称",
        "description": "更新后的服务描述",
        "is_system": true,
        "tenant": null,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

### 1.5 删除服务

删除指定的服务。

- **请求方法**: `DELETE`
- **请求路径**: `/api/management/services/{id}/`
- **路径参数**:
  - `id`: 服务ID

- **响应示例**:
```json
{
    "success": true,
    "message": "服务删除成功",
    "results": null
}
```

### 1.6 导入默认服务

导入系统预设的默认服务、资源和操作。

- **请求方法**: `POST`
- **请求路径**: `/api/management/services/import_default/`

- **响应示例**:
```json
{
    "success": true,
    "message": "默认服务数据导入完成",
    "results": {
        "services": {
            "created": 5,
            "existed": 4,
            "failed": 0
        },
        "resources": {
            "created": 20,
            "existed": 5,
            "failed": 0
        },
        "actions": {
            "created": 8,
            "existed": 3,
            "failed": 0
        }
    }
}
```

## 2. 资源管理API

### 2.1 获取资源列表

获取系统中所有资源的列表，支持过滤、搜索和分页。

- **请求方法**: `GET`
- **请求路径**: `/api/management/resources/`
- **请求参数**:
  - `page`: 页码，默认为1
  - `page_size`: 每页记录数，默认为10
  - `search`: 搜索关键词，会匹配资源的代码、名称、描述和所属服务
  - `ordering`: 排序字段，可选值包括 `code`, `name`, `service__code`, `created_at`, `updated_at`，前面加 `-` 表示降序
  - `code`: 按代码过滤
  - `name`: 按名称过滤
  - `description`: 按描述过滤
  - `service_id`: 按服务ID过滤
  - `service_code`: 按服务代码过滤
  - `is_system`: 按是否系统资源过滤，可选值为 `true` 或 `false`
  - `tenant_id`: 按租户ID过滤

- **响应示例**:
```json
{
    "success": true,
    "message": null,
    "results": {
        "count": 25,
        "next": "http://example.com/api/management/resources/?page=2",
        "previous": null,
        "results": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "code": "users",
                "name": "用户",
                "description": "用户资源",
                "service_code": "auth_service",
                "is_system": true,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            },
            // ... 更多资源
        ]
    }
}
```

### 2.2 获取资源详情

获取指定资源的详细信息。

- **请求方法**: `GET`
- **请求路径**: `/api/management/resources/{id}/`
- **路径参数**:
  - `id`: 资源ID

- **响应示例**:
```json
{
    "success": true,
    "message": null,
    "results": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "code": "users",
        "name": "用户",
        "description": "用户资源",
        "service": {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "code": "auth_service",
            "name": "认证服务",
            "description": "提供用户认证、授权、权限管理等功能",
            "is_system": true,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        "is_system": true,
        "tenant_id": null,
        "tenant_name": null,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

### 2.3 创建资源

创建新的资源。

- **请求方法**: `POST`
- **请求路径**: `/api/management/resources/`
- **请求体**:
```json
{
    "code": "custom_resource",
    "name": "自定义资源",
    "description": "这是一个自定义资源",
    "service_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

- **响应示例**:
```json
{
    "success": true,
    "message": "资源创建成功",
    "results": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "code": "custom_resource",
        "name": "自定义资源",
        "description": "这是一个自定义资源",
        "service": {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "code": "auth_service",
            "name": "认证服务",
            "description": "提供用户认证、授权、权限管理等功能",
            "is_system": true,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        "is_system": true,
        "tenant_id": null,
        "tenant_name": null,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

### 2.4 更新资源

更新指定资源的信息。

- **请求方法**: `PUT` 或 `PATCH`
- **请求路径**: `/api/management/resources/{id}/`
- **路径参数**:
  - `id`: 资源ID
- **请求体**:
```json
{
    "name": "更新后的资源名称",
    "description": "更新后的资源描述"
}
```

- **响应示例**:
```json
{
    "success": true,
    "message": "资源更新成功",
    "results": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "code": "users",
        "name": "更新后的资源名称",
        "description": "更新后的资源描述",
        "service": {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "code": "auth_service",
            "name": "认证服务",
            "description": "提供用户认证、授权、权限管理等功能",
            "is_system": true,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        "is_system": true,
        "tenant_id": null,
        "tenant_name": null,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

### 2.5 删除资源

删除指定的资源。

- **请求方法**: `DELETE`
- **请求路径**: `/api/management/resources/{id}/`
- **路径参数**:
  - `id`: 资源ID

- **响应示例**:
```json
{
    "success": true,
    "message": "资源删除成功",
    "results": null
}
```

### 2.6 按服务获取资源

根据服务代码获取资源列表。

- **请求方法**: `GET`
- **请求路径**: `/api/management/resources/by_service/`
- **请求参数**:
  - `service_code`: 服务代码
  - `tenant_id`: 租户ID（可选）

- **响应示例**:
```json
{
    "success": true,
    "message": null,
    "results": [
        {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "code": "users",
            "name": "用户",
            "description": "用户资源",
            "service_code": "auth_service",
            "is_system": true,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        // ... 更多资源
    ]
}
```

## 3. 操作管理API

### 3.1 获取操作列表

获取系统中所有操作的列表，支持过滤、搜索和分页。

- **请求方法**: `GET`
- **请求路径**: `/api/management/actions/`
- **请求参数**:
  - `page`: 页码，默认为1
  - `page_size`: 每页记录数，默认为10
  - `search`: 搜索关键词，会匹配操作的代码、名称和描述
  - `ordering`: 排序字段，可选值包括 `code`, `name`, `is_system`, `created_at`, `updated_at`，前面加 `-` 表示降序
  - `code`: 按代码过滤
  - `name`: 按名称过滤
  - `description`: 按描述过滤
  - `is_system`: 按是否系统操作过滤，可选值为 `true` 或 `false`
  - `tenant_id`: 按租户ID过滤

- **响应示例**:
```json
{
    "success": true,
    "message": null,
    "results": {
        "count": 11,
        "next": "http://example.com/api/management/actions/?page=2",
        "previous": null,
        "results": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "code": "create",
                "name": "创建",
                "description": "创建操作",
                "is_system": true,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            },
            // ... 更多操作
        ]
    }
}
```

### 3.2 获取操作详情

获取指定操作的详细信息。

- **请求方法**: `GET`
- **请求路径**: `/api/management/actions/{id}/`
- **路径参数**:
  - `id`: 操作ID

- **响应示例**:
```json
{
    "success": true,
    "message": null,
    "results": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "code": "create",
        "name": "创建",
        "description": "创建操作",
        "is_system": true,
        "tenant": null,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

### 3.3 创建操作

创建新的操作。

- **请求方法**: `POST`
- **请求路径**: `/api/management/actions/`
- **请求体**:
```json
{
    "code": "custom_action",
    "name": "自定义操作",
    "description": "这是一个自定义操作",
    "is_system": false,
    "tenant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

- **响应示例**:
```json
{
    "success": true,
    "message": "操作创建成功",
    "results": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "code": "custom_action",
        "name": "自定义操作",
        "description": "这是一个自定义操作",
        "is_system": false,
        "tenant": {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "测试租户",
            // ... 其他租户信息
        },
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

### 3.4 更新操作

更新指定操作的信息。

- **请求方法**: `PUT` 或 `PATCH`
- **请求路径**: `/api/management/actions/{id}/`
- **路径参数**:
  - `id`: 操作ID
- **请求体**:
```json
{
    "name": "更新后的操作名称",
    "description": "更新后的操作描述"
}
```

- **响应示例**:
```json
{
    "success": true,
    "message": "操作更新成功",
    "results": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "code": "create",
        "name": "更新后的操作名称",
        "description": "更新后的操作描述",
        "is_system": true,
        "tenant": null,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

### 3.5 删除操作

删除指定的操作。

- **请求方法**: `DELETE`
- **请求路径**: `/api/management/actions/{id}/`
- **路径参数**:
  - `id`: 操作ID

- **响应示例**:
```json
{
    "success": true,
    "message": "操作删除成功",
    "results": null
}
```

## 4. 服务范围兼容API

以下API提供与旧版服务范围API兼容的功能，用于获取服务、资源和操作的选项信息。

### 4.1 获取服务选项列表

获取系统中所有服务的选项列表。

- **请求方法**: `GET`
- **请求路径**: `/api/management/service-scopes/services/`
- **请求参数**:
  - `tenant_id`: 租户ID（可选）

- **响应示例**:
```json
{
    "success": true,
    "message": null,
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
        // ... 更多服务
    ]
}
```

### 4.2 获取资源选项列表

获取系统中所有资源的选项列表，可按服务过滤。

- **请求方法**: `GET`
- **请求路径**: `/api/management/service-scopes/resources/`
- **请求参数**:
  - `service`: 服务代码（可选）
  - `tenant_id`: 租户ID（可选）

- **响应示例**:

如果提供了服务代码：
```json
{
    "success": true,
    "message": null,
    "results": [
        {
            "code": "users",
            "name": "用户"
        },
        {
            "code": "roles",
            "name": "角色"
        },
        // ... 更多资源
    ]
}
```

如果没有提供服务代码：
```json
{
    "success": true,
    "message": null,
    "results": {
        "auth_service": [
            {
                "code": "users",
                "name": "用户"
            },
            {
                "code": "roles",
                "name": "角色"
            }
            // ... 更多资源
        ],
        "tenant_service": [
            {
                "code": "tenants",
                "name": "租户"
            }
            // ... 更多资源
        ]
        // ... 更多服务的资源
    }
}
```

### 4.3 获取操作选项列表

获取系统中所有操作的选项列表。

- **请求方法**: `GET`
- **请求路径**: `/api/management/service-scopes/actions/`
- **请求参数**:
  - `tenant_id`: 租户ID（可选）

- **响应示例**:
```json
{
    "success": true,
    "message": null,
    "results": [
        {
            "code": "create",
            "name": "创建"
        },
        {
            "code": "read",
            "name": "读取"
        },
        {
            "code": "update",
            "name": "更新"
        },
        // ... 更多操作
    ]
}
```

### 4.4 获取所有选项信息

获取系统中所有服务、资源和操作的选项信息。

- **请求方法**: `GET`
- **请求路径**: `/api/management/service-scopes/all/`
- **请求参数**:
  - `tenant_id`: 租户ID（可选）

- **响应示例**:
```json
{
    "success": true,
    "message": null,
    "results": {
        "services": [
            {
                "code": "auth_service",
                "name": "认证服务",
                "description": "提供用户认证、授权、权限管理等功能"
            },
            // ... 更多服务
        ],
        "resources": {
            "auth_service": [
                {
                    "code": "users",
                    "name": "用户"
                },
                // ... 更多资源
            ],
            // ... 更多服务的资源
        },
        "actions": [
            {
                "code": "create",
                "name": "创建"
            },
            // ... 更多操作
        ]
    }
}
``` 