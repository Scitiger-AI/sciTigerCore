# 日志分类管理API文档

本文档描述了SciTigerCore平台的日志分类管理API，这些API专为系统管理员设计，提供日志分类的创建、查询、更新和删除等功能。

## API基础信息

- **基础路径**: `/api/management/logs/categories/`
- **认证方式**: JWT令牌认证
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

### 1. 获取日志分类列表

获取系统中的日志分类列表。

- **URL**: `/api/management/logs/categories/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名    | 类型   | 必填 | 描述                |
|-----------|--------|------|---------------------|
| is_system | boolean| 否   | 是否系统分类        |
| is_active | boolean| 否   | 是否激活            |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "系统日志",
            "code": "system",
            "description": "记录系统级别的操作和事件",
            "is_system": true,
            "is_active": true,
            "created_at": "2023-05-10T08:30:45Z",
            "updated_at": "2023-05-10T08:30:45Z"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "name": "认证日志",
            "code": "auth",
            "description": "记录用户认证相关的操作和事件",
            "is_system": true,
            "is_active": true,
            "created_at": "2023-05-10T08:30:45Z",
            "updated_at": "2023-05-10T08:30:45Z"
        },
        // 更多日志分类...
    ]
}
```

**失败响应 (401 Unauthorized)**

```json
{
    "success": false,
    "message": "认证凭据未提供"
}
```

### 2. 获取日志分类详情

获取单个日志分类的详细信息。

- **URL**: `/api/management/logs/categories/{category_id}/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "系统日志",
        "code": "system",
        "description": "记录系统级别的操作和事件",
        "is_system": true,
        "is_active": true,
        "created_at": "2023-05-10T08:30:45Z",
        "updated_at": "2023-05-10T08:30:45Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "日志分类不存在"
}
```

### 3. 创建日志分类

创建新的日志分类。

- **URL**: `/api/management/logs/categories/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名      | 类型    | 必填 | 描述                |
|-------------|---------|------|---------------------|
| name        | string  | 是   | 分类名称            |
| code        | string  | 是   | 分类代码            |
| description | string  | 否   | 分类描述            |
| is_system   | boolean | 否   | 是否系统分类 (默认: false) |
| is_active   | boolean | 否   | 是否激活 (默认: true) |

#### 请求示例

```json
{
    "name": "API日志",
    "code": "api",
    "description": "记录API调用相关的操作和事件",
    "is_system": false,
    "is_active": true
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "日志分类创建成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "name": "API日志",
        "code": "api",
        "description": "记录API调用相关的操作和事件",
        "is_system": false,
        "is_active": true,
        "created_at": "2023-06-15T09:45:30Z",
        "updated_at": "2023-06-15T09:45:30Z"
    }
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "分类代码已存在"
}
```

### 4. 更新日志分类

更新现有的日志分类。

- **URL**: `/api/management/logs/categories/{category_id}/`
- **方法**: `PUT`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名      | 类型    | 必填 | 描述                |
|-------------|---------|------|---------------------|
| name        | string  | 是   | 分类名称            |
| description | string  | 否   | 分类描述            |
| is_active   | boolean | 否   | 是否激活            |

**注意**: 分类代码(code)和系统分类标志(is_system)不能通过此接口更新

#### 请求示例

```json
{
    "name": "API调用日志",
    "description": "记录所有API调用相关的操作和事件",
    "is_active": true
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "日志分类更新成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "name": "API调用日志",
        "code": "api",
        "description": "记录所有API调用相关的操作和事件",
        "is_system": false,
        "is_active": true,
        "created_at": "2023-06-15T09:45:30Z",
        "updated_at": "2023-06-15T10:20:15Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "日志分类不存在"
}
```

### 5. 部分更新日志分类

部分更新现有的日志分类。

- **URL**: `/api/management/logs/categories/{category_id}/`
- **方法**: `PATCH`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名      | 类型    | 必填 | 描述                |
|-------------|---------|------|---------------------|
| name        | string  | 否   | 分类名称            |
| description | string  | 否   | 分类描述            |
| is_active   | boolean | 否   | 是否激活            |

**注意**: 分类代码(code)和系统分类标志(is_system)不能通过此接口更新

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
    "message": "日志分类更新成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "name": "API调用日志",
        "code": "api",
        "description": "记录所有API调用相关的操作和事件",
        "is_system": false,
        "is_active": false,
        "created_at": "2023-06-15T09:45:30Z",
        "updated_at": "2023-06-15T11:05:45Z"
    }
}
```

### 6. 删除日志分类

删除现有的日志分类。

- **URL**: `/api/management/logs/categories/{category_id}/`
- **方法**: `DELETE`
- **权限要求**: 管理员权限

**注意**: 系统分类不能被删除

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "日志分类删除成功"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "日志分类删除失败，可能是系统分类不能删除"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "日志分类不存在"
}
```

### 7. 初始化系统日志分类

初始化系统预定义的日志分类。

- **URL**: `/api/management/logs/categories/init_system_categories/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "系统日志分类初始化成功",
    "results": {
        "created_count": 5,
        "categories": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "系统日志",
                "code": "system",
                "is_system": true,
                "is_active": true
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "name": "认证日志",
                "code": "auth",
                "is_system": true,
                "is_active": true
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440004",
                "name": "用户操作日志",
                "code": "user_action",
                "is_system": true,
                "is_active": true
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440005",
                "name": "安全审计日志",
                "code": "security",
                "is_system": true,
                "is_active": true
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440006",
                "name": "性能监控日志",
                "code": "performance",
                "is_system": true,
                "is_active": true
            }
        ]
    }
}
``` 