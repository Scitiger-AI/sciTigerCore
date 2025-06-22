# SciTigerCore 架构设计

## 项目概述

SciTigerCore是一个基于Django的模块化单体架构，通过统一的API接口提供企业级应用的核心基础功能。实现了多租户支持、统一认证体系、通知管理、日志记录以及支付订单等基础功能模块。

## 整体架构

项目采用Django模块化单体架构，通过Django Apps进行功能划分，保持高内聚低耦合的设计原则。

### 技术栈

- **后端框架**：Django 5.0+ + Django REST Framework 3.14+
- **认证机制**：JWT (djangorestframework-simplejwt 5.3.0+)
- **跨域支持**：django-cors-headers 4.3.1+
- **过滤功能**：django-filter 23.5+
- **环境变量管理**：django-environ 0.11.2+
- **数据库**：Mysql
- **缓存与消息队列**：Redis + Celery + django-celery-results
- **日志存储**：MongoDB (通过pymongo)
- **支付集成**：python-alipay-sdk 3.3.0+
- **性能监控**：Prometheus + Grafana
- **APM工具**：Elastic APM / New Relic

## 系统组件

系统由以下核心服务模块组成：

### 1. 用户授权认证模块 (auth_service)

提供统一的用户认证和授权管理功能。

**核心模型**：
- `User`：用户模型，定义用户和个人资料
- `Permission`：权限模型，定义系统权限
- `Role`：角色模型，可关联多个权限
- `UserVerification`：用户验证（邮箱、手机、密码重置）
- `ApiKey`：API密钥管理
- `ApiKeyScope`：API密钥作用域，定义API密钥可访问的服务和操作
- `ApiKeyUsageLog`：API密钥使用日志，记录API密钥的使用情况
- `LoginAttempt`：登录尝试记录，用于安全审计和防暴力破解

**主要API**：
- 用户注册与登录
- JWT令牌管理（获取、刷新、验证）
- 用户资料管理
- 密码重置
- 权限与角色管理
- 双因素认证 (2FA) 支持
- API密钥管理与验证

**API密钥管理系统**：

1. **API密钥类型**：
   - 系统级API密钥 (System API Keys)：颁发给第三方应用系统，具有较高权限，可以访问API密钥管理接口，必须关联到特定租户（第三方应用）
   - 用户级API密钥 (User API Keys)：针对特定用户，权限范围受限，与特定用户和租户关联

2. **API密钥数据模型**：
   ```
   ApiKey
   ├── id: UUID
   ├── key_type: Enum(SYSTEM, USER)
   ├── key_hash: String
   ├── name: String
   ├── tenant_id: ForeignKey  // 系统级API密钥必须关联租户，用户级可选
   ├── user_id: ForeignKey(nullable)  // 仅用户级API密钥关联用户
   ├── created_by_key_id: ForeignKey(nullable) // 记录由哪个系统级Key创建
   ├── is_active: Boolean
   ├── created_at: DateTime
   ├── expires_at: DateTime
   ├── last_used_at: DateTime
   ├── metadata: JSONField
   └── application_name: String  // 系统级API密钥关联的第三方应用名称

   ApiKeyScope
   ├── api_key_id: ForeignKey
   ├── service: String  // 服务名称 (auth_service, tenant_service等)
   ├── resource: String // 资源类型 (users, roles等)
   └── action: String   // 操作类型 (read, write, delete等)

   ApiKeyUsageLog
   ├── api_key_id: ForeignKey
   ├── tenant_id: ForeignKey  // 关联租户，便于租户级审计
   ├── request_path: String
   ├── request_method: String
   ├── response_status: Integer
   ├── timestamp: DateTime
   ├── client_ip: String
   └── request_id: String
   ```

3. **API密钥认证流程**：
   - 系统级API密钥：第三方应用使用API密钥调用服务接口，系统验证密钥有效性、租户关联和权限范围。每个租户（第三方应用）有自己独立的系统级API密钥，只能访问该租户的资源。
   - 用户级API密钥：第三方应用使用系统级API密钥为其用户生成用户级API密钥，用户使用这些密钥调用其他微服务，微服务通过本系统验证密钥有效性

