# 日志保留策略管理API文档

本文档描述了SciTigerCore平台的日志保留策略管理API，这些API专为系统管理员设计，提供日志保留策略的创建、查询、更新和删除等功能。

## API基础信息

- **基础路径**: `/api/management/logs/retention-policies/`
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

### 1. 获取日志保留策略列表

获取系统中的日志保留策略列表。

- **URL**: `/api/management/logs/retention-policies/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名      | 类型    | 必填 | 描述                |
|-------------|---------|------|---------------------|
| tenant_id   | string  | 否   | 按租户ID过滤        |
| category_id | string  | 否   | 按日志分类ID过滤    |
| is_active   | boolean | 否   | 是否激活            |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "tenant": {
                "id": "550e8400-e29b-41d4-a716-446655440010",
                "name": "示例租户"
            },
            "category": {
                "id": "550e8400-e29b-41d4-a716-446655440020",
                "name": "系统日志",
                "code": "system"
            },
            "retention_days": 90,
            "is_active": true,
            "created_at": "2023-05-10T08:30:45Z",
            "updated_at": "2023-05-10T08:30:45Z"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "tenant": null,
            "category": {
                "id": "550e8400-e29b-41d4-a716-446655440021",
                "name": "认证日志",
                "code": "auth"
            },
            "retention_days": 180,
            "is_active": true,
            "created_at": "2023-05-10T08:30:45Z",
            "updated_at": "2023-05-10T08:30:45Z"
        },
        // 更多日志保留策略...
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

### 2. 获取日志保留策略详情

获取单个日志保留策略的详细信息。

- **URL**: `/api/management/logs/retention-policies/{policy_id}/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "tenant": {
            "id": "550e8400-e29b-41d4-a716-446655440010",
            "name": "示例租户"
        },
        "category": {
            "id": "550e8400-e29b-41d4-a716-446655440020",
            "name": "系统日志",
            "code": "system"
        },
        "retention_days": 90,
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
    "message": "日志保留策略不存在"
}
```

### 3. 创建日志保留策略

创建新的日志保留策略。

- **URL**: `/api/management/logs/retention-policies/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名         | 类型    | 必填 | 描述                           |
|----------------|---------|------|--------------------------------|
| category       | string  | 是   | 日志分类ID                     |
| tenant         | string  | 否   | 租户ID (不提供则为全局策略)    |
| retention_days | integer | 否   | 保留天数 (默认: 30)            |
| is_active      | boolean | 否   | 是否激活 (默认: true)          |

#### 请求示例

```json
{
    "category": "550e8400-e29b-41d4-a716-446655440020",
    "tenant": "550e8400-e29b-41d4-a716-446655440010",
    "retention_days": 60,
    "is_active": true
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "日志保留策略创建成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "tenant": {
            "id": "550e8400-e29b-41d4-a716-446655440010",
            "name": "示例租户"
        },
        "category": {
            "id": "550e8400-e29b-41d4-a716-446655440020",
            "name": "系统日志",
            "code": "system"
        },
        "retention_days": 60,
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
    "message": "该租户和分类的保留策略已存在"
}
```

### 4. 更新日志保留策略

更新现有的日志保留策略。

- **URL**: `/api/management/logs/retention-policies/{policy_id}/`
- **方法**: `PUT`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名         | 类型    | 必填 | 描述                           |
|----------------|---------|------|--------------------------------|
| retention_days | integer | 是   | 保留天数                       |
| is_active      | boolean | 是   | 是否激活                       |

**注意**: 租户和分类关联不能通过此接口更新

#### 请求示例

```json
{
    "retention_days": 120,
    "is_active": true
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "日志保留策略更新成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "tenant": {
            "id": "550e8400-e29b-41d4-a716-446655440010",
            "name": "示例租户"
        },
        "category": {
            "id": "550e8400-e29b-41d4-a716-446655440020",
            "name": "系统日志",
            "code": "system"
        },
        "retention_days": 120,
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
    "message": "日志保留策略不存在"
}
```

### 5. 部分更新日志保留策略

部分更新现有的日志保留策略。

- **URL**: `/api/management/logs/retention-policies/{policy_id}/`
- **方法**: `PATCH`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名         | 类型    | 必填 | 描述                           |
|----------------|---------|------|--------------------------------|
| retention_days | integer | 否   | 保留天数                       |
| is_active      | boolean | 否   | 是否激活                       |

**注意**: 租户和分类关联不能通过此接口更新

#### 请求示例

```json
{
    "retention_days": 180
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "日志保留策略更新成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "tenant": {
            "id": "550e8400-e29b-41d4-a716-446655440010",
            "name": "示例租户"
        },
        "category": {
            "id": "550e8400-e29b-41d4-a716-446655440020",
            "name": "系统日志",
            "code": "system"
        },
        "retention_days": 180,
        "is_active": true,
        "created_at": "2023-06-15T09:45:30Z",
        "updated_at": "2023-06-15T11:05:45Z"
    }
}
```

### 6. 删除日志保留策略

删除现有的日志保留策略。

- **URL**: `/api/management/logs/retention-policies/{policy_id}/`
- **方法**: `DELETE`
- **权限要求**: 管理员权限

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "日志保留策略删除成功"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "日志保留策略不存在"
}
```

### 7. 初始化默认日志保留策略

初始化系统默认的日志保留策略。

- **URL**: `/api/management/logs/retention-policies/init_default_policies/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "默认日志保留策略初始化成功",
    "results": {
        "created_count": 5,
        "policies": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "category": {
                    "id": "550e8400-e29b-41d4-a716-446655440020",
                    "name": "系统日志",
                    "code": "system"
                },
                "tenant": null,
                "retention_days": 90,
                "is_active": true
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "category": {
                    "id": "550e8400-e29b-41d4-a716-446655440021",
                    "name": "认证日志",
                    "code": "auth"
                },
                "tenant": null,
                "retention_days": 180,
                "is_active": true
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440004",
                "category": {
                    "id": "550e8400-e29b-41d4-a716-446655440022",
                    "name": "用户操作日志",
                    "code": "user_action"
                },
                "tenant": null,
                "retention_days": 60,
                "is_active": true
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440005",
                "category": {
                    "id": "550e8400-e29b-41d4-a716-446655440023",
                    "name": "安全审计日志",
                    "code": "security"
                },
                "tenant": null,
                "retention_days": 365,
                "is_active": true
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440006",
                "category": {
                    "id": "550e8400-e29b-41d4-a716-446655440024",
                    "name": "性能监控日志",
                    "code": "performance"
                },
                "tenant": null,
                "retention_days": 30,
                "is_active": true
            }
        ]
    }
}
``` 