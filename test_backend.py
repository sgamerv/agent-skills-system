#!/usr/bin/env python3
"""
测试后端是否正常启动
"""

import time
import requests
import sys
import subprocess
import signal

def test_endpoint(url, timeout=10, retries=3):
    """测试端点是否可访问"""
    for i in range(retries):
        try:
            print(f"尝试 {i+1}/{retries}: 访问 {url} ...")
            response = requests.get(url, timeout=timeout)
            print(f"✅ 成功! 状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            if response.text:
                print(f"响应内容 (前500字符): {response.text[:500]}")
            return True
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误: {e}")
            time.sleep(2)
        except requests.exceptions.Timeout as e:
            print(f"❌ 超时: {e}")
            time.sleep(2)
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            time.sleep(2)
    return False

def check_process_on_port(port):
    """检查端口上是否有进程"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split()
            print(f"端口 {port} 上的进程PID: {', '.join(pids)}")
            return True
        else:
            print(f"端口 {port} 上没有进程")
            return False
    except Exception as e:
        print(f"检查端口时出错: {e}")
        return False

def main():
    print("🔧 开始测试后端服务...")
    
    # 检查端口
    print("\n📊 检查端口8000状态...")
    if not check_process_on_port(8000):
        print("❌ 后端服务未在端口8000上运行")
        sys.exit(1)
    
    # 测试健康端点
    print("\n🏥 测试健康检查端点...")
    health_url = "http://localhost:8000/health"
    if test_endpoint(health_url):
        print("🎉 后端服务正常运行!")
    else:
        print("\n❌ 健康检查失败，尝试其他端点...")
        
        # 测试根路径
        print("\n🔗 测试根路径...")
        root_url = "http://localhost:8000/"
        if test_endpoint(root_url):
            print("✅ 根路径可访问，可能/health路径不存在")
        else:
            print("❌ 根路径也无法访问")
            
        # 测试docs页面
        print("\n📚 测试API文档...")
        docs_url = "http://localhost:8000/docs"
        if test_endpoint(docs_url):
            print("✅ API文档可访问")
        else:
            print("❌ API文档也无法访问")
            print("\n⚠️ 后端可能在启动过程中卡住了")
            print("可能的原因：")
            print("1. LLM初始化失败")
            print("2. Redis连接问题")
            print("3. 应用启动时的死锁")
            print("\n建议检查后端启动日志")

if __name__ == "__main__":
    main()