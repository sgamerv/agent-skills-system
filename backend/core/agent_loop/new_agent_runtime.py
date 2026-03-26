"""新的Agent运行时 - 基于Agent Loop架构"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from backend.config import settings
from backend.core.llm_provider_factory import LLMProviderFactory
from backend.core.agent_loop import (
    AgentLoop,
    AgentSession,
    ContextManager,
    ToolRegistry,
    AgentTool,
    ToolParameter,
    ToolCategory
)
from backend.core.skill_manager import SkillRegistry, SkillLoader, ResourceManager
from backend.core.skill_orchestrator import SkillOrchestrator
from backend.core.dialogue_manager import DialogueManager
from backend.core.memory import (
    MemoryExtractor,
    MemoryManager,
    MemoryInjector,
    ProfileManager
)
from backend.core.session_manager import MessageManager

logger = logging.getLogger(__name__)


class SkillExecutionTool(AgentTool):
    """Skill执行工具（适配原有的Skill系统）"""
    
    def __init__(self, skill_orchestrator: SkillOrchestrator, skill_name: str, skill_metadata: Dict[str, Any]):
        super().__init__()
        self.skill_orchestrator = skill_orchestrator
        self.skill_name = skill_name
        self.skill_metadata = skill_metadata
        self.name = f"skill_{skill_name}"
        self.category = ToolCategory.SKILL
    
    @property
    def description(self) -> str:
        """工具描述"""
        return self.skill_metadata.get("description", f"执行 {self.skill_name} 技能")
    
    @property
    def parameters(self) -> List[ToolParameter]:
        """工具参数定义"""
        # 从skill_metadata中提取参数定义
        params = []
        
        # 通用参数
        params.append(ToolParameter(
            name="query",
            description="用户查询或指令",
            type="string",
            required=True
        ))
        
        # 如果有slot定义，可以进一步解析
        slots = self.skill_metadata.get('slots', [])
        for slot in slots:
            params.append(ToolParameter(
                name=slot.get("name", "unknown"),
                description=slot.get("description", "参数"),
                type=slot.get("type", "string"),
                required=slot.get("required", False)
            ))
        
        return params
    
    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """执行技能"""
        try:
            # 提取参数
            query = kwargs.get("query", "")
            parameters = {k: v for k, v in kwargs.items() if k != "query"}
            
            # 使用skill orchestrator执行
            result = await self.skill_orchestrator.execute_single(
                self.skill_name,
                parameters,
                {}
            )
            
            if result.success:
                return {
                    "success": True,
                    "output": result.output,
                    "skill_name": self.skill_name,
                    "execution_details": {
                        "success": True,
                        "error": None
                    }
                }
            else:
                return {
                    "success": False,
                    "output": None,
                    "error": result.error,
                    "skill_name": self.skill_name,
                    "execution_details": {
                        "success": False,
                        "error": result.error
                    }
                }
                
        except Exception as e:
            logger.error(f"技能执行失败: {self.skill_name}, {e}")
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "skill_name": self.skill_name
            }


class LLMChatTool(AgentTool):
    """LLM聊天工具（普通问答）"""
    
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
        self.name = "chat"
        self.category = ToolCategory.SKILL
    
    @property
    def description(self) -> str:
        return "回答用户的一般性问题，进行日常对话"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="question",
                description="用户的问题或对话内容",
                type="string",
                required=True
            )
        ]
    
    async def _execute(self, **kwargs) -> Dict[str, Any]:
        question = kwargs.get("question", "")
        
        try:
            response = await self.llm.invoke(question)
            if hasattr(response, 'content'):
                content = str(response.content)
            else:
                content = str(response)
            
            return {
                "success": True,
                "output": content,
                "tool_name": "chat"
            }
        except Exception as e:
            logger.error(f"聊天工具执行失败: {e}")
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }


class NewAgentRuntime:
    """新的Agent运行时（基于Agent Loop）"""
    
    def __init__(
        self,
        llm: ChatOpenAI | None = None,
        redis_client: Any | None = None,
    ) -> None:
        # 使用工厂类创建统一的LLM客户端
        self.llm = llm or LLMProviderFactory.create_llm()
        
        # 初始化原有的技能管理组件（保持兼容）
        self.skill_registry = SkillRegistry(settings.SKILLS_DIR)
        self.skill_loader = SkillLoader(settings.SKILLS_DIR)
        self.resource_manager = ResourceManager(settings.SKILLS_DIR)
        self.skill_orchestrator = SkillOrchestrator(
            self.skill_registry,
            self.skill_loader,
            self.resource_manager,
        )
        
        # 初始化原有的对话和记忆系统
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
        
        # 初始化Redis客户端
        self.redis_client = redis_client
        
        # 初始化新的Agent Loop系统
        self.tool_registry = ToolRegistry()
        self.agent_loop = AgentLoop(self.llm, self.tool_registry, redis_client)
        
        # 构建工具
        self._build_tools()
        
        logger.info("新的Agent运行时初始化完成（基于Agent Loop架构）")
    
    def _build_tools(self):
        """构建工具集"""
        logger.info("构建工具集...")
        
        # 1. 添加聊天工具
        chat_tool = LLMChatTool(self.llm)
        self.tool_registry.register_tool(chat_tool)
        
        # 2. 从技能库添加技能工具
        for skill_name, metadata in self.skill_registry.skill_metadata.items():
            try:
                skill_tool = SkillExecutionTool(self.skill_orchestrator, skill_name, metadata)
                self.tool_registry.register_tool(skill_tool)
                logger.info(f"注册技能工具: {skill_name}")
            except Exception as e:
                logger.error(f"注册技能工具失败: {skill_name}, {e}")
        
        logger.info(f"总共注册工具: {len(self.tool_registry.get_all_tools())}")
    
    async def chat(
        self,
        user_input: str,
        user_id: str,
        conversation_id: str = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        统一聊天接口（兼容原有API）
        
        新的实现基于Agent Loop架构，但返回相同的响应格式
        """
        logger.info(f"新的Agent Loop聊天接口: user={user_id}, session={session_id}")
        
        try:
            # 1. 注入记忆（保持原有功能）
            memory_context = await self.memory_injector.build_context(user_id, user_input)
            
            # 2. 更新用户画像
            await self.profile_manager.increment_messages(user_id)
            
            # 3. 使用Agent Loop处理
            result = await self.agent_loop.run_single_turn(
                user_input=user_input,
                user_id=user_id,
                session_id=session_id
            )
            
            # 4. 保存消息（保持原有功能）
            if result.get("success", False) and "response" in result:
                await self.message_manager.add_message(
                    session_id=session_id or "default",
                    role="user",
                    content=user_input,
                    conversation_id=conversation_id
                )
                await self.message_manager.add_message(
                    session_id=session_id or "default",
                    role="assistant",
                    content=result["response"],
                    conversation_id=conversation_id
                )
            
            # 5. 转换为兼容格式
            compatible_result = self._convert_to_compatible_format(result, conversation_id, session_id)
            return compatible_result
            
        except Exception as e:
            logger.error(f"聊天接口执行失败: {e}")
            return {
                "response": f"处理出错: {str(e)}",
                "conversation_id": conversation_id,
                "session_id": session_id,
                "mode": "direct",
                "state": "failed",
                "error": str(e)
            }
    
    def _convert_to_compatible_format(
        self, 
        loop_result: Dict[str, Any], 
        conversation_id: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """将Agent Loop结果转换为兼容原有API的格式"""
        
        base_result = {
            "response": loop_result.get("response", ""),
            "conversation_id": conversation_id or loop_result.get("conversation_id"),
            "session_id": session_id or loop_result.get("session_id") or "default",
            "mode": loop_result.get("mode", "direct"),
            "state": loop_result.get("state", "completed"),
            "filled_slots": None,
            "next_slot": None,
            "ready_to_execute": loop_result.get("state") == "completed",
            "needs_confirmation": False,
            "available_skills": None,
            "current_slot": None,
            "collected_parameters": loop_result.get("collected_parameters"),
            "execution_result": loop_result.get("execution_result") or loop_result.get("tool_result", {}).get("output"),
            "task_id": loop_result.get("task_id"),
            "feedback_required": False,
            "feedback": None,
            "next_action": loop_result.get("next_action")
        }
        
        # 根据状态设置额外字段
        state = loop_result.get("state", "")
        if state == "waiting_input":
            base_result["needs_confirmation"] = True
            base_result["ready_to_execute"] = False
            base_result["next_action"] = "collect_parameters"
            base_result["current_slot"] = {
                "name": "user_input",
                "description": "请提供所需信息",
                "required": True
            }
        
        elif state == "tool_use_completed":
            base_result["execution_result"] = loop_result.get("tool_result", {}).get("output")
            base_result["mode"] = "dialogue"
            base_result["next_action"] = "continue_processing"
        
        elif state == "todo_created":
            base_result["response"] += f"\n\n已创建TODO任务，共有{len(loop_result.get('todos', []))}个待办任务。"
            base_result["mode"] = "dialogue"
            base_result["next_action"] = "process_todo"
        
        # 如果有工具结果，尝试提取更多信息
        if "tool_result" in loop_result:
            tool_result = loop_result["tool_result"]
            if "skill_name" in tool_result:
                base_result["current_skill"] = tool_result["skill_name"]
                if tool_result.get("success"):
                    base_result["mode"] = "direct"
                    base_result["state"] = "completed"
                else:
                    base_result["mode"] = "dialogue"
                    base_result["state"] = "failed"
        
        return base_result
    
    async def execute_skill(self, skill_name: str, parameters: Dict[str, Any], 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """直接执行技能（兼容原有API）"""
        # 使用Agent Loop的直接工具执行功能
        tool_name = f"skill_{skill_name}"
        
        # 合并参数
        exec_params = parameters.copy()
        if "query" not in exec_params:
            # 如果没有query参数，创建一个默认的
            exec_params["query"] = f"执行技能: {skill_name}"
        
        result = await self.agent_loop.execute_tool_directly(
            tool_name=tool_name,
            arguments=exec_params,
            context=context
        )
        
        # 转换为兼容格式
        if result.get("success", False):
            output = result.get("result", {})
            return {
                "skill_name": skill_name,
                "success": True,
                "output": output.get("output"),
                "error": None
            }
        else:
            return {
                "skill_name": skill_name,
                "success": False,
                "output": None,
                "error": result.get("error", "未知错误")
            }
    
    async def continue_session(self, user_input: str, user_id: str,
                             session_id: str = None, continuation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """继续会话（处理参数收集等）"""
        if continuation_data is None:
            continuation_data = {}
        
        # 添加用户输入到继续数据中
        continuation_data["user_input"] = user_input
        
        # 使用Agent Loop继续处理
        result = await self.agent_loop.process_continuation(
            user_id=user_id,
            session_id=session_id,
            continuation_data=continuation_data
        )
        
        # 转换为兼容格式
        conversation_id = continuation_data.get("conversation_id")
        compatible_result = self._convert_to_compatible_format(result, conversation_id, session_id)
        
        # 保存消息
        if result.get("success", False) and "response" in result:
            await self.message_manager.add_message(
                session_id=session_id or "default",
                role="user",
                content=user_input,
                conversation_id=conversation_id
            )
            await self.message_manager.add_message(
                session_id=session_id or "default",
                role="assistant",
                content=result["response"],
                conversation_id=conversation_id
            )
        
        return compatible_result
    
    async def get_session_state(self, user_id: str, session_id: str = None) -> Dict[str, Any]:
        """获取会话状态"""
        return await self.agent_loop.get_session_state(user_id, session_id)
    
    async def clear_session(self, user_id: str, session_id: str = None) -> Dict[str, Any]:
        """清除会话"""
        return await self.agent_loop.clear_session(user_id, session_id)
    
    def get_tools_info(self) -> List[Dict[str, Any]]:
        """获取工具信息"""
        return self.tool_registry.get_tool_descriptions()
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """获取活动会话信息"""
        try:
            import asyncio
            # 注意：这里可能需要异步调用
            return asyncio.run(self.agent_loop.get_active_sessions_info())
        except Exception as e:
            logger.error(f"获取活动会话失败: {e}")
            return []


# 为了保持兼容性，我们暂时保留原有接口
AgentRuntime = NewAgentRuntime