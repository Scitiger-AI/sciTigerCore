"""
管理API密钥视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
MANAGEMENT_AUTH_URL = f"{BASE_URL}/api/management/auth"
MANAGEMENT_API_KEY_URL = f"{BASE_URL}/api/management/auth/api-keys"

# 测试数据 - 管理员账号需要预先在系统中创建
ADMIN_USER = {
    'username': os.getenv('ADMIN_USERNAME', '2504504@qq.com'),
    'password': os.getenv('ADMIN_PASSWORD', 'admin123')
}

# 存储测试过程中的数据
test_data = {
    'access_token': None,
    'refresh_token': None,
    'created_system_key_id': None,
    'created_user_key_id': None,
    'system_key_value': None,
    'user_key_value': None
}

# 测试系统级API密钥数据
TEST_SYSTEM_KEY = {
    'name': f'test_system_key_{int(datetime.now().timestamp())}',
    'application_name': 'Test Application',
    'expires_in_days': 30,
    'is_active': True,
    'scopes': [
        {
            'service': 'auth',
            'resource': 'user',
            'action': 'read'
        },
        {
            'service': 'auth',
            'resource': 'user',
            'action': 'write'
        }
    ],
    'metadata': {
        'description': 'Test system API key',
        'created_by': 'API Test'
    }
}

# 测试用户级API密钥数据
TEST_USER_KEY = {
    'name': f'test_user_key_{int(datetime.now().timestamp())}',
    'expires_in_days': 15,
    'is_active': True,
    'scopes': [
        {
            'service': 'auth',
            'resource': 'user',
            'action': 'read'
        }
    ],
    'metadata': {
        'description': 'Test user API key',
        'created_by': 'API Test'
    }
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

def test_list_api_keys():
    """测试获取API密钥列表"""
    print("\n=== 测试获取API密钥列表 ===")
    
    url = f"{MANAGEMENT_API_KEY_URL}/"
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
            print("✅ 获取API密钥列表成功")
        else:
            print("❌ 获取API密钥列表失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_create_system_api_key():
    """测试创建系统级API密钥"""
    print("\n=== 测试创建系统级API密钥 ===")
    
    url = f"{MANAGEMENT_API_KEY_URL}/create_system_key/"
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
    
    # 获取租户ID
    tenant_id = None
    try:
        # 获取租户列表 - 使用正确的租户API路径
        tenant_url = f"{BASE_URL}/api/management/tenants/tenants/"
        tenant_response = requests.get(tenant_url, headers=headers)
        if tenant_response.status_code == 200:
            tenant_data = tenant_response.json()
            tenants = tenant_data.get('results', [])
            if tenants and len(tenants) > 0:
                # 获取第一个租户的ID
                tenant_id = tenants[0].get('id')
                print(f"自动获取到租户ID: {tenant_id}")
    except Exception as e:
        print(f"获取租户ID失败: {e}")
    
    # 如果没有获取到租户ID，则无法继续测试
    if not tenant_id:
        print("❌ 无法获取有效的租户ID，跳过测试")
        return False
    
    # 设置租户ID
    TEST_SYSTEM_KEY['tenant'] = tenant_id
    print(f"使用租户ID: {tenant_id}")
    
    print(f"请求数据: {json.dumps(TEST_SYSTEM_KEY, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.post(url, json=TEST_SYSTEM_KEY, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 201:
            print("✅ 创建系统级API密钥成功")
            # 保存创建的API密钥ID和值
            try:
                json_data = response.json()
                api_key_data = json_data.get('results', {}).get('api_key', {})
                test_data['created_system_key_id'] = api_key_data.get('id')
                test_data['system_key_value'] = json_data.get('results', {}).get('key')
                print(f"创建的系统级API密钥ID: {test_data['created_system_key_id']}")
                print(f"系统级API密钥值: {test_data['system_key_value'][:10]}..." if test_data['system_key_value'] else "系统级API密钥值: None")
            except json.JSONDecodeError:
                print("⚠️ 无法解析响应JSON")
        else:
            print("❌ 创建系统级API密钥失败")
        
        return response.status_code == 201
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_create_user_api_key():
    """测试创建用户级API密钥"""
    print("\n=== 测试创建用户级API密钥 ===")
    
    url = f"{MANAGEMENT_API_KEY_URL}/create_user_key/"
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
    
    # 获取用户ID
    user_id = None
    try:
        # 获取当前用户信息
        profile_url = f"{MANAGEMENT_AUTH_URL}/profile/"
        profile_response = requests.get(profile_url, headers=headers)
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            user_id = profile_data.get('results', {}).get('id')
            print(f"自动获取到用户ID: {user_id}")
    except Exception as e:
        print(f"获取用户ID失败: {e}")
    
    # 如果没有获取到用户ID，则无法继续测试
    if not user_id:
        print("❌ 无法获取有效的用户ID，跳过测试")
        return False
    
    # 获取租户ID
    tenant_id = None
    try:
        # 获取租户列表 - 使用正确的租户API路径
        tenant_url = f"{BASE_URL}/api/management/tenants/tenants/"
        tenant_response = requests.get(tenant_url, headers=headers)
        if tenant_response.status_code == 200:
            tenant_data = tenant_response.json()
            tenants = tenant_data.get('results', [])
            if tenants and len(tenants) > 0:
                # 获取第一个租户的ID
                tenant_id = tenants[0].get('id')
                print(f"自动获取到租户ID: {tenant_id}")
    except Exception as e:
        print(f"获取租户ID失败: {e}")
    
    # 如果没有获取到租户ID，则无法继续测试
    if not tenant_id:
        print("❌ 无法获取有效的租户ID，跳过测试")
        return False
    
    # 设置用户ID和租户ID
    TEST_USER_KEY['user'] = user_id
    TEST_USER_KEY['tenant'] = tenant_id
    print(f"使用用户ID: {user_id}")
    print(f"使用租户ID: {tenant_id}")
    
    print(f"请求数据: {json.dumps(TEST_USER_KEY, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.post(url, json=TEST_USER_KEY, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 201:
            print("✅ 创建用户级API密钥成功")
            # 保存创建的API密钥ID和值
            try:
                json_data = response.json()
                api_key_data = json_data.get('results', {}).get('api_key', {})
                test_data['created_user_key_id'] = api_key_data.get('id')
                test_data['user_key_value'] = json_data.get('results', {}).get('key')
                print(f"创建的用户级API密钥ID: {test_data['created_user_key_id']}")
                print(f"用户级API密钥值: {test_data['user_key_value'][:10]}..." if test_data['user_key_value'] else "用户级API密钥值: None")
            except json.JSONDecodeError:
                print("⚠️ 无法解析响应JSON")
        else:
            print("❌ 创建用户级API密钥失败")
        
        return response.status_code == 201
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_retrieve_api_key():
    """测试获取API密钥详情"""
    print("\n=== 测试获取API密钥详情 ===")
    
    # 检查是否有创建的API密钥ID
    if not test_data.get('created_system_key_id'):
        print("❌ 没有创建的系统级API密钥ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_API_KEY_URL}/{test_data['created_system_key_id']}/"
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
            print("✅ 获取API密钥详情成功")
        else:
            print("❌ 获取API密钥详情失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_update_api_key():
    """测试更新API密钥"""
    print("\n=== 测试更新API密钥 ===")
    
    # 检查是否有创建的API密钥ID
    if not test_data.get('created_system_key_id'):
        print("❌ 没有创建的系统级API密钥ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_API_KEY_URL}/{test_data['created_system_key_id']}/"
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
        'name': f'updated_system_key_{int(datetime.now().timestamp())}',
        'application_name': 'Updated Application',
        'metadata': {
            'description': 'Updated test system API key',
            'updated_by': 'API Test'
        }
    }
    print(f"请求数据: {json.dumps(update_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.patch(url, json=update_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 更新API密钥成功")
        else:
            print("❌ 更新API密钥失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_deactivate_api_key():
    """测试禁用API密钥"""
    print("\n=== 测试禁用API密钥 ===")
    
    # 检查是否有创建的API密钥ID
    if not test_data.get('created_system_key_id'):
        print("❌ 没有创建的系统级API密钥ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_API_KEY_URL}/{test_data['created_system_key_id']}/deactivate/"
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
            print("✅ 禁用API密钥成功")
        else:
            print("❌ 禁用API密钥失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_activate_api_key():
    """测试激活API密钥"""
    print("\n=== 测试激活API密钥 ===")
    
    # 检查是否有创建的API密钥ID
    if not test_data.get('created_system_key_id'):
        print("❌ 没有创建的系统级API密钥ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_API_KEY_URL}/{test_data['created_system_key_id']}/activate/"
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
            print("✅ 激活API密钥成功")
        else:
            print("❌ 激活API密钥失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_usage_logs():
    """测试获取API密钥使用日志"""
    print("\n=== 测试获取API密钥使用日志 ===")
    
    # 检查是否有创建的API密钥ID
    if not test_data.get('created_system_key_id'):
        print("❌ 没有创建的系统级API密钥ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_API_KEY_URL}/{test_data['created_system_key_id']}/usage_logs/"
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
            print("✅ 获取API密钥使用日志成功")
        else:
            print("❌ 获取API密钥使用日志失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_stats():
    """测试获取API密钥统计信息"""
    print("\n=== 测试获取API密钥统计信息 ===")
    
    url = f"{MANAGEMENT_API_KEY_URL}/stats/"
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
            print("✅ 获取API密钥统计信息成功")
        else:
            print("❌ 获取API密钥统计信息失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_delete_api_key():
    """测试删除API密钥"""
    print("\n=== 测试删除API密钥 ===")
    
    # 检查是否有创建的API密钥ID
    if not test_data.get('created_system_key_id'):
        print("❌ 没有创建的系统级API密钥ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_API_KEY_URL}/{test_data['created_system_key_id']}/"
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
            print("✅ 删除API密钥成功")
        else:
            print("❌ 删除API密钥失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始管理API密钥视图测试 =====")
    print(f"API基础URL: {BASE_URL}")
    print(f"管理员用户名: {ADMIN_USER['username']}")
    
    # 测试管理员登录
    if not test_admin_login():
        print("⚠️ 管理员登录失败，跳过后续测试")
        return
    
    # 测试获取API密钥列表
    test_list_api_keys()
    
    # 测试创建系统级API密钥
    system_key_created = test_create_system_api_key()
    
    if system_key_created:
        # 测试获取API密钥详情
        test_retrieve_api_key()
        
        # 测试更新API密钥
        test_update_api_key()
        
        # 测试禁用API密钥
        test_deactivate_api_key()
        
        # 测试激活API密钥
        test_activate_api_key()
        
        # 测试获取API密钥使用日志
        test_usage_logs()
    
    # 测试创建用户级API密钥
    test_create_user_api_key()
    
    # 测试获取API密钥统计信息
    test_stats()
    
    # 测试删除API密钥
    if system_key_created:
        test_delete_api_key()
    
    print("\n===== 管理API密钥视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 