4. **API密钥与租户隔离**：
   - 系统级API密钥严格绑定到特定租户，只能访问该租户的资源
   - 租户管理员可管理其租户下的所有系统级API密钥
   - 平台超级管理员可管理所有租户的API密钥
   - 跨租户资源访问需要特殊授权，并通过审计日志记录

5. **API密钥权限管理**：
   - 服务级权限：控制对特定服务模块的访问
   - 资源级权限：控制对特定资源类型的操作
   - 操作级权限：控制可执行的操作类型

6. **API密钥安全措施**：
   - 密钥存储：仅存储哈希值，使用强哈希算法
   - 密钥传递：仅通过HTTPS传输，优先使用Authorization头
   - 滥用防护：实现请求速率限制，监控异常使用模式
   - 密钥轮换：强制系统级API密钥定期轮换，支持宽限期
   - 审计日志：记录所有密钥操作和重要使用事件

7. **API密钥管理接口**：
   - `/api/platform/api-keys/` - API密钥管理接口
   - `/api/platform/api-keys/verify` - API密钥验证接口
   - `/api/platform/api-keys/user-keys` - 用户级API密钥管理接口

### 2. 多租户支持模块 (tenant_service)

实现多租户数据隔离和租户管理功能。

**核心模型**：
- `Tenant`：租户模型，包含名称、子域名等基本信息
- `TenantUser`：租户用户关联，定义用户与租户的关系
- `TenantSettings`：租户配置，存储租户特定的设置和首选项
- `TenantQuota`：租户资源配额管理

**主要功能**：
- 租户创建与管理
- 租户用户管理（添加、移除用户，设置管理员权限）
- 通过中间件实现请求级别的租户识别和数据隔离
- 租户资源使用统计与限制
- 租户配置管理

### 3. 通知中心模块 (notification_service)

提供统一的通知管理和分发功能。

**核心模型**：
- `NotificationTemplate`：通知模板，支持不同类型和类别
- `Notification`：通知记录，包含发送状态和阅读状态
- `NotificationChannel`：通知渠道配置
- `UserNotificationPreference`：用户通知偏好设置
- `NotificationType`：通知类型定义，用于分类不同种类的通知

**主要功能**：
- 模板化通知管理
- 多渠道通知发送（邮件、短信、系统内通知、推送通知）
- 通知状态管理（已读/未读、删除）
- 通知频率控制
- 用户通知偏好设置
- 批量通知处理

**通知类型分类**：
1. **系统通知**：
   - 系统维护通知
   - 服务状态更新
   - 功能发布公告
   - 平台政策变更

2. **账户通知**：
   - 注册确认
   - 密码重置
   - 账户安全警告
   - 登录异常提醒

3. **业务通知**：
   - 任务分配与完成
   - 审批流程通知
   - 项目进度更新
   - 截止日期提醒

4. **交易通知**：
   - 支付确认
   - 订单状态变更
   - 退款处理
   - 订阅到期提醒

5. **协作通知**：
   - 评论与回复
   - 提及与引用
   - 共享与权限变更
   - 团队动态

6. **集成通知**：
   - 第三方系统事件
   - API调用状态
   - 集成服务警报
   - 外部触发事件

**通知优先级**：
- 紧急（需立即处理）
- 高（24小时内处理）
- 中（常规通知）
- 低（信息性通知）

**通知分发策略**：
- 基于用户角色的通知分发
- 基于通知类型和优先级的渠道选择
- 通知批量与实时发送决策
- 免打扰时段配置支持

### 4. 日志记录模块 (logger_service)

实现集中式日志管理功能。

**核心模型**：
- `LogEntry`：临时日志条目，实际数据存储在MongoDB
- `LogCategory`：日志分类定义
- `LogRetentionPolicy`：日志保留策略

