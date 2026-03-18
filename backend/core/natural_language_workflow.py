"""基于自然语言的Workflow执行器"""
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from backend.llm.zhipuai_client import ZhipuAIClient
from backend.core.skill_orchestrator import SkillOrchestrator
from backend.core.skill_manager import SkillRegistry

logger = logging.getLogger(__name__)

# LLM客户端类型
LLMClientType = Union[ZhipuAIClient, Any]  # Any 用于兼容 LangChain ChatOpenAI


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_number: int
    description: str
    tool_type: str  # "mcp_tool" or "skill"
    tool_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[int] = field(default_factory=list)
    requires_user_input: bool = False
    user_prompt: str = ""
    status: StepStatus = StepStatus.PENDING

    def to_dict(self) -> Dict:
        return {
            "step_number": self.step_number,
            "description": self.description,
            "tool_type": self.tool_type,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "depends_on": self.depends_on,
            "requires_user_input": self.requires_user_input,
            "user_prompt": self.user_prompt,
            "status": self.status.value
        }


@dataclass
class WorkflowPlan:
    """工作流计划"""
    steps: List[WorkflowStep]
    required_params: List[str] = field(default_factory=list)
    extracted_params: Dict[str, Any] = field(default_factory=dict)
    missing_params: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "steps": [step.to_dict() for step in self.steps],
            "required_params": self.required_params,
            "extracted_params": self.extracted_params,
            "missing_params": self.missing_params
        }


@dataclass
class ExecutionState:
    """执行状态"""
    skill_name: str
    workflow_text: str
    user_input: str
    plan: WorkflowPlan
    current_step: int = 0
    collected_params: Dict[str, Any] = field(default_factory=dict)
    missing_params: List[str] = field(default_factory=list)
    execution_results: Dict[int, Any] = field(default_factory=dict)
    is_first_execution: bool = True  # 标记是否是首次执行

    def to_dict(self) -> Dict:
        return {
            "skill_name": self.skill_name,
            "workflow_text": self.workflow_text,
            "user_input": self.user_input,
            "current_step": self.current_step,
            "collected_params": self.collected_params,
            "missing_params": self.missing_params,
            "execution_results": self.execution_results,
            "is_first_execution": self.is_first_execution,
            "plan": self.plan.to_dict()
        }


@dataclass
class ExecutionResult:
    """执行结果"""
    status: str  # "pending", "waiting_input", "completed", "failed"
    message: str = ""
    output: Any = None
    error: Optional[str] = None
    execution_state: Optional[ExecutionState] = None
    missing_params: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        result = {
            "status": self.status,
            "message": self.message
        }
        if self.output is not None:
            result["output"] = self.output
        if self.error:
            result["error"] = self.error
        if self.execution_state:
            result["execution_state"] = self.execution_state.to_dict()
        if self.missing_params:
            result["missing_params"] = self.missing_params
        return result


@dataclass
class StepExecutionResult:
    """步骤执行结果"""
    status: str
    output: Any = None
    error: Optional[str] = None
    message: str = ""


@dataclass
class ParamAnalysisResult:
    """参数分析结果"""
    success: bool
    extracted_params: Dict[str, Any]
    remaining_missing: List[str]
    message: str


