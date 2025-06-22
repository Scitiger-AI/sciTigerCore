# 管理用户API文档

本文档描述了SciTigerCore平台的管理用户API，这些API专为系统管理员设计，提供用户的增删改查、状态管理等功能。

## API基础信息

- **基础路径**: `/api/management/auth/users/`
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
        "next": "http://example.com/api/management/auth/users/?page=2",
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

### 1. 获取用户列表

获取系统中的用户列表。

- **URL**: `/api/management/auth/users/`
- **方法**: `GET`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 查询参数

| 参数名          | 类型    | 必填 | 描述           |
|-----------------|---------|----- |----------------|
| username        | string  | 否   | 按用户名过滤    |
| email           | string  | 否   | 按邮箱地址过滤  |
| is_active       | boolean | 否   | 按状态过滤      |
| role            | string  | 否   | 按角色名称过滤  |
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
        "total": 25,
        "page_size": 10,
        "current_page": 1,
        "total_pages": 3,
        "next": "http://example.com/api/management/auth/users/?page=2",
        "previous": null,
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
}
```

### 2. 获取当前管理员信息

获取当前登录管理员的详细信息。

- **URL**: `/api/management/auth/users/userInfo/`
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
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "is_active": true,
        "phone": "13800138000",
        "email_verified": true,
        "phone_verified": false,
        "last_login": "2023-06-15T08:30:45Z",
        "date_joined": "2023-01-01T00:00:00Z",
        "bio": "管理员个人简介",
        "avatar": "https://example.com/avatars/admin.jpg",
        "roles": [
            {
                "id": "650e8400-e29b-41d4-a716-446655440002",
                "name": "系统管理员",
                "code": "system_admin"
            }
        ]
    }
}
```

### 3. 获取用户详情

获取特定用户的详细信息。

- **URL**: `/api/management/auth/users/{user_id}/`
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

### 4. 创建用户

创建新用户。

- **URL**: `/api/management/auth/users/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名          | 类型    | 必填 | 描述           |
|-----------------|---------|------|----------------|
| username        | string  | 是   | 用户名         |
| email           | string  | 是   | 邮箱地址       |
| password        | string  | 是   | 密码           |
| password_confirm| string  | 是   | 确认密码       |
| first_name      | string  | 否   | 名             |
| last_name       | string  | 否   | 姓             |
| phone           | string  | 否   | 电话号码       |
| is_active       | boolean | 否   | 是否激活       |
| bio             | string  | 否   | 个人简介       |
| avatar          | file    | 否   | 头像文件       |
| roles           | array   | 否   | 角色ID列表     |

#### 请求示例

```json
{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "secure_password",
    "password_confirm": "secure_password",
    "first_name": "New",
    "last_name": "User",
    "phone": "13800138000",
    "is_active": true,
    "bio": "新用户个人简介",
    "roles": ["650e8400-e29b-41d4-a716-446655440000"]
}
```

#### 响应示例

**成功响应 (201 Created)**

```json
{
    "success": true,
    "message": "用户创建成功",
    "results": {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "username": "newuser",
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "is_active": true,
        "phone": "13800138000",
        "email_verified": false,
        "phone_verified": false,
        "last_login": null,
        "date_joined": "2023-06-20T12:00:00Z",
        "bio": "新用户个人简介",
        "avatar": null,
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

### 5. 更新用户信息

更新特定用户的信息。

- **URL**: `/api/management/auth/users/{user_id}/`
- **方法**: `PUT`
- **权限要求**: 管理员权限

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
| is_active       | boolean | 否   | 是否激活       |
| bio             | string  | 否   | 个人简介       |
| avatar          | file    | 否   | 头像文件       |
| roles           | array   | 否   | 角色ID列表     |

#### 请求示例

```json
{
    "username": "updateduser",
    "email": "updated@example.com",
    "first_name": "Updated",
    "last_name": "User",
    "phone": "13900139000",
    "is_active": true,
    "bio": "更新后的个人简介",
    "roles": ["650e8400-e29b-41d4-a716-446655440000", "650e8400-e29b-41d4-a716-446655440001"]
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
            },
            {
                "id": "650e8400-e29b-41d4-a716-446655440001",
                "name": "高级用户",
                "code": "advanced_user"
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

### 6. 部分更新用户信息

部分更新特定用户的信息。

- **URL**: `/api/management/auth/users/{user_id}/`
- **方法**: `PATCH`
- **权限要求**: 管理员权限

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

### 7. 删除用户

删除特定用户。

- **URL**: `/api/management/auth/users/{user_id}/`
- **方法**: `DELETE`
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
    "message": "用户删除成功"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "用户删除失败，可能是用户不存在"
}
```

### 8. 激活用户

激活特定用户。

- **URL**: `/api/management/auth/users/{user_id}/activate/`
- **方法**: `POST`
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
    "message": "用户已激活"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "用户不存在"
}
```

### 9. 禁用用户

禁用特定用户。

- **URL**: `/api/management/auth/users/{user_id}/deactivate/`
- **方法**: `POST`
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
    "message": "用户已禁用"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "用户不存在"
}
```

### 10. 验证用户邮箱

将特定用户的邮箱标记为已验证。

- **URL**: `/api/management/auth/users/{user_id}/verify_email/`
- **方法**: `POST`
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
    "message": "用户邮箱已验证"
}
```

**失败响应 (404 Not Found)**

```json
{
    "success": false,
    "message": "用户不存在"
}
```

### 11. 重置用户密码

重置特定用户的密码。

- **URL**: `/api/management/auth/users/{user_id}/reset_password/`
- **方法**: `POST`
- **权限要求**: 管理员权限

#### 请求头

| 参数名          | 描述                            |
|-----------------|---------------------------------|
| Authorization   | Bearer {access_token}           |

#### 请求参数

| 参数名      | 类型   | 必填 | 描述     |
|-------------|--------|------|----------|
| new_password| string | 是   | 新密码   |

#### 请求示例

```json
{
    "new_password": "new_secure_password"
}
```

#### 响应示例

**成功响应 (200 OK)**

```json
{
    "success": true,
    "message": "用户密码已重置"
}
```

**失败响应 (400 Bad Request)**

```json
{
    "success": false,
    "message": "必须提供新密码"
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
| 404    | 资源不存在                           |
| 500    | 服务器内部错误                       |

## 注意事项

1. 所有接口都需要管理员权限，非管理员用户无法访问
2. 超级管理员可以查看和管理所有租户的用户，普通管理员只能管理自己租户的用户
3. 更新用户邮箱时，邮箱验证状态会被重置为未验证
4. 创建或更新用户时，如果指定的角色不存在，将返回错误
5. 删除用户操作不可逆，请谨慎使用 