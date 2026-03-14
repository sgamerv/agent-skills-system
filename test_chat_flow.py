#!/usr/bin/env python3
"""测试完整的五步 Chat 流程"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chat_flow():
    """测试完整的 Chat 流程"""
    print("=" * 60)
    print("测试完整的五步 Chat 流程")
    print("=" * 60)

    user_id = "test_flow_user"
    session_id = "flow_session_001"

    # 第一步：技能匹配
    print("\n【第一步：技能匹配与推荐】")
    print("用户输入: '我想分析一下数据'")

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "user_input": "我想分析一下数据",
            "user_id": user_id,
            "session_id": session_id
        }
    )
    result = response.json()

    print(f"\n响应状态: {result.get('state')}")
    print(f"可用技能: {result.get('available_skills')}")
    print(f"\nAgent 回复:\n{result['response']}")

    if result.get('state') == 'skill_selection':
        # 第二步：用户选择技能
        print("\n" + "=" * 60)
        print("【第二步：用户选择技能】")
        print("用户输入: '1' (选择第一个技能)")

        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "user_input": "1",
                "user_id": user_id,
                "session_id": session_id
            }
        )
        result = response.json()

        print(f"\n响应状态: {result.get('state')}")
        print(f"当前槽位: {result.get('current_slot')}")
        print(f"\nAgent 回复:\n{result['response']}")

        if result.get('state') == 'collecting_parameters':
            # 模拟提供第一个参数
            print("\n" + "=" * 60)
            print("【第二步：提供参数】")
            print("用户输入: '/path/to/data.csv' (提供数据文件)")

            response = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "user_input": "/path/to/data.csv",
                    "user_id": user_id,
                    "session_id": session_id
                }
            )
            result = response.json()

            print(f"\n响应状态: {result.get('state')}")
            print(f"当前槽位: {result.get('current_slot')}")
            print(f"\nAgent 回复:\n{result['response']}")

            # 模拟提供第二个参数
            print("\n" + "=" * 60)
            print("【第二步：提供参数】")
            print("用户输入: 'descriptive' (选择分析类型)")

            response = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "user_input": "descriptive",
                    "user_id": user_id,
                    "session_id": session_id
                }
            )
            result = response.json()

            print(f"\n响应状态: {result.get('state')}")
            print(f"已收集参数: {result.get('collected_parameters')}")
            print(f"\nAgent 回复:\n{result['response']}")

            if result.get('state') == 'awaiting_confirmation':
                # 第三步：用户确认
                print("\n" + "=" * 60)
                print("【第三步：用户确认执行】")
                print("用户输入: '确认'")

                response = requests.post(
                    f"{BASE_URL}/chat",
                    json={
                        "user_input": "确认",
                        "user_id": user_id,
                        "session_id": session_id
                    }
                )
                result = response.json()

                print(f"\n响应状态: {result.get('state')}")
                print(f"执行结果: {result.get('execution_result')}")
                print(f"\nAgent 回复:\n{result['response']}")

                if result.get('state') == 'completed' and result.get('feedback_required'):
                    # 第四步：用户反馈
                    print("\n" + "=" * 60)
                    print("【第四步：用户反馈】")
                    print("用户输入: '结果很好，谢谢'")

                    response = requests.post(
                        f"{BASE_URL}/chat",
                        json={
                            "user_input": "结果很好，谢谢",
                            "user_id": user_id,
                            "session_id": session_id
                        }
                    )
                    result = response.json()

                    print(f"\n响应状态: {result.get('state')}")
                    print(f"反馈信息: {result.get('feedback')}")
                    print(f"\nAgent 回复:\n{result['response']}")

                    # 第五步：反馈处理
                    print("\n" + "=" * 60)
                    print("【第五步：反馈处理完成】")
                    print(f"最终状态: {result.get('state')}")
                    print(f"下一步动作: {result.get('next_action')}")
            else:
                print(f"\n❌ 未能到达确认阶段，当前状态: {result.get('state')}")
        else:
            print(f"\n❌ 未能进入参数收集阶段，当前状态: {result.get('state')}")
    else:
        print(f"\n❌ 未能进入技能选择阶段，当前状态: {result.get('state')}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_chat_flow()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