class NaturalLanguageWorkflowParser:
    """自然语言workflow解析器"""

    SYSTEM_PROMPT = """你是一个workflow解析器，负责将自然语言描述的workflow转换为可执行的步骤序列。

解析规则：
1. 识别每个执行步骤
2. 提取步骤中使用的工具或技能
3. 识别步骤间的依赖关系
4. 检测需要用户提供的参数

工具类型说明：
- mcp_tool: MCP工具（如web_search、summarize等）
- skill: 内部技能（如data-analysis、visualization等）

返回格式必须是有效的JSON。"""

    def __init__(self, llm_client: LLMClientType):
        self.llm_client = llm_client

    async def parse(
        self,
        workflow_text: str,
        user_input: str,
        skill_name: str = ""
    ) -> WorkflowPlan:
        """
        解析自然语言workflow

        Args:
            workflow_text: workflow的自然语言描述
            user_input: 用户原始输入
            skill_name: 技能名称（用于fallback解析）

        Returns:
            WorkflowPlan: 解析出的执行计划
        """
        prompt = self._build_parse_prompt(workflow_text, user_input)

        try:
            # 准备输出示例
            output_example = {
                "steps": [
                    {
                        "step_number": 1,
                        "description": "读取数据文件",
                        "tool_type": "skill",
                        "tool_name": skill_name or "data-analysis",
                        "parameters": {
                            "data_file": "{data_file}"
                        },
                        "depends_on": [],
                        "requires_user_input": False,
                        "user_prompt": ""
                    },
                    {
                        "step_number": 2,
                        "description": "分析数据",
                        "tool_type": "skill",
                        "tool_name": skill_name or "data-analysis",
                        "parameters": {
                            "analysis_type": "{analysis_type}"
                        },
                        "depends_on": [1],
                        "requires_user_input": False,
                        "user_prompt": ""
                    }
                ],
                "required_params": ["data_file", "analysis_type"],
                "extracted_params": {},
                "missing_params": ["data_file", "analysis_type"]
            }

            result = await self.llm_client.structured_output(
                messages=[{"role": "user", "content": prompt}],
                output_schema={
                    "type": "object",
                    "properties": {
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step_number": {"type": "integer"},
                                    "description": {"type": "string"},
                                    "tool_type": {"type": "string"},
                                    "tool_name": {"type": "string"},
                                    "parameters": {"type": "object"},
                                    "depends_on": {"type": "array", "items": {"type": "integer"}},
                                    "requires_user_input": {"type": "boolean"},
                                    "user_prompt": {"type": "string"}
                                }
                            }
                        },
                        "required_params": {"type": "array", "items": {"type": "string"}},
                        "extracted_params": {"type": "object"},
                        "missing_params": {"type": "array", "items": {"type": "string"}}
                    }
                },
                output_example=output_example,
                max_tokens=4000  # 增加 max_tokens 以支持更长的 JSON 响应
            )

            return WorkflowPlan(
                steps=[self._parse_step(step) for step in result.get("steps", [])],
                required_params=result.get("required_params", []),
                extracted_params=result.get("extracted_params", {}),
                missing_params=result.get("missing_params", [])
            )

        except Exception as e:
            logger.error(f"解析workflow失败: {e}")
            # 降级：使用简单的规则解析
            return self._fallback_parse(workflow_text, user_input, skill_name)

    def _build_parse_prompt(self, workflow_text: str, user_input: str) -> str:
        """构建解析提示词"""
        return f"""请解析以下自然语言workflow，提取执行步骤和所需参数。

用户输入: {user_input}

Workflow描述:
{workflow_text}

可用的工具类型:
- mcp_tool: MCP工具（web_search、summarize等）
- skill: 内部技能（data-analysis、visualization、PPT等）

解析要求：
1. 识别每个步骤的序号和描述
2. 判断每个步骤使用的是mcp_tool还是skill
3. 提取工具名称（如web_search、data-analysis等）
4. 识别步骤中提到的参数（用{{param}}格式表示的）
5. 判断步骤间的依赖关系（如"根据上一步结果"）
6. 检测哪些步骤需要用户输入

请返回JSON格式，包含：
- steps: 步骤列表
- required_params: 必需参数列表
- extracted_params: 从用户输入中提取的参数
- missing_params: 缺失的参数列表"""

    def _parse_step(self, step_def: Dict) -> WorkflowStep:
        """解析单个步骤"""
        return WorkflowStep(
            step_number=step_def.get("step_number", 0),
            description=step_def.get("description", ""),
            tool_type=step_def.get("tool_type", "skill"),
            tool_name=step_def.get("tool_name", ""),
            parameters=step_def.get("parameters", {}),
            depends_on=step_def.get("depends_on", []),
            requires_user_input=step_def.get("requires_user_input", False),
            user_prompt=step_def.get("user_prompt", ""),
            status=StepStatus.PENDING
        )

    def _fallback_parse(self, workflow_text: str, user_input: str, skill_name: str = "") -> WorkflowPlan:
        """降级解析：使用简单的规则"""
        import re

        steps = []
        lines = workflow_text.split('\n')
        all_params = set()  # 收集所有参数占位符

        # 使用传入的 skill_name，如果没有则尝试推断
        inferred_skill = skill_name
        if not inferred_skill:
            if "data-analysis" in workflow_text or "数据分析" in workflow_text:
                inferred_skill = "data-analysis"
            elif "visualization" in workflow_text or "可视化" in workflow_text:
                inferred_skill = "visualization"
            elif "knowledge-qa" in workflow_text or "知识问答" in workflow_text:
                inferred_skill = "knowledge-qa"

        step_number = 0
        for line in lines:
            # 匹配步骤：1. xxx 或 1) xxx 或 1、xxx
            match = re.match(r'^\s*(\d+)[.)、]\s*(.+)', line)
            if match:
                step_number += 1
                description = match.group(2)

                # 从步骤描述中提取参数占位符 {param_name}
                param_matches = re.findall(r'\{(\w+)\}', description)
                for param in param_matches:
                    all_params.add(param)

                # 简单判断工具类型
                tool_type = "skill"
                tool_name = inferred_skill  # 使用传入或推断的技能名称
                if "web_search" in description:
                    tool_type = "mcp_tool"
                    tool_name = "web_search"
                elif "summarize" in description:
                    tool_type = "mcp_tool"
                    tool_name = "summarize"
                elif "PPT" in description:
                    tool_name = "PPT"

                # 构建参数字典
                parameters = {}
                for param in param_matches:
                    parameters[param] = f"{{{param}}}"

                steps.append(WorkflowStep(
                    step_number=step_number,
                    description=description,
                    tool_type=tool_type,
                    tool_name=tool_name,
                    parameters=parameters,
                    status=StepStatus.PENDING
                ))

        # 转换为列表
        required_params = list(all_params)

        logger.info(f"Fallback解析完成: {len(steps)} 个步骤, {len(required_params)} 个参数, skill: {inferred_skill}")

        return WorkflowPlan(
            steps=steps,
            required_params=required_params,
            extracted_params={},
            missing_params=required_params  # 初始时所有参数都是缺失的
        )