**主要功能**：
- 日志提交（单条和批量）
- 日志查询与统计
- 租户级日志隔离
- 日志导出与归档
- 日志保留期限管理
- 审计日志支持

### 5. 支付订单模块 (billing_service)

管理支付、订单和订阅等功能。

**核心模型**：
- `Payment`：支付记录
- `Order`：订单信息
- `Subscription`：订阅记录
- `SubscriptionPlan`：订阅计划
- `UserPoints`：用户积分账户
- `PointsTransaction`：积分交易记录
- `Invoice`：发票记录
- `PaymentGatewayConfig`：支付网关配置

**主要功能**：
- 订单创建与管理
- 支付处理与状态跟踪
- 订阅计划管理
- 积分系统管理
- 发票生成与管理
- 多支付渠道支持（支付宝、微信支付等）
- 支付失败重试机制

## API设计

系统采用RESTful API设计，API路径例子如下：

1. **平台API**（面向终端用户）：
   - `/api/platform/auth/` - 认证服务API
   - `/api/platform/users/` - 用户服务API
   - `/api/platform/roles/` - 角色服务API
   - `/api/platform/permissions/` - 权限服务API
   - `/api/platform/api-keys/` - api-keys服务API
   - `/api/platform/tenants/` - 租户服务API
   - `/api/platform/payments/` - 支付订单服务API
   - `/api/platform/logs/` - 日志记录服务API
   - `/api/platform/notifications/` - 通知中心服务API

2. **管理API**（面向超级管理员）：
   - `/api/management/auth/` - 认证管理API
   - `/api/management/tenants/` - 租户管理API
   - `/api/management/payments/` - 支付管理API
   - `/api/management/logs/` - 日志管理API
   - `/api/management/notifications/` - 通知管理API

### 统一响应格式

为确保API响应的一致性和可预测性，系统采用统一的响应格式：

1. **成功响应格式**：
```json
{
    "success": true,
    "message": "操作成功描述（可选）",
    "results": {
        // 返回的数据内容
    }
}
```

2. **错误响应格式**：
```json
{
    "success": false,
    "message": "错误描述信息"
}
```

系统通过以下辅助方法实现统一响应：

```python
def get_success_response(self, data=None, message=None, status_code=status.HTTP_200_OK):
    """统一的成功响应格式"""
    return Response({
        'success': True,
        'message': message,
        'results': data
    }, status=status_code)

def get_error_response(self, message, status_code=status.HTTP_400_BAD_REQUEST):
    """统一的错误响应格式"""
    return Response({
        'success': False,
        'message': message
    }, status=status_code)
```

这种统一响应格式的优势：

1. **一致性**：所有API端点返回结构一致的响应
2. **明确性**：通过`success`字段明确表示操作成功或失败
3. **友好性**：提供清晰的消息说明操作结果
4. **可扩展性**：结构设计便于未来添加额外信息（如分页、元数据等）
5. **前端友好**：简化前端处理逻辑，提高开发效率

## 多租户实现

系统通过以下方式识别租户：

1. 请求头：`X-Tenant-ID`
2. 查询参数：`tenant_id`
3. 子域名：`<tenant_subdomain>.yourdomain.com`
4. JWT令牌中包含的租户信息

通过`TenantMiddleware`中间件在请求处理过程中识别和设置当前租户上下文，实现数据隔离和多租户支持。

### 数据隔离策略

系统采用共享数据库、独立表空间的隔离策略：
1. 每个租户相关的数据表都包含`tenant_id`字段
2. 通过租户上下文自动过滤查询，确保数据隔离
3. 提供租户级别的数据导出和备份功能

## 安全设计

1. **JWT认证**：采用现代化的JWT认证机制，支持令牌刷新
2. **细粒度权限控制**：基于角色的权限管理系统
3. **API密钥机制**：支持第三方应用访问API时的安全认证
4. **租户隔离**：数据按租户严格隔离，确保安全性
5. **安全审计**：关键操作日志记录与审计
6. **数据加密**：敏感数据字段加密存储
7. **CSRF防护**：防止跨站请求伪造攻击
8. **请求限流**：防止API滥用和DDoS攻击
9. **安全头部**：实现现代Web安全头部（X-XSS-Protection等）

