# 平台认证API文档

本文档描述了SciTigerCore平台的认证API，这些API面向终端用户，提供用户登录、登出、令牌刷新和注册等功能。

## 租户识别

作为多租户系统，大多数平台API需要识别当前租户上下文。系统支持多种租户识别方式，详见[平台API租户识别机制说明](./README.md)。

**注意**：本文档中的认证相关接口（登录、注册、令牌刷新等）不需要租户识别，但其他平台API接口需要在请求中提供租户ID。

### 租户信息与认证接口

虽然认证接口不强制要求提供租户信息，但在以下情况下，提供租户信息会影响接口行为：

1. **登录时提供租户信息**：系统会验证用户是否属于该租户。如果用户不属于该租户或在该租户中未激活，登录将被拒绝。

2. **注册时提供租户信息**：新注册的用户将自动被添加到指定的租户中。如果不提供租户信息，用户将被创建但不会关联到任何租户。

租户信息可以通过请求头`X-Tenant-ID`、查询参数`tenant_id`或子域名等方式提供。

## API基础信息

- **基础路径**: `/api/platform/auth/`
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

### 1. 用户登录

用户登录接口，验证用户身份并返回JWT令牌。

- **URL**: `/api/platform/auth/login/`
- **方法**: `POST`
- **权限要求**: 无（公开接口）

#### 请求参数

| 参数名   | 类型   | 必填 | 描述         |
|----------|--------|------|--------------|
| username | string | 是   | 用户名或邮箱 |
| password | string | 是   | 密码         |

#### 租户上下文（可选）

可以通过以下方式提供租户信息：

- 请求头: `X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000`
- 查询参数: `/api/platform/auth/login/?tenant_id=550e8400-e29b-41d4-a716-446655440000`
- 子域名: `https://tenant-name.yourdomain.com/api/platform/auth/login/`

如果提供了租户信息，系统会验证用户是否属于该租户。如果用户不属于该租户或在该租户中未激活，登录将被拒绝。

#### 请求示例

```json
{
    "username": "user@example.com",
    "password": "secure_password"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "登录成功",
    "results": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "user",
            "email": "user@example.com",
            "is_active": true,
            "last_login": "2023-06-15T08:30:45Z"
        },
        "tokens": {
            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        },
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
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
    "message": "账户未激活，请联系管理员"
}
```

```json
{
    "success": false,
    "message": "用户不属于当前租户或未激活"
}
```

### 2. 用户登出

用户登出接口，使当前令牌失效。

- **URL**: `/api/platform/auth/logout/`
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
    "message": "登出成功",
    "results": null
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

- **URL**: `/api/platform/auth/refresh-token/`
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
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
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

### 4. 用户注册

用户注册接口，创建新用户账户。

- **URL**: `/api/platform/auth/register/`
- **方法**: `POST`
- **权限要求**: 无（公开接口）

#### 请求参数

| 参数名          | 类型   | 必填 | 描述           |
|-----------------|--------|------|----------------|
| username        | string | 是   | 用户名         |
| email           | string | 是   | 邮箱地址       |
| password        | string | 是   | 密码           |
| password_confirm| string | 是   | 确认密码       |
| first_name      | string | 否   | 名             |
| last_name       | string | 否   | 姓             |
| phone           | string | 否   | 电话号码       |

#### 租户上下文（可选）

可以通过以下方式提供租户信息：

- 请求头: `X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000`
- 查询参数: `/api/platform/auth/register/?tenant_id=550e8400-e29b-41d4-a716-446655440000`
- 子域名: `https://tenant-name.yourdomain.com/api/platform/auth/register/`

如果提供了租户信息，新注册的用户将自动被添加到指定的租户中。如果不提供租户信息，用户将被创建但不会关联到任何租户。

#### 请求示例

```json
{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "secure_password",
    "password_confirm": "secure_password",
    "first_name": "New",
    "last_name": "User",
    "phone": "13800138000"
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "注册成功",
    "results": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "newuser",
            "email": "newuser@example.com"
        }
    }
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "用户名已存在"
}
```

```json
{
    "success": false,
    "message": "邮箱已被注册"
}
```

```json
{
    "success": false,
    "message": "两次密码输入不一致"
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
| 500    | 服务器内部错误                       |

## 注意事项

1. 用户登录时会检查用户是否属于当前租户，不属于当前租户的用户将无法登录
2. 登出接口会将刷新令牌加入黑名单，使其立即失效，提高系统安全性
3. 注册成功后，如果有当前租户上下文，用户会自动添加到该租户中
4. 密码必须符合系统的强度要求，包括长度、复杂度等 