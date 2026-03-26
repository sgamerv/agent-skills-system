"""工具注册和管理系统"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """工具类别"""
    FILE = "file"
    SHELL = "shell"
    CODE = "code"
    SKILL = "skill"
    METADATA = "metadata"
    PLANNING = "planning"
    DEBUG = "debug"
    MONITORING = "monitoring"


@dataclass
class ToolParameter:
    """工具参数定义"""
    name: str
    description: str
    type: str
    required: bool = True
    default: Any = None


class AgentTool(ABC):
    """Agent工具基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.category = ToolCategory.SKILL  # 默认为技能类
        self.enabled = True
    
    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """工具参数定义"""
        pass
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具"""
        try:
            # 验证参数
            self._validate_parameters(kwargs)
            
            # 执行具体逻辑
            return await self._execute(**kwargs)
        except Exception as e:
            logger.error(f"Tool {self.name} execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "output": None
            }
    
    @abstractmethod
    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """具体执行逻辑（子类实现）"""
        pass
    
    def _validate_parameters(self, provided_params: Dict[str, Any]):
        """验证参数"""
        param_names = {p.name for p in self.parameters}
        required_params = {p.name for p in self.parameters if p.required}
        
        # 检查必填参数
        missing_params = required_params - set(provided_params.keys())
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
        
        # 检查未定义的参数
        extra_params = set(provided_params.keys()) - param_names
        if extra_params:
            logger.warning(f"Ignoring extra parameters: {extra_params}")


class ToolRegistry:
    """工具注册器"""
    
    def __init__(self):
        self._tools: Dict[str, AgentTool] = {}
        self._tool_categories: Dict[ToolCategory, Set[str]] = {cat: set() for cat in ToolCategory}
    
    def register_tool(self, tool: AgentTool):
        """注册工具"""
        if tool.name in self._tools:
            logger.warning(f"Tool {tool.name} already registered, overwriting")
        
        self._tools[tool.name] = tool
        self._tool_categories[tool.category].add(tool.name)
        logger.info(f"Registered tool: {tool.name} ({tool.category.value})")
    
    def unregister_tool(self, tool_name: str):
        """注销工具"""
        if tool_name in self._tools:
            tool = self._tools[tool_name]
            self._tool_categories[tool.category].remove(tool_name)
            del self._tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
    
    def get_tool(self, tool_name: str) -> Optional[AgentTool]:
        """获取工具"""
        return self._tools.get(tool_name)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[AgentTool]:
        """根据类别获取工具"""
        tool_names = self._tool_categories.get(category, set())
        return [self._tools[name] for name in tool_names if name in self._tools and self._tools[name].enabled]
    
    def get_all_tools(self) -> List[AgentTool]:
        """获取所有工具"""
        return [tool for tool in self._tools.values() if tool.enabled]
    
    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """获取所有工具的描述信息"""
        descriptions = []
        for tool in self._tools.values():
            if not tool.enabled:
                continue
                
            descriptions.append({
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "parameters": [
                    {
                        "name": p.name,
                        "description": p.description,
                        "type": p.type,
                        "required": p.required,
                        "default": p.default
                    }
                    for p in tool.parameters
                ]
            })
        return descriptions
    
    def enable_tool(self, tool_name: str):
        """启用工具"""
        if tool_name in self._tools:
            self._tools[tool_name].enabled = True
            logger.info(f"Enabled tool: {tool_name}")
    
    def disable_tool(self, tool_name: str):
        """禁用工具"""
        if tool_name in self._tools:
            self._tools[tool_name].enabled = False
            logger.info(f"Disabled tool: {tool_name}")
    
    def filter_tools_for_context(self, context: Dict[str, Any]) -> List[AgentTool]:
        """根据上下文过滤工具"""
        # 简化的过滤逻辑：可以根据用户意图、当前任务、已用工具等进行智能过滤
        # 当前实现返回所有启用的工具，后续可以优化
        return self.get_all_tools()