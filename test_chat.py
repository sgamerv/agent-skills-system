#!/usr/bin/env python3
"""测试聊天接口"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.config import settings
from backend.core.agent_runtime import AgentRuntime
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

async def test_chat():
    print("Initializing agent...")
    agent = AgentRuntime(redis_client=None)
    
    print("\nTest 1: Simple greeting")
    try:
        result = await agent.chat('你好', 'test_user')
        print(f"✓ Success: {result}")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nTest 2: Get skills summary")
    try:
        summary = agent.skill_registry.get_skills_summary()
        print(f"✓ Skills summary:\n{summary}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