## 性能优化

1. **缓存策略**：
   - 使用Redis进行应用级缓存
   - 对频繁访问的资源实施缓存机制
   - 实现缓存失效和更新策略

2. **数据库优化**：
   - 合理设计索引
   - 使用查询优化和批量操作
   - 实现数据分区策略，特别是对日志和历史数据

3. **异步处理**：
   - 使用Celery处理耗时操作
   - 实现任务优先级和队列管理
   - 批量处理机制减少系统负载

4. **资源限制**：
   - 对API请求实施速率限制
   - 按租户划分资源配额
   - 大型查询分页处理

## 扩展性考虑

1. **模块化设计**：各功能模块高内聚低耦合，可独立演进
2. **通用接口设计**：统一的API规范，便于集成和扩展
3. **可配置化**：通过配置和环境变量管理关键参数，减少代码修改
4. **异步任务支持**：通过Celery实现异步任务处理，提高系统响应能力
5. **插件机制**：支持通过插件扩展系统功能，无需修改核心代码
6. **前后端分离**：API设计支持多种前端实现

## 监控与可观测性

1. **健康检查**：
   - 提供API端点用于健康状态监控
   - 监控关键依赖服务可用性

2. **指标收集**：
   - 使用Prometheus收集性能指标
   - 监控请求延迟、错误率和资源使用情况

3. **日志聚合**：
   - 集中式日志收集与分析
   - 按租户和服务类型分类日志

4. **告警机制**：
   - 基于阈值的自动告警
   - 多渠道告警通知（邮件、短信、webhooks）

5. **APM集成**：
   - 应用性能监控工具集成
   - 请求追踪和性能瓶颈分析

## 部署策略

系统设计为单体部署模式，但内部模块保持独立性，便于未来可能的微服务拆分。推荐使用以下部署环境：

- **Web服务器**：Nginx + Gunicorn
- **数据库**：Mysql
- **缓存与消息队列**：Redis
- **日志存储**：MongoDB
- **容器化**：支持Docker和Kubernetes部署
- **CI/CD**：持续集成和部署管道

### 部署方案

1. **开发环境**：
   - Docker Compose本地开发环境
   - 自动化测试集成

2. **测试环境**：
   - 与生产环境相似的配置
   - 自动化部署和回滚

3. **生产环境**：
   - 高可用配置
   - 水平扩展能力
   - 蓝绿部署支持

## 数据备份与恢复

1. **备份策略**：
   - 数据库定时自动备份
   - 租户级数据备份选项
   - 增量和全量备份机制

2. **恢复流程**：
   - 明确的数据恢复流程
   - 时间点恢复能力
   - 恢复测试和验证机制

3. **灾难恢复**：
   - 跨区域备份策略
   - 灾难恢复计划和演练

## 技术债务管理

1. **代码质量管理**：
   - 静态代码分析集成
   - 代码覆盖率监控
   - 定期代码审查

2. **依赖管理**：
   - 定期更新依赖包
   - 安全漏洞监控
   - 依赖生命周期管理

3. **重构策略**：
   - 识别需要重构的区域
   - 增量重构计划
   - 技术债务跟踪和评估

## 项目代码架构

系统采用分散式组织方式，将API路由与视图放在各自的应用模块内部，以提高内聚性和模块独立性。

### 整体项目结构

