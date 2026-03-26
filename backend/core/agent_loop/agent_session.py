"""Agent会话管理"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .context_manager import ContextManager
from .tool_registry import ToolRegistry, AgentTool
from .thought import Thought, ActionType, FinalAnswer, ToolUse, CreateTodo, DispatchSubagent, WaitForInput

logger = logging.getLogger(__name__)


class AgentSession:
    """Agent会话"""
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        llm,
        tool_registry: ToolRegistry,
        initial_context: Optional[Dict[str, Any]] = None
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.llm = llm
        self.tool_registry = tool_registry
        
        # 初始化上下文管理器
        self.context = ContextManager()
        
        # 会话状态
        self.state = "initial"  # initial, thinking, tool_use, collecting, done
        self.current_todo = None  # 当前执行的Todo任务
        self.todos = []  # TODO列表
        self.subagents = {}  # 子代理映射
        self.collected_parameters = {}  # 收集的参数
        self.required_parameters = []  # 需要的参数
        
        # 初始化会话元数据
        self.context.set_session_metadata("session_id", session_id)
        self.context.set_session_metadata("user_id", user_id)
        self.context.set_session_metadata("created_at", datetime.now().isoformat())
        
        # 添加上下文
        if initial_context:
            for key, value in initial_context.items():
                self.context.set_session_metadata(key, value)
    
    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """处理用户输入"""
        logger.info(f"处理用户输入: session={self.session_id}, user={self.user_id}")
        
        # 添加上下文消息
        self.context.add_message("user", user_input)
        
        # 开始思考
        self.state = "thinking"
        
        try:
            # 构建LLM上下文
            context_messages = self.context.get_context_for_llm()
            
            # 获取可用工具描述
            available_tools = self.tool_registry.get_all_tools()
            tool_descriptions = self.tool_registry.get_tool_descriptions()
            
            # 调用LLM进行思考（这里需要适配具体的LLM接口）
            thought = await self._llm_think(context_messages, tool_descriptions, user_input)
            
            # 处理思考结果
            result = await self._process_thought(thought)
            return result
            
        except Exception as e:
            logger.error(f"处理用户输入失败: {e}")
            self.state = "initial"
            return {
                "success": False,
                "error": str(e),
                "response": f"处理出错: {str(e)}",
                "state": "failed"
            }
    
    async def _llm_think(
        self, 
        context_messages: List[Dict[str, Any]], 
        tool_descriptions: List[Dict[str, Any]], 
        current_input: str
    ) -> Thought:
        """LLM思考过程"""
        # 构建LLM请求
        # 这里需要根据具体的LLM实现进行调整
        
        # 为了解耦，使用单独的Prompt构建
        prompt = self._build_llm_prompt(context_messages, tool_descriptions, current_input)
        
        try:
            # 调用LLM（这里使用原有系统的调用方式）
            # 先简单实现，后续可以重构
            llm_response = await self.llm.invoke(prompt)
            
            # 解析LLM响应为Thought对象
            thought = self._parse_llm_response(llm_response)
            return thought
            
        except Exception as e:
            logger.error(f"LLM思考失败: {e}")
            # 返回默认思考结果（Fallback）
            return Thought(
                reasoning="LLM调用失败，回退到默认处理",
                action_type=ActionType.FINAL_ANSWER,
                action_content=FinalAnswer(
                    content="抱歉，思考过程中出现了问题。请重试或者简化您的请求。",
                    reasoning=str(e)
                )
            )
    
    def _build_llm_prompt(
        self, 
        context_messages: List[Dict[str, Any]], 
        tool_descriptions: List[Dict[str, Any]], 
        current_input: str
    ) -> str:
        """构建LLM提示词"""
        # 基础系统提示
        prompt_lines = [
            "# 角色设定",
            "你是一个智能助手，可以帮助用户完成各种任务。",
            "你可以使用提供的工具来执行具体操作。",
            "",
            "# 工作流程",
            "1. 理解用户的请求",
            "2. 思考需要什么工具来完成请求",
            "3. 如果需要多个步骤，可以创建TODO来规划任务",
            "4. 执行工具并等待结果",
            "5. 根据结果继续处理或返回最终答案",
            "",
            "# 可选动作类型",
            "1. final_answer: 当你能直接回答用户问题时",
            "2. use_tool: 当你需要使用某个工具时",
            "3. create_todo: 当需要多步骤规划时",
            "4. dispatch_subagent: 当需要子代理专门处理复杂任务时",
            "",
            "# 可用工具",
        ]
        
        for tool in tool_descriptions:
            prompt_lines.append(f"## {tool['name']}")
            prompt_lines.append(f"描述: {tool['description']}")
            prompt_lines.append(f"类别: {tool['category']}")
            prompt_lines.append("参数:")
            for param in tool['parameters']:
                required = "必填" if param['required'] else "可选"
                prompt_lines.append(f"  - {param['name']}: {param['description']} ({param['type']}, {required})")
            prompt_lines.append("")
        
        # 添加对话历史
        prompt_lines.append("# 对话历史")
        for msg in context_messages:
            role_name = {
                "system": "系统",
                "user": "用户",
                "assistant": "助手"
            }.get(msg["role"], msg["role"])
            prompt_lines.append(f"{role_name}: {msg['content'][:200]}...")
        
        # 添加当前输入
        prompt_lines.append("")
        prompt_lines.append(f"# 当前请求")
        prompt_lines.append(f"用户: {current_input}")
        prompt_lines.append("")
        prompt_lines.append("# 请思考并返回JSON格式的响应")
        prompt_lines.append("响应格式:")
        prompt_lines.append('```json')
        prompt_lines.append('{')
        prompt_lines.append('  "reasoning": "你的思考过程",')
        prompt_lines.append('  "action_type": "final_answer | use_tool | create_todo | dispatch_subagent",')
        prompt_lines.append('  "action_content": {')
        prompt_lines.append('    // 根据action_type不同而不同')
        prompt_lines.append('  }')
        prompt_lines.append('}')
        prompt_lines.append('```')
        prompt_lines.append("")
        prompt_lines.append("请思考并返回JSON响应:")
        
        return "\n".join(prompt_lines)
    
    def _parse_llm_response(self, llm_response: Any) -> Thought:
        """解析LLM响应为Thought对象"""
        try:
            # 尝试从响应中提取JSON
            if hasattr(llm_response, 'content'):
                response_text = str(llm_response.content)
            else:
                response_text = str(llm_response)
            
            # 提取JSON部分
            import re
            json_pattern = r'```json\s*(.*?)\s*```'
            json_match = re.search(json_pattern, response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接查找JSON对象
                json_pattern2 = r'\{.*\}'
                json_match = re.search(json_pattern2, response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    # 如果没有JSON，尝试直接从文本推断
                    logger.warning("无法从LLM响应中提取JSON，回退到文本响应")
                    return Thought(
                        reasoning="LLM返回了非JSON格式的响应",
                        action_type=ActionType.FINAL_ANSWER,
                        action_content=FinalAnswer(
                            content=response_text[:500] + ("..." if len(response_text) > 500 else ""),
                            reasoning="直接使用LLM的输出作为回答"
                        )
                    )
            
            # 解析JSON
            logger.debug(f"[DEBUG] JSON字符串: {json_str[:500]}...")
            parsed_data = json.loads(json_str)
            logger.debug(f"[DEBUG] 解析后的数据: {parsed_data}")
            return Thought.from_dict(parsed_data)
            
        except Exception as e:
            logger.error(f"解析LLM响应失败: {e}")
            # 记录原始响应以便调试
            logger.error(f"[DEBUG] 原始响应: {response_text[:500]}...")
            logger.error(f"[DEBUG] 提取的JSON: {json_str[:500] if 'json_str' in locals() else 'N/A'}...")
            # 返回错误处理
            return Thought(
                reasoning=f"解析失败: {str(e)}",
                action_type=ActionType.FINAL_ANSWER,
                action_content=FinalAnswer(
                    content="抱歉，处理您的请求时出现了问题。",
                    reasoning=f"LLM响应解析失败: {str(e)}"
                )
            )
    
    async def _process_thought(self, thought: Thought) -> Dict[str, Any]:
        """处理思考结果"""
        logger.info(f"处理思考结果: action_type={thought.action_type}")
        
        # 添加助手思考消息到上下文
        self.context.add_message(
            "assistant", 
            f"思考: {thought.reasoning}",
            {"thought": thought.to_dict()}
        )
        
        # 根据动作类型处理
        if thought.action_type == ActionType.FINAL_ANSWER:
            return await self._handle_final_answer(thought.action_content)
        elif thought.action_type == ActionType.TOOL_USE:
            return await self._handle_tool_use(thought.action_content)
        elif thought.action_type == ActionType.CREATE_TODO:
            return await self._handle_create_todo(thought.action_content)
        elif thought.action_type == ActionType.DISPATCH_SUBAGENT:
            return await self._handle_dispatch_subagent(thought.action_content)
        elif thought.action_type == ActionType.WAIT_FOR_INPUT:
            return await self._handle_wait_for_input(thought.action_content)
        else:
            logger.warning(f"未知动作类型: {thought.action_type}")
            return {
                "success": False,
                "response": f"未知动作类型: {thought.action_type}",
                "state": "failed"
            }
    
    async def _handle_final_answer(self, final_answer: FinalAnswer) -> Dict[str, Any]:
        """处理最终回答"""
        logger.info(f"返回最终回答: {final_answer.content[:50]}...")
        
        # 添加到上下文
        self.context.add_message("assistant", final_answer.content)
        
        # 更新状态
        self.state = "done"
        
        return {
            "success": True,
            "response": final_answer.content,
            "state": "completed",
            "session_id": self.session_id,
            "user_id": self.user_id,
            "mode": "direct"
        }
    
    async def _handle_tool_use(self, tool_use: ToolUse) -> Dict[str, Any]:
        """处理工具使用"""
        logger.info(f"使用工具: {tool_use.tool_name}")
        
        # 获取工具
        tool = self.tool_registry.get_tool(tool_use.tool_name)
        if not tool:
            return {
                "success": False,
                "response": f"未找到工具: {tool_use.tool_name}",
                "state": "failed"
            }
        
        try:
            # 执行工具
            import time
            start_time = time.time()
            result = await tool.execute(**tool_use.arguments)
            execution_time = time.time() - start_time
            
            # 添加工具结果到上下文
            self.context.add_tool_result(
                tool_name=tool_use.tool_name,
                arguments=tool_use.arguments,
                result=result,
                execution_time=execution_time
            )
            
            # 更新状态
            self.state = "tool_use"
            
            # 准备下一步处理的响应
            return {
                "success": True,
                "response": f"已执行工具 {tool_use.tool_name}",
                "state": "tool_use_completed",
                "session_id": self.session_id,
                "user_id": self.user_id,
                "mode": "dialogue",
                "tool_result": result,
                "next_action": "continue_processing"
            }
            
        except Exception as e:
            logger.error(f"工具执行失败: {e}")
            return {
                "success": False,
                "response": f"工具执行失败: {str(e)}",
                "state": "failed",
                "session_id": self.session_id,
                "user_id": self.user_id
            }
    
    async def _handle_create_todo(self, create_todo: CreateTodo) -> Dict[str, Any]:
        """处理创建Todo"""
        logger.info(f"创建Todo: {create_todo.task}")
        
        # 添加到TODO列表
        todo_item = {
            "id": len(self.todos) + 1,
            "task": create_todo.task,
            "description": create_todo.description,
            "priority": create_todo.priority,
            "dependencies": create_todo.dependencies,
            "status": "pending",  # pending, in_progress, completed, blocked
            "created_at": datetime.now().isoformat()
        }
        self.todos.append(todo_item)
        
        # 如果是第一个TODO，开始执行
        if len(self.todos) == 1:
            self.current_todo = todo_item
            todo_item["status"] = "in_progress"
        
        response = f"已创建Todo任务: {create_todo.task}\n描述: {create_todo.description}"
        
        return {
            "success": True,
            "response": response,
            "state": "todo_created",
            "session_id": self.session_id,
            "user_id": self.user_id,
            "mode": "dialogue",
            "todo": todo_item
        }
    
    async def _handle_dispatch_subagent(self, dispatch: DispatchSubagent) -> Dict[str, Any]:
        """处理调度子代理"""
        logger.info(f"调度子代理: {dispatch.task_name}")
        
        # 这里实现子代理调度逻辑
        # 现在先返回一个占位响应
        
        return {
            "success": True,
            "response": f"已调度子代理处理任务: {dispatch.task_name}",
            "state": "subagent_dispatched",
            "session_id": self.session_id,
            "user_id": self.user_id,
            "mode": "dialogue"
        }
    
    async def _handle_wait_for_input(self, wait_input: WaitForInput) -> Dict[str, Any]:
        """处理等待用户输入"""
        logger.info(f"等待用户输入: {wait_input.prompt[:50]}...")
        
        # 更新状态为收集参数
        self.state = "collecting"
        self.required_parameters = wait_input.required_fields
        
        return {
            "success": True,
            "response": wait_input.prompt,
            "state": "waiting_input",
            "session_id": self.session_id,
            "user_id": self.user_id,
            "mode": "dialogue",
            "required_parameters": wait_input.required_fields,
            "next_action": "collect_parameters"
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "state": self.state,
            "todos": self.todos,
            "current_todo": self.current_todo,
            "collected_parameters": self.collected_parameters,
            "required_parameters": self.required_parameters,
            "context": self.context.save_state()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], llm, tool_registry: ToolRegistry) -> "AgentSession":
        """从字典恢复会话"""
        session = cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            llm=llm,
            tool_registry=tool_registry
        )
        
        # 恢复状态
        session.state = data.get("state", "initial")
        session.todos = data.get("todos", [])
        session.current_todo = data.get("current_todo")
        session.collected_parameters = data.get("collected_parameters", {})
        session.required_parameters = data.get("required_parameters", [])
        
        # 恢复上下文
        if "context" in data:
            session.context.load_state(data["context"])
        
        return session