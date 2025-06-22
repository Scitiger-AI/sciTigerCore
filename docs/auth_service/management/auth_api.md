# 管理认证API文档

本文档描述了SciTigerCore平台的管理认证API，这些API专为系统管理员设计，提供管理员登录、令牌刷新和个人资料查询等功能。

## API基础信息

- **基础路径**: `/api/management/auth/`
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

### 1. 管理员登录

管理员登录接口，验证管理员身份并返回JWT令牌。

- **URL**: `/api/management/auth/login/`
- **方法**: `POST`
- **权限要求**: 无（公开接口）

#### 请求参数

| 参数名   | 类型   | 必填 | 描述         |
|----------|--------|------|--------------|
| username | string | 是   | 用户名或邮箱 |
| password | string | 是   | 密码         |

#### 请求示例

```json
{
    "username": "admin@example.com",
    "password": "secure_password"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "管理员登录成功",
    "results": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "admin",
            "email": "admin@example.com",
            "is_active": true,
            "is_staff": true,
            "is_superuser": true,
            "last_login": "2023-06-15T08:30:45Z"
        },
        "tokens": {
            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        },
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

**失败响应 (401 Unauthorized)**

```json
{
    "success": false,
    "message": "用户名或密码不正确"
}
```

```json
{
    "success": false,
    "message": "账户未激活，请联系超级管理员"
}
```

```json
{
    "success": false,
    "message": "您没有管理员权限"
}
```

### 2. 管理员登出

管理员登出接口，使当前令牌失效。

- **URL**: `/api/management/auth/logout/`
- **方法**: `POST`
- **权限要求**: 已认证用户（需要有效的JWT令牌）

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名  | 类型   | 必填 | 描述     |
|---------|--------|------|----------|
| refresh | string | 是   | 刷新令牌 |

#### 请求示例

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "管理员登出成功"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "登出失败: 令牌无效"
}
```

**失败响应 (401 Unauthorized)**

```json
{
    "success": false,
    "message": "认证凭据未提供"
}
```

### 3. 刷新令牌

刷新JWT访问令牌的接口。

- **URL**: `/api/management/auth/refresh-token/`
- **方法**: `POST`
- **权限要求**: 无（公开接口，但需要有效的刷新令牌）

#### 请求参数

| 参数名  | 类型   | 必填 | 描述     |
|---------|--------|------|----------|
| refresh | string | 是   | 刷新令牌 |

#### 请求示例

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "令牌刷新成功",
    "results": {
        "tokens": {
            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        },
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

**失败响应 (401 Unauthorized)**

```json
{
    "success": false,
    "message": "无效的刷新令牌"
}
```

```json
{
    "success": false,
    "message": "非管理员令牌"
}
```

### 4. 获取管理员个人资料

获取当前登录管理员的个人资料信息。

- **URL**: `/api/management/auth/profile/`
- **方法**: `GET`
- **权限要求**: 管理员权限（需要有效的管理员JWT令牌）

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
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "is_active": true,
        "is_staff": true,
        "is_superuser": true,
        "last_login": "2023-06-15T08:30:45Z",
        "date_joined": "2023-01-01T00:00:00Z",
        "permissions": ["*"]
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

**失败响应 (403 Forbidden)**

```json
{
    "success": false,
    "message": "您没有执行该操作的权限"
}
```

## 错误码说明

| 状态码 | 描述                                 |
|--------|------------------------------------|
| 200    | 请求成功                             |
| 400    | 请求参数错误                         |
| 401    | 未授权（未提供认证凭据或凭据无效）     |
| 403    | 禁止访问（权限不足）                 |
| 500    | 服务器内部错误                       |

## 注意事项

1. 管理员登录接口仅供具有管理员权限的用户使用，系统会验证用户的`is_staff`或`is_superuser`属性
2. 管理员令牌包含特殊的管理员声明（`is_admin`, `is_staff`, `is_superuser`），用于标识管理员身份
3. 刷新令牌接口会验证令牌是否为管理员令牌，非管理员令牌将被拒绝刷新
4. 登出接口会将刷新令牌加入黑名单，使其立即失效，提高系统安全性
5. 个人资料接口会返回管理员的权限列表，超级管理员拥有所有权限（用`*`表示） 