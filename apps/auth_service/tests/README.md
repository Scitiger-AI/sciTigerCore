# 认证服务接口测试

本目录包含用于测试认证服务接口的脚本。这些测试脚本使用 `requests` 库模拟真实的 HTTP 请求，用于验证 API 接口的功能是否正常。

## 测试内容

测试分为两部分：

1. **平台 API 测试**：测试面向终端用户的认证接口
   - 用户注册
   - 用户登录
   - 令牌刷新

2. **管理 API 测试**：测试面向管理员的认证接口
   - 管理员登录
   - 管理员令牌刷新
   - 管理员个人资料获取

## 运行测试

### 安装依赖

确保已安装 `requests` 库：

```bash
pip install requests
```

### 运行所有测试

```bash
python apps/auth_service/tests/run_api_tests.py --all
```

### 仅运行平台 API 测试

```bash
python apps/auth_service/tests/run_api_tests.py --platform
```

### 仅运行管理 API 测试

```bash
python apps/auth_service/tests/run_api_tests.py --management
```

### 指定 API 基础 URL

默认情况下，测试脚本会使用 `http://localhost:8000` 作为 API 基础 URL。如果需要指定其他 URL，可以使用 `--base-url` 参数：

```bash
python apps/auth_service/tests/run_api_tests.py --all --base-url http://example.com
```

### 指定管理员账号

对于管理 API 测试，需要提供有效的管理员账号。可以使用 `--admin-username` 和 `--admin-password` 参数：

```bash
python apps/auth_service/tests/run_api_tests.py --management --admin-username admin --admin-password admin123
```

## 注意事项

1. 在运行测试前，确保 API 服务已启动并正常运行。
2. 管理 API 测试需要提供有效的管理员账号，否则会登录失败。
3. 平台 API 测试会创建新的测试用户，每次运行会生成不同的用户名和邮箱。
4. 测试脚本会输出详细的请求和响应信息，便于调试。 