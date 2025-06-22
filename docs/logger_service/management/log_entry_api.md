# 日志条目管理API文档

本文档描述了SciTigerCore平台的日志条目管理API，这些API专为系统管理员设计，提供日志查询、统计、创建和删除等功能。

## API基础信息

- **基础路径**: `/api/management/logs/entries/`
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

### 1. 获取日志条目列表

获取系统中的日志条目列表，支持多种过滤条件。

- **URL**: `/api/management/logs/entries/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名      | 类型   | 必填 | 描述                                 |
|-------------|--------|------|--------------------------------------|
| tenant_id   | string | 否   | 按租户ID过滤                         |
| category_id | string | 否   | 按日志分类ID过滤                     |
| user_id     | string | 否   | 按用户ID过滤                         |
| level       | string | 否   | 按日志级别过滤 (debug/info/warning/error/critical) |
| source      | string | 否   | 按日志来源过滤                       |
| start_time  | string | 否   | 开始时间 (ISO格式)                   |
| end_time    | string | 否   | 结束时间 (ISO格式)                   |
| search_text | string | 否   | 搜索文本                             |
| page        | int    | 否   | 页码 (默认: 1)                       |
| page_size   | int    | 否   | 每页数量 (默认: 20, 最大: 100)       |
| sort_field  | string | 否   | 排序字段 (默认: timestamp)           |
| sort_order  | string | 否   | 排序方式 (asc/desc, 默认: desc)      |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "results": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
                "tenant_name": "示例租户",
                "category_id": "550e8400-e29b-41d4-a716-446655440002",
                "category_name": "系统日志",
                "category_code": "system",
                "level": "info",
                "message": "用户登录成功",
                "source": "auth_service",
                "user_id": "550e8400-e29b-41d4-a716-446655440003",
                "username": "admin",
                "ip_address": "192.168.1.1",
                "request_id": "req-123456",
                "timestamp": "2023-06-15T08:30:45Z"
            },
            // 更多日志条目...
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 150,
            "total_pages": 8
        }
    }
}
```

**失败响应 (401 Unauthorized)**

```json
{
    "success": false,
    "message": "认证凭据未提供"
}
```

### 2. 获取日志条目详情

获取单个日志条目的详细信息。

- **URL**: `/api/management/logs/entries/{log_id}/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
        "tenant_name": "示例租户",
        "category_id": "550e8400-e29b-41d4-a716-446655440002",
        "category_name": "系统日志",
        "category_code": "system",
        "level": "info",
        "message": "用户登录成功",
        "source": "auth_service",
        "user_id": "550e8400-e29b-41d4-a716-446655440003",
        "username": "admin",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "request_id": "req-123456",
        "metadata": {
            "browser": "Chrome",
            "os": "Windows",
            "device": "Desktop"
        },
        "timestamp": "2023-06-15T08:30:45Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "日志条目不存在"
}
```

### 3. 创建日志条目

创建新的日志条目。

- **URL**: `/api/management/logs/entries/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名      | 类型   | 必填 | 描述                                 |
|-------------|--------|------|--------------------------------------|
| message     | string | 是   | 日志消息                             |
| level       | string | 否   | 日志级别 (默认: info)                |
| category_id | string | 否   | 日志分类ID                           |
| tenant_id   | string | 否   | 租户ID                               |
| user_id     | string | 否   | 用户ID                               |
| source      | string | 否   | 日志来源                             |
| ip_address  | string | 否   | IP地址                               |
| user_agent  | string | 否   | 用户代理                             |
| request_id  | string | 否   | 请求ID                               |
| metadata    | object | 否   | 元数据                               |

#### 请求示例

```json
{
    "message": "系统配置更新",
    "level": "info",
    "category_id": "550e8400-e29b-41d4-a716-446655440002",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
    "source": "system_service",
    "metadata": {
        "config_name": "email_settings",
        "changed_by": "admin"
    }
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "日志条目创建成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440004",
        "message": "系统配置更新",
        "level": "info",
        "category_id": "550e8400-e29b-41d4-a716-446655440002",
        "category_name": "系统日志",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
        "tenant_name": "示例租户",
        "source": "system_service",
        "metadata": {
            "config_name": "email_settings",
            "changed_by": "admin"
        },
        "timestamp": "2023-06-15T09:45:30Z"
    }
}
```

### 4. 批量创建日志条目

批量创建多个日志条目。

- **URL**: `/api/management/logs/entries/batch_create/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名 | 类型  | 必填 | 描述         |
|--------|-------|------|--------------|
| logs   | array | 是   | 日志条目数组 |

