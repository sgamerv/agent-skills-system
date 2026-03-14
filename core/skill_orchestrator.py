"""技能编排器 - 管理 Skill 间调用和依赖关系"""
import os
import uuid
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import networkx as nx

from core.skill_manager import SkillRegistry, SkillLoader, ResourceManager


@dataclass
class SkillCall:
    """Skill 调用定义"""
    skill_name: str
    parameters: Dict[str, any]
    output_key: Optional[str] = None  # 输出结果的键名,用于传递给下一个 Skill


@dataclass
class SkillExecutionResult:
    """Skill 执行结果"""
    skill_name: str
    success: bool
    output: any
    next_calls: List[SkillCall] = None  # 下一步需要调用的 Skills
    error: Optional[str] = None


class DependencyGraph:
    """Skill 依赖关系图"""
    
    def __init__(self, skill_registry: SkillRegistry):
        self.registry = skill_registry
        self.graph = nx.DiGraph()
        self._build_dependency_graph()
    
    def _build_dependency_graph(self):
        """构建依赖关系图"""
        for skill_name, metadata in self.registry.skill_metadata.items():
            # 添加节点
            self.graph.add_node(skill_name, **metadata)
            
            # 解析 can_call 字段,建立边
            can_call = metadata.get('can_call', [])
            if can_call:
                for called_skill in can_call:
                    if called_skill in self.registry.skill_metadata:
                        self.graph.add_edge(skill_name, called_skill)
    
    def get_execution_order(self, start_skill: str) -> List[str]:
        """
        获取执行顺序(拓扑排序)
        返回从 start_skill 开始可以调用的所有 Skills 的执行顺序
        """
        if start_skill not in self.graph:
            raise ValueError(f"Skill {start_skill} not found")
        
        # 获取所有可达的节点
        reachable = nx.descendants(self.graph, start_skill)
        reachable.add(start_skill)
        
        # 子图并拓扑排序
        subgraph = self.graph.subgraph(reachable)
        execution_order = list(nx.topological_sort(subgraph))
        
        return execution_order
    
    def validate_call_chain(self, caller: str, callee: str) -> bool:
        """验证 caller 是否可以调用 callee"""
        return self.graph.has_edge(caller, callee)
    
    def get_reachable_skills(self, start_skill: str) -> List[str]:
        """获取从 start_skill 可达的所有技能"""
        if start_skill not in self.graph:
            return []
        
        reachable = nx.descendants(self.graph, start_skill)
        return list(reachable)


class SkillOrchestrator:
    """Skill 编排器 - 管理 Skill 间调用"""
    
    def __init__(
        self,
        skill_registry: SkillRegistry,
        skill_loader: SkillLoader,
        resource_manager: ResourceManager
    ):
        self.registry = skill_registry
        self.loader = skill_loader
        self.resource_manager = resource_manager
        self.dependency_graph = DependencyGraph(skill_registry)
        self.execution_history = []
    
    async def execute_with_chain(
        self,
        initial_call: SkillCall,
        context: Dict[str, any] = None
    ) -> Dict[str, any]:
        """
        执行 Skill 调用链
        
        Args:
            initial_call: 初始 Skill 调用
            context: 共享上下文,用于在 Skills 之间传递数据
        
        Returns:
            所有 Skills 的执行结果
        """
        if context is None:
            context = {}
        
        execution_order = self.dependency_graph.get_execution_order(initial_call.skill_name)
        
        results = {}
        call_queue = [initial_call]
        
        for skill_name in execution_order:
            if not call_queue:
                break
            
            # 获取当前需要执行的 Skill 调用
            current_call = self._find_next_call(call_queue, skill_name)
            if not current_call:
                continue
            
            # 执行 Skill
            result = await self._execute_single_skill(current_call, context)
            
            # 保存结果到上下文
            if current_call.output_key:
                context[current_call.output_key] = result.output
            results[skill_name] = result
            
            # 如果 Skill 返回了下一步调用,添加到队列
            if result.next_calls:
                call_queue.extend(result.next_calls)
            
            # 记录执行历史
            self.execution_history.append({
                "skill": skill_name,
                "success": result.success,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "results": results,
            "context": context,
            "execution_order": execution_order
        }
    
    async def execute_single(
        self,
        skill_name: str,
        parameters: Dict[str, any],
        context: Dict[str, any] = None
    ) -> SkillExecutionResult:
        """
        执行单个 Skill
        
        Args:
            skill_name: Skill 名称
            parameters: 执行参数
            context: 上下文数据
        
        Returns:
            执行结果
        """
        call = SkillCall(skill_name=skill_name, parameters=parameters)
        return await self._execute_single_skill(call, context or {})
    
    def _find_next_call(self, call_queue: List[SkillCall], skill_name: str) -> Optional[SkillCall]:
        """从队列中查找指定 Skill 的调用"""
        for i, call in enumerate(call_queue):
            if call.skill_name == skill_name:
                return call_queue.pop(i)
        return None
    
    async def _execute_single_skill(
        self,
        call: SkillCall,
        context: Dict[str, any]
    ) -> SkillExecutionResult:
        """执行单个 Skill"""
        try:
            # 设置当前 caller
            context['_caller'] = call.skill_name
            
            # 检查是否有执行脚本
            script_result = await self._try_execute_script(
                call.skill_name, call.parameters, context
            )
            
            if script_result is not None:
                # 脚本执行成功
                next_calls = self._parse_next_calls(script_result)
                return SkillExecutionResult(
                    skill_name=call.skill_name,
                    success=True,
                    output=script_result,
                    next_calls=next_calls
                )
            
            # 没有脚本,返回提示信息
            return SkillExecutionResult(
                skill_name=call.skill_name,
                success=True,
                output={
                    "message": f"执行了 {call.skill_name}",
                    "parameters": call.parameters
                },
                next_calls=[]
            )
            
        except Exception as e:
            return SkillExecutionResult(
                skill_name=call.skill_name,
                success=False,
                output=None,
                error=str(e)
            )
    
    async def _try_execute_script(
        self,
        skill_name: str,
        parameters: Dict[str, any],
        context: Dict[str, any]
    ) -> Optional[any]:
        """尝试执行 Skill 脚本"""
        script_path = os.path.join(
            self.resource_manager.skills_dir,
            skill_name,
            "scripts",
            "main.py"
        )
        
        if os.path.exists(script_path):
            try:
                return self.resource_manager.execute_script(
                    skill_name,
                    "main.py",
                    **parameters,
                    context=context
                )
            except Exception as e:
                print(f"Error executing script for {skill_name}: {e}")
                return None
        return None
    
    def _parse_next_calls(self, result: any) -> List[SkillCall]:
        """从执行结果中解析下一步的 Skill 调用"""
        next_calls = []
        
        if isinstance(result, dict):
            # 检查结果中是否包含 skill_call 字段
            if 'skill_call' in result:
                call_def = result['skill_call']
                next_calls.append(SkillCall(
                    skill_name=call_def['skill'],
                    parameters=call_def.get('params', {}),
                    output_key=call_def.get('output_key')
                ))
            
            # 检查是否包含多个 skill_calls
            if 'skill_calls' in result:
                for call_def in result['skill_calls']:
                    next_calls.append(SkillCall(
                        skill_name=call_def['skill'],
                        parameters=call_def.get('params', {}),
                        output_key=call_def.get('output_key')
                    ))
        
        return next_calls
    
    def get_execution_history(self) -> List[Dict[str, any]]:
        """获取执行历史"""
        return self.execution_history
    
    def clear_execution_history(self):
        """清空执行历史"""
        self.execution_history = []
