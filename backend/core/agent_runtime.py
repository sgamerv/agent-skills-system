"""Agent 运行时 - 核心执行引擎（完整 Chat 流程实现）"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from backend.config import settings
from backend.config.prompts import (
    INTENT_ANALYSIS_PROMPT,
    SKILL_EXECUTION_PROMPT,
    SYSTEM_PROMPT,
)
from backend.core.dialogue_manager import DialogueManager
from backend.core.memory import (
    MemoryExtractor,
    MemoryInjector,
    MemoryManager,
    ProfileManager,
)
from backend.core.skill_manager import SkillLoader, ResourceManager, SkillRegistry
from backend.core.skill_orchestrator import (
    SkillExecutionResult,
    SkillOrchestrator,
    SkillCall,
)


logger = logging.getLogger(__name__)


class InsufficientParametersError(Exception):
    """参数不足异常"""
    pass


class SkillTool(BaseTool):
    """Skill 包装为 LangChain BaseTool"""

    name: str
    description: str
    skill_loader: SkillLoader
    skill_name: str

    def _run(self, query: str) -> str:
        """同步执行(不使用)"""
        return "Async only"

    async def _arun(self, query: str) -> str:
        """异步执行"""
        # 加载技能指令
        skill_instructions = self.skill_loader.load_skill(self.skill_name)

        # 使用 LLM 执行
        llm = ChatOpenAI(
            base_url=settings.XINFERENCE_URL,
            api_key="empty",
            model=settings.XINFERENCE_MODEL_UID,
        )

        prompt = SKILL_EXECUTION_PROMPT.format(
            skill_name=self.skill_name,
            description=self.description,
            steps=skill_instructions or "无详细步骤",
            parameters={"query": query},
        )

        response = await llm.ainvoke(prompt)
        return response


class AgentRuntime:
    """Agent 运行时 - 核心执行引擎（完整五步 Chat 流程）"""

    def __init__(
        self,
        llm: ChatOpenAI | None = None,
        redis_client: Any | None = None,
    ) -> None:
        # 初始化 LLM
        self.llm = llm or ChatOpenAI(
            base_url=settings.XINFERENCE_URL,
            api_key="empty",
            model=settings.XINFERENCE_MODEL_UID,
            temperature=0.7,
        )

        # 初始化技能管理
        self.skill_registry = SkillRegistry(settings.SKILLS_DIR)
        self.skill_loader = SkillLoader(settings.SKILLS_DIR)
        self.resource_manager = ResourceManager(settings.SKILLS_DIR)
        self.skill_orchestrator = SkillOrchestrator(
            self.skill_registry,
            self.skill_loader,
            self.resource_manager,
        )

        # 初始化对话管理
        self.dialogue_manager = DialogueManager(
            self.skill_registry,
            self.skill_loader,
            self.llm,
            redis_client,
        )

        # 初始化记忆系统
        self.memory_extractor = MemoryExtractor(self.llm)
        self.memory_manager = MemoryManager(redis_client)
        self.memory_injector = MemoryInjector(self.memory_manager)
        self.profile_manager = ProfileManager(redis_client)

        # 构建 Tools
        self.tools = self._build_tools()

        # 存储会话状态
        self._session_states: Dict[str, Dict[str, Any]] = {}

    def _build_tools(self) -> List[BaseTool]:
        """从 Skills 构建 LangChain Tools"""
        tools = []
        for skill_name, metadata in self.skill_registry.skill_metadata.items():
            tool = SkillTool(
                name=skill_name,
                description=metadata.get("description", skill_name),
                skill_loader=self.skill_loader,
                skill_name=skill_name,
            )
            tools.append(tool)
        return tools

    async def chat(
        self,
        user_input: str,
        user_id: str,
        conversation_id: str = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        统一聊天接口，实现完整的五步 Chat 流程

        Args:
            user_input: 用户输入
            user_id: 用户 ID
            conversation_id: 对话 ID(可选)
            session_id: 会话 ID(可选)

        Returns:
            {
                "response": str,
                "conversation_id": str,
                "session_id": str,
                "mode": "direct" | "dialogue",
                "state": str,
                "available_skills": List[Dict] | None,
                "current_slot": Dict | None,
                "collected_parameters": Dict | None,
                "execution_result": Dict | None,
                "task_id": str | None,
                "feedback_required": bool,
                "feedback": Dict | None,
                "next_action": str
            }
        """
        # 注入记忆
        memory_context = await self.memory_injector.build_context(user_id, user_input)

        # 更新用户画像
        await self.profile_manager.increment_messages(user_id)

        # 检查会话状态
        state_key = f"{user_id}:{session_id or 'default'}"
        session_state = self._session_states.get(state_key)

        # 如果有会话状态，根据状态继续流程
        if session_state:
            return await self._continue_flow(user_input, user_id, conversation_id, session_id, session_state)

        # 第一步：技能匹配与推荐
        return await self._step1_skill_matching(user_input, user_id, conversation_id, session_id, memory_context)

    async def _continue_flow(
        self,
        user_input: str,
        user_id: str,
        conversation_id: str = None,
        session_id: str = None,
        session_state: Dict = None
    ) -> Dict[str, Any]:
        """根据会话状态继续流程"""
        state_key = f"{user_id}:{session_id or 'default'}"
        current_state = session_state.get("state")

        if current_state == "skill_selection":
            # 用户选择了技能，进入第二步
            return await self._step2_parameter_collection(user_input, user_id, conversation_id, session_id, session_state)
        elif current_state == "collecting_parameters":
            # 用户提供了参数，继续收集或进入确认
            return await self._step2_parameter_collection(user_input, user_id, conversation_id, session_id, session_state)
        elif current_state == "awaiting_confirmation":
            # 用户确认或修改参数
            if "确认" in user_input or "确定" in user_input:
                return await self._step3_skill_execution(user_id, conversation_id, session_id, session_state)
            else:
                # 用户想修改参数，重新进入参数收集
                return await self._step2_parameter_collection(user_input, user_id, conversation_id, session_id, session_state)
        elif current_state == "feedback_required":
            # 用户提供了反馈
            return await self._step5_feedback_handling(user_input, user_id, conversation_id, session_id, session_state)
        else:
            # 未知状态，重新开始
            del self._session_states[state_key]
            return await self._step1_skill_matching(user_input, user_id, conversation_id, session_id)

    async def _step1_skill_matching(
        self,
        user_input: str,
        user_id: str,
        conversation_id: str = None,
        session_id: str = None,
        memory_context: Dict = None
    ) -> Dict[str, Any]:
        """
        第一步：技能匹配与推荐
        - 通过用户输入，查找匹配的 skill
        - 组织语言向用户说明原因
        - 给出可以使用的 skill 列表
        - 如果没有匹配到任何 skill，则给出兜底方法（找人工处理）
        """
        # 匹配技能（简单的关键词匹配）
        matched_skills = self._match_skills(user_input)

        if not matched_skills:
            # 兜底处理：没有匹配到任何技能
            response = "很抱歉，我没有找到能够处理您请求的技能。\n\n"
            response += "这可能是因为：\n"
            response += "1. 您的需求不在当前系统功能范围内\n"
            response += "2. 我可能没有正确理解您的意图\n\n"
            response += "建议您：\n"
            response += "- 尝试用更具体的描述重新提问\n"
            response += "- 输入\"转人工\"连接人工客服\n"
            response += "- 查看系统支持的技能列表（输入\"查看技能\"）\n\n"
            response += "我们会持续改进系统功能，感谢您的理解！"

            return {
                "response": response,
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "dialogue",
                "state": "escalated",
                "available_skills": None,
                "next_action": "wait_or_escalate"
            }

        # 有匹配的技能，向用户推荐
        skill_list_text = "\n".join([
            f"{i+1}. {name} - {metadata.get('description', '无描述')}"
            for i, (name, metadata) in enumerate(matched_skills.items())
        ])

        response = f"根据您的描述，我为您找到了以下技能：\n\n{skill_list_text}\n\n"
        response += "请告诉我您想使用哪个技能（输入技能名称或编号），或输入\"无匹配\"转人工处理。"

        # 保存会话状态
        state_key = f"{user_id}:{session_id or 'default'}"
        self._session_states[state_key] = {
            "state": "skill_selection",
            "matched_skills": matched_skills,
            "user_input": user_input,
            "memory_context": memory_context,
            "timestamp": datetime.now().isoformat()
        }

        return {
            "response": response,
            "conversation_id": conversation_id,
            "session_id": session_id,
            "mode": "dialogue",
            "state": "skill_selection",
            "available_skills": [
                {"name": name, "description": metadata.get("description", "")}
                for name, metadata in matched_skills.items()
            ],
            "next_action": "user_select_skill"
        }

    async def _step2_parameter_collection(
        self,
        user_input: str,
        user_id: str,
        conversation_id: str = None,
        session_id: str = None,
        session_state: Dict = None
    ) -> Dict[str, Any]:
        """
        第二步：参数收集与确认
        - 当用户确认使用某个 skill 解决问题后
        - 通过多轮对话来满足可以使用 skill 的前提条件
        """
        state_key = f"{user_id}:{session_id or 'default'}"

        # 如果当前状态是 skill_selection，说明用户刚选择了技能
        if session_state.get("state") == "skill_selection":
            selected_skill_name = self._parse_skill_selection(user_input, session_state.get("matched_skills"))

            if not selected_skill_name:
                # 用户没有选择有效技能，重新提示
                return await self._step1_skill_matching(user_input, user_id, conversation_id, session_id)

            # 用户选择了技能，开始收集参数
            skill_metadata = self.skill_registry.get_skill_metadata(selected_skill_name)
            slots = self.skill_loader.get_skill_slots(selected_skill_name)

            # 保存选择的技能
            session_state["state"] = "collecting_parameters"
            session_state["selected_skill"] = selected_skill_name
            session_state["slots"] = slots
            session_state["collected_parameters"] = {}
            session_state["current_slot_index"] = 0
            self._session_states[state_key] = session_state

            # 询问第一个参数
            current_slot = slots[0]
            response = f"好的，我将使用 {selected_skill_name} 技能帮您处理。\n\n"
            response += f"{current_slot.get('prompt', '')}\n"
            if current_slot.get("options"):
                options_text = "\n".join([
                    f"- {opt} - {desc}" if isinstance(opt, str) else f"- {opt}"
                    for opt, desc in current_slot.get("options", {}).items()
                ])
                response += f"\n可选选项：\n{options_text}"

            return {
                "response": response,
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "dialogue",
                "state": "collecting_parameters",
                "current_slot": current_slot,
                "collected_parameters": session_state.get("collected_parameters"),
                "next_action": "provide_parameter"
            }

        # 继续收集参数
        current_slot_index = session_state.get("current_slot_index", 0)
        slots = session_state.get("slots", [])
        collected_parameters = session_state.get("collected_parameters", {})

        # 保存当前参数
        current_slot = slots[current_slot_index]
        param_value = user_input.strip()
        collected_parameters[current_slot["name"]] = param_value

        # 移动到下一个参数
        current_slot_index += 1

        if current_slot_index < len(slots):
            # 还有参数需要收集
            next_slot = slots[current_slot_index]

            # 跳过可选参数（如果用户没有提供）
            if not next_slot.get("required", True):
                session_state["collected_parameters"] = collected_parameters
                session_state["current_slot_index"] = current_slot_index
                self._session_states[state_key] = session_state
                return await self._step2_parameter_collection("跳过", user_id, conversation_id, session_id, session_state)

            # 询问下一个参数
            response = next_slot.get("prompt", "")
            if next_slot.get("options"):
                options_text = "\n".join([
                    f"- {opt} - {desc}" if isinstance(opt, str) else f"- {opt}"
                    for opt, desc in next_slot.get("options", {}).items()
                ])
                response += f"\n可选选项：\n{options_text}"

            session_state["collected_parameters"] = collected_parameters
            session_state["current_slot_index"] = current_slot_index
            self._session_states[state_key] = session_state

            return {
                "response": response,
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "dialogue",
                "state": "collecting_parameters",
                "current_slot": next_slot,
                "collected_parameters": collected_parameters,
                "next_action": "provide_parameter"
            }
        else:
            # 所有参数收集完成，进入确认阶段
            session_state["state"] = "awaiting_confirmation"
            session_state["collected_parameters"] = collected_parameters
            self._session_states[state_key] = session_state

            # 生成确认信息
            params_text = "\n".join([
                f"- {key}: {value}"
                for key, value in collected_parameters.items()
            ])

            response = "参数已收集完成，请确认：\n\n"
            response += f"{params_text}\n\n"
            response += '是否确认执行？（输入"确认"开始执行，或"修改"调整参数）'

            return {
                "response": response,
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "dialogue",
                "state": "awaiting_confirmation",
                "collected_parameters": collected_parameters,
                "next_action": "confirm_or_modify"
            }

    async def _step3_skill_execution(
        self,
        user_id: str,
        conversation_id: str = None,
        session_id: str = None,
        session_state: Dict = None
    ) -> Dict[str, Any]:
        """
        第三步：技能执行与结果返回
        - 当条件都满足后，开始执行 skill
        - 如果能迅速获取结果的，则返回用户
        - 如果是需要执行一段时间的，则告知用户如何获取执行结果
        """
        state_key = f"{user_id}:{session_id or 'default'}"
        selected_skill = session_state.get("selected_skill")
        collected_parameters = session_state.get("collected_parameters", {})

        # 执行技能
        try:
            result = await self.skill_orchestrator.execute_skill(
                selected_skill,
                collected_parameters
            )

            # 清除会话状态
            del self._session_states[state_key]

            # 生成结果响应
            response = "✅ 执行完成！\n\n"
            response += f"执行结果：\n{result.output}\n\n"
            response += "请对结果进行评价，或继续使用其他功能。"

            return {
                "response": response,
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "direct",
                "state": "completed",
                "execution_result": {
                    "success": result.success,
                    "output": result.output,
                    "error": result.error
                },
                "feedback_required": True,
                "next_action": "provide_feedback"
            }

        except Exception as e:
            logger.error(f"Skill execution error: {e}")
            return {
                "response": f"执行过程中出现错误：{str(e)}\n\n请重试或联系人工客服。",
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "dialogue",
                "state": "failed",
                "error": str(e),
                "next_action": "retry_or_escalate"
            }

    async def _step5_feedback_handling(
        self,
        user_input: str,
        user_id: str,
        conversation_id: str = None,
        session_id: str = None,
        session_state: Dict = None
    ) -> Dict[str, Any]:
        """
        第五步：反馈处理与响应
        - 当用户表达不满时，需要表示会反馈给人工跟踪处理
        - 如果用户满意结果时，可以谦虚表示谢谢用户的支持
        """
        # 简单的情感分析
        positive_keywords = ["满意", "好", "优秀", "不错", "赞", "thanks", "谢谢", "感谢"]
        negative_keywords = ["不满", "差", "不好", "失望", "不满意", "糟糕", "错误"]

        is_positive = any(keyword in user_input for keyword in positive_keywords)
        is_negative = any(keyword in user_input for keyword in negative_keywords)

        feedback_data = {
            "user_id": user_id,
            "feedback_text": user_input,
            "timestamp": datetime.now().isoformat(),
            "task_id": session_state.get("task_id"),
            "skill_name": session_state.get("selected_skill")
        }

        if is_negative:
            # 用户不满意
            feedback_data["rating"] = "negative"
            feedback_data["escalated"] = True

            response = "非常抱歉给您带来了不好的体验！😔\n\n"
            response += "我已经将您的反馈记录下来，并会立即反馈给人工团队进行跟踪处理。"
            response += "我们的工作人员会在 24 小时内联系您。\n\n"
            response += "如果您希望立即转接人工客服，请输入\"转人工\"。"

            return {
                "response": response,
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "dialogue",
                "state": "feedback_processed",
                "feedback": feedback_data,
                "next_action": "wait_or_escalate"
            }
        elif is_positive:
            # 用户满意
            feedback_data["rating"] = "positive"

            response = "太好了，谢谢您的支持和肯定！🎉\n\n"
            response += "能够帮到您是我们的荣幸。我们会继续努力，为您提供更好的服务。\n\n"
            response += "还有其他我可以帮助您的吗？"

            return {
                "response": response,
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "dialogue",
                "state": "feedback_processed",
                "feedback": feedback_data,
                "next_action": "continue_conversation"
            }
        else:
            # 中立反馈
            feedback_data["rating"] = "neutral"

            response = "感谢您的反馈！\n\n"
            response += "我们会认真考虑您的意见，持续改进服务质量。\n\n"
            response += "如果您有更多建议，欢迎随时告诉我们。还有其他我可以帮助您的吗？"

            return {
                "response": response,
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "dialogue",
                "state": "feedback_processed",
                "feedback": feedback_data,
                "next_action": "continue_conversation"
            }

    def _match_skills(self, user_input: str) -> Dict[str, Dict[str, Any]]:
        """匹配用户输入与可用技能"""
        matched = {}
        user_input_lower = user_input.lower()

        # 扩展的关键词匹配
        keywords_mapping = {
            "data-analysis": ["分析", "数据", "统计", "数据表", "excel", "csv", "报表", "计算"],
            "knowledge-qa": ["问答", "知识", "文档", "搜索", "查询", "检索", "答案"],
            "visualization": ["可视化", "图表", "画图", "绘图", "展示", "图形", "饼图", "柱状图", "折线图"]
        }

        # 简单的关键词匹配
        for skill_name, metadata in self.skill_registry.skill_metadata.items():
            description = metadata.get("description", "").lower()
            tags = [tag.lower() for tag in metadata.get("tags", [])]
            category = metadata.get("category", "").lower()

            # 检查关键词映射
            keywords = keywords_mapping.get(skill_name, [])
            if any(keyword in user_input_lower for keyword in keywords):
                matched[skill_name] = metadata
                continue

            # 检查描述、标签、类别是否包含用户输入的关键词
            if any(keyword in description for keyword in user_input_lower.split()):
                matched[skill_name] = metadata
            elif any(tag in user_input_lower for tag in tags):
                matched[skill_name] = metadata
            elif category in user_input_lower:
                matched[skill_name] = metadata

        return matched

    def _parse_skill_selection(self, user_input: str, matched_skills: Dict[str, Dict]) -> str | None:
        """解析用户选择的技能"""
        user_input = user_input.strip()

        # 检查是否输入了编号
        if user_input.isdigit():
            skill_names = list(matched_skills.keys())
            index = int(user_input) - 1
            if 0 <= index < len(skill_names):
                return skill_names[index]

        # 检查是否输入了技能名称
        for skill_name in matched_skills.keys():
            if skill_name.lower() in user_input.lower():
                return skill_name

        return None
