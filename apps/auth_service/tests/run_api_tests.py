"""
运行所有API测试
"""

import os
import sys
import argparse

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# 导入测试模块
from apps.auth_service.tests.platform.test_auth_views import run_tests as run_platform_auth_tests
from apps.auth_service.tests.management.test_auth_views import run_tests as run_management_auth_tests


def main():
    """主函数，解析命令行参数并运行测试"""
    parser = argparse.ArgumentParser(description='运行API测试')
    parser.add_argument('--platform', action='store_true', help='运行平台API测试')
    parser.add_argument('--management', action='store_true', help='运行管理API测试')
    parser.add_argument('--all', action='store_true', help='运行所有API测试')
    parser.add_argument('--base-url', type=str, help='API基础URL')
    parser.add_argument('--admin-username', type=str, help='管理员用户名')
    parser.add_argument('--admin-password', type=str, help='管理员密码')
    
    args = parser.parse_args()
    
    # 设置环境变量
    if args.base_url:
        os.environ['API_BASE_URL'] = args.base_url
    if args.admin_username:
        os.environ['ADMIN_USERNAME'] = args.admin_username
    if args.admin_password:
        os.environ['ADMIN_PASSWORD'] = args.admin_password
    
    # 运行测试
    if args.all or (not args.platform and not args.management):
        print("\n===== 运行所有API测试 =====")
        run_platform_auth_tests()
        run_management_auth_tests()
    else:
        if args.platform:
            run_platform_auth_tests()
        if args.management:
            run_management_auth_tests()


if __name__ == "__main__":
    main() 