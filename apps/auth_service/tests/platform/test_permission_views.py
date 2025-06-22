"""
平台API权限视图接口测试
"""

import os
import requests
import json
from datetime import datetime
import time

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
PLATFORM_PERMISSION_URL = f"{BASE_URL}/api/platform/auth/permissions"
PLATFORM_AUTH_URL = f"{BASE_URL}/api/platform/auth"

# 测试租户ID - 需要预先在系统中创建
TENANT_ID = os.getenv('TEST_TENANT_ID', 'ead1998d-bcfb-4e5f-82f5-fa9edd0f636c')

# 测试数据 - 租户管理员账号需要预先在系统中创建
TENANT_ADMIN_USER = {
    'username': os.getenv('TENANT_ADMIN_USERNAME', '2504504@qq.com'),
    'password': os.getenv('TENANT_ADMIN_PASSWORD', 'admin123')
}

# 存储测试过程中的数据
test_data = {
    'access_token': None,
    'refresh_token': None,
    'created_permission_id': None
}

# 生成时间戳，确保唯一性
timestamp = int(time.time())

# 测试权限数据
TEST_PERMISSION = {
    'name': f'测试权限_{timestamp}',
    'service': f'test_service_{timestamp}',
    'resource': f'test_resource_{timestamp}',
    'action': f'test_action_{timestamp}',
    'description': '这是一个测试权限',
    'is_system': False,
    'is_tenant_level': True
}

