# SciTigerCore(开发中....)

SciTigerCore 是一个基于 Django 和 Django REST Framework 的多租户后端系统，提供企业级 API 服务。

## 功能特点

- 多租户支持：完整的多租户数据隔离机制
- 统一认证：基于 JWT 的认证系统和 API 密钥管理
- 权限管理：细粒度的基于角色的权限控制
- 统一响应：标准化的 API 响应格式
- 日志记录：集中式日志管理和查询
- 通知中心：多渠道通知发送和管理
- 支付订单：支付处理和订阅管理

## 系统架构

系统采用三层架构设计：

1. **表现层**：视图和序列化器，处理 HTTP 请求和响应
2. **业务逻辑层**：服务类，封装核心业务逻辑
3. **数据访问层**：模型和查询管理器，处理数据存储和检索

## 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0+
- Redis 6.0+
- MongoDB 5.0+ (用于日志存储)

### 安装步骤

1. 克隆代码库

```bash
git clone https://github.com/yourusername/sciTigerCore.git
cd sciTigerCore
```

2. 创建并激活虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖

```bash
pip install -r requirements/dev.txt  # 开发环境
# 或
pip install -r requirements/prod.txt  # 生产环境
```

4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

5. 运行数据库迁移

```bash
python manage.py migrate
```

6. 创建超级用户

```bash
python manage.py createsuperuser
```

7. 运行开发服务器

```bash
python manage.py runserver
```

## API 文档

启动开发服务器后，可以通过以下地址访问 API 文档：

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
