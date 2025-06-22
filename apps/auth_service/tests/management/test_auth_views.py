"""
管理API认证视图接口测试
"""

import os
import requests
import json
from datetime import datetime

# 基础URL配置
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
MANAGEMENT_AUTH_URL = f"{BASE_URL}/api/management/auth"

# 测试数据 - 管理员账号需要预先在系统中创建
ADMIN_USER = {
    'username': os.getenv('ADMIN_USERNAME', '2504504@qq.com'),
    'password': os.getenv('ADMIN_PASSWORD', 'admin123')
}

# 存储测试过程中的数据
test_data = {
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

def test_admin_refresh_token():
    """测试管理员令牌刷新接口"""
    print("\n=== 测试管理员令牌刷新接口 ===")
    
    url = f"{MANAGEMENT_AUTH_URL}/refresh-token/"
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
    
    # 发送刷新令牌请求
    try:
        response = requests.post(url, json=refresh_data)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 管理员令牌刷新成功")
            # 尝试解析响应并更新访问令牌
            try:
                json_data = response.json()
                tokens = json_data.get('results', {}).get('tokens', {})
                test_data['access_token'] = tokens.get('access')
                print(f"新访问令牌: {test_data['access_token'][:20]}...")
            except json.JSONDecodeError:
                print("⚠️ 无法解析响应JSON")
        else:
            print("❌ 管理员令牌刷新失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_admin_profile():
    """测试管理员个人资料接口"""
    print("\n=== 测试管理员个人资料接口 ===")
    
    url = f"{MANAGEMENT_AUTH_URL}/profile/"
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
    
    # 发送获取个人资料请求
    try:
        response = requests.get(url, headers=headers)
        print_response(response)
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 获取管理员个人资料成功")
        else:
            print("❌ 获取管理员个人资料失败")
        
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("\n===== 开始管理API认证视图测试 =====")
    print(f"API基础URL: {BASE_URL}")
    print(f"管理员用户名: {ADMIN_USER['username']}")
    
    # 测试管理员登录
    if not test_admin_login():
        print("⚠️ 管理员登录失败，跳过后续测试")
        return
    
    # 测试管理员令牌刷新
    test_admin_refresh_token()
    
    # 测试管理员个人资料
    test_admin_profile()
    
    print("\n===== 管理API认证视图测试完成 =====")

if __name__ == "__main__":
    run_tests() 