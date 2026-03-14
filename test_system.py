#!/usr/bin/env python3
"""
系统测试脚本
"""
import asyncio
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_skill_loading():
    """测试技能加载"""
    print("=" * 60)
    print("测试 1: 技能加载")
    print("=" * 60)
    
    from core.skill_manager import SkillRegistry, SkillLoader, ResourceManager
    from config import settings
    
    # 初始化技能管理器
    registry = SkillRegistry(settings.SKILLS_DIR)
    loader = SkillLoader(settings.SKILLS_DIR)
    
    # 列出所有技能
    skills = registry.list_skills()
    print(f"\n发现 {len(skills)} 个技能:")
    
    for skill_name in skills:
        metadata = registry.get_skill_metadata(skill_name)
        print(f"\n  技能: {skill_name}")
        print(f"    描述: {metadata.get('description', 'N/A')}")
        print(f"    类别: {metadata.get('category', 'N/A')}")
        print(f"    版本: {metadata.get('version', 'N/A')}")
        print(f"    可调用: {metadata.get('can_call', [])}")
        
        # 获取槽位定义
        slots = loader.get_skill_slots(skill_name)
        if slots:
            print(f"    槽位:")
            for slot in slots:
                print(f"      - {slot['name']} ({slot['type']}): {'必需' if slot['required'] else '可选'}")
    
    print("\n✓ 技能加载测试通过")
    return True


async def test_agent_chat():
    """测试 Agent 聊天"""
    print("\n" + "=" * 60)
    print("测试 2: Agent 聊天")
    print("=" * 60)
    
    try:
        from core.agent_runtime import AgentRuntime
        
        # 创建 Agent
        agent = AgentRuntime()
        
        # 测试简单聊天
        print("\n测试对话: 你好,请介绍一下自己")
        result = await agent.chat(
            user_input="你好,请介绍一下自己",
            user_id="test_user"
        )
        
        print(f"\nAgent 回复: {result['response']}")
        print(f"模式: {result['mode']}")
        print(f"状态: {result['state']}")
        
        print("\n✓ Agent 聊天测试通过")
        return True
        
    except Exception as e:
        print(f"\n✗ Agent 聊天测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_skill_execution():
    """测试技能执行"""
    print("\n" + "=" * 60)
    print("测试 3: 技能执行")
    print("=" * 60)
    
    try:
        from core.agent_runtime import AgentRuntime
        
        agent = AgentRuntime()
        
        # 测试 knowledge-qa 技能
        print("\n测试知识问答技能...")
        result = await agent.execute_skill(
            skill_name="knowledge-qa-expert",
            parameters={
                "query": "什么是机器学习?"
            }
        )
        
        if result.success:
            print(f"✓ knowledge-qa 技能执行成功")
            print(f"  回答: {result.output['answer'][:100]}...")
        else:
            print(f"✗ knowledge-qa 技能执行失败: {result.error}")
            return False
        
        # 测试数据分析技能(使用示例数据)
        print("\n测试数据分析技能...")
        import pandas as pd
        import os
        
        # 创建测试数据
        test_data = "./data/test_sales.csv"
        if not os.path.exists(test_data):
            # 生成测试数据
            import numpy as np
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
            df = pd.DataFrame({
                'date': dates,
                'product': np.random.choice(['A', 'B', 'C'], len(dates)),
                'sales': np.random.randint(100, 1000, len(dates)),
                'revenue': np.random.randint(1000, 10000, len(dates))
            })
            df.to_csv(test_data, index=False)
        
        result = await agent.execute_skill(
            skill_name="data-analysis",
            parameters={
                "data_file": test_data,
                "analysis_type": "descriptive",
                "output_format": "json"
            }
        )
        
        if result.success:
            print(f"✓ data-analysis 技能执行成功")
            print(f"  数据行数: {result.output['data_info']['rows']}")
        else:
            print(f"✗ data-analysis 技能执行失败: {result.error}")
            return False
        
        print("\n✓ 技能执行测试通过")
        return True
        
    except Exception as e:
        print(f"\n✗ 技能执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_slot_filling():
    """测试 Slot Filling"""
    print("\n" + "=" * 60)
    print("测试 4: Slot Filling")
    print("=" * 60)
    
    try:
        from core.dialogue_manager import DialogueManager
        from core.skill_manager import SkillRegistry, SkillLoader
        from core.agent_runtime import AgentRuntime
        
        agent = AgentRuntime()
        
        # 开始一个需要 Slot Filling 的对话
        print("\n开始数据分析对话...")
        result = await agent.chat(
            user_input="我想分析一下销售数据",
            user_id="test_user"
        )
        
        print(f"Agent: {result['response']}")
        print(f"状态: {result['state']}")
        print(f"需要执行: {result['ready_to_execute']}")
        
        if result['mode'] == 'dialogue' and result['conversation_id']:
            conversation_id = result['conversation_id']
            
            # 模拟多轮对话
            print("\n模拟多轮对话...")
            
            # 第一轮: 提供数据文件
            result1 = await agent.chat(
                user_input="./data/test_sales.csv",
                user_id="test_user",
                conversation_id=conversation_id
            )
            print(f"Agent: {result1['response']}")
            
            # 第二轮: 选择分析类型
            result2 = await agent.chat(
                user_input="描述性统计",
                user_id="test_user",
                conversation_id=conversation_id
            )
            print(f"Agent: {result2['response']}")
            
            if result2['ready_to_execute']:
                print("\n✓ Slot Filling 测试通过")
                print(f"  所有必填槽位已填充,可以执行")
                return True
        
        print("\n✗ Slot Filling 测试未完成")
        return False
        
    except Exception as e:
        print(f"\n✗ Slot Filling 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Agent Skills 系统测试" + " " * 24 + "║")
    print("╚" + "═" * 58 + "╝")
    
    results = []
    
    # 测试 1: 技能加载
    results.append(await test_skill_loading())
    
    # 测试 2: Agent 聊天
    results.append(await test_agent_chat())
    
    # 测试 3: 技能执行
    results.append(await test_skill_execution())
    
    # 测试 4: Slot Filling
    results.append(await test_slot_filling())
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    test_names = [
        "技能加载",
        "Agent 聊天",
        "技能执行",
        "Slot Filling"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{i}. {name}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
    
    print()


if __name__ == "__main__":
    asyncio.run(main())
