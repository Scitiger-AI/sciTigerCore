"""
平台API租户配额视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
PLATFORM_TENANT_QUOTA_URL = f"{BASE_URL}/api/platform/tenants/tenant-quotas"
PLATFORM_AUTH_URL = f"{BASE_URL}/api/platform/auth"

# 租户ID - 请替换为实际的租户ID
TENANT_ID = os.getenv('TENANT_ID', '376f9753-c6dd-4ccb-8e9e-0ba920054349')

# 测试数据
TEST_USER = {
    'username': f'testuser_{int(datetime.now().timestamp())}',
    'email': f'test_{int(datetime.now().timestamp())}@example.com',
    'password': 'Test@123456',
    'password_confirm': 'Test@123456',
    'first_name': 'Test',
    'last_name': 'User'
}

# 存储测试过程中的数据
test_data = {
    'user_id': None,
    'access_token': None,
    'refresh_token': None,
    'tenant_id': TENANT_ID
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

def test_register_and_login():
    """测试用户注册和登录"""
    print("\n=== 测试用户注册和登录 ===")
    
    # 注册用户
    register_url = f"{PLATFORM_AUTH_URL}/register/"
    print(f"请求URL: {register_url}")
    print(f"请求数据: {json.dumps(TEST_USER, indent=2, ensure_ascii=False)}")
    
    headers = {
        'X-Tenant-ID': TENANT_ID
    }
    
    try:
        response = requests.post(register_url, json=TEST_USER, headers=headers)
        print_response(response)
        
        if response.status_code == 201:
            print("✅ 用户注册成功")
            json_data = response.json()
            test_data['user_id'] = json_data.get('results', {}).get('user', {}).get('id')
        else:
            print("❌ 用户注册失败")
            return False
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    
    # 登录用户
    login_url = f"{PLATFORM_AUTH_URL}/login/"
    print(f"请求URL: {login_url}")
    
    login_data = {
        'username': TEST_USER['username'],
        'password': TEST_USER['password']
    }
    
    try:
        response = requests.post(login_url, json=login_data, headers=headers)
        print_response(response)
        
        if response.status_code == 200:
            print("✅ 用户登录成功")
            json_data = response.json()
            tokens = json_data.get('results', {}).get('tokens', {})
            test_data['access_token'] = tokens.get('access')
            test_data['refresh_token'] = tokens.get('refresh')
            return True
        else:
            print("❌ 用户登录失败")
            return False
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_retrieve_quota():
    """测试获取当前租户的配额"""
    print("\n=== 测试获取当前租户的配额 ===")
    
    url = f"{PLATFORM_TENANT_QUOTA_URL}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': test_data['tenant_id']
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.get(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 获取租户配额成功")
        else:
            print("❌ 获取租户配额失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_check_user_quota():
    """测试检查用户配额"""
    print("\n=== 测试检查用户配额 ===")
    
    url = f"{PLATFORM_TENANT_QUOTA_URL}/check_user_quota/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': test_data['tenant_id']
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.get(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 检查用户配额成功")
        else:
            print("❌ 检查用户配额失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_check_storage_quota():
    """测试检查存储配额"""
    print("\n=== 测试检查存储配额 ===")
    
    url = f"{PLATFORM_TENANT_QUOTA_URL}/check_storage_quota/?required_space=1024"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': test_data['tenant_id']
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.get(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 检查存储配额成功")
        else:
            print("❌ 检查存储配额失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_check_project_quota():
    """测试检查项目配额"""
    print("\n=== 测试检查项目配额 ===")
    
    url = f"{PLATFORM_TENANT_QUOTA_URL}/check_project_quota/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': test_data['tenant_id']
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.get(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 检查项目配额成功")
        else:
            print("❌ 检查项目配额失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_check_api_call_quota():
    """测试检查API调用配额"""
    print("\n=== 测试检查API调用配额 ===")
    
    url = f"{PLATFORM_TENANT_QUOTA_URL}/check_api_call_quota/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}",
        'X-Tenant-ID': test_data['tenant_id']
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.get(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 检查API调用配额成功")
        else:
            print("❌ 检查API调用配额失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始平台API租户配额视图测试 =====")
    print(f"API基础URL: {BASE_URL}")
    print(f"租户ID: {TENANT_ID}")
    
    # 测试注册和登录
    if not test_register_and_login():
        print("⚠️ 用户注册或登录失败，跳过后续测试")
        return
    
    # 测试获取租户配额
    test_retrieve_quota()
    
    # 测试检查用户配额
    test_check_user_quota()
    
    # 测试检查存储配额
    test_check_storage_quota()
    
    # 测试检查项目配额
    test_check_project_quota()
    
    # 测试检查API调用配额
    test_check_api_call_quota()
    
    print("\n===== 平台API租户配额视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 