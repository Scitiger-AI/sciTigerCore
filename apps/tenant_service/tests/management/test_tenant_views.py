"""
管理API租户视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
MANAGEMENT_TENANT_URL = f"{BASE_URL}/api/management/tenants/tenants"
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
    'created_tenant_id': None,
    'admin_user_id': None  # 添加存储管理员用户ID的字段
}

# 测试租户数据
TEST_TENANT = {
    'name': f'测试租户_{int(datetime.now().timestamp())}',
    'slug': f'test-tenant-{int(datetime.now().timestamp())}',
    'subdomain': f'test-{int(datetime.now().timestamp())}',
    'description': '这是一个测试租户',
    'contact_email': 'test@example.com',
    'contact_phone': '13800138000',
    'address': '北京市海淀区',
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
                
                # 保存管理员用户ID
                user_data = json_data.get('results', {}).get('user', {})
                test_data['admin_user_id'] = user_data.get('id')
                
                print(f"访问令牌: {test_data['access_token'][:20]}..." if test_data['access_token'] else "访问令牌: None")
                print(f"刷新令牌: {test_data['refresh_token'][:20]}..." if test_data['refresh_token'] else "刷新令牌: None")
                print(f"管理员用户ID: {test_data['admin_user_id']}")
            except json.JSONDecodeError:
                print("⚠️ 无法解析响应JSON")
        else:
            print("❌ 管理员登录失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_list_tenants():
    """测试获取所有租户列表"""
    print("\n=== 测试获取所有租户列表 ===")
    
    url = f"{MANAGEMENT_TENANT_URL}/"
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
            print("✅ 获取所有租户列表成功")
        else:
            print("❌ 获取所有租户列表失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_create_tenant():
    """测试创建租户"""
    print("\n=== 测试创建租户 ===")
    
    url = f"{MANAGEMENT_TENANT_URL}/"
    print(f"请求URL: {url}")
    
    # 检查是否有访问令牌和管理员用户ID
    if not test_data.get('access_token'):
        print("❌ 没有访问令牌，无法测试")
        return False
    
    if not test_data.get('admin_user_id'):
        print("❌ 没有管理员用户ID，无法测试")
        return False
    
    # 设置请求头
    headers = {
        'Authorization': f"Bearer {test_data['access_token']}"
    }
    print(f"请求头: {headers}")
    
    # 使用登录时获取的管理员用户ID作为租户所有者
    TEST_TENANT['owner_user_id'] = test_data['admin_user_id']
    
    print(f"请求数据: {json.dumps(TEST_TENANT, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.post(url, json=TEST_TENANT, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 201:
            print("✅ 创建租户成功")
            # 保存创建的租户ID
            try:
                json_data = response.json()
                test_data['created_tenant_id'] = json_data.get('results', {}).get('id')
                print(f"创建的租户ID: {test_data['created_tenant_id']}")
            except json.JSONDecodeError:
                print("⚠️ 无法解析响应JSON")
        else:
            print("❌ 创建租户失败")
        
        return response.status_code == 201
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_retrieve_tenant():
    """测试获取租户详情"""
    print("\n=== 测试获取租户详情 ===")
    
    # 检查是否有创建的租户ID
    if not test_data.get('created_tenant_id'):
        print("❌ 没有创建的租户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_URL}/{test_data['created_tenant_id']}/"
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
            print("✅ 获取租户详情成功")
        else:
            print("❌ 获取租户详情失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_update_tenant():
    """测试更新租户信息"""
    print("\n=== 测试更新租户信息 ===")
    
    # 检查是否有创建的租户ID
    if not test_data.get('created_tenant_id'):
        print("❌ 没有创建的租户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_URL}/{test_data['created_tenant_id']}/"
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
        'name': f'更新的租户_{int(datetime.now().timestamp())}',
        'description': '这是更新后的测试租户描述'
    }
    print(f"请求数据: {json.dumps(update_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        response = requests.patch(url, json=update_data, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 更新租户信息成功")
        else:
            print("❌ 更新租户信息失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_delete_tenant():
    """测试删除租户"""
    print("\n=== 测试删除租户 ===")
    
    # 检查是否有创建的租户ID
    if not test_data.get('created_tenant_id'):
        print("❌ 没有创建的租户ID，无法测试")
        return False
    
    url = f"{MANAGEMENT_TENANT_URL}/{test_data['created_tenant_id']}/"
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
        if response.status_code == 204:
            print("✅ 删除租户成功")
        else:
            print("❌ 删除租户失败")
        
        return response.status_code == 204
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始管理API租户视图测试 =====")
    print(f"API基础URL: {BASE_URL}")
    print(f"管理员用户名: {ADMIN_USER['username']}")
    
    # 测试管理员登录
    if not test_admin_login():
        print("⚠️ 管理员登录失败，跳过后续测试")
        return
    
    # 测试获取所有租户列表
    test_list_tenants()
    
    # 测试创建租户
    if not test_create_tenant():
        print("⚠️ 创建租户失败，跳过租户相关测试")
    else:
        # 测试获取租户详情
        test_retrieve_tenant()
        
        # 测试更新租户信息
        test_update_tenant()
        
        # # 测试删除租户
        # test_delete_tenant()
    
    print("\n===== 管理API租户视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 