```
sciTigerCore/
├── sciTigerCore/                    # 项目配置目录 (Django默认生成)
│   ├── __init__.py
│   ├── settings/                    # Django 设置
│   │   ├── __init__.py
│   │   ├── base.py                  # 基础配置
│   │   ├── development.py           # 开发环境配置
│   │   ├── production.py            # 生产环境配置
│   │   └── testing.py               # 测试环境配置
│   ├── urls.py                      # 主路由配置
│   ├── asgi.py                      # ASGI配置
│   ├── wsgi.py                      # WSGI配置
│   └── celery.py                    # Celery 配置
├── apps/                            # 应用模块
│   ├── auth_service/                # 认证服务
│   ├── tenant_service/              # 租户服务
│   ├── notification_service/        # 通知服务
│   ├── logger_service/              # 日志服务
│   └── billing_service/             # 支付服务
├── core/                            # 核心公共组件
│   ├── middleware/                  # 中间件组件
│   ├── permissions/                 # 权限组件
│   ├── utils/                       # 通用工具
│   ├── cache/                       # 缓存管理
│   ├── db/                          # 数据库工具
│   └── serializers/                 # 通用序列化器
├── tests/                           # 集成测试代码
├── docs/                            # 项目文档
├── scripts/                         # 实用脚本
├── manage.py                        # Django管理脚本
├── requirements/                    # 依赖管理
│   ├── base.txt                     # 基础依赖
│   ├── dev.txt                      # 开发依赖
│   └── prod.txt                     # 生产依赖
├── .env.example                     # 环境变量示例
├── docker-compose.yml               # Docker配置
├── Dockerfile                       # Docker构建文件
└── README.md                        # 项目说明
```

### 主URL配置设计

在主URL配置中统一注册各模块的路由，保持API结构的一致性：

```python
# sciTigerCore/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 平台API
    path('api/platform/auth/', include('apps.auth_service.urls.platform')),
    path('api/platform/tenants/', include('apps.tenant_service.urls.platform')),
    path('api/platform/notifications/', include('apps.notification_service.urls.platform')),
    path('api/platform/logs/', include('apps.logger_service.urls.platform')),
    path('api/platform/payments/', include('apps.billing_service.urls.platform')),
    
    # 管理API
    path('api/management/auth/', include('apps.auth_service.urls.management')),
    path('api/management/tenants/', include('apps.tenant_service.urls.management')),
    path('api/management/notifications/', include('apps.notification_service.urls.management')),
    path('api/management/logs/', include('apps.logger_service.urls.management')),
    path('api/management/payments/', include('apps.billing_service.urls.management')),
]
```

### 应用模块内部结构

每个功能模块（Django应用）内部结构如下，以auth_service为例：

```
apps/auth_service/
├── __init__.py
├── apps.py                          # 应用配置
├── models/                          # 数据模型
│   ├── __init__.py
│   ├── user.py                      # 用户模型
│   ├── role.py                      # 角色模型
│   ├── permission.py                # 权限模型
│   ├── api_key.py                   # API密钥模型
│   └── verification.py              # 验证模型
├── serializers/                     # 序列化器
│   ├── __init__.py
│   ├── user_serializers.py
│   ├── role_serializers.py
│   ├── permission_serializers.py
│   └── api_key_serializers.py
├── views/                           # 视图
│   ├── __init__.py
│   ├── platform/                    # 平台API视图
│   │   ├── __init__.py
│   │   ├── user_views.py
│   │   ├── role_views.py
│   │   ├── permission_views.py
│   │   └── api_key_views.py
│   └── management/                  # 管理API视图
│       ├── __init__.py
│       ├── user_views.py
│       ├── role_views.py
│       └── api_key_views.py
├── urls/                            # 路由配置
│   ├── __init__.py
│   ├── platform.py                  # 平台API路由
│   └── management.py                # 管理API路由
├── services/                        # 业务逻辑
│   ├── __init__.py
│   ├── auth_service.py              # 认证服务
│   ├── user_service.py              # 用户服务
│   ├── role_service.py              # 角色服务
│   └── api_key_service.py           # API密钥服务
├── permissions/                     # 自定义权限
│   ├── __init__.py
│   └── custom_permissions.py
├── tests/                           # 单元测试
│   ├── __init__.py
│   ├── test_user.py
│   ├── test_role.py
│   └── test_api_key.py
├── admin.py                         # 管理界面配置
└── migrations/                      # 数据库迁移
```

