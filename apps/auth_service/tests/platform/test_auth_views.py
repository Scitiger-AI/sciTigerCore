"""
平台API认证视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
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
    'refresh_token': None
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

def test_register():
    """测试用户注册接口"""
    print("\n=== 测试用户注册接口 ===")
    
    url = f"{PLATFORM_AUTH_URL}/register/"
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(TEST_USER, indent=2, ensure_ascii=False)}")
    
    # 添加租户ID到请求头
    headers = {
        'X-Tenant-ID': TENANT_ID
    }
    print(f"请求头: {headers}")
    
    # 发送注册请求
    try:
        response = requests.post(url, json=TEST_USER, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 201:
            print("✅ 用户注册成功")
            # 尝试解析响应并保存用户ID
            try:
                json_data = response.json()
                test_data['user_id'] = json_data.get('results', {}).get('user', {}).get('id')
                print(f"用户ID: {test_data['user_id']}")
            except json.JSONDecodeError:
                print("⚠️ 无法解析响应JSON")
        else:
            print("❌ 用户注册失败")
        
        return response.status_code == 201
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_login():
    """测试用户登录接口"""
    print("\n=== 测试用户登录接口 ===")
    
    url = f"{PLATFORM_AUTH_URL}/login/"
    print(f"请求URL: {url}")
    
    # 登录数据
    login_data = {
        'username': TEST_USER['username'],
        'password': TEST_USER['password']
    }
    print(f"请求数据: {json.dumps(login_data, indent=2, ensure_ascii=False)}")
    
    # 添加租户ID到请求头
    headers = {
        'X-Tenant-ID': TENANT_ID
    }
    print(f"请求头: {headers}")
    
    # 发送登录请求
    try:
        response = requests.post(url, json=login_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 用户登录成功")
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
            print("❌ 用户登录失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_refresh_token():
    """测试令牌刷新接口"""
    print("\n=== 测试令牌刷新接口 ===")
    
    url = f"{PLATFORM_AUTH_URL}/refresh-token/"
    print(f"请求URL: {url}")
    
    # 检查是否有刷新令牌
    if not test_data.get('refresh_token'):
        print("❌ 没有刷新令牌，无法测试")
        return False
    
    # 刷新令牌数据
    refresh_data = {
        'refresh': test_data['refresh_token']
    }
    print(f"请求数据: {json.dumps(refresh_data, indent=2, ensure_ascii=False)}")
    
    # 添加租户ID到请求头
    headers = {
        'X-Tenant-ID': TENANT_ID
    }
    print(f"请求头: {headers}")
    
    # 发送刷新令牌请求
    try:
        response = requests.post(url, json=refresh_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 令牌刷新成功")
            # 尝试解析响应并更新访问令牌
            try:
                json_data = response.json()
                tokens = json_data.get('results', {}).get('tokens', {})
                test_data['access_token'] = tokens.get('access')
                print(f"新访问令牌: {test_data['access_token'][:20]}...")
            except json.JSONDecodeError:
                print("⚠️ 无法解析响应JSON")
        else:
            print("❌ 令牌刷新失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始平台API认证视图测试 =====")
    print(f"API基础URL: {BASE_URL}")
    print(f"租户ID: {TENANT_ID}")
    
    # 测试注册
    if not test_register():
        print("⚠️ 注册失败，跳过后续测试")
        return
    
    # 测试登录
    if not test_login():
        print("⚠️ 登录失败，跳过后续测试")
        return
    
    # 测试令牌刷新
    test_refresh_token()
    
    print("\n===== 平台API认证视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 