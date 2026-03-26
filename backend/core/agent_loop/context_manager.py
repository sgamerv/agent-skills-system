"""上下文管理器 - 管理对话历史和工具执行结果"""
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """对话消息"""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ToolResult:
    """工具执行结果"""
    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]
    execution_time: float  # 秒
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "result": self.result,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat()
        }


class ContextManager:
    """上下文管理器"""
    
    def __init__(self, max_messages: int = 100, max_tool_results: int = 50):
        self.max_messages = max_messages
        self.max_tool_results = max_tool_results
        self.messages: List[Message] = []
        self.tool_results: List[ToolResult] = []
        self.system_prompts: List[str] = []
        self.session_metadata: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """添加消息"""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        
        # 保持消息数量不超过限制
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def add_tool_result(self, tool_name: str, arguments: Dict[str, Any], 
                       result: Dict[str, Any], execution_time: float):
        """添加工具执行结果"""
        tool_result = ToolResult(
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            execution_time=execution_time
        )
        self.tool_results.append(tool_result)
        
        # 保持工具结果数量不超过限制
        if len(self.tool_results) > self.max_tool_results:
            self.tool_results = self.tool_results[-self.max_tool_results:]
    
    def add_system_prompt(self, prompt: str):
        """添加系统提示"""
        self.system_prompts.append(prompt)
    
    def set_session_metadata(self, key: str, value: Any):
        """设置会话元数据"""
        self.session_metadata[key] = value
    
    def get_session_metadata(self, key: str, default: Any = None) -> Any:
        """获取会话元数据"""
        return self.session_metadata.get(key, default)
    
    def get_recent_messages(self, count: int = 10, include_tool_results: bool = False) -> List[Dict[str, Any]]:
        """获取最近消息"""
        recent_messages = self.messages[-count:]
        
        if not include_tool_results:
            return [msg.to_dict() for msg in recent_messages]
        
        # 包括工具结果
        formatted_messages = []
        for msg in recent_messages:
            formatted_messages.append(msg.to_dict())
            
            # 如果是工具执行结果，添加对应的工具消息
            # 这里简化处理，实际应该根据消息内容的关联性进行匹配
        
        return formatted_messages
    
    def get_recent_tool_results(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取最近工具执行结果"""
        recent_results = self.tool_results[-count:]
        return [result.to_dict() for result in recent_results]
    
    def get_context_for_llm(self, include_history: bool = True) -> List[Dict[str, Any]]:
        """为LLM构建上下文"""
        # Claude Code风格的上下文构建
        messages = []
        
        # 系统提示
        for prompt in self.system_prompts:
            messages.append({"role": "system", "content": prompt})
        
        # 基础系统提示（可以根据需要进行定制）
        messages.append({
            "role": "system",
            "content": "你是一个智能助手，可以帮助用户完成各种任务。你可以使用提供的工具来执行操作。思考需要什么工具来完成用户请求，然后使用相应的工具。如果用户问题需要多步骤完成，你可以创建TODO来规划任务。"
        })
        
        # 对话历史
        if include_history and self.messages:
            for msg in self.messages:
                if msg.role == "tool":
                    # 工具消息格式化为Claude风格
                    messages.append({
                        "role": "assistant",
                        "content": f"使用工具{msg.metadata.get('tool_name', 'unknown')}"
                    })
                    messages.append({
                        "role": "user",
                        "content": json.dumps(msg.metadata.get('result', {}), ensure_ascii=False, indent=2)
                    })
                else:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
        
        return messages
    
    def get_tools_summary(self) -> str:
        """获取工具使用总结"""
        if not self.tool_results:
            return "还没有使用过任何工具。"
        
        summary = "工具使用历史:\n"
        for i, result in enumerate(self.tool_results[-5:], 1):  # 显示最近5个
            tool_name = result.tool_name
            success = result.result.get("success", False)
            exec_time = result.execution_time
            
            summary += f"{i}. {tool_name}: {'成功' if success else '失败'} (用时: {exec_time:.2f}s)\n"
        
        return summary
    
    def clear(self):
        """清除上下文"""
        self.messages.clear()
        self.tool_results.clear()
        self.system_prompts.clear()
        self.session_metadata.clear()
        logger.info("Context cleared")
    
    def save_state(self) -> Dict[str, Any]:
        """保存状态到字典"""
        return {
            "messages": [msg.to_dict() for msg in self.messages],
            "tool_results": [tr.to_dict() for tr in self.tool_results],
            "system_prompts": self.system_prompts.copy(),
            "session_metadata": self.session_metadata.copy()
        }
    
    def load_state(self, state: Dict[str, Any]):
        """从字典加载状态"""
        self.clear()
        
        # 恢复消息
        for msg_data in state.get("messages", []):
            msg = Message(
                role=msg_data["role"],
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                metadata=msg_data.get("metadata", {})
            )
            self.messages.append(msg)
        
        # 恢复工具结果
        for tr_data in state.get("tool_results", []):
            tr = ToolResult(
                tool_name=tr_data["tool_name"],
                arguments=tr_data["arguments"],
                result=tr_data["result"],
                execution_time=tr_data["execution_time"],
                timestamp=datetime.fromisoformat(tr_data["timestamp"])
            )
            self.tool_results.append(tr)
        
        # 恢复系统提示
        self.system_prompts = state.get("system_prompts", [])
        
        # 恢复会话元数据
        self.session_metadata = state.get("session_metadata", {})
        
        logger.info("Context state loaded")