### 业务逻辑设计

系统采用三层架构设计：

1. **表现层**：视图和序列化器，处理HTTP请求和响应
2. **业务逻辑层**：服务类，封装核心业务逻辑
3. **数据访问层**：模型和查询管理器，处理数据存储和检索

服务类示例：

```python
# apps/auth_service/services/api_key_service.py
class ApiKeyService:
    @staticmethod
    def generate_system_api_key(tenant, name, application_name, scopes):
        """生成系统级API密钥"""
        # 实现密钥生成逻辑
        pass
        
    @staticmethod
    def generate_user_api_key(tenant, user, name, scopes):
        """生成用户级API密钥"""
        # 实现密钥生成逻辑
        pass
        
    @staticmethod
    def verify_api_key(key_value):
        """验证API密钥的有效性和权限"""
        # 实现密钥验证逻辑
        pass
```

### 分散式组织的优势

1. **高内聚**：每个应用模块包含其完整功能，符合Django的应用设计理念
2. **模块独立性**：各模块可以独立开发、测试和演进
3. **代码就近原则**：相关代码放在一起，易于理解和维护
4. **可重用性**：模块可以更容易地在不同项目间复用
5. **团队协作**：不同团队可以专注于不同功能模块，减少代码冲突

### API实现策略

系统采用**视图分离+服务层共享**的API实现策略，这是企业级应用的最佳实践。

#### 视图分离原则

1. **平台API和管理API使用不同的视图类**：
   - 平台API视图位于 `views/platform/` 目录
   - 管理API视图位于 `views/management/` 目录
   - 两者针对不同的用户群体和使用场景设计

2. **视图职责明确**：
   - 视图层负责请求处理、权限验证和响应格式化
   - 平台视图实现针对终端用户的功能和权限控制
   - 管理视图实现针对管理员的高级功能和全局管理能力

3. **序列化器差异化**：
   - 为不同API提供专用序列化器或序列化器配置
   - 平台API序列化器可能隐藏敏感字段或管理字段
   - 管理API序列化器提供更完整的数据视图和管理选项

#### 服务层共享机制

1. **业务逻辑封装在服务层**：
   - 核心业务规则和数据处理逻辑位于服务类中
   - 服务类方法设计为可重用的功能单元
   - 支持不同视图的调用需求

2. **服务方法参数化**：
   - 服务方法通过参数控制行为变化
   - 支持权限级别、数据范围等差异化需求
   - 避免在服务层硬编码视图特定的逻辑

3. **上下文传递机制**：
   - 视图将请求上下文（用户、租户、权限等）传递给服务层
   - 服务层根据上下文调整处理逻辑和数据访问范围
   - 确保数据安全性和租户隔离

#### 实现示例

**用户管理功能**的实现示例：

1. **服务层实现**：

```python
# apps/auth_service/services/user_service.py
class UserService:
    @staticmethod
    def get_users(tenant_id=None, user_id=None, include_inactive=False, **filters):
        """
        获取用户列表
        
        参数:
            tenant_id: 租户ID，None表示所有租户
            user_id: 用户ID，None表示所有用户
            include_inactive: 是否包含非活跃用户
            filters: 其他过滤条件
        """
        queryset = User.objects.all()
        
        # 租户过滤
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
            
        # 用户ID过滤
        if user_id:
            queryset = queryset.filter(id=user_id)
            
        # 活跃状态过滤
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
            
        # 应用其他过滤条件
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    @staticmethod
    def create_user(tenant_id, email, password, **user_data):
        """创建用户"""
        # 实现用户创建逻辑
        pass
    
    @staticmethod
    def update_user(user_id, **update_data):
        """更新用户"""
        # 实现用户更新逻辑
        pass
    
    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        # 实现用户删除逻辑
        pass
```

2. **平台API视图实现**：

