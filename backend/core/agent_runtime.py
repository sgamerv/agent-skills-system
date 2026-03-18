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
from backend.core.session_manager import MessageManager
from backend.core.skill_manager import SkillLoader, ResourceManager, SkillRegistry
from backend.core.skill_orchestrator import (
    SkillExecutionResult,
    SkillOrchestrator,
    SkillCall,
)
# 新增：集成LLM router和natural language workflow
from backend.llm.zhipuai_client import ZhipuAIClient
from backend.core.llm_skill_router import LLMSkillRouter
from backend.core.natural_language_workflow import (
    NaturalLanguageWorkflowExecutor,
    MCPToolExecutor,
)
from backend.core.llm_provider_factory import LLMProviderFactory


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
        # 使用工厂类创建统一的LLM客户端
        self.llm = llm or LLMProviderFactory.create_llm()

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

        # 初始化消息管理器
        self.message_manager = MessageManager(redis_client)

        # 构建 Tools
        self.tools = self._build_tools()

        # 存储会话状态
        self._session_states: Dict[str, Dict[str, Any]] = {}

        # Redis客户端用于持久化session_state
        self.redis_client = redis_client

        # 初始化LLM Router和Workflow执行器（统一使用self.llm）
        logger.info("初始化LLM Skill Router和Workflow执行器...")

        self.llm_router = LLMSkillRouter(
            self.llm,
            self.skill_registry
        )

        # 初始化MCP工具执行器
        self.mcp_executor = MCPToolExecutor()

        # 初始化自然语言workflow执行器
        self.workflow_executor = NaturalLanguageWorkflowExecutor(
            llm_client=self.llm,
            mcp_executor=self.mcp_executor,
            skill_orchestrator=self.skill_orchestrator,
            skill_registry=self.skill_registry
        )

        logger.info("LLM组件初始化完成")

    async def _get_session_state(self, state_key: str) -> Dict[str, Any] | None:
        """从Redis或内存获取会话状态"""
        # 先从Redis获取
        if self.redis_client:
            try:
                state_data = await self.redis_client.get(f"session_state:{state_key}")
                if state_data:
                    logger.info(f"[DEBUG] 从Redis获取到session_state: {state_key}")
                    return json.loads(state_data)
            except Exception as e:
                logger.error(f"从Redis获取会话状态失败: {e}")

        # 降级到内存获取
        return self._session_states.get(state_key)

    async def _set_session_state(self, state_key: str, state: Dict[str, Any]):
        """将会话状态保存到Redis和内存"""
        # 保存到Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"session_state:{state_key}",
                    3600,  # 1小时过期
                    json.dumps(state)
                )
                logger.info(f"[DEBUG] session_state已保存到Redis: {state_key}")
            except Exception as e:
                logger.error(f"保存会话状态到Redis失败: {e}")

        # 同时保存到内存（降级）
        self._session_states[state_key] = state
        logger.info(f"[DEBUG] session_state已保存到内存: {state_key}")

    async def _clear_session_state(self, state_key: str):
        """清除会话状态"""
        # 从Redis删除
        if self.redis_client:
            try:
                await self.redis_client.delete(f"session_state:{state_key}")
            except Exception as e:
                logger.error(f"从Redis删除会话状态失败: {e}")

        # 从内存删除
        if state_key in self._session_states:
            del self._session_states[state_key]

    async def _save_messages(
        self,
        user_input: str,
        response: str,
        user_id: str,
        conversation_id: str | None = None,
        session_id: str | None = None
    ):
        """保存用户和助手的消息"""
        if not session_id:
            return

        try:
            # 保存用户消息
            await self.message_manager.add_message(
                session_id=session_id,
                role="user",
                content=user_input,
                conversation_id=conversation_id
            )

            # 保存助手消息
            await self.message_manager.add_message(
                session_id=session_id,
                role="assistant",
                content=response,
                conversation_id=conversation_id
            )
        except Exception as e:
            logger.error(f"保存消息失败: {e}")
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
        session_state = await self._get_session_state(state_key)
        logger.info(f"[DEBUG] 检查会话状态: state_key={state_key}, session_id={session_id}, session_state={session_state}")

        # 如果有会话状态，根据状态继续流程
        if session_state:
            result = await self._continue_flow(user_input, user_id, conversation_id, session_id, session_state)
        else:
            # 第一步：技能匹配与推荐
            result = await self._step1_skill_matching(user_input, user_id, conversation_id, session_id, memory_context)

        # 统一保存消息
        if result and "response" in result:
            await self._save_messages(user_input, result["response"], user_id, conversation_id, session_id)

        return result

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

        if current_state == "workflow_execution":
            # 自然语言workflow执行中
            return await self._continue_workflow_execution(
                user_input,
                user_id,
                conversation_id,
                session_id,
                session_state
            )
        else:
            # 未知状态，重新开始
            logger.warning(f"未知状态: {current_state}，重新开始")
            await self._clear_session_state(state_key)
            return await self._step1_skill_matching(user_input, user_id, conversation_id, session_id)

    async def _continue_workflow_execution(
        self,
        user_input: str,
        user_id: str,
        conversation_id: str = None,
        session_id: str = None,
        session_state: Dict = None
    ) -> Dict[str, Any]:
        """继续自然语言workflow执行"""
        if not self.workflow_executor:
            logger.error("Workflow executor未初始化")
            return await self._step1_skill_matching(user_input, user_id, conversation_id, session_id)

        try:
            # 恢复执行状态
            from backend.core.natural_language_workflow import ExecutionState, WorkflowPlan, WorkflowStep, StepStatus

            # 从保存的状态中恢复 plan
            saved_plan = session_state.get("execution_state", {}).get("plan", {})
            saved_steps = saved_plan.get("steps", [])

            # 重建 steps 列表
            steps = []
            for step_data in saved_steps:
                step = WorkflowStep(
                    step_number=step_data.get("step_number", 0),
                    description=step_data.get("description", ""),
                    tool_type=step_data.get("tool_type", "skill"),
                    tool_name=step_data.get("tool_name", ""),
                    parameters=step_data.get("parameters", {}),
                    depends_on=step_data.get("depends_on", []),
                    requires_user_input=step_data.get("requires_user_input", False),
                    user_prompt=step_data.get("user_prompt", ""),
                    status=StepStatus(step_data.get("status", "pending"))
                )
                steps.append(step)

            # 重建 WorkflowPlan
            plan = WorkflowPlan(
                steps=steps,
                required_params=saved_plan.get("required_params", []),
                extracted_params=saved_plan.get("extracted_params", {}),
                missing_params=saved_plan.get("missing_params", [])
            )

            # 重建 ExecutionState
            execution_state = ExecutionState(
                skill_name=session_state.get("skill_name", ""),
                workflow_text=session_state.get("workflow_text", ""),
                user_input=user_input,
                plan=plan,
                current_step=session_state.get("execution_state", {}).get("current_step", 0),
                collected_params=session_state.get("execution_state", {}).get("collected_params", {}),
                missing_params=session_state.get("execution_state", {}).get("missing_params", []),
                execution_results=session_state.get("execution_state", {}).get("execution_results", {}),
                is_first_execution=False  # 恢复执行时不是首次执行
            )

            # 继续执行workflow
            workflow_result = await self.workflow_executor.execute(
                skill_name=session_state.get("skill_name"),
                workflow_text=session_state.get("workflow_text"),
                user_input=user_input,
                context={},
                execution_state=execution_state
            )

            # 处理workflow执行结果
            if workflow_result.status == "waiting_input":
                # 需要用户提供参数
                state_key = f"{user_id}:{session_id or 'default'}"
                await self._set_session_state(state_key, {
                    "state": "workflow_execution",
                    "skill_name": session_state.get("skill_name"),
                    "workflow_text": session_state.get("workflow_text"),
                    "execution_state": workflow_result.execution_state.to_dict(),
                    "timestamp": datetime.now().isoformat()
                })

                return {
                    "response": workflow_result.message,
                    "conversation_id": conversation_id,
                    "session_id": session_id,
                    "mode": "dialogue",
                    "state": "workflow_execution",
                    "current_skill": session_state.get("skill_name"),
                    "collected_parameters": workflow_result.execution_state.collected_params,
                    "next_action": "collect_parameters",
                    "missing_params": workflow_result.missing_params if hasattr(workflow_result, 'missing_params') else []
                }

            elif workflow_result.status == "completed":
                # 执行完成
                await self._clear_session_state(f"{user_id}:{session_id or 'default'}")

                return {
                    "response": f"执行完成！\n\n{json.dumps(workflow_result.output, ensure_ascii=False, indent=2)}",
                    "conversation_id": conversation_id,
                    "session_id": session_id,
                    "mode": "direct",
                    "state": "completed",
                    "execution_result": workflow_result.output
                }

            elif workflow_result.status == "failed":
                # 执行失败
                await self._clear_session_state(f"{user_id}:{session_id or 'default'}")

                return {
                    "response": f"执行失败：{workflow_result.error}",
                    "conversation_id": conversation_id,
                    "session_id": session_id,
                    "mode": "direct",
                    "state": "failed",
                    "execution_result": None
                }

        except Exception as e:
            logger.error(f"继续workflow执行失败: {e}")
            await self._clear_session_state(f"{user_id}:{session_id or 'default'}")
            return {
                "response": f"执行出错：{str(e)}",
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "direct",
                "state": "failed"
            }

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
        - 使用LLM router进行智能匹配
        - 如果匹配到技能，使用natural language workflow执行
        - 如果没有匹配到任何 skill，则给出提示
        """
        # 使用 LLM router 和 natural language workflow 执行
        return await self._execute_with_natural_language_workflow(
            user_input,
            user_id,
            conversation_id,
            session_id,
            memory_context
        )

    async def _execute_with_natural_language_workflow(
        self,
        user_input: str,
        user_id: str,
        conversation_id: str = None,
        session_id: str = None,
        memory_context: Dict = None
    ) -> Dict[str, Any]:
        """使用自然语言workflow执行"""
        try:
            # 1. 使用LLM router匹配技能
            context = {
                "conversation_history": [],
                "session_state": {}
            }

            route_result = await self.llm_router.route(user_input, context)

            # 处理特殊动作
            if route_result["action"] == "view_skills":
                return {
                    "response": route_result.get("message", "查看技能列表"),
                    "conversation_id": conversation_id,
                    "session_id": session_id,
                    "mode": "direct",
                    "state": "completed"
                }

            elif route_result["action"] == "help":
                # 使用LLM router的帮助响应
                return {
                    "response": "欢迎使用智能助手系统！\n\n我可以帮您：\n- 执行各种技能任务（数据分析、可视化、知识问答等）\n- 查看可用的技能列表\n- 提供操作帮助\n\n使用方法：\n1. 直接描述您的需求，我会自动匹配最合适的技能\n2. 输入\"查看技能\"查看所有可用技能\n3. 在执行过程中，根据提示提供所需信息\n4. 随时输入\"取消\"可以中断当前操作\n\n有什么我可以帮助您的吗？",
                    "conversation_id": conversation_id,
                    "session_id": session_id,
                    "mode": "direct",
                    "state": "completed"
                }

            elif route_result["action"] == "no_match":
                response = "很抱歉，我没有找到能够处理您请求的技能。\n\n"
                response += "建议您：\n"
                response += "- 尝试用更具体的描述重新提问\n"
                response += "- 输入\"查看技能\"查看可用技能列表\n\n"
                return {
                    "response": response,
                    "conversation_id": conversation_id,
                    "session_id": session_id,
                    "mode": "dialogue",
                    "state": "escalated",
                    "available_skills": None,
                    "next_action": "wait_or_escalate"
                }

            elif route_result["action"] == "chat":
                # 普通聊天，使用LLM直接回复
                return {
                    "response": route_result.get("message", "请问您需要什么帮助？"),
                    "conversation_id": conversation_id,
                    "session_id": session_id,
                    "mode": "direct",
                    "state": "completed"
                }

            elif route_result["action"] == "execute_skill":
                skill_name = route_result["skill_name"]
                logger.info(f"LLM router匹配到技能: {skill_name}")

                # 获取技能名称和workflow文本
                skill_md_path = f"{settings.SKILLS_DIR}/{skill_name}/SKILL.md"
                try:
                    with open(skill_md_path, 'r', encoding='utf-8') as f:
                        skill_content = f.read()

                    # 提取workflow部分（## 执行步骤之后的内容）
                    workflow_start = skill_content.find("## 执行步骤")

                    if workflow_start == -1:
                        # 没有workflow定义，直接执行skill
                        result = await self.skill_orchestrator.execute_single(
                            skill_name,
                            route_result.get("intent_parameters", {}),
                            {}
                        )

                        if result.success:
                            return {
                                "response": f"已执行技能：{skill_name}\n\n{str(result.output)}",
                                "conversation_id": conversation_id,
                                "session_id": session_id,
                                "mode": "direct",
                                "state": "completed",
                                "execution_result": result.output
                            }
                        else:
                            return {
                                "response": f"执行失败：{result.error}",
                                "conversation_id": conversation_id,
                                "session_id": session_id,
                                "mode": "direct",
                                "state": "failed",
                                "execution_result": result.output
                            }

                    workflow_text = skill_content[workflow_start:]

                    # 3. 执行natural language workflow
                    workflow_result = await self.workflow_executor.execute(
                        skill_name=skill_name,
                        workflow_text=workflow_text,
                        user_input=user_input,
                        context={}
                    )

                    # 4. 处理workflow执行结果
                    if workflow_result.status == "waiting_input":
                        # 需要用户提供参数
                        state_key = f"{user_id}:{session_id or 'default'}"
                        await self._set_session_state(state_key, {
                            "state": "workflow_execution",
                            "skill_name": skill_name,
                            "workflow_text": workflow_text,
                            "execution_state": workflow_result.execution_state.to_dict(),
                            "timestamp": datetime.now().isoformat()
                        })

                        return {
                            "response": workflow_result.message,
                            "conversation_id": conversation_id,
                            "session_id": session_id,
                            "mode": "dialogue",
                            "state": "workflow_execution",
                            "current_skill": skill_name,
                            "collected_parameters": workflow_result.execution_state.collected_params,
                            "next_action": "collect_parameters",
                            "missing_params": workflow_result.missing_params
                        }

                    elif workflow_result.status == "completed":
                        # 执行完成
                        return {
                            "response": f"执行完成！\n\n{json.dumps(workflow_result.output, ensure_ascii=False, indent=2)}",
                            "conversation_id": conversation_id,
                            "session_id": session_id,
                            "mode": "direct",
                            "state": "completed",
                            "execution_result": workflow_result.output
                        }

                    elif workflow_result.status == "failed":
                        # 执行失败
                        return {
                            "response": f"执行失败：{workflow_result.error}",
                            "conversation_id": conversation_id,
                            "session_id": session_id,
                            "mode": "direct",
                            "state": "failed",
                            "execution_result": None
                        }

                except FileNotFoundError:
                    logger.error(f"Skill文件不存在: {skill_md_path}")
                    return {
                        "response": f"未找到技能：{skill_name}",
                        "conversation_id": conversation_id,
                        "session_id": session_id,
                        "mode": "dialogue",
                        "state": "failed"
                    }

        except Exception as e:
            logger.error(f"Natural language workflow执行失败: {e}")
            # 返回错误信息
            return {
                "response": f"执行出错：{str(e)}",
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "direct",
                "state": "failed"
            }

    # ==================== 传统匹配逻辑已移除 ====================
    # 以下方法已被移除：
    # - _step1_skill_matching_legacy (传统关键词匹配)
    # - _step2_parameter_collection (参数收集)
    # - _step3_skill_execution (技能执行)
    # - _step5_feedback_handling (反馈处理)
    # - _match_skills (关键词匹配)
    # - _parse_skill_selection (解析技能选择)
    # - _show_all_skills (显示技能列表)
    #
    # 现在使用 LLM Router + Natural Language Workflow 完成所有功能
