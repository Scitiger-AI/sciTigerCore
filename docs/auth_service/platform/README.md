# 平台API租户识别机制说明

## 租户识别概述

SciTigerCore平台API采用多租户架构，所有平台API（`/api/platform/`路径下的接口）都需要识别当前租户上下文。系统通过多种方式识别请求的租户，确保数据隔离和安全访问。

## 租户识别方法

系统按照以下优先级顺序识别租户：

1. **请求头**: `X-Tenant-ID` 头部
2. **查询参数**: URL中的 `tenant_id` 参数
3. **子域名**: 通过子域名识别租户（如 `tenant-name.yourdomain.com`）
4. **JWT令牌**: 令牌中包含的租户信息
5. **API密钥**: API密钥关联的租户

## 如何在请求中传递租户ID

### 1. 使用请求头（推荐方式）

在HTTP请求头中添加 `X-Tenant-ID` 字段：

```
X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000
```

### 2. 使用查询参数

在URL中添加 `tenant_id` 参数：

```
/api/platform/auth/users/?tenant_id=550e8400-e29b-41d4-a716-446655440000
```

### 3. 使用子域名

通过特定子域名访问API：

```
https://tenant-name.yourdomain.com/api/platform/auth/users/
```

### 4. 通过JWT令牌（自动处理）

登录成功后，系统返回的JWT令牌中已包含租户信息，使用该令牌进行认证时会自动识别租户。

### 5. 通过API密钥（自动处理）

使用API密钥进行认证时，系统会自动使用该API密钥关联的租户。

## 租户识别例外

以下接口不需要租户识别：

- `/api/platform/auth/login/` - 登录接口
- `/api/platform/auth/register/` - 注册接口
- `/api/platform/auth/refresh-token/` - 令牌刷新接口
- `/api/platform/auth/verify-api-key/` - API密钥验证接口

## 错误处理

如果平台API请求中未能识别有效的租户，系统将返回403 Forbidden错误：

```json
{
    "success": false,
    "message": "Tenant ID is required"
}
```

如果提供了无效的租户ID，系统也会返回403 Forbidden错误：

```json
{
    "success": false,
    "message": "Invalid tenant"
}
```

## 认证方式

SciTigerCore平台支持两种认证方式：

### 1. JWT令牌认证

JWT令牌认证是主要的认证方式，适用于用户交互场景。详细信息请参考[平台认证API文档](./auth_api.md)。

### 2. API密钥认证

API密钥认证适用于服务器间通信、自动化脚本、第三方集成等场景。系统支持系统级和用户级两种API密钥。详细信息请参考[API密钥认证文档](./api_key_auth.md)。

### 认证方式选择

- **用户交互场景**: 使用JWT令牌认证
- **服务器间通信**: 使用系统级API密钥认证
- **第三方应用集成**: 使用用户级API密钥认证

## 文档索引

- [平台认证API文档](./auth_api.md) - JWT认证、用户登录、注册等接口
- [平台用户API文档](./user_api.md) - 用户信息管理接口
- [API密钥认证文档](./api_key_auth.md) - API密钥创建、管理和使用 