```python
# apps/auth_service/views/platform/user_views.py
from apps.auth_service.services.user_service import UserService

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 平台API只能访问当前租户的用户
        return UserService.get_users(
            tenant_id=self.request.tenant.id,
            # 可能还有其他过滤条件
        )
    
    def perform_create(self, serializer):
        # 调用服务层创建用户
        user_data = serializer.validated_data
        user = UserService.create_user(
            tenant_id=self.request.tenant.id,
            **user_data
        )
        return user
```

3. **管理API视图实现**：

```python
# apps/auth_service/views/management/user_views.py
from apps.auth_service.services.user_service import UserService

class UserManagementViewSet(viewsets.ModelViewSet):
    serializer_class = UserManagementSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        # 超级管理员可以查看所有租户的用户
        if self.request.user.is_superadmin:
            return UserService.get_users(
                include_inactive=True  # 管理视图可以看到非活跃用户
            )
        # 租户管理员只能查看自己租户的用户
        return UserService.get_users(
            tenant_id=self.request.tenant.id,
            include_inactive=True
        )
    
    def get_serializer_class(self):
        # 可以根据操作类型返回不同的序列化器
        if self.action == 'list':
            return UserListManagementSerializer
        return UserDetailManagementSerializer
```

#### 视图分离+服务层共享的优势

1. **代码复用与职责分离平衡**：
   - 避免业务逻辑重复实现
   - 保持视图层的清晰职责划分
   - 简化测试和维护

2. **安全性增强**：
   - 视图层实施严格的权限控制
   - 服务层实施一致的业务规则
   - 双层防护减少安全漏洞风险

3. **灵活性与可扩展性**：
   - 可以独立扩展平台API或管理API功能
   - 服务层可以支持新的API类型或接入点
   - 便于实现API版本控制

4. **一致性保证**：
   - 核心业务逻辑在服务层统一实现
   - 确保不同API入口的行为一致性
   - 减少业务规则分散导致的不一致

5. **团队协作优化**：
   - 前端团队可以专注于视图层
   - 后端团队可以专注于服务层
   - 明确的接口约定减少沟通成本

### 模块内URL配置示例

每个功能模块内部将路由分为平台API和管理API两部分：

```python
# apps/auth_service/urls/platform.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.auth_service.views.platform import user_views, role_views, api_key_views

router = DefaultRouter()
router.register(r'users', user_views.UserViewSet)
router.register(r'roles', role_views.RoleViewSet)
router.register(r'permissions', role_views.PermissionViewSet)
router.register(r'api-keys', api_key_views.ApiKeyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', user_views.LoginView.as_view()),
    path('refresh-token/', user_views.TokenRefreshView.as_view()),
    path('register/', user_views.RegisterView.as_view()),
    path('verify-api-key/', api_key_views.VerifyApiKeyView.as_view()),
]
```

### 业务逻辑设计

// ... existing code ...

# SciTigerCore 实现计划


## 第一阶段：基础架构与核心服务

### 1. 项目骨架搭建
- 创建项目目录结构
- 配置 Django 基础设置
- 配置数据库连接（MySQL）
- 实现环境变量管理

### 2. 核心公共中间件和多租户支持模块
- 实现多租户所需模型
- 开发核心公共中间件，如租户中间件（TenantMiddleware）
- 实现租户识别机制（请求头、查询参数、子域名、JWT）
- 开发租户数据隔离策略
- 创建基础租户管理 API

### 3. 核心工具类和辅助功能
- 实现统一响应格式
- 开发通用异常处理机制
- 创建基础工具类（加密、验证等）
- 实现基础中间件（请求ID、日志等）
- 配置 CORS 支持

### 4. 用户授权认证模块
- 实现用户模型和基本认证机制
- 集成 JWT 认证（djangorestframework-simplejwt）
- 开发角色和权限系统
- 实现基本的用户管理 API
- 开发登录、注册、令牌刷新等基础功能


## 第二阶段：扩展功能模块

### 5. API密钥管理系统
- 实现 `ApiKey` 和 `ApiKeyScope` 模型
- 开发系统级和用户级 API 密钥生成机制
- 实现 API 密钥认证中间件
- 开发 API 密钥验证接口


