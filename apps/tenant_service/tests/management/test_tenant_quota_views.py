"""
管理API租户配额视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
MANAGEMENT_TENANT_QUOTA_URL = f"{BASE_URL}/api/management/tenants/tenant-quotas"
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
    'quota_id': None
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

def test_list_tenant_quotas():
    """测试获取租户配额列表"""
    print("\n=== 测试获取租户配额列表 ===")
    
    url = f"{MANAGEMENT_TENANT_QUOTA_URL}/"
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
            print("✅ 获取租户配额列表成功")
            # 尝试获取第一个租户配额ID用于后续测试
            try:
                json_data = response.json()
                quota_list = json_data.get('results', [])
                if quota_list:
                    test_data['quota_id'] = quota_list[0].get('id')
                    print(f"租户配额ID: {test_data['quota_id']}")
            except Exception:
                pass
        else:
            print("❌ 获取租户配额列表失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_list_tenant_quotas_by_tenant():
    """测试根据租户ID获取租户配额列表"""
    print("\n=== 测试根据租户ID获取租户配额列表 ===")
    
    # 检查是否有租户ID
    if not test_data.get('tenant_id'):
        print("❌ 没有租户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_QUOTA_URL}/?tenant_id={test_data['tenant_id']}"
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
            print("✅ 根据租户ID获取租户配额列表成功")
            # 尝试获取租户配额ID用于后续测试
            try:
                json_data = response.json()
                quota_list = json_data.get('results', [])
                if quota_list:
                    test_data['quota_id'] = quota_list[0].get('id')
                    print(f"租户配额ID: {test_data['quota_id']}")
            except Exception:
                pass
        else:
            print("❌ 根据租户ID获取租户配额列表失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_retrieve_tenant_quota():
    """测试获取租户配额详情"""
    print("\n=== 测试获取租户配额详情 ===")
    
    # 检查是否有租户配额ID
    if not test_data.get('quota_id'):
        print("❌ 没有租户配额ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_QUOTA_URL}/{test_data['quota_id']}/"
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
            print("✅ 获取租户配额详情成功")
        else:
            print("❌ 获取租户配额详情失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_update_tenant_quota():
    """测试更新租户配额"""
    print("\n=== 测试更新租户配额 ===")
    
    # 检查是否有租户配额ID
    if not test_data.get('quota_id'):
        print("❌ 没有租户配额ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_QUOTA_URL}/{test_data['quota_id']}/"
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
        'max_users': 20,
        'max_api_keys': 10,
        'max_api_requests_per_day': 10000,
        'max_storage_gb': 10,
        'max_log_retention_days': 60,
        'max_notifications_per_day': 2000
    }
    print(f"请求数据: {json.dumps(update_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.patch(url, json=update_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 更新租户配额成功")
        else:
            print("❌ 更新租户配额失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_get_quota_by_tenant():
    """测试根据租户ID获取配额"""
    print("\n=== 测试根据租户ID获取配额 ===")
    
    # 检查是否有租户ID
    if not test_data.get('tenant_id'):
        print("❌ 没有租户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_QUOTA_URL}/by_tenant/?tenant_id={test_data['tenant_id']}"
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
            print("✅ 根据租户ID获取配额成功")
        else:
            print("❌ 根据租户ID获取配额失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_reset_api_calls():
    """测试重置API调用计数"""
    print("\n=== 测试重置API调用计数 ===")
    
    # 检查是否有租户配额ID
    if not test_data.get('quota_id'):
        print("❌ 没有租户配额ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_QUOTA_URL}/{test_data['quota_id']}/reset_api_calls/"
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
            print("✅ 重置API调用计数成功")
        else:
            print("❌ 重置API调用计数失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始管理API租户配额视图测试 =====")
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
    
    # 测试获取租户配额列表
    test_list_tenant_quotas()
    
    # 测试根据租户ID获取租户配额列表
    test_list_tenant_quotas_by_tenant()
    
    # 测试获取租户配额详情
    test_retrieve_tenant_quota()
    
    # 测试更新租户配额
    test_update_tenant_quota()
    
    # 测试根据租户ID获取配额
    test_get_quota_by_tenant()
    
    # 测试重置API调用计数
    test_reset_api_calls()
    
    print("\n===== 管理API租户配额视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 