"""
平台API租户用户视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
PLATFORM_TENANT_USER_URL = f"{BASE_URL}/api/platform/tenants/tenant-users"
PLATFORM_AUTH_URL = f"{BASE_URL}/api/platform/auth"

# 租户ID - 请替换为实际的租户ID
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
    'refresh_token': None,
    'tenant_id': TENANT_ID,
    'tenant_user_id': None,
    'invited_user_id': None
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
        'username': TEST_USER['email'],
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

def test_list_tenant_users():
    """测试获取租户用户列表"""
    print("\n=== 测试获取租户用户列表 ===")
    
    url = f"{PLATFORM_TENANT_USER_URL}/"
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
            print("✅ 获取租户用户列表成功")
            # 尝试获取第一个租户用户ID用于后续测试
            try:
                json_data = response.json()
                tenant_users = json_data.get('results', [])
                if tenant_users:
                    test_data['tenant_user_id'] = tenant_users[0].get('id')
                    print(f"租户用户ID: {test_data['tenant_user_id']}")
            except Exception:
                pass
        else:
            print("❌ 获取租户用户列表失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_invite_user():
    """测试邀请用户加入租户"""
    print("\n=== 测试邀请用户加入租户 ===")
    
    url = f"{PLATFORM_TENANT_USER_URL}/invite/"
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
    
    # 邀请数据
    invite_data = {
        'email': f'invited_{int(datetime.now().timestamp())}@example.com',
        'role': 'member',
        'first_name': 'Invited',
        'last_name': 'User'
    }
    print(f"请求数据: {json.dumps(invite_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.post(url, json=invite_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 201:
            print("✅ 邀请用户成功")
            # 保存邀请的用户ID
            try:
                json_data = response.json()
                test_data['invited_user_id'] = json_data.get('results', {}).get('user_id')
                print(f"邀请的用户ID: {test_data['invited_user_id']}")
            except Exception:
                pass
        else:
            print("❌ 邀请用户失败")
        
        return response.status_code == 201
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_retrieve_tenant_user():
    """测试获取租户用户详情"""
    print("\n=== 测试获取租户用户详情 ===")
    
    # 检查是否有租户用户ID
    if not test_data.get('tenant_user_id'):
        print("❌ 没有租户用户ID，无法测试")
        return False
    
    url = f"{PLATFORM_TENANT_USER_URL}/{test_data['tenant_user_id']}/"
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
            print("✅ 获取租户用户详情成功")
        else:
            print("❌ 获取租户用户详情失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_update_tenant_user_role():
    """测试更新租户用户角色"""
    print("\n=== 测试更新租户用户角色 ===")
    
    # 检查是否有租户用户ID
    if not test_data.get('tenant_user_id'):
        print("❌ 没有租户用户ID，无法测试")
        return False
    
    url = f"{PLATFORM_TENANT_USER_URL}/{test_data['tenant_user_id']}/"
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
    
    # 更新数据
    update_data = {
        'role': 'admin'
    }
    print(f"请求数据: {json.dumps(update_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.patch(url, json=update_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 更新租户用户角色成功")
        else:
            print("❌ 更新租户用户角色失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_remove_tenant_user():
    """测试移除租户用户"""
    print("\n=== 测试移除租户用户 ===")
    
    # 检查是否有租户用户ID
    if not test_data.get('tenant_user_id'):
        print("❌ 没有租户用户ID，无法测试")
        return False
    
    url = f"{PLATFORM_TENANT_USER_URL}/{test_data['tenant_user_id']}/"
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
        response = requests.delete(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 204:
            print("✅ 移除租户用户成功")
        else:
            print("❌ 移除租户用户失败")
        
        return response.status_code == 204
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始平台API租户用户视图测试 =====")
    print(f"API基础URL: {BASE_URL}")
    print(f"租户ID: {TENANT_ID}")
    
    # 测试注册和登录
    if not test_register_and_login():
        print("⚠️ 用户注册或登录失败，跳过后续测试")
        return
    
    # 测试获取租户用户列表
    test_list_tenant_users()
    
    # 测试邀请用户
    test_invite_user()
    
    # 测试获取租户用户详情
    test_retrieve_tenant_user()
    
    # 测试更新租户用户角色
    test_update_tenant_user_role()
    
    # 测试移除租户用户
    # 注意：这是破坏性操作，可能会影响其他测试，所以放在最后
    test_remove_tenant_user()
    
    print("\n===== 平台API租户用户视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 