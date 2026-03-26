"""测试新的Agent Loop"""
import asyncio
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.agent_loop.new_agent_runtime import NewAgentRuntime
from backend.core.llm_provider_factory import LLMProviderFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_basic_chat():
    """测试基础聊天功能"""
    print("测试基础聊天功能...")
    
    # 创建Agent Runtime
    try:
        # 先测试LLM连接
        llm = LLMProviderFactory.create_llm()
        print(f"LLM创建成功: {type(llm)}")
        
        # 创建Agent Runtime（不使用Redis）
        agent = NewAgentRuntime(llm=llm, redis_client=None)
        print("Agent Runtime创建成功")
        
        # 测试聊天
        test_cases = [
            ("你好，你是谁？", "test_user_1", "session_1"),
            ("你能做什么？", "test_user_1", "session_1"),
            ("查看技能列表", "test_user_1", "session_1"),
        ]
        
        for user_input, user_id, session_id in test_cases:
            print(f"\n测试: {user_input}")
            result = await agent.chat(
                user_input=user_input,
                user_id=user_id,
                session_id=session_id
            )
            
            print(f"响应: {result.get('response', '')[:100]}...")
            print(f"状态: {result.get('state')}")
            print(f"模式: {result.get('mode')}")
        
        # 测试技能信息
        tools_info = agent.get_tools_info()
        print(f"\n总共可用工具: {len(tools_info)}")
        for tool in tools_info[:3]:  # 只显示前3个
            print(f"工具: {tool['name']} - {tool['description'][:50]}...")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_session_continuation():
    """测试会话继续功能"""
    print("\n\n测试会话继续功能...")
    
    try:
        llm = LLMProviderFactory.create_llm()
        agent = NewAgentRuntime(llm=llm, redis_client=None)
        
        user_id = "test_user_2"
        session_id = "session_2"
        
        # 第一次输入
        print(f"第一轮输入...")
        result1 = await agent.chat(
            user_input="我想创建一个数据分析报告",
            user_id=user_id,
            session_id=session_id
        )
        print(f"响应1: {result1.get('response', '')[:100]}...")
        print(f"状态1: {result1.get('state')}")
        
        # 获取会话状态
        session_state = await agent.get_session_state(user_id, session_id)
        print(f"会话状态: {session_state.get('state', 'unknown')}")
        
        # 清除会话
        clear_result = await agent.clear_session(user_id, session_id)
        print(f"清除结果: {clear_result}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_skill_execution():
    """测试技能执行功能"""
    print("\n\n测试技能执行功能...")
    
    try:
        llm = LLMProviderFactory.create_llm()
        agent = NewAgentRuntime(llm=llm, redis_client=None)
        
        # 获取可用工具
        tools_info = agent.get_tools_info()
        skill_tools = [t for t in tools_info if t['name'].startswith('skill_')]
        
        if not skill_tools:
            print("没有找到技能工具")
            return
        
        print(f"找到 {len(skill_tools)} 个技能工具")
        
        # 测试第一个技能工具
        skill_tool = skill_tools[0]
        skill_name = skill_tool['name'].replace('skill_', '')
        print(f"测试技能: {skill_name}")
        
        # 直接执行技能
        result = await agent.execute_skill(
            skill_name=skill_name,
            parameters={"query": f"测试{skill_name}技能"}
        )
        
        print(f"技能执行结果:")
        print(f"  成功: {result.get('success')}")
        print(f"  输出: {result.get('output', '无')}")
        if result.get('error'):
            print(f"  错误: {result.get('error')}")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_tool_registry():
    """测试工具注册功能"""
    print("\n\n测试工具注册功能...")
    
    try:
        from backend.core.agent_loop.tool_registry import ToolRegistry, ToolCategory
        from backend.core.agent_loop.agent_session import AgentSession
        from backend.core.agent_loop.context_manager import ContextManager
        
        tool_registry = ToolRegistry()
        print(f"工具注册器创建成功")
        
        # 创建一些测试工具
        class TestTool:
            name = "test_tool"
            description = "测试工具"
            category = ToolCategory.DEBUG
            enabled = True
            parameters = []
            
            async def execute(self, **kwargs):
                return {"success": True, "output": "测试成功"}
        
        # 注意：这里需要实际的AgentTool实例，上面只是示例
        
        print(f"工具数量: {len(tool_registry.get_all_tools())}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主测试函数"""
    print("开始测试新的Agent Loop架构...")
    print("=" * 60)
    
    # 测试顺序
    try:
        await test_basic_chat()
        await test_session_continuation()
        await test_skill_execution()
        # await test_tool_registry()  # 这个测试需要更多依赖
        
    except Exception as e:
        print(f"整体测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")


if __name__ == "__main__":
    asyncio.run(main())