"""LLM思考和决策相关类定义"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class ActionType(Enum):
    """动作类型枚举"""
    FINAL_ANSWER = "final_answer"
    TOOL_USE = "use_tool"
    CREATE_TODO = "create_todo"
    DISPATCH_SUBAGENT = "dispatch_subagent"
    MODIFY_PARAMETERS = "modify_parameters"
    WAIT_FOR_INPUT = "wait_for_input"


@dataclass
class ToolUse:
    """工具使用指令"""
    tool_name: str
    arguments: Dict[str, Any]
    reasoning: str


@dataclass
class CreateTodo:
    """创建Todo任务"""
    task: str
    description: str
    priority: str = "medium"
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class DispatchSubagent:
    """调度子代理"""
    task_name: str
    task_description: str
    tools: List[str] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []


@dataclass
class FinalAnswer:
    """最终回答"""
    content: str
    reasoning: str = ""


@dataclass
class WaitForInput:
    """等待用户输入"""
    prompt: str
    required_fields: List[str] = None
    
    def __post_init__(self):
        if self.required_fields is None:
            self.required_fields = []


@dataclass
class Thought:
    """LLM思考结果"""
    reasoning: str
    action_type: ActionType
    action_content: Union[FinalAnswer, ToolUse, CreateTodo, DispatchSubagent, WaitForInput]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "reasoning": self.reasoning,
            "action_type": self.action_type.value,
        }
        
        if isinstance(self.action_content, FinalAnswer):
            result["final_answer"] = {
                "content": self.action_content.content,
                "reasoning": self.action_content.reasoning
            }
        elif isinstance(self.action_content, ToolUse):
            result["tool_use"] = {
                "tool_name": self.action_content.tool_name,
                "arguments": self.action_content.arguments,
                "reasoning": self.action_content.reasoning
            }
        elif isinstance(self.action_content, CreateTodo):
            result["create_todo"] = {
                "task": self.action_content.task,
                "description": self.action_content.description,
                "priority": self.action_content.priority,
                "dependencies": self.action_content.dependencies
            }
        elif isinstance(self.action_content, DispatchSubagent):
            result["dispatch_subagent"] = {
                "task_name": self.action_content.task_name,
                "task_description": self.action_content.task_description,
                "tools": self.action_content.tools
            }
        elif isinstance(self.action_content, WaitForInput):
            result["wait_for_input"] = {
                "prompt": self.action_content.prompt,
                "required_fields": self.action_content.required_fields
            }
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Thought":
        """从字典创建"""
        import logging
        logger = logging.getLogger(__name__)
        
        # 处理action_type字段，可能是字符串也可能是ActionType枚举对象
        action_type_value = data["action_type"]
        logger.debug(f"[DEBUG] from_dict received action_type_value: {repr(action_type_value)}, type: {type(action_type_value)}")
        
        # 情况1: 已经是ActionType枚举对象
        if isinstance(action_type_value, ActionType):
            action_type = action_type_value
            logger.debug(f"[DEBUG] action_type already is ActionType: {action_type}")
        else:
            # 转换为字符串
            str_value = str(action_type_value)
            logger.debug(f"[DEBUG] Converting to string: {repr(str_value)}")
            
            # 先尝试直接使用字符串值
            try:
                action_type = ActionType(str_value)
                logger.debug(f"[DEBUG] Successfully created ActionType from string: {action_type}")
            except ValueError:
                # 如果直接使用字符串失败，尝试更多方法
                logger.debug(f"[DEBUG] Failed to create ActionType from {repr(str_value)} directly")
                
                # 情况2: 字符串可能是枚举名称或值
                # 检查是否是 "ActionType.TOOL_USE" 格式
                if "ActionType." in str_value:
                    import re
                    match = re.search(r"ActionType\.(\w+)", str_value)
                    if match:
                        enum_name = match.group(1)
                        logger.debug(f"[DEBUG] Extracted enum name from ActionType.XXX: {enum_name}")
                        try:
                            # 尝试获取枚举成员
                            action_type = getattr(ActionType, enum_name)
                            logger.debug(f"[DEBUG] Got ActionType from attribute: {action_type}")
                        except AttributeError:
                            # 尝试使用字符串值（可能是枚举值而不是名称）
                            try:
                                action_type = ActionType(enum_name.lower())
                                logger.debug(f"[DEBUG] Got ActionType from lowercase: {action_type}")
                            except ValueError as e:
                                raise ValueError(f"Cannot find ActionType for '{str_value}': {e}")
                else:
                    # 情况3: 尝试其他可能的值映射
                    # 常见错误：LLM返回 "tool_use" 但实际上应该是 "use_tool"
                    value_mapping = {
                        "tool_use": "use_tool",
                        "finalanswer": "final_answer",
                        "create_todo": "create_todo",
                        "create todo": "create_todo",
                        "dispatch_subagent": "dispatch_subagent",
                        "dispatch subagent": "dispatch_subagent",
                        "wait_for_input": "wait_for_input",
                        "wait for input": "wait_for_input",
                        "modify_parameters": "modify_parameters",
                        "modify parameters": "modify_parameters"
                    }
                    
                    normalized_value = str_value.strip().lower().replace(" ", "_")
                    if normalized_value in value_mapping:
                        mapped_value = value_mapping[normalized_value]
                        logger.debug(f"[DEBUG] Mapping {repr(normalized_value)} to {repr(mapped_value)}")
                        try:
                            action_type = ActionType(mapped_value)
                            logger.debug(f"[DEBUG] Successfully created ActionType from mapped value: {action_type}")
                        except ValueError as e:
                            raise ValueError(f"Cannot map '{str_value}' to ActionType: {e}")
                    else:
                        # 最后尝试直接使用原始值
                        try:
                            action_type = ActionType(str_value)
                        except ValueError as e:
                            raise ValueError(f"Unknown action type: {str_value}. Valid values are: {[e.value for e in ActionType]}")
        
        reasoning = data.get("reasoning", "")
        
        # 支持两种数据结构格式：
        # 1. 嵌套格式：有 "final_answer"、"tool_use" 等顶级键
        # 2. 扁平格式：有 "action_type" 和 "action_content" 键
        
        action_content = None
        
        # 首先检查是否为扁平格式（LLM通常返回这种格式）
        if "action_content" in data:
            action_content_data = data["action_content"]
            logger.debug(f"[DEBUG] 处理扁平格式 action_content: {action_content_data}")
            
            if action_type == ActionType.FINAL_ANSWER:
                # 支持多种可能的字段名：content、answer、text、response
                content = (action_content_data.get("content") or 
                          action_content_data.get("answer") or 
                          action_content_data.get("text") or 
                          action_content_data.get("response") or 
                          str(action_content_data))
                action_content = FinalAnswer(
                    content=content,
                    reasoning=action_content_data.get("reasoning", "")
                )
            elif action_type == ActionType.TOOL_USE:
                # tool_use 格式
                tool_name = action_content_data.get("tool_name")
                # 对于LLM返回的chat工具，可能需要特殊的参数处理
                if tool_name == "chat":
                    # LLM返回的chat工具可能使用"question"而不是"arguments"
                    if "parameters" in action_content_data and "question" in action_content_data["parameters"]:
                        arguments = {"question": action_content_data["parameters"]["question"]}
                    else:
                        arguments = action_content_data.get("arguments", {})
                else:
                    arguments = action_content_data.get("arguments", {})
                
                action_content = ToolUse(
                    tool_name=tool_name or "unknown_tool",
                    arguments=arguments,
                    reasoning=action_content_data.get("reasoning", "")
                )
            elif action_type == ActionType.CREATE_TODO:
                action_content = CreateTodo(
                    task=action_content_data.get("task", ""),
                    description=action_content_data.get("description", ""),
                    priority=action_content_data.get("priority", "medium"),
                    dependencies=action_content_data.get("dependencies", [])
                )
            elif action_type == ActionType.DISPATCH_SUBAGENT:
                action_content = DispatchSubagent(
                    task_name=action_content_data.get("task_name", ""),
                    task_description=action_content_data.get("task_description", ""),
                    tools=action_content_data.get("tools", [])
                )
            elif action_type == ActionType.WAIT_FOR_INPUT:
                action_content = WaitForInput(
                    prompt=action_content_data.get("prompt", ""),
                    required_fields=action_content_data.get("required_fields", [])
                )
            elif action_type == ActionType.MODIFY_PARAMETERS:
                # MODIFY_PARAMETERS 暂时未实现
                raise ValueError(f"Action type {action_type} not yet implemented for flat format")
        
        # 如果不是扁平格式，检查嵌套格式
        elif "final_answer" in data:
            fa_data = data["final_answer"]
            action_content = FinalAnswer(
                content=fa_data["content"],
                reasoning=fa_data.get("reasoning", "")
            )
        elif "tool_use" in data:
            tu_data = data["tool_use"]
            action_content = ToolUse(
                tool_name=tu_data["tool_name"],
                arguments=tu_data["arguments"],
                reasoning=tu_data.get("reasoning", "")
            )
        elif "create_todo" in data:
            ct_data = data["create_todo"]
            action_content = CreateTodo(
                task=ct_data["task"],
                description=ct_data["description"],
                priority=ct_data.get("priority", "medium"),
                dependencies=ct_data.get("dependencies", [])
            )
        elif "dispatch_subagent" in data:
            ds_data = data["dispatch_subagent"]
            action_content = DispatchSubagent(
                task_name=ds_data["task_name"],
                task_description=ds_data["task_description"],
                tools=ds_data.get("tools", [])
            )
        elif "wait_for_input" in data:
            wi_data = data["wait_for_input"]
            action_content = WaitForInput(
                prompt=wi_data["prompt"],
                required_fields=wi_data.get("required_fields", [])
            )
        else:
            raise ValueError(f"Unknown action type: {action_type}. Data format not recognized.")
        
        return cls(
            reasoning=reasoning,
            action_type=action_type,
            action_content=action_content
        )