### 6. 日志记录模块
- 配置 MongoDB 连接
- 实现 `LogEntry` 模型和日志分类
- 开发日志记录服务
- 创建日志查询 API
- 实现租户级日志隔离

### 7. 通知中心模块
- 实现通知相关模型
- 开发通知模板系统
- 实现基础通知渠道（邮件、系统内通知）
- 创建通知管理 API
- 开发通知状态管理功能

## 第三阶段：高级功能与集成

### 8. 支付订单模块
- 实现订单和支付相关模型
- 集成支付宝支付（python-alipay-sdk）
- 开发订阅计划管理
- 实现发票生成功能
- 创建支付管理 API

### 9. 异步任务处理
- 配置 Redis 和 Celery
- 实现异步任务队列
- 开发定时任务管理
- 将耗时操作迁移到异步任务
- 实现任务状态监控

### 10. 高级安全功能
- 实现双因素认证（2FA）
- 开发请求限流机制
- 实现敏感数据加密存储
- 配置安全相关中间件
- 完善 CSRF 和 XSS 防护

## 第四阶段：优化与部署

### 11. 性能优化
- 实现 Redis 缓存策略
- 优化数据库查询
- 实现批量处理机制
- 开发资源配额管理
- 优化大型查询的分页处理

### 12. 监控与可观测性
- 集成 Prometheus 和 Grafana
- 实现健康检查端点
- 配置日志聚合
- 设置告警机制
- 集成 APM 工具

### 13. 部署配置
- 完善 Docker 和 Kubernetes 配置
- 设置 CI/CD 管道
- 配置生产环境设置
- 实现数据备份策略
- 准备部署文档

## 第五阶段：测试与文档

### 14. 全面测试
- 编写单元测试
- 开发集成测试
- 执行性能测试
- 进行安全测试
- 实施用户验收测试

### 15. 文档完善
- 创建 API 文档
- 编写开发者指南
- 准备用户手册
- 完善部署文档
- 创建系统架构图

## 优先级考虑因素

在实施过程中，考虑以下因素来确定优先级：

1. **基础依赖关系**：先实现其他模块依赖的核心功能
2. **业务价值**：优先实现对用户最有价值的功能
3. **技术风险**：先解决高风险的技术挑战
4. **开发效率**：按照从简单到复杂的顺序安排任务
5. **资源利用**：考虑团队技能和资源分配

## 关键里程碑

1. **基础平台可用**（第一阶段结束）：
   - 多租户系统可运行
   - 用户可以注册、登录
   - 基本权限系统工作

2. **核心功能完成**（第二阶段结束）：
   - API 密钥系统可用
   - 日志记录功能完善
   - 通知系统可用

3. **功能完整系统**（第三阶段结束）：
   - 所有计划功能模块实现
   - 异步处理机制工作
   - 安全机制完善

4. **生产就绪系统**（第四阶段结束）：
   - 性能优化完成
   - 监控系统就位
   - 部署配置完善

5. **正式发布**（第五阶段结束）：
   - 全面测试通过
   - 文档完善
   - 系统可交付使用

## 并行开发建议

为提高开发效率，以下任务可考虑并行开发：

1. 基础架构搭建与数据库设计可同时进行
2. 多租户模块和认证模块可部分并行开发
3. API密钥系统与日志记录模块可并行实现
4. 前端界面开发可在后端API实现后立即开始
5. 文档编写可以与各阶段开发同步进行

## 风险管理

1. **技术风险**：
   - 多租户数据隔离的复杂性
   - API密钥安全性保障
   - 异步任务可靠性

2. **时间风险**：
   - 认证模块可能需要更多时间
   - 支付集成可能面临第三方依赖问题
   - 性能优化可能发现意外问题

3. **缓解策略**：
   - 为高风险模块预留缓冲时间
   - 实施持续集成和自动化测试
   - 定期技术评审和风险评估

