"""
平台API角色视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
PLATFORM_ROLE_URL = f"{BASE_URL}/api/platform/auth/roles"
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

# 测试角色数据
TEST_ROLE = {
    'name': f'测试角色_{int(datetime.now().timestamp())}',
    'code': f'test_role_{int(datetime.now().timestamp())}',
    'description': '这是一个测试角色',
    'is_system': False,
    'is_default': False
}

# 存储测试过程中的数据
test_data = {
    'user_id': None,
    'access_token': None,
    'refresh_token': None,
    'created_role_id': None
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

def test_list_roles():
    """测试获取角色列表"""
    print("\n=== 测试获取角色列表 ===")
    
    url = f"{PLATFORM_ROLE_URL}/"
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
            print("✅ 获取角色列表成功")
        else:
            print("❌ 获取角色列表失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_create_role():
    """测试创建角色"""
    print("\n=== 测试创建角色 ===")
    
    url = f"{PLATFORM_ROLE_URL}/"
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
    
    print(f"请求数据: {json.dumps(TEST_ROLE, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.post(url, json=TEST_ROLE, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 201:
            print("✅ 创建角色成功")
            # 保存创建的角色ID
            try:
                json_data = response.json()
                test_data['created_role_id'] = json_data.get('results', {}).get('id')
                print(f"创建的角色ID: {test_data['created_role_id']}")
            except json.JSONDecodeError:
                print("⚠️ 无法解析响应JSON")
        else:
            print("❌ 创建角色失败")
        
        return response.status_code == 201
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_retrieve_role():
    """测试获取角色详情"""
    print("\n=== 测试获取角色详情 ===")
    
    # 检查是否有创建的角色ID
    if not test_data.get('created_role_id'):
        print("❌ 没有创建的角色ID，无法测试")
        return False
    
    url = f"{PLATFORM_ROLE_URL}/{test_data['created_role_id']}/"
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
            print("✅ 获取角色详情成功")
        else:
            print("❌ 获取角色详情失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_update_role():
    """测试更新角色信息"""
    print("\n=== 测试更新角色信息 ===")
    
    # 检查是否有创建的角色ID
    if not test_data.get('created_role_id'):
        print("❌ 没有创建的角色ID，无法测试")
        return False
    
    url = f"{PLATFORM_ROLE_URL}/{test_data['created_role_id']}/"
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
        'name': f'更新的角色名称_{int(datetime.now().timestamp())}',
        'description': '这是更新后的角色描述'
    }
    print(f"请求数据: {json.dumps(update_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.patch(url, json=update_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 更新角色信息成功")
        else:
            print("❌ 更新角色信息失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_assign_role_to_user():
    """测试将角色分配给用户"""
    print("\n=== 测试将角色分配给用户 ===")
    
    # 检查是否有创建的角色ID和用户ID
    if not test_data.get('created_role_id'):
        print("❌ 没有创建的角色ID，无法测试")
        return False
    
    if not test_data.get('user_id'):
        print("❌ 没有用户ID，无法测试")
        return False
    
    url = f"{PLATFORM_ROLE_URL}/{test_data['created_role_id']}/assign_to_user/"
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
    
    # 请求数据
    assign_data = {
        'user_id': test_data['user_id']
    }
    print(f"请求数据: {json.dumps(assign_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.post(url, json=assign_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 将角色分配给用户成功")
        else:
            print("❌ 将角色分配给用户失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_remove_role_from_user():
    """测试从用户中移除角色"""
    print("\n=== 测试从用户中移除角色 ===")
    
    # 检查是否有创建的角色ID和用户ID
    if not test_data.get('created_role_id'):
        print("❌ 没有创建的角色ID，无法测试")
        return False
    
    if not test_data.get('user_id'):
        print("❌ 没有用户ID，无法测试")
        return False
    
    url = f"{PLATFORM_ROLE_URL}/{test_data['created_role_id']}/remove_from_user/"
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
    
    # 请求数据
    remove_data = {
        'user_id': test_data['user_id']
    }
    print(f"请求数据: {json.dumps(remove_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.post(url, json=remove_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 从用户中移除角色成功")
        else:
            print("❌ 从用户中移除角色失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_delete_role():
    """测试删除角色"""
    print("\n=== 测试删除角色 ===")
    
    # 检查是否有创建的角色ID
    if not test_data.get('created_role_id'):
        print("❌ 没有创建的角色ID，无法测试")
        return False
    
    url = f"{PLATFORM_ROLE_URL}/{test_data['created_role_id']}/"
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
        if response.status_code == 200:
            print("✅ 删除角色成功")
        else:
            print("❌ 删除角色失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始平台API角色视图测试 =====")
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
    
    # 测试获取角色列表
    test_list_roles()
    
    # 测试创建角色
    if not test_create_role():
        print("⚠️ 创建角色失败，跳过角色相关测试")
    else:
        # 测试获取角色详情
        test_retrieve_role()
        
        # 测试更新角色信息
        test_update_role()
        
        # 测试将角色分配给用户
        test_assign_role_to_user()
        
        # 测试从用户中移除角色
        test_remove_role_from_user()
        
        # 测试删除角色
        test_delete_role()
    
    print("\n===== 平台API角色视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 