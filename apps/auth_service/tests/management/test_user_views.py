"""
管理API用户视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
MANAGEMENT_USER_URL = f"{BASE_URL}/api/management/auth/users"
MANAGEMENT_AUTH_URL = f"{BASE_URL}/api/management/auth"

# 测试数据 - 管理员账号需要预先在系统中创建
ADMIN_USER = {
    'username': os.getenv('ADMIN_USERNAME', '2504504@qq.com'),
    'password': os.getenv('ADMIN_PASSWORD', 'admin123')
}

# 存储测试过程中的数据
test_data = {
    'access_token': None,
    'refresh_token': None,
    'created_user_id': None
}

# 测试用户数据
TEST_USER = {
    'username': f'testuser_{int(datetime.now().timestamp())}',
    'email': f'test_{int(datetime.now().timestamp())}@example.com',
    'password': 'Test@123456',
    'password_confirm': 'Test@123456',
    'first_name': 'Test',
    'last_name': 'User',
    'is_active': True
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

def test_admin_login():
    """测试管理员登录接口"""
    print("\n=== 测试管理员登录接口 ===")
    
    url = f"{MANAGEMENT_AUTH_URL}/login/"
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(ADMIN_USER, indent=2, ensure_ascii=False)}")
    
    # 发送登录请求
    try:
        response = requests.post(url, json=ADMIN_USER)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 管理员登录成功")
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
            print("❌ 管理员登录失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_list_users():
    """测试获取用户列表"""
    print("\n=== 测试获取用户列表 ===")
    
    url = f"{MANAGEMENT_USER_URL}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}"
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

def test_create_user():
    """测试创建用户"""
    print("\n=== 测试创建用户 ===")
    
    url = f"{MANAGEMENT_USER_URL}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}"
    }
    print(f"请求头: {headers}")
    
    print(f"请求数据: {json.dumps(TEST_USER, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.post(url, json=TEST_USER, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 201:
            print("✅ 创建用户成功")
            # 保存创建的用户ID
            try:
                json_data = response.json()
                test_data['created_user_id'] = json_data.get('results', {}).get('id')
                print(f"创建的用户ID: {test_data['created_user_id']}")
            except json.JSONDecodeError:
                print("⚠️ 无法解析响应JSON")
        else:
            print("❌ 创建用户失败")
        
        return response.status_code == 201
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_retrieve_user():
    """测试获取用户详情"""
    print("\n=== 测试获取用户详情 ===")
    
    # 检查是否有创建的用户ID
    if not test_data.get('created_user_id'):
        print("❌ 没有创建的用户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_USER_URL}/{test_data['created_user_id']}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}"
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
    
    # 检查是否有创建的用户ID
    if not test_data.get('created_user_id'):
        print("❌ 没有创建的用户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_USER_URL}/{test_data['created_user_id']}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}"
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

def test_activate_user():
    """测试激活用户"""
    print("\n=== 测试激活用户 ===")
    
    # 检查是否有创建的用户ID
    if not test_data.get('created_user_id'):
        print("❌ 没有创建的用户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_USER_URL}/{test_data['created_user_id']}/activate/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}"
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.post(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 激活用户成功")
        else:
            print("❌ 激活用户失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_deactivate_user():
    """测试禁用用户"""
    print("\n=== 测试禁用用户 ===")
    
    # 检查是否有创建的用户ID
    if not test_data.get('created_user_id'):
        print("❌ 没有创建的用户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_USER_URL}/{test_data['created_user_id']}/deactivate/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}"
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.post(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 禁用用户成功")
        else:
            print("❌ 禁用用户失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_reset_password():
    """测试重置密码"""
    print("\n=== 测试重置密码 ===")
    
    # 检查是否有创建的用户ID
    if not test_data.get('created_user_id'):
        print("❌ 没有创建的用户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_USER_URL}/{test_data['created_user_id']}/reset_password/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}"
    }
    print(f"请求头: {headers}")
    
    # 重置密码数据
    reset_data = {
        'new_password': 'NewPassword@123'
    }
    print(f"请求数据: {json.dumps(reset_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.post(url, json=reset_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 重置密码成功")
        else:
            print("❌ 重置密码失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_delete_user():
    """测试删除用户"""
    print("\n=== 测试删除用户 ===")
    
    # 检查是否有创建的用户ID
    if not test_data.get('created_user_id'):
        print("❌ 没有创建的用户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_USER_URL}/{test_data['created_user_id']}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}"
    }
    print(f"请求头: {headers}")
    
    # 发送请求
    try:
        response = requests.delete(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 删除用户成功")
        else:
            print("❌ 删除用户失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始管理API用户视图测试 =====")
    print(f"API基础URL: {BASE_URL}")
    print(f"管理员用户名: {ADMIN_USER['username']}")
    
    # 测试管理员登录
    if not test_admin_login():
        print("⚠️ 管理员登录失败，跳过后续测试")
        return
    
    # 测试获取用户列表
    test_list_users()
    
    # 测试创建用户
    if not test_create_user():
        print("⚠️ 创建用户失败，跳过用户相关测试")
    else:
        # 测试获取用户详情
        test_retrieve_user()
        
        # 测试更新用户信息
        test_update_user()
        
        # 测试激活用户
        test_activate_user()
        
        # 测试禁用用户
        test_deactivate_user()
        
        # 测试重置密码
        test_reset_password()
        
        # 测试删除用户
        test_delete_user()
    
    print("\n===== 管理API用户视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 