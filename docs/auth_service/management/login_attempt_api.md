# 管理登录尝试API文档

本文档描述了SciTigerCore平台的管理登录尝试API，这些API专为系统管理员设计，提供登录尝试记录的查询、统计分析等功能。

## API基础信息

- **基础路径**: `/api/management/auth/login-attempts/`
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
        "next": "http://example.com/api/management/auth/login-attempts/?page=2",
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

### 1. 获取登录尝试记录列表

获取系统中的登录尝试记录列表。

- **URL**: `/api/management/auth/login-attempts/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 查询参数

| 参数名          | 类型    | 必填 | 描述           |
|-----------------|---------|------|----------------|
| email           | string  | 否   | 按邮箱地址过滤  |
| ip_address      | string  | 否   | 按IP地址过滤    |
| status          | string  | 否   | 按状态过滤      |
| is_admin_login  | boolean | 否   | 按登录类型过滤  |
| user_id         | string  | 否   | 按用户ID过滤    |
| tenant_id       | string  | 否   | 按租户ID过滤    |
| timestamp_after | datetime| 否   | 按时间下限过滤  |
| timestamp_before| datetime| 否   | 按时间上限过滤  |
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
        "total": 35,
        "page_size": 10,
        "current_page": 1,
        "total_pages": 4,
        "next": "http://example.com/api/management/auth/login-attempts/?page=2",
        "previous": null,
        "results": [
            {
                "id": "850e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "ip_address": "192.168.1.1",
                "status": "success",
                "status_display": "成功",
                "reason": null,
                "is_admin_login": false,
                "timestamp": "2023-06-15T08:30:45Z",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
            },
            {
                "id": "850e8400-e29b-41d4-a716-446655440001",
                "email": "admin@example.com",
                "ip_address": "192.168.1.2",
                "status": "failed",
                "status_display": "失败",
                "reason": "用户名或密码不正确",
                "is_admin_login": true,
                "timestamp": "2023-06-15T08:25:30Z",
                "user_id": null,
                "tenant_id": null
            }
        ]
    }
}
```

### 2. 获取登录尝试记录详情

获取特定登录尝试记录的详细信息。

- **URL**: `/api/management/auth/login-attempts/{login_attempt_id}/`
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
        "id": "850e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "status": "success",
        "status_display": "成功",
        "reason": null,
        "is_admin_login": false,
        "timestamp": "2023-06-15T08:30:45Z",
        "failure_reason": null,
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "user1",
            "email": "user@example.com",
            "first_name": "Test",
            "last_name": "User",
            "is_active": true
        },
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "测试租户",
            "subdomain": "test"
        },
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "登录尝试记录不存在"
}
```

### 3. 获取登录尝试统计信息

获取登录尝试记录的统计信息。

- **URL**: `/api/management/auth/login-attempts/stats/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 查询参数

与获取登录尝试记录列表接口相同，用于过滤统计范围。

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "total": 150,
        "success": 100,
        "failed": 45,
        "blocked": 5,
        "admin_login": 30,
        "user_login": 120,
        "time_ranges": {
            "last_24h": 25,
            "last_7d": 80,
            "last_30d": 150
        },
        "reasons": [
            {
                "reason": "用户名或密码不正确",
                "count": 30
            },
            {
                "reason": "账户未激活",
                "count": 10
            },
            {
                "reason": "非管理员用户",
                "count": 5
            }
        ],
        "ip_addresses": [
            {
                "ip_address": "192.168.1.1",
                "count": 20
            },
            {
                "ip_address": "192.168.1.2",
                "count": 15
            }
        ]
    }
}
```

### 4. 获取失败登录尝试统计信息

获取失败登录尝试记录的详细统计信息。

- **URL**: `/api/management/auth/login-attempts/failed_login_stats/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 查询参数

与获取登录尝试记录列表接口相同，用于过滤统计范围。

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": {
        "total_failed": 45,
        "failed_24h": 10,
        "failed_7d": 30,
        "ip_stats": [
            {
                "ip_address": "192.168.1.1",
                "count": 15
            },
            {
                "ip_address": "192.168.1.2",
                "count": 10
            }
        ],
        "email_stats": [
            {
                "email": "user@example.com",
                "count": 8
            },
            {
                "email": "admin@example.com",
                "count": 7
            }
        ],
        "reason_stats": [
            {
                "reason": "用户名或密码不正确",
                "count": 30
            },
            {
                "reason": "账户未激活",
                "count": 10
            }
        ],
        "hourly_stats": [
            {
                "hour": 0,
                "count": 2
            },
            {
                "hour": 1,
                "count": 1
            },
            {
                "hour": 8,
                "count": 5
            },
            {
                "hour": 9,
                "count": 2
            }
        ]
    }
}
```

## 错误码说明

| 状态码 | 描述                                 |
|--------|------------------------------------|
| 200    | 请求成功                             |
| 400    | 请求参数错误                         |
| 401    | 未授权（未提供认证凭据或凭据无效）     |
| 403    | 禁止访问（权限不足）                 |
| 404    | 资源不存在                           |
| 500    | 服务器内部错误                       |

## 注意事项

1. 所有接口都需要管理员权限，非管理员用户无法访问
2. 超级管理员可以查看所有租户的登录尝试记录，普通管理员只能查看自己租户的记录
3. 查询大量记录或执行复杂统计可能需要较长时间，建议使用适当的过滤条件
4. 登录尝试记录为只读数据，不提供创建、更新或删除操作
5. 统计信息接口会根据查询参数过滤数据，可以结合使用以获取特定范围的统计信息 