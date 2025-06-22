"""
管理API租户设置视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
MANAGEMENT_TENANT_SETTINGS_URL = f"{BASE_URL}/api/management/tenants/tenant-settings"
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
    'tenant_id': None,
    'settings_id': None
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

def test_get_tenant_id():
    """获取一个可用的租户ID"""
    print("\n=== 获取可用的租户ID ===")
    
    # 检查是否有访问令牌
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    # 获取租户列表
    url = f"{BASE_URL}/api/management/tenants/tenants/"
    print(f"请求URL: {url}")
    
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print_response(response)
        
        if response.status_code == 200:
            json_data = response.json()
            tenants = json_data.get('results', [])
            if tenants:
                test_data['tenant_id'] = tenants[0].get('id')
                print(f"获取到租户ID: {test_data['tenant_id']}")
                return True
            else:
                print("⚠️ 没有可用的租户")
                return False
        else:
            print("❌ 获取租户列表失败")
            return False
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_list_tenant_settings():
    """测试获取租户设置列表"""
    print("\n=== 测试获取租户设置列表 ===")
    
    url = f"{MANAGEMENT_TENANT_SETTINGS_URL}/"
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
            print("✅ 获取租户设置列表成功")
            # 尝试获取第一个租户设置ID用于后续测试
            try:
                json_data = response.json()
                settings_list = json_data.get('results', [])
                if settings_list:
                    test_data['settings_id'] = settings_list[0].get('id')
                    print(f"租户设置ID: {test_data['settings_id']}")
            except Exception:
                pass
        else:
            print("❌ 获取租户设置列表失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_list_tenant_settings_by_tenant():
    """测试根据租户ID获取租户设置列表"""
    print("\n=== 测试根据租户ID获取租户设置列表 ===")
    
    # 检查是否有租户ID
    if not test_data.get('tenant_id'):
        print("❌ 没有租户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_SETTINGS_URL}/?tenant_id={test_data['tenant_id']}"
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
            print("✅ 根据租户ID获取租户设置列表成功")
            # 尝试获取租户设置ID用于后续测试
            try:
                json_data = response.json()
                settings_list = json_data.get('results', [])
                if settings_list:
                    test_data['settings_id'] = settings_list[0].get('id')
                    print(f"租户设置ID: {test_data['settings_id']}")
            except Exception:
                pass
        else:
            print("❌ 根据租户ID获取租户设置列表失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_retrieve_tenant_settings():
    """测试获取租户设置详情"""
    print("\n=== 测试获取租户设置详情 ===")
    
    # 检查是否有租户设置ID
    if not test_data.get('settings_id'):
        print("❌ 没有租户设置ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_SETTINGS_URL}/{test_data['settings_id']}/"
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
            print("✅ 获取租户设置详情成功")
        else:
            print("❌ 获取租户设置详情失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_update_tenant_settings():
    """测试更新租户设置"""
    print("\n=== 测试更新租户设置 ===")
    
    # 检查是否有租户设置ID
    if not test_data.get('settings_id'):
        print("❌ 没有租户设置ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_SETTINGS_URL}/{test_data['settings_id']}/"
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
        'theme_primary_color': '#2196f3',
        'theme_secondary_color': '#ff9800',
        'timezone': 'UTC',
        'date_format': 'MM/DD/YYYY',
        'time_format': 'hh:mm A',
        'enable_notifications': True,
        'enable_api_keys': True,
        'enable_two_factor_auth': False,
        'password_expiry_days': 60,
        'max_login_attempts': 3,
        'session_timeout_minutes': 60,
        'settings_json': {
            'custom_theme': {
                'header_background': '#333333',
                'sidebar_background': '#f5f5f5'
            }
        }
    }
    print(f"请求数据: {json.dumps(update_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.patch(url, json=update_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 更新租户设置成功")
        else:
            print("❌ 更新租户设置失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_get_settings_by_tenant():
    """测试根据租户ID获取设置"""
    print("\n=== 测试根据租户ID获取设置 ===")
    
    # 检查是否有租户ID
    if not test_data.get('tenant_id'):
        print("❌ 没有租户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_SETTINGS_URL}/by_tenant/?tenant_id={test_data['tenant_id']}"
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
            print("✅ 根据租户ID获取设置成功")
        else:
            print("❌ 根据租户ID获取设置失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始管理API租户设置视图测试 =====")
    print(f"API基础URL: {BASE_URL}")
    print(f"管理员用户名: {ADMIN_USER['username']}")
    
    # 测试管理员登录
    if not test_admin_login():
        print("⚠️ 管理员登录失败，跳过后续测试")
        return
    
    # 获取可用的租户ID
    if not test_get_tenant_id():
        print("⚠️ 获取租户ID失败，跳过后续测试")
        return
    
    # 测试获取租户设置列表
    test_list_tenant_settings()
    
    # 测试根据租户ID获取租户设置列表
    test_list_tenant_settings_by_tenant()
    
    # 测试获取租户设置详情
    test_retrieve_tenant_settings()
    
    # 测试更新租户设置
    test_update_tenant_settings()
    
    # 测试根据租户ID获取设置
    test_get_settings_by_tenant()
    
    print("\n===== 管理API租户设置视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 