def print_response(response):
    """打印响应信息"""
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    # 尝试解析JSON响应
    try:
        json_data = response.json()
        print(f"响应内容: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError:
        print(f"响应内容(非JSON): {response.text}")

def test_tenant_admin_login():
    """测试租户管理员登录接口"""
    print("\n=== 测试租户管理员登录接口 ===")
    
    url = f"{PLATFORM_AUTH_URL}/login/"
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(TENANT_ADMIN_USER, indent=2, ensure_ascii=False)}")
    
    # 设置请求头，包含租户ID
    headers = {
        'X-Tenant-ID': TENANT_ID
    }
    print(f"请求头: {headers}")
    
    # 发送登录请求
    try:
        response = requests.post(url, json=TENANT_ADMIN_USER, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 租户管理员登录成功")
            # 尝试解析响应并保存令牌
            try:
                json_data = response.json()
                tokens = json_data.get('results', {}).get('tokens', {})
                test_data['access_token'] = tokens.get('access')
                test_data['refresh_token'] = tokens.get('refresh')
                print(f"访问令牌: {test_data['access_token'][:20]}..." if test_data['access_token'] else "访问令牌: None")
                print(f"刷新令牌: {test_data['refresh_token'][:20]}..." if test_data['refresh_token'] else "刷新令牌: None")
            except json.JSONDecodeError:
                print("⚠️ 无法解析响应JSON")
        else:
            print("❌ 租户管理员登录失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def clean_test_permissions():
    """清理测试权限数据"""
    print("\n=== 清理测试权限数据 ===")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法清理测试数据")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': TENANT_ID
    }
    
    # 获取权限列表
    try:
        response = requests.get(f"{PLATFORM_PERMISSION_URL}/", headers=headers)
        if response.status_code == 200:
            permissions = response.json().get('results', [])
            
            # 删除包含"test_service"的测试权限
            for permission in permissions:
                if 'test_service' in permission.get('service', ''):
                    permission_id = permission.get('id')
                    if permission_id:
                        delete_url = f"{PLATFORM_PERMISSION_URL}/{permission_id}/"
                        delete_response = requests.delete(delete_url, headers=headers)
                        if delete_response.status_code in [200, 204]:
                            print(f"✅ 已删除测试权限: {permission.get('name')} (ID: {permission_id})")
                        else:
                            print(f"❌ 删除测试权限失败: {permission.get('name')} (ID: {permission_id})")
            
            print("✅ 测试权限数据清理完成")
            return True
        else:
            print("❌ 获取权限列表失败，无法清理测试数据")
            return False
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_list_permissions():
    """测试获取权限列表"""
    print("\n=== 测试获取权限列表 ===")
    
    url = f"{PLATFORM_PERMISSION_URL}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': TENANT_ID
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.get(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 获取权限列表成功")
        else:
            print("❌ 获取权限列表失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_create_permission():
    """测试创建权限"""
    print("\n=== 测试创建权限 ===")
    
    url = f"{PLATFORM_PERMISSION_URL}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': TENANT_ID
    }
    print(f"请求头: {headers}")
    
    print(f"请求数据: {json.dumps(TEST_PERMISSION, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.post(url, json=TEST_PERMISSION, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 201:
            print("✅ 创建权限成功")
            # 保存创建的权限ID
            try:
                json_data = response.json()
                test_data['created_permission_id'] = json_data.get('results', {}).get('id')
                print(f"创建的权限ID: {test_data['created_permission_id']}")
            except json.JSONDecodeError:
                print("⚠️ 无法解析响应JSON")
        else:
            print("❌ 创建权限失败")
        
        return response.status_code == 201
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_retrieve_permission():
    """测试获取权限详情"""
    print("\n=== 测试获取权限详情 ===")
    
    # 检查是否有创建的权限ID
    if not test_data.get('created_permission_id'):
        print("❌ 没有创建的权限ID，无法测试")
        return False
    
    url = f"{PLATFORM_PERMISSION_URL}/{test_data['created_permission_id']}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': TENANT_ID
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.get(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 获取权限详情成功")
        else:
            print("❌ 获取权限详情失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_update_permission():
    """测试更新权限信息"""
    print("\n=== 测试更新权限信息 ===")
    
    # 检查是否有创建的权限ID
    if not test_data.get('created_permission_id'):
        print("❌ 没有创建的权限ID，无法测试")
        return False
    
    url = f"{PLATFORM_PERMISSION_URL}/{test_data['created_permission_id']}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': TENANT_ID
    }
    print(f"请求头: {headers}")
    
    # 更新数据
    update_data = {
        'name': f'更新的权限名称_{timestamp}',
        'description': '这是更新后的权限描述'
    }
    print(f"请求数据: {json.dumps(update_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.patch(url, json=update_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 更新权限信息成功")
        else:
            print("❌ 更新权限信息失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_delete_permission():
    """测试删除权限"""
    print("\n=== 测试删除权限 ===")
    
    # 检查是否有创建的权限ID
    if not test_data.get('created_permission_id'):
        print("❌ 没有创建的权限ID，无法测试")
        return False
    
    url = f"{PLATFORM_PERMISSION_URL}/{test_data['created_permission_id']}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': TENANT_ID
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.delete(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code in [200, 204]:
            print("✅ 删除权限成功")
        else:
            print("❌ 删除权限失败")
        
        return response.status_code in [200, 204]
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_filter_permissions():
    """测试按服务和资源过滤权限"""
    print("\n=== 测试按服务和资源过滤权限 ===")
    
    url = f"{PLATFORM_PERMISSION_URL}/?service={TEST_PERMISSION['service']}&resource={TEST_PERMISSION['resource']}"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': TENANT_ID
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.get(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 过滤权限列表成功")
        else:
            print("❌ 过滤权限列表失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始平台API权限视图测试 =====")
    print(f"API基础URL: {BASE_URL}")
    print(f"租户ID: {TENANT_ID}")
    print(f"租户管理员用户名: {TENANT_ADMIN_USER['username']}")
    
    # 测试租户管理员登录
    if not test_tenant_admin_login():
        print("⚠️ 租户管理员登录失败，跳过后续测试")
        return
    
    # 清理测试权限数据
    clean_test_permissions()
    
    # 测试获取权限列表
    test_list_permissions()
    
    # 测试按服务和资源过滤权限
    test_filter_permissions()
    
    # 测试创建权限
    if not test_create_permission():
        print("⚠️ 创建权限失败，跳过权限相关测试")
    else:
        # 测试获取权限详情
        test_retrieve_permission()
        
        # 测试更新权限信息
        test_update_permission()
        
        # 测试删除权限
        test_delete_permission()
    
    print("\n===== 平台API权限视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 