#### 请求示例

```json
{
    "logs": [
        {
            "message": "用户登录",
            "level": "info",
            "category_id": "550e8400-e29b-41d4-a716-446655440002",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
            "user_id": "550e8400-e29b-41d4-a716-446655440003",
            "source": "auth_service"
        },
        {
            "message": "权限变更",
            "level": "warning",
            "category_id": "550e8400-e29b-41d4-a716-446655440002",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
            "user_id": "550e8400-e29b-41d4-a716-446655440003",
            "source": "auth_service"
        }
    ]
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "成功创建2条日志",
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440005",
            "message": "用户登录",
            "level": "info",
            "category_id": "550e8400-e29b-41d4-a716-446655440002",
            "category_name": "系统日志",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
            "tenant_name": "示例租户",
            "user_id": "550e8400-e29b-41d4-a716-446655440003",
            "username": "admin",
            "source": "auth_service",
            "timestamp": "2023-06-15T10:15:20Z"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440006",
            "message": "权限变更",
            "level": "warning",
            "category_id": "550e8400-e29b-41d4-a716-446655440002",
            "category_name": "系统日志",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
            "tenant_name": "示例租户",
            "user_id": "550e8400-e29b-41d4-a716-446655440003",
            "username": "admin",
            "source": "auth_service",
            "timestamp": "2023-06-15T10:15:20Z"
        }
    ]
}
```

### 5. 删除日志

根据条件删除日志条目。

- **URL**: `/api/management/logs/entries/delete_logs/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名      | 类型   | 必填 | 描述                       |
|-------------|--------|------|----------------------------|
| tenant_id   | string | 否   | 按租户ID删除               |
| category_id | string | 否   | 按日志分类ID删除           |
| before_date | string | 否   | 删除指定日期之前的日志     |

**注意**: 必须提供至少一个过滤条件

#### 请求示例

```json
{
    "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
    "category_id": "550e8400-e29b-41d4-a716-446655440002",
    "before_date": "2023-05-01T00:00:00Z"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "成功删除150条日志",
    "results": {
        "deleted_count": 150
    }
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "必须提供至少一个过滤条件"
}
```

### 6. 应用日志保留策略

应用系统中配置的日志保留策略，删除过期日志。

- **URL**: `/api/management/logs/entries/apply_retention_policies/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "成功删除250条过期日志",
    "results": {
        "deleted_count": 250
    }
}
```

### 7. 获取日志统计信息

获取日志统计数据。

- **URL**: `/api/management/logs/entries/stats/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求参数

| 参数名    | 类型   | 必填 | 描述                             |
|-----------|--------|------|----------------------------------|
| tenant_id | string | 否   | 按租户ID过滤                     |
| days      | int    | 否   | 统计天数 (默认: 30, 最大: 365)   |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "total_logs": 15240,
        "logs_by_level": {
            "debug": 5120,
            "info": 8560,
            "warning": 1200,
            "error": 320,
            "critical": 40
        },
        "logs_by_category": {
            "system": 4500,
            "auth": 3800,
            "user": 2100,
            "api": 4840
        },
        "daily_stats": [
            {
                "date": "2023-06-15",
                "count": 520,
                "by_level": {
                    "debug": 180,
                    "info": 290,
                    "warning": 40,
                    "error": 8,
                    "critical": 2
                }
            },
            // 更多每日统计...
        ]
    }
}
``` 