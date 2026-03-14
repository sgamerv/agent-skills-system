"""Agent 运行时 - 核心执行引擎"""
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
    """Agent 运行时 - 核心执行引擎"""

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
        统一聊天接口,支持多轮对话
        
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
                "state": str
            }
        """
        # 注入记忆
        memory_context = await self.memory_injector.build_context(user_id, user_input)
        
        # 首先尝试直接执行
        try:
            result = await self._try_direct_execution(
                user_input,
                memory_context
            )
            
            # 更新用户画像
            await self.profile_manager.increment_messages(user_id)
            
            return {
                "response": result,
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "direct",
                "state": "completed"
            }
        except InsufficientParametersError:
            # 参数不足,进入多轮对话
            return await self.chat_with_dialogue(
                user_input,
                user_id,
                conversation_id,
                session_id
            )
    
    async def _try_direct_execution(
        self,
        user_input: str,
        memory_context: Dict[str, Any] = None
    ) -> str:
        """尝试直接执行(不需要 Slot Filling)"""
        try:
            # 判断是否有足够的参数
            has_enough_params = await self._check_parameters(user_input)

            if not has_enough_params:
                raise InsufficientParametersError()

            # 构建系统提示词
            system_prompt = SYSTEM_PROMPT.format(
                skills_info=self.skill_registry.get_skills_summary()
            )

            # 添加记忆上下文
            if memory_context:
                system_prompt += f"\n\n用户记忆:\n{memory_context.get('facts', '无')}"
                system_prompt += f"\n\n用户偏好:\n{memory_context.get('preferences', '无')}"

            # 直接执行
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])

            chain = prompt | self.llm
            result = await chain.ainvoke({"input": user_input})

            return result.content
        except Exception as e:
            logger.error(f"Error in direct execution: {e}")
            # 如果 LLM 连接失败，返回简单的默认响应
            return f"收到您的消息：{user_input}\n\n（注意：LLM 服务未连接，返回的是模拟响应。请启动 Xinference 服务以获得真实 AI 回复。）"
    
    async def chat_with_dialogue(
        self,
        user_input: str,
        user_id: str,
        conversation_id: str = None,
        session_id: str = None
    ):
        """多轮对话模式"""
        if conversation_id:
            # 继续已有对话
            result = await self.dialogue_manager.process_user_input(
                conversation_id,
                user_input
            )
        else:
            # 新对话,首先识别意图和需要的 Skill
            intent_result = await self._analyze_intent(user_input)
            
            if intent_result['skill'] and intent_result['needs_slot_filling']:
                # 需要 Slot Filling
                context = await self.dialogue_manager.start_dialogue(
                    skill_name=intent_result['skill'],
                    user_id=user_id,
                    initial_input=user_input
                )
                
                # 获取第一个响应
                result = await self.dialogue_manager.process_user_input(
                    context.conversation_id,
                    user_input
                )
                
                result['conversation_id'] = context.conversation_id
                
                # 更新用户画像
                await self.profile_manager.increment_dialogues(user_id)
                await self.profile_manager.update_skill_usage(user_id, intent_result['skill'])
            else:
                # 不需要 Slot Filling,直接执行
                return await self.chat(user_input, user_id)
        
        result['session_id'] = session_id
        return result
    
    async def _analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """
        分析用户意图

        Returns:
            {
                "skill": str,
                "needs_slot_filling": bool,
                "extracted_params": {...},
                "confidence": float
            }
        """
        skills_summary = self.skill_registry.get_skills_summary()

        prompt = INTENT_ANALYSIS_PROMPT.format(
            user_input=user_input,
            skills_summary=skills_summary,
        )

        try:
            response = await self.llm.ainvoke(prompt)
            response = response.strip()
            logger.debug(f"Raw LLM response for intent analysis: {response}")

            # 清理响应
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # 尝试提取 JSON
            json_start = response.find("{")
            json_end = response.rfind("}")
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end + 1]
                result = json.loads(json_str)
                return {
                    "skill": result.get("skill"),
                    "needs_slot_filling": result.get("needs_slot_filling", False),
                    "extracted_params": result.get("extracted_params", {}),
                    "confidence": result.get("confidence", 0.0),
                }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent analysis response: {e}\nResponse: {response}")
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")

        # 默认返回，表示没有特定的技能需要调用
        return {
            "skill": None,
            "needs_slot_filling": False,
            "extracted_params": {},
            "confidence": 0.0,
        }
    
    async def _check_parameters(self, user_input: str) -> bool:
        """检查参数是否充足"""
        prompt = f"""判断用户输入是否包含执行任务所需的足够信息:

用户输入: {user_input}

可用技能:
{self.skill_registry.get_skills_summary()}

以 JSON 格式返回:
{{
  "has_enough": true/false,
  "missing_params": ["param1", "param2"],
  "reason": "原因"
}}

注意: 如果只是简单的问答或闲聊,has_enough 应该为 true。
"""

        try:
            response = await self.llm.ainvoke(prompt)
            response = response.strip()
            logger.debug(f"Raw LLM response for parameter check: {response}")

            # 清理响应
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # 尝试提取 JSON
            json_start = response.find("{")
            json_end = response.rfind("}")
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end + 1]
                result = json.loads(json_str)
                return result.get("has_enough", False)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse parameter check response: {e}\nResponse: {response}")
        except Exception as e:
            logger.error(f"Error checking parameters: {e}")

        # 默认为 true（对于简单问答），走直接执行
        return True
    
    async def execute_skill(
        self,
        skill_name: str,
        parameters: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> SkillExecutionResult:
        """
        执行单个技能

        Args:
            skill_name: 技能名称
            parameters: 执行参数
            context: 上下文数据

        Returns:
            技能执行结果
        """
        return await self.skill_orchestrator.execute_single(
            skill_name,
            parameters,
            context or {}
        )
    
    async def extract_and_save_memories(
        self,
        user_id: str,
        conversation_history: List[Dict[str, Any]]
    ):
        """
        从对话中提取并保存记忆
        
        Args:
            user_id: 用户 ID
            conversation_history: 对话历史
        """
        # 提取事实
        facts = await self.memory_extractor.extract_facts(
            conversation_history,
            user_id
        )
        for fact in facts:
            await self.memory_manager.save_memory(fact)
        
        # 提取偏好
        preferences = await self.memory_extractor.extract_preferences(
            conversation_history,
            user_id
        )
        for pref in preferences:
            await self.memory_manager.save_memory(pref)