class MCPToolExecutor:
    """MCP工具执行器"""

    def __init__(self, mcp_clients: Dict[str, Any] = None):
        """
        初始化MCP工具执行器

        Args:
            mcp_clients: MCP客户端字典，key为工具名
        """
        self.mcp_clients = mcp_clients or {}

    def register_tool(self, tool_name: str, client: Any):
        """
        注册MCP工具

        Args:
            tool_name: 工具名称
            client: MCP客户端
        """
        self.mcp_clients[tool_name] = client

    async def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> StepExecutionResult:
        """
        执行MCP工具

        Args:
            tool_name: 工具名称
            parameters: 参数
            context: 上下文

        Returns:
            StepExecutionResult: 执行结果
        """
        if tool_name not in self.mcp_clients:
            logger.warning(f"MCP工具不存在: {tool_name}")
            return StepExecutionResult(
                status="failed",
                error=f"MCP工具不存在: {tool_name}"
            )

        client = self.mcp_clients[tool_name]

        try:
            # 调用MCP工具
            # 这里需要根据实际的MCP客户端API调整
            if hasattr(client, 'call'):
                result = await client.call(parameters)
            elif hasattr(client, 'execute'):
                result = await client.execute(**parameters)
            else:
                # 降级：返回模拟结果
                result = f"模拟执行MCP工具 {tool_name}，参数：{parameters}"

            return StepExecutionResult(
                status="completed",
                output=result
            )

        except Exception as e:
            logger.error(f"MCP工具执行失败: {e}")
            return StepExecutionResult(
                status="failed",
                error=str(e)
            )


