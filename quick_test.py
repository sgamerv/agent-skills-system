#!/usr/bin/env python3
"""
快速测试后端服务
"""
import sys
import time

# 添加项目路径
sys.path.append('./backend')

try:
    # 导入并创建测试客户端
    from fastapi.testclient import TestClient
    from api.main import app
    
    print("✅ 导入成功，创建测试客户端...")
    client = TestClient(app)
    
    # 测试根路径
    print("测试根路径...")
    response = client.get("/")
    print(f"  状态码: {response.status_code}")
    print(f"  响应类型: {response.headers.get('content-type', 'unknown')}")
    
    # 测试健康检查
    print("\n测试健康检查...")
    try:
        response = client.get("/health")
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"  响应: {response.json()}")
        else:
            print(f"  响应文本: {response.text[:200]}")
    except Exception as e:
        print(f"  健康检查失败: {e}")
    
    # 测试其他端点
    print("\n测试API端点...")
    endpoints = ["/docs", "/openapi.json", "/api/skills"]
    
    for endpoint in endpoints:
        try:
            response = client.get(endpoint, timeout=5)
            print(f"  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: 失败 - {e}")
    
    print("\n🎉 后端内部测试完成!")
    print("如果内部测试成功但外部访问失败，可能是网络配置问题")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()