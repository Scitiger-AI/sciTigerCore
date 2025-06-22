"""
平台API用户视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
PLATFORM_USER_URL = f"{BASE_URL}/api/platform/auth/users"
PLATFORM_AUTH_URL = f"{BASE_URL}/api/platform/auth"

# 租户ID - 使用有效的租户ID
TENANT_ID = os.getenv('TENANT_ID', '855691a9-81a5-408f-beaf-ff91421437e1')

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
    
    # 登录数据 - 使用邮箱而不是用户名
    login_data = {
        'username': TEST_USER['email'],  # 使用邮箱作为登录标识符
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

def test_list_users():
    """测试获取用户列表"""
    print("\n=== 测试获取用户列表 ===")
    
    url = f"{PLATFORM_USER_URL}/"
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
            print("✅ 获取用户列表成功")
        else:
            print("❌ 获取用户列表失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_retrieve_user():
    """测试获取用户详情"""
    print("\n=== 测试获取用户详情 ===")
    
    # 检查是否有用户ID
    if not test_data.get('user_id'):
        print("❌ 没有用户ID，无法测试")
        return False
    
    url = f"{PLATFORM_USER_URL}/{test_data['user_id']}/"
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
            print("✅ 获取用户详情成功")
        else:
            print("❌ 获取用户详情失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_update_user():
    """测试更新用户信息"""
    print("\n=== 测试更新用户信息 ===")
    
    # 检查是否有用户ID
    if not test_data.get('user_id'):
        print("❌ 没有用户ID，无法测试")
        return False
    
    url = f"{PLATFORM_USER_URL}/{test_data['user_id']}/"
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
        'first_name': '更新的名字',
        'last_name': '更新的姓氏'
    }
    print(f"请求数据: {json.dumps(update_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.patch(url, json=update_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 更新用户信息成功")
        else:
            print("❌ 更新用户信息失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_change_password():
    """测试修改密码"""
    print("\n=== 测试修改密码 ===")
    
    # 检查是否有用户ID
    if not test_data.get('user_id'):
        print("❌ 没有用户ID，无法测试")
        return False
    
    url = f"{PLATFORM_USER_URL}/{test_data['user_id']}/change_password/"
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
    
    # 修改密码数据
    password_data = {
        'old_password': TEST_USER['password'],
        'new_password': 'NewPassword@123',
        'new_password_confirm': 'NewPassword@123'
    }
    print(f"请求数据: {json.dumps(password_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.post(url, json=password_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 修改密码成功")
            # 更新测试用户密码
            TEST_USER['password'] = password_data['new_password']
        else:
            print("❌ 修改密码失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_verify_email():
    """测试验证邮箱"""
    print("\n=== 测试验证邮箱 ===")
    
    # 检查是否有用户ID
    if not test_data.get('user_id'):
        print("❌ 没有用户ID，无法测试")
        return False
    
    url = f"{PLATFORM_USER_URL}/{test_data['user_id']}/verify_email/"
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
        response = requests.post(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 验证邮箱成功")
        else:
            print("❌ 验证邮箱失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始平台API用户视图测试 =====")
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
    
    # 测试获取用户列表
    test_list_users()
    
    # 测试获取用户详情
    test_retrieve_user()
    
    # 测试更新用户信息
    test_update_user()
    
    # 测试修改密码
    test_change_password()
    
    # 测试验证邮箱
    test_verify_email()
    
    print("\n===== 平台API用户视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 