class NaturalLanguageWorkflowExecutor:
    """自然语言workflow执行器"""

    def __init__(
        self,
        llm_client: LLMClientType,
        mcp_executor: MCPToolExecutor,
        skill_orchestrator: SkillOrchestrator,
        skill_registry: SkillRegistry
    ):
        """
        初始化workflow执行器

        Args:
            llm_client: LLM客户端
            mcp_executor: MCP工具执行器
            skill_orchestrator: 技能编排器
            skill_registry: 技能注册表
        """
        self.llm_client = llm_client
        self.mcp_executor = mcp_executor
        self.skill_orchestrator = skill_orchestrator
        self.skill_registry = skill_registry
        self.parser = NaturalLanguageWorkflowParser(llm_client)

    async def execute(
        self,
        skill_name: str,
        workflow_text: str,
        user_input: str,
        context: Dict[str, Any],
        execution_state: Optional[ExecutionState] = None
    ) -> ExecutionResult:
        """
        执行自然语言workflow

        Args:
            skill_name: 技能名称
            workflow_text: workflow的自然语言描述
            user_input: 用户输入
            context: 上下文
            execution_state: 执行状态（用于继续执行）

        Returns:
            ExecutionResult: 执行结果
        """
        try:
            # 如果是首次执行，解析workflow
            if execution_state is None:
                execution_state = await self._initialize_execution(
                    skill_name, workflow_text, user_input, context
                )

            # 检查是否有缺失参数
            if execution_state.missing_params:
                return await self._handle_missing_params(execution_state, user_input)

            # 执行workflow步骤
            return await self._execute_workflow_steps(execution_state, context)

        except Exception as e:
            logger.error(f"执行workflow失败: {e}", exc_info=True)
            return ExecutionResult(
                status="failed",
                error=str(e)
            )

    async def _initialize_execution(
        self,
        skill_name: str,
        workflow_text: str,
        user_input: str,
        context: Dict[str, Any]
    ) -> ExecutionState:
        """初始化执行状态"""
        logger.info(f"初始化workflow执行: {skill_name}")

        # 解析workflow，传递技能名称
        plan = await self.parser.parse(workflow_text, user_input, skill_name)

        logger.info(f"解析出 {len(plan.steps)} 个步骤")
        for step in plan.steps:
            logger.info(f"  步骤 {step.step_number}: {step.description}")

        return ExecutionState(
            skill_name=skill_name,
            workflow_text=workflow_text,
            user_input=user_input,
            plan=plan,
            current_step=0,
            collected_params=plan.extracted_params.copy(),
            missing_params=plan.missing_params.copy(),
            execution_results={}
        )

    async def _handle_missing_params(
        self,
        execution_state: ExecutionState,
        user_input: str
    ) -> ExecutionResult:
        """处理缺失参数"""
        logger.info(f"处理缺失参数: {execution_state.missing_params}")
        logger.info(f"是否首次执行: {execution_state.is_first_execution}")

        # 如果这是首次执行，生成参数收集提示
        if execution_state.is_first_execution:
            prompt = await self._generate_param_prompt(execution_state)
            logger.info(f"首次检测到缺失参数，生成提示: {prompt[:100]}...")
            # 标记为非首次执行
            execution_state.is_first_execution = False
            return ExecutionResult(
                status="waiting_input",
                message=prompt,
                execution_state=execution_state,
                missing_params=execution_state.missing_params
            )

        # 使用LLM分析用户输入，提取参数
        result = await self._analyze_user_input_for_params(
            execution_state,
            user_input
        )

        if result.success:
            # 更新收集的参数
            execution_state.collected_params.update(result.extracted_params)
            execution_state.missing_params = result.remaining_missing

            logger.info(f"提取参数: {result.extracted_params}")
            logger.info(f"剩余缺失参数: {execution_state.missing_params}")

            # 如果还有缺失参数，继续询问
            if execution_state.missing_params:
                prompt = await self._generate_param_prompt(execution_state)
                return ExecutionResult(
                    status="waiting_input",
                    message=prompt,
                    execution_state=execution_state,
                    missing_params=execution_state.missing_params
                )

            # 参数收集完成，继续执行
            return await self._execute_workflow_steps(execution_state, {})
        else:
            # 分析失败，返回错误
            logger.error(f"参数分析失败: {result.message}")
            return ExecutionResult(
                status="failed",
                error=result.message
            )

    async def _execute_workflow_steps(
        self,
        execution_state: ExecutionState,
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """执行workflow步骤"""
        plan = execution_state.plan

        logger.info(f"开始执行workflow步骤，当前步骤: {execution_state.current_step}/{len(plan.steps)}")

        # 执行所有pending步骤
        for step_idx in range(execution_state.current_step, len(plan.steps)):
            step = plan.steps[step_idx]

            # 检查依赖是否满足
            if not self._check_dependencies(step, execution_state):
                logger.info(f"步骤 {step.step_number} 依赖未满足，跳过")
                step.status = StepStatus.SKIPPED
                continue

            # 检查是否需要用户输入
            if step.requires_user_input and step.user_prompt:
                logger.info(f"步骤 {step.step_number} 需要用户输入")
                execution_state.current_step = step_idx
                return ExecutionResult(
                    status="waiting_input",
                    message=step.user_prompt,
                    execution_state=execution_state
                )

            # 执行步骤
            step.status = StepStatus.IN_PROGRESS
            result = await self._execute_single_step(
                step,
                execution_state,
                context
            )

            if result.status == "completed":
                step.status = StepStatus.COMPLETED
                execution_state.execution_results[step.step_number] = result.output
                execution_state.current_step = step_idx + 1
                logger.info(f"步骤 {step.step_number} 执行完成")
            elif result.status == "waiting_input":
                # 步骤需要用户输入，返回等待状态
                step.status = StepStatus.PENDING
                execution_state.current_step = step_idx
                prompt = result.output.get("prompt", "请提供更多信息")
                return ExecutionResult(
                    status="waiting_input",
                    message=prompt,
                    execution_state=execution_state,
                    missing_params=result.output.get("missing_params", [])
                )
            else:
                # 步骤执行失败
                step.status = StepStatus.FAILED
                logger.error(f"步骤 {step.step_number} 执行失败: {result.error}")
                return ExecutionResult(
                    status="failed",
                    error=result.error
                )

        # 所有步骤完成
        logger.info("所有workflow步骤执行完成")
        return ExecutionResult(
            status="completed",
            output=self._generate_final_output(execution_state),
            message="Workflow执行完成"
        )

    async def _execute_single_step(
        self,
        step: WorkflowStep,
        execution_state: ExecutionState,
        context: Dict[str, Any]
    ) -> StepExecutionResult:
        """执行单个步骤"""
        logger.info(f"执行步骤 {step.step_number}: {step.description}")

        # 检查参数是否完整
        param_check = self._check_step_parameters(step, execution_state)
        if not param_check["complete"]:
            # 参数不完整，生成提示信息
            missing_params = param_check["missing"]
            prompt = await self._generate_param_request_prompt(
                step,
                missing_params,
                execution_state
            )
            logger.info(f"步骤 {step.step_number} 缺少参数: {missing_params}")
            return StepExecutionResult(
                status="waiting_input",
                output={"prompt": prompt, "missing_params": missing_params},
                error=f"缺少必需参数: {', '.join(missing_params)}"
            )

        # 准备参数
        parameters = self._prepare_step_parameters(step, execution_state)

        try:
            if step.tool_type == "mcp_tool":
                # 执行MCP工具
                logger.info(f"调用MCP工具: {step.tool_name}")
                tool_result = await self.mcp_executor.execute(
                    step.tool_name,
                    parameters,
                    context
                )

                return tool_result

            elif step.tool_type == "skill":
                # 执行内部技能
                logger.info(f"调用内部技能: {step.tool_name}")
                skill_result = await self.skill_orchestrator.execute_single(
                    step.tool_name,
                    parameters,
                    context
                )

                return StepExecutionResult(
                    status="completed" if skill_result.success else "failed",
                    output=skill_result.output if skill_result.success else None,
                    error=skill_result.error
                )

            else:
                return StepExecutionResult(
                    status="failed",
                    error=f"未知的工具类型: {step.tool_type}"
                )

        except Exception as e:
            logger.error(f"步骤执行失败: {e}")
            return StepExecutionResult(
                status="failed",
                error=str(e)
            )

    async def _analyze_user_input_for_params(
        self,
        execution_state: ExecutionState,
        user_input: str
    ) -> ParamAnalysisResult:
        """分析用户输入，提取参数"""
        prompt = f"""请分析用户的输入，提取workflow所需的参数。

当前缺失的参数: {', '.join(execution_state.missing_params)}
用户输入: {user_input}

上下文信息:
- 技能名称: {execution_state.skill_name}
- 用户原始输入: {execution_state.user_input}
- 已收集的参数: {json.dumps(execution_state.collected_params, ensure_ascii=False)}

请仔细分析用户的输入，提取能够提供的参数。如果用户提供了所有缺失参数，则success为true。

请返回JSON格式:
{{
  "success": true/false,
  "extracted_params": {{"param_name": "value"}},
  "remaining_missing": ["param1", "param2"],
  "message": "分析消息"
}}"""

        try:
            result = await self.llm_client.structured_output(
                messages=[{"role": "user", "content": prompt}],
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "extracted_params": {"type": "object"},
                        "remaining_missing": {"type": "array", "items": {"type": "string"}},
                        "message": {"type": "string"}
                    }
                },
                max_tokens=2000  # 参数提取的响应相对较短
            )

            return ParamAnalysisResult(
                success=result.get("success", False),
                extracted_params=result.get("extracted_params", {}),
                remaining_missing=result.get("remaining_missing", execution_state.missing_params),
                message=result.get("message", "")
            )

        except Exception as e:
            logger.error(f"参数分析失败: {e}")
            # 降级：返回失败
            return ParamAnalysisResult(
                success=False,
                extracted_params={},
                remaining_missing=execution_state.missing_params,
                message="参数分析失败"
            )

    async def _generate_param_prompt(self, execution_state: ExecutionState) -> str:
        """生成参数收集提示词"""
        # 不使用LLM，直接生成友好的提示
        missing_params_desc = "、".join([f"**{p}**" for p in execution_state.missing_params])

        prompt = f"为了帮您执行 **{execution_state.skill_name}** 任务，我需要以下信息：\n\n"
        prompt += f"• {missing_params_desc}\n\n"
        prompt += f"请您提供这些信息，以便我继续为您服务。"

        return prompt

    def _prepare_step_parameters(
        self,
        step: WorkflowStep,
        execution_state: ExecutionState
    ) -> Dict[str, Any]:
        """准备步骤参数"""
        parameters = step.parameters.copy()

        # 替换参数占位符
        for key, value in list(parameters.items()):
            if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                param_name = value[1:-1]

                # 先从收集的参数中查找
                if param_name in execution_state.collected_params:
                    parameters[key] = execution_state.collected_params[param_name]
                # 再从执行结果中查找
                elif param_name in execution_state.execution_results:
                    parameters[key] = execution_state.execution_results[param_name]
                # 如果找不到，保留原值
                else:
                    logger.warning(f"参数 {param_name} 未找到")

        # 添加用户输入
        parameters["user_input"] = execution_state.user_input

        # 添加所有已收集的参数
        parameters.update(execution_state.collected_params)

        return parameters

    def _check_dependencies(
        self,
        step: WorkflowStep,
        execution_state: ExecutionState
    ) -> bool:
        """检查步骤依赖"""
        for dep_step in step.depends_on:
            if dep_step not in execution_state.execution_results:
                return False
        return True

    def _check_step_parameters(
        self,
        step: WorkflowStep,
        execution_state: ExecutionState
    ) -> Dict[str, Any]:
        """
        检查步骤参数是否完整

        Args:
            step: 工作流步骤
            execution_state: 执行状态

        Returns:
            Dict: {"complete": bool, "missing": List[str]}
        """
        missing_params = []

        # 检查步骤参数中的占位符
        for key, value in step.parameters.items():
            if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                param_name = value[1:-1]
                # 检查参数是否可用
                if param_name not in execution_state.collected_params and \
                   param_name not in execution_state.execution_results:
                    missing_params.append(param_name)
                    logger.warning(f"步骤 {step.step_number} 缺少参数: {param_name}")

        return {
            "complete": len(missing_params) == 0,
            "missing": missing_params
        }

    async def _generate_param_request_prompt(
        self,
        step: WorkflowStep,
        missing_params: List[str],
        execution_state: ExecutionState
    ) -> str:
        """
        生成参数请求提示

        Args:
            step: 工作流步骤
            missing_params: 缺失的参数列表
            execution_state: 执行状态

        Returns:
            str: 参数请求提示
        """
        # 降级到简单提示（优先使用，避免LLM调用失败）
        param_desc = "、".join([f"**{p}**" for p in missing_params])
        return (
            f"执行步骤 {step.step_number} 时需要您提供以下参数：{param_desc}\n\n"
            f"当前操作：{step.description}\n\n"
            f"请提供这些参数以便继续执行。"
        )

    def _generate_final_output(self, execution_state: ExecutionState) -> Dict[str, Any]:
        """生成最终输出"""
        return {
            "skill_name": execution_state.skill_name,
            "steps_completed": len(execution_state.execution_results),
            "total_steps": len(execution_state.plan.steps),
            "results": execution_state.execution_results,
            "collected_params": execution_state.collected_params
        }
