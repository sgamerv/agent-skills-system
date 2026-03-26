"""Agent Loop 核心实现"""
import asyncio
import logging
import json
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod

from .agent_session import AgentSession
from .context_manager import ContextManager
from .tool_registry import ToolRegistry, AgentTool
from .thought import Thought, ActionType

logger = logging.getLogger(__name__)


class BaseAgentLoop(ABC):
    """Agent Loop基类"""
    
    @abstractmethod
    async def run_single_turn(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """运行单次循环"""
        pass
    
    @abstractmethod
    async def process_continuation(self, session_id: str, continuation_data: Dict[str, Any]) -> Dict[str, Any]:
        """继续处理（如参数收集后继续）"""
        pass
    
    @abstractmethod
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """获取会话状态"""
        pass
    
    @abstractmethod
    async def clear_session(self, session_id: str):
        """清除会话"""
        pass


class AgentLoop(BaseAgentLoop):
    """Claude Code风格的Agent Loop实现"""
    
    def __init__(
        self,
        llm,
        tool_registry: ToolRegistry,
        session_storage: Optional[Any] = None  # 可以是Redis或其他存储
    ):
        self.llm = llm
        self.tool_registry = tool_registry
        self.session_storage = session_storage
        
        # 会话管理
        self.active_sessions: Dict[str, AgentSession] = {}
        
        # 系统提示
        self.system_prompts = [
            "你是一个智能助手，可以帮助用户完成各种任务。",
            "你可以使用提供的工具来执行具体操作。",
            "思考需要什么工具来完成用户请求，然后使用相应的工具。",
            "如果用户问题需要多步骤完成，你可以创建TODO来规划任务。",
            "在执行过程中，如果需要用户提供更多信息，可以请求用户输入。"
        ]
        
        logger.info("Agent Loop初始化完成")
    
    def _get_session_key(self, session_id: str, user_id: str) -> str:
        """生成会话键"""
        return f"{user_id}:{session_id}" if session_id else f"{user_id}:default"
    
    async def _load_session(self, session_key: str, user_id: str, session_id: str) -> AgentSession:
        """加载会话"""
        # 1. 从内存缓存获取
        if session_key in self.active_sessions:
            logger.info(f"从内存缓存获取会话: {session_key}")
            return self.active_sessions[session_key]
        
        # 2. 从存储加载
        if self.session_storage:
            try:
                session_data = await self._load_from_storage(session_key)
                if session_data:
                    session = AgentSession.from_dict(session_data, self.llm, self.tool_registry)
                    self.active_sessions[session_key] = session
                    logger.info(f"从存储恢复会话: {session_key}")
                    return session
            except Exception as e:
                logger.error(f"从存储加载会话失败: {e}")
        
        # 3. 创建新会话
        logger.info(f"创建新会话: {session_key}")
        session = AgentSession(
            session_id=session_id or "default",
            user_id=user_id,
            llm=self.llm,
            tool_registry=self.tool_registry,
            initial_context={"created_from": "new"}
        )
        
        # 添加系统提示
        for prompt in self.system_prompts:
            session.context.add_system_prompt(prompt)
        
        self.active_sessions[session_key] = session
        return session
    
    async def _load_from_storage(self, session_key: str) -> Optional[Dict[str, Any]]:
        """从存储加载会话数据"""
        if not self.session_storage:
            return None
        
        try:
            # 这里需要根据具体的存储实现进行调整
            if hasattr(self.session_storage, 'get'):
                data = await self.session_storage.get(f"agent_session:{session_key}")
                if data:
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                    return json.loads(data)
        except Exception as e:
            logger.error(f"从存储加载失败: {e}")
        
        return None
    
    async def _save_session(self, session: AgentSession):
        """保存会话"""
        session_key = self._get_session_key(session.session_id, session.user_id)
        
        # 1. 保存到会话存储
        if self.session_storage:
            try:
                session_data = session.to_dict()
                session_json = json.dumps(session_data, ensure_ascii=False)
                
                if hasattr(self.session_storage, 'setex'):
                    # Redis风格
                    await self.session_storage.setex(
                        f"agent_session:{session_key}",
                        3600,  # 1小时过期
                        session_json
                    )
                elif hasattr(self.session_storage, 'set'):
                    # 其他存储
                    await self.session_storage.set(f"agent_session:{session_key}", session_json)
                    
                logger.debug(f"会话保存到存储: {session_key}")
            except Exception as e:
                logger.error(f"保存会话到存储失败: {e}")
        
        # 2. 保持内存缓存
        self.active_sessions[session_key] = session
    
    async def run_single_turn(self, user_input: str, user_id: str, 
                            session_id: Optional[str] = None) -> Dict[str, Any]:
        """运行单次循环（核心入口点）"""
        logger.info(f"运行Agent Loop单次循环: user={user_id}, session={session_id}")
        
        try:
            # 加载会话
            session_key = self._get_session_key(session_id, user_id)
            session = await self._load_session(session_key, user_id, session_id or "default")
            
            # 处理用户输入
            result = await session.process_user_input(user_input)
            
            # 保存会话状态
            await self._save_session(session)
            
            # 添加公共字段
            result.update({
                "session_id": session.session_id,
                "user_id": user_id,
                "agent_loop_version": "1.0"
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Agent Loop执行失败: {e}")
            return {
                "success": False,
                "response": f"Agent Loop执行失败: {str(e)}",
                "state": "failed",
                "session_id": session_id,
                "user_id": user_id,
                "error": str(e)
            }
    
    async def process_continuation(self, user_id: str, session_id: Optional[str],
                                 continuation_data: Dict[str, Any]) -> Dict[str, Any]:
        """继续处理（如参数收集后继续）"""
        logger.info(f"继续处理: user={user_id}, session={session_id}")
        
        try:
            session_key = self._get_session_key(session_id, user_id)
            if session_key not in self.active_sessions:
                return {
                    "success": False,
                    "response": "会话不存在或已过期",
                    "state": "failed",
                    "session_id": session_id,
                    "user_id": user_id
                }
            
            session = self.active_sessions[session_key]
            
            # 检查会话状态
            if session.state != "collecting":
                return {
                    "success": False,
                    "response": "会话当前不处于参数收集状态",
                    "state": "failed",
                    "session_id": session.session_id,
                    "user_id": user_id,
                    "current_state": session.state
                }
            
            # 处理继续逻辑
            # 1. 如果是参数收集继续，处理参数
            if "collected_parameters" in continuation_data:
                params = continuation_data["collected_parameters"]
                for key, value in params.items():
                    session.collected_parameters[key] = value
                    logger.info(f"收集参数: {key} = {value}")
                
                # 检查是否收集完所有必需参数
                missing_params = set(session.required_parameters) - set(session.collected_parameters.keys())
                if missing_params:
                    # 还需要更多参数
                    response = f"还需要以下参数: {', '.join(missing_params)}\n请逐一提供:"
                    for param in missing_params:
                        response += f"\n- {param}"
                    
                    return {
                        "success": True,
                        "response": response,
                        "state": "waiting_input",
                        "session_id": session.session_id,
                        "user_id": user_id,
                        "mode": "dialogue",
                        "required_parameters": list(missing_params),
                        "next_action": "collect_parameters"
                    }
                else:
                    # 参数收集完成，可以继续处理
                    session.state = "thinking"
                    session.required_parameters = []
                    
                    # 构建包含收集参数的输入
                    params_summary = "\n".join([f"{k}: {v}" for k, v in session.collected_parameters.items()])
                    user_input = f"用户提供了以下参数:\n{params_summary}\n\n请继续处理原始请求。"
                    
                    return await self.run_single_turn(user_input, user_id, session_id)
            
            # 2. 其他继续逻辑（TODO继续、工具结果处理等）
            elif "todo_action" in continuation_data:
                action = continuation_data["todo_action"]
                if action == "next_todo":
                    # 执行下一个TODO
                    await self._process_next_todo(session)
                    return await self.run_single_turn("继续执行下一个TODO任务", user_id, session_id)
            
            return {
                "success": False,
                "response": "未知的继续操作类型",
                "state": "failed",
                "session_id": session.session_id,
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"继续处理失败: {e}")
            return {
                "success": False,
                "response": f"继续处理失败: {str(e)}",
                "state": "failed",
                "session_id": session_id,
                "user_id": user_id,
                "error": str(e)
            }
    
    async def _process_next_todo(self, session: AgentSession):
        """处理下一个TODO任务"""
        if not session.todos:
            return
        
        # 找到第一个待处理的TODO
        next_todo = None
        for todo in session.todos:
            if todo["status"] == "pending":
                # 检查依赖是否满足
                deps_met = True
                for dep in todo.get("dependencies", []):
                    dep_todo = next((t for t in session.todos if t["id"] == dep and t["status"] == "completed"), None)
                    if not dep_todo:
                        deps_met = False
                        break
                
                if deps_met:
                    next_todo = todo
                    break
        
        if next_todo:
            next_todo["status"] = "in_progress"
            session.current_todo = next_todo
            
            # 生成处理该TODO的提示
            session.context.add_message(
                "system",
                f"现在开始处理TODO任务: {next_todo['task']}\n描述: {next_todo['description']}"
            )
    
    async def get_session_state(self, user_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """获取会话状态"""
        session_key = self._get_session_key(session_id, user_id)
        
        if session_key in self.active_sessions:
            session = self.active_sessions[session_key]
            return session.to_dict()
        elif self.session_storage:
            try:
                data = await self._load_from_storage(session_key)
                if data:
                    return data
            except Exception as e:
                logger.error(f"从存储获取会话状态失败: {e}")
        
        return {
            "session_id": session_id or "default",
            "user_id": user_id,
            "exists": False,
            "state": "not_found"
        }
    
    async def clear_session(self, user_id: str, session_id: Optional[str] = None):
        """清除会话"""
        session_key = self._get_session_key(session_id, user_id)
        
        # 从内存移除
        if session_key in self.active_sessions:
            del self.active_sessions[session_key]
            logger.info(f"从内存移除会话: {session_key}")
        
        # 从存储删除
        if self.session_storage:
            try:
                if hasattr(self.session_storage, 'delete'):
                    await self.session_storage.delete(f"agent_session:{session_key}")
                    logger.info(f"从存储删除会话: {session_key}")
            except Exception as e:
                logger.error(f"从存储删除会话失败: {e}")
        
        return {"success": True, "session_key": session_key}
    
    async def get_active_sessions_info(self) -> List[Dict[str, Any]]:
        """获取活动会话信息"""
        sessions_info = []
        for key, session in self.active_sessions.items():
            sessions_info.append({
                "session_key": key,
                "session_id": session.session_id,
                "user_id": session.user_id,
                "state": session.state,
                "message_count": len(session.context.messages),
                "todo_count": len(session.todos),
                "current_todo": session.current_todo,
                "created_at": session.context.get_session_metadata("created_at")
            })
        return sessions_info
    
    async def execute_tool_directly(self, tool_name: str, arguments: Dict[str, Any], 
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """直接执行工具（绕过Agent Loop思考）"""
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"工具不存在: {tool_name}"
            }
        
        try:
            # 合并上下文参数
            exec_args = arguments.copy()
            if context:
                exec_args["context"] = context
            
            # 执行工具
            import time
            start_time = time.time()
            result = await tool.execute(**exec_args)
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "tool_name": tool_name,
                "execution_time": execution_time,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"直接执行工具失败: {tool_name}, {e}")
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e)
            }