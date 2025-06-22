# 平台用户API文档

本文档描述了SciTigerCore平台的用户API，这些API面向终端用户，提供用户信息查询、更新和密码管理等功能。

## 租户识别

作为多租户系统，所有平台用户API都需要识别当前租户上下文。请在请求中提供租户ID，否则API将返回403 Forbidden错误。

系统支持多种租户识别方式，包括：
- 请求头：`X-Tenant-ID`
- 查询参数：`tenant_id`
- 子域名
- JWT令牌中的租户信息
- API密钥关联的租户

详细信息请参考[平台API租户识别机制说明](./README.md)。

## API基础信息

- **基础路径**: `/api/platform/auth/users/`
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

### 1. 获取用户列表

获取当前租户下的用户列表。

- **URL**: `/api/platform/auth/users/`
- **方法**: `GET`
- **权限要求**: 已认证用户

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "user1",
            "email": "user1@example.com",
            "first_name": "First",
            "last_name": "User",
            "is_active": true,
            "phone": "13800138000",
            "email_verified": true,
            "phone_verified": false,
            "last_login": "2023-06-15T08:30:45Z",
            "date_joined": "2023-01-01T00:00:00Z"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "username": "user2",
            "email": "user2@example.com",
            "first_name": "Second",
            "last_name": "User",
            "is_active": true,
            "phone": "13900139000",
            "email_verified": true,
            "phone_verified": true,
            "last_login": "2023-06-16T10:20:30Z",
            "date_joined": "2023-01-02T00:00:00Z"
        }
    ]
}
```

### 2. 获取当前用户信息

获取当前登录用户的详细信息。

- **URL**: `/api/platform/auth/users/userInfo/`
- **方法**: `GET`
- **权限要求**: 已认证用户

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
        "username": "user1",
        "email": "user1@example.com",
        "first_name": "First",
        "last_name": "User",
        "is_active": true,
        "phone": "13800138000",
        "email_verified": true,
        "phone_verified": false,
        "last_login": "2023-06-15T08:30:45Z",
        "date_joined": "2023-01-01T00:00:00Z",
        "bio": "用户个人简介",
        "avatar": "https://example.com/avatars/user1.jpg",
        "roles": [
            {
                "id": "650e8400-e29b-41d4-a716-446655440000",
                "name": "普通用户",
                "code": "normal_user"
            }
        ]
    }
}
```

### 3. 获取用户详情

获取特定用户的详细信息。

- **URL**: `/api/platform/auth/users/{user_id}/`
- **方法**: `GET`
- **权限要求**: 已认证用户

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
        "username": "user1",
        "email": "user1@example.com",
        "first_name": "First",
        "last_name": "User",
        "is_active": true,
        "phone": "13800138000",
        "email_verified": true,
        "phone_verified": false,
        "last_login": "2023-06-15T08:30:45Z",
        "date_joined": "2023-01-01T00:00:00Z",
        "bio": "用户个人简介",
        "avatar": "https://example.com/avatars/user1.jpg",
        "roles": [
            {
                "id": "650e8400-e29b-41d4-a716-446655440000",
                "name": "普通用户",
                "code": "normal_user"
            }
        ]
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "用户不存在"
}
```

### 4. 更新用户信息

更新当前用户或有权限管理的用户信息。

- **URL**: `/api/platform/auth/users/{user_id}/`
- **方法**: `PUT`
- **权限要求**: 已认证用户（只能更新自己的信息，除非有管理权限）

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名          | 类型    | 必填 | 描述           |
|-----------------|---------|------|----------------|
| username        | string  | 是   | 用户名         |
| email           | string  | 是   | 邮箱地址       |
| first_name      | string  | 否   | 名             |
| last_name       | string  | 否   | 姓             |
| phone           | string  | 否   | 电话号码       |
| bio             | string  | 否   | 个人简介       |
| avatar          | file    | 否   | 头像文件       |

#### 请求示例

```json
{
    "username": "updateduser",
    "email": "updated@example.com",
    "first_name": "Updated",
    "last_name": "User",
    "phone": "13900139000",
    "bio": "更新后的个人简介"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "用户信息更新成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "updateduser",
        "email": "updated@example.com",
        "first_name": "Updated",
        "last_name": "User",
        "is_active": true,
        "phone": "13900139000",
        "email_verified": false,
        "phone_verified": false,
        "last_login": "2023-06-15T08:30:45Z",
        "date_joined": "2023-01-01T00:00:00Z",
        "bio": "更新后的个人简介",
        "avatar": "https://example.com/avatars/user1.jpg",
        "roles": [
            {
                "id": "650e8400-e29b-41d4-a716-446655440000",
                "name": "普通用户",
                "code": "normal_user"
            }
        ]
    }
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "用户不存在"
}
```

**失败响应 (403 Forbidden)**

```json
{
    "success": false,
    "message": "只能修改自己的信息"
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
    "message": "邮箱已被使用"
}
```

### 5. 部分更新用户信息

部分更新当前用户或有权限管理的用户信息。

- **URL**: `/api/platform/auth/users/{user_id}/`
- **方法**: `PATCH`
- **权限要求**: 已认证用户（只能更新自己的信息，除非有管理权限）

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

与更新用户信息接口相同，但所有字段均为可选。

#### 请求示例

```json
{
    "first_name": "Partially",
    "last_name": "Updated"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "用户信息更新成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "user1",
        "email": "user1@example.com",
        "first_name": "Partially",
        "last_name": "Updated",
        "is_active": true,
        "phone": "13800138000",
        "email_verified": true,
        "phone_verified": false,
        "last_login": "2023-06-15T08:30:45Z",
        "date_joined": "2023-01-01T00:00:00Z",
        "bio": "用户个人简介",
        "avatar": "https://example.com/avatars/user1.jpg",
        "roles": [
            {
                "id": "650e8400-e29b-41d4-a716-446655440000",
                "name": "普通用户",
                "code": "normal_user"
            }
        ]
    }
}
```

**失败响应与更新用户信息接口相同**

### 6. 修改密码

修改当前用户的密码。

- **URL**: `/api/platform/auth/users/{user_id}/change_password/`
- **方法**: `POST`
- **权限要求**: 已认证用户（只能修改自己的密码）

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名              | 类型   | 必填 | 描述     |
|---------------------|--------|------|----------|
| old_password        | string | 是   | 旧密码   |
| new_password        | string | 是   | 新密码   |
| new_password_confirm| string | 是   | 确认新密码 |

#### 请求示例

```json
{
    "old_password": "current_password",
    "new_password": "new_secure_password",
    "new_password_confirm": "new_secure_password"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "密码修改成功"
}
```

**失败响应 (403 Forbidden)**

```json
{
    "success": false,
    "message": "只能修改自己的密码"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "旧密码不正确"
}
```

```json
{
    "success": false,
    "message": "两次密码输入不一致"
}
```

### 7. 验证邮箱

验证用户的邮箱地址。

- **URL**: `/api/platform/auth/users/{user_id}/verify_email/`
- **方法**: `POST`
- **权限要求**: 已认证用户

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "邮箱验证成功"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "用户不存在"
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

1. 用户只能查看和修改自己的信息，除非拥有特殊权限
2. 更新邮箱地址会导致邮箱验证状态被重置为未验证
3. 密码修改需要提供正确的旧密码，并确保新密码符合系统的强度要求
4. 邮箱验证通常需要通过邮件中的验证链接完成，本API简化了这一流程 