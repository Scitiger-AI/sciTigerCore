"""
管理API角色视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
MANAGEMENT_ROLE_URL = f"{BASE_URL}/api/management/auth/roles"
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
    'created_role_id': None
}

# 测试角色数据
TEST_ROLE = {
    'name': f'测试角色_{int(datetime.now().timestamp())}',
    'code': f'test_role_{int(datetime.now().timestamp())}',
    'description': '这是一个测试角色',
    'is_system': False,
    'is_default': False
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

def test_list_roles():
    """测试获取角色列表"""
    print("\n=== 测试获取角色列表 ===")
    
    url = f"{MANAGEMENT_ROLE_URL}/"
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
    
    url = f"{MANAGEMENT_ROLE_URL}/"
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
    
    url = f"{MANAGEMENT_ROLE_URL}/{test_data['created_role_id']}/"
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
    
    url = f"{MANAGEMENT_ROLE_URL}/{test_data['created_role_id']}/"
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

def test_set_default_role():
    """测试设置为默认角色"""
    print("\n=== 测试设置为默认角色 ===")
    
    # 检查是否有创建的角色ID
    if not test_data.get('created_role_id'):
        print("❌ 没有创建的角色ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_ROLE_URL}/{test_data['created_role_id']}/set_default/"
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
            print("✅ 设置默认角色成功")
        else:
            print("❌ 设置默认角色失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_unset_default_role():
    """测试取消默认角色设置"""
    print("\n=== 测试取消默认角色设置 ===")
    
    # 检查是否有创建的角色ID
    if not test_data.get('created_role_id'):
        print("❌ 没有创建的角色ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_ROLE_URL}/{test_data['created_role_id']}/unset_default/"
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
            print("✅ 取消默认角色设置成功")
        else:
            print("❌ 取消默认角色设置失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_assign_permissions():
    """测试为角色分配权限"""
    print("\n=== 测试为角色分配权限 ===")
    
    # 检查是否有创建的角色ID
    if not test_data.get('created_role_id'):
        print("❌ 没有创建的角色ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_ROLE_URL}/{test_data['created_role_id']}/assign_permissions/"
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
    
    # 权限数据 - 这里需要实际存在的权限ID
    permission_data = {
        'permission_ids': []  # 实际测试时需要填入有效的权限ID
    }
    print(f"请求数据: {json.dumps(permission_data, indent=2, ensure_ascii=False)}")
    print("注意: 此测试需要有效的权限ID，如果没有提供，测试可能会失败")
    
    # 发送请求
    try:
        response = requests.post(url, json=permission_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 为角色分配权限成功")
            return True
        else:
            print("❌ 为角色分配权限失败")
            return False
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_get_role_users():
    """测试获取拥有此角色的用户列表"""
    print("\n=== 测试获取拥有此角色的用户列表 ===")
    
    # 检查是否有创建的角色ID
    if not test_data.get('created_role_id'):
        print("❌ 没有创建的角色ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_ROLE_URL}/{test_data['created_role_id']}/users/"
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
            print("✅ 获取角色用户列表成功")
        else:
            print("❌ 获取角色用户列表失败")
        
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
    
    url = f"{MANAGEMENT_ROLE_URL}/{test_data['created_role_id']}/"
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
            print("✅ 删除角色成功")
        else:
            print("❌ 删除角色失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始管理API角色视图测试 =====")
    print(f"API基础URL: {BASE_URL}")
    print(f"管理员用户名: {ADMIN_USER['username']}")
    
    # 测试管理员登录
    if not test_admin_login():
        print("⚠️ 管理员登录失败，跳过后续测试")
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
        
        # 测试设置为默认角色
        test_set_default_role()
        
        # 测试取消默认角色设置
        test_unset_default_role()
        
        # 测试为角色分配权限
        test_assign_permissions()
        
        # 测试获取拥有此角色的用户列表
        test_get_role_users()
        
        # 测试删除角色
        test_delete_role()
    
    print("\n===== 管理API角色视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 