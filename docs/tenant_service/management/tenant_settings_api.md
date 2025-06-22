# 租户设置管理API文档

本文档描述了SciTigerCore平台的租户设置管理API，这些API专为系统管理员设计，提供租户设置的查询和修改功能。

## API基础信息

- **基础路径**: `/api/management/tenants/settings/`
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

### 1. 获取租户设置列表

获取系统中的租户设置列表。

- **URL**: `/api/management/tenants/settings/`
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
            "timezone": "Asia/Shanghai",
            "date_format": "YYYY-MM-DD",
            "time_format": "HH:mm:ss",
            "language": "zh-CN",
            "theme": "light",
            "allow_registration": true,
            "require_email_verification": true,
            "session_timeout_minutes": 30,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "tenant": {
                "id": "650e8400-e29b-41d4-a716-446655440001",
                "name": "租户2",
                "slug": "tenant2"
            },
            "timezone": "America/New_York",
            "date_format": "MM/DD/YYYY",
            "time_format": "hh:mm:ss a",
            "language": "en-US",
            "theme": "dark",
            "allow_registration": false,
            "require_email_verification": true,
            "session_timeout_minutes": 60,
            "created_at": "2023-01-02T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z"
        }
    ]
}
```

### 2. 获取租户设置详情

获取特定租户设置的详细信息。

- **URL**: `/api/management/tenants/settings/{settings_id}/`
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
        "timezone": "Asia/Shanghai",
        "date_format": "YYYY-MM-DD",
        "time_format": "HH:mm:ss",
        "language": "zh-CN",
        "theme": "light",
        "allow_registration": true,
        "require_email_verification": true,
        "session_timeout_minutes": 30,
        "password_policy": {
            "min_length": 8,
            "require_uppercase": true,
            "require_lowercase": true,
            "require_number": true,
            "require_special_char": true,
            "password_expiry_days": 90
        },
        "notification_settings": {
            "email_notifications": true,
            "system_notifications": true,
            "marketing_emails": false
        },
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "租户设置不存在"
}
```

### 3. 根据租户ID获取设置

根据租户ID获取对应的租户设置。

- **URL**: `/api/management/tenants/settings/by_tenant/`
- **方法**: `GET`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名    | 类型   | 必填 | 描述       |
|-----------|--------|------|------------|
| tenant_id | string | 是   | 租户ID     |

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
            "slug": "tenant1"
        },
        "timezone": "Asia/Shanghai",
        "date_format": "YYYY-MM-DD",
        "time_format": "HH:mm:ss",
        "language": "zh-CN",
        "theme": "light",
        "allow_registration": true,
        "require_email_verification": true,
        "session_timeout_minutes": 30,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
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

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "指定的租户不存在"
}
```

### 4. 更新租户设置

更新特定租户设置的信息。

- **URL**: `/api/management/tenants/settings/{settings_id}/`
- **方法**: `PUT`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名                   | 类型    | 必填 | 描述                   |
|--------------------------|---------|------|----------------------|
| timezone                 | string  | 是   | 时区                   |
| date_format              | string  | 是   | 日期格式               |
| time_format              | string  | 是   | 时间格式               |
| language                 | string  | 是   | 语言                   |
| theme                    | string  | 是   | 主题                   |
| allow_registration       | boolean | 是   | 是否允许注册           |
| require_email_verification| boolean | 是   | 是否要求邮箱验证       |
| session_timeout_minutes  | integer | 是   | 会话超时时间（分钟）   |

#### 请求示例

```json
{
    "timezone": "Asia/Shanghai",
    "date_format": "YYYY/MM/DD",
    "time_format": "HH:mm",
    "language": "zh-CN",
    "theme": "dark",
    "allow_registration": false,
    "require_email_verification": true,
    "session_timeout_minutes": 60
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "租户设置已更新",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "name": "租户1",
            "slug": "tenant1"
        },
        "timezone": "Asia/Shanghai",
        "date_format": "YYYY/MM/DD",
        "time_format": "HH:mm",
        "language": "zh-CN",
        "theme": "dark",
        "allow_registration": false,
        "require_email_verification": true,
        "session_timeout_minutes": 60,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z"
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "租户设置不存在"
}
```

### 5. 部分更新租户设置

部分更新特定租户设置的信息。

- **URL**: `/api/management/tenants/settings/{settings_id}/`
- **方法**: `PATCH`
- **权限要求**: 超级管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

与更新租户设置接口相同，但所有字段均为可选。

#### 请求示例

```json
{
    "theme": "dark",
    "session_timeout_minutes": 60
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "租户设置已更新",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant": {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "name": "租户1",
            "slug": "tenant1"
        },
        "timezone": "Asia/Shanghai",
        "date_format": "YYYY-MM-DD",
        "time_format": "HH:mm:ss",
        "language": "zh-CN",
        "theme": "dark",
        "allow_registration": true,
        "require_email_verification": true,
        "session_timeout_minutes": 60,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-06-20T12:00:00Z"
    }
}
```

**失败响应与更新租户设置接口相同**

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

1. 所有接口都需要超级管理员权限，非超级管理员用户无法访问
2. 租户设置在创建租户时会自动生成默认配置
3. 时区、日期格式和时间格式会影响整个租户的时间显示
4. 会话超时时间设置会影响用户登录状态的保持时长
5. 语言设置会影响系统默认显示的语言，但用户可以在个人设置中覆盖此设置 