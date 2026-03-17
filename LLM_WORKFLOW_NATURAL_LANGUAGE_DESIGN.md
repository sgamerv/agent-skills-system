# 基于自然语言的Workflow执行设计

## 核心理念

不再使用结构化的YAML定义workflow，而是使用自然语言描述执行步骤。LLM负责：
1. 解析自然语言workflow
2. 识别需要的工具和技能
3. 检测缺失信息并询问用户
4. 动态调用MCP工具和其他技能
5. 管理执行流程直到完成

## Skill定义格式

### 简化后的SKILL.md

```markdown
---
name: research-and-presentation
description: 研究并生成演示文稿的技能
version: 1.0.0
author: Agent Team
category: research
tags: [research, presentation, mcp]
requires: []
provides: [presentation-file]
can_call: []
mcp_tools: [web_search, summarize]
---

# 研究并生成演示文稿

## 执行步骤
1. 使用web_search tool获取关于{topic}的最新进展
2. 使用summarize skill对搜索结果进行总结
3. 使用PPT skill根据总结内容生成演示文稿
4. 将生成的演示文稿返回给用户

## 使用示例
用户输入: "帮我研究一下人工智能的最新进展，并生成一个演示文稿"

执行流程:
1. 识别topic为"人工智能"
2. 调用web_search搜索"人工智能最新进展"
3. 调用summarize总结搜索结果
4. 调用PPT技能生成演示文稿
5. 返回演示文稿路径

## 注意事项
- web_search工具需要MCP集成
- 如果用户没有指定具体方向，可以询问用户关注的领域
- 演示文稿可以包含多个部分，每个部分对应一个要点
```

## 核心组件

### 1. NaturalLanguageWorkflowParser

解析自然语言workflow，提取执行步骤和所需工具/技能。

```python
class NaturalLanguageWorkflowParser:
    """自然语言workflow解析器"""

    SYSTEM_PROMPT = """你是一个workflow解析器，负责将自然语言描述的workflow转换为可执行的步骤序列。

解析规则：
1. 识别每个执行步骤
2. 提取步骤中使用的工具或技能
3. 识别步骤间的依赖关系
4. 检测需要用户提供的参数

返回格式必须是JSON。"""

    def __init__(self, llm_client: ZhipuAIClient):
        self.llm_client = llm_client

    async def parse(
        self,
        workflow_text: str,
        user_input: str
    ) -> WorkflowPlan:
        """
        解析自然语言workflow

        Args:
            workflow_text: workflow的自然语言描述
            user_input: 用户原始输入

        Returns:
            WorkflowPlan: 解析出的执行计划
        """
        prompt = self._build_parse_prompt(workflow_text, user_input)

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
                                "tool_type": {"type": "string"},  # "mcp_tool" or "skill"
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
            }
        )

        return WorkflowPlan(
            steps=[self._parse_step(step) for step in result["steps"]],
            required_params=result.get("required_params", []),
            extracted_params=result.get("extracted_params", {}),
            missing_params=result.get("missing_params", [])
        )

    def _build_parse_prompt(self, workflow_text: str, user_input: str) -> str:
        """构建解析提示词"""
        return f"""请解析以下自然语言workflow，提取执行步骤和所需参数。

用户输入: {user_input}

Workflow描述:
{workflow_text}

可用的工具类型:
- mcp_tool: MCP工具（web_search, summarize等）
- skill: 内部技能（data-analysis, visualization等）

请返回JSON格式，包含：
- steps: 步骤列表
- required_params: 必需参数列表
- extracted_params: 从用户输入中提取的参数
- missing_params: 缺失的参数
"""

    def _parse_step(self, step_def: Dict) -> WorkflowStep:
        """解析单个步骤"""
        return WorkflowStep(
            step_number=step_def["step_number"],
            description=step_def["description"],
            tool_type=step_def["tool_type"],
            tool_name=step_def["tool_name"],
            parameters=step_def.get("parameters", {}),
            depends_on=step_def.get("depends_on", []),
            requires_user_input=step_def.get("requires_user_input", False),
            user_prompt=step_def.get("user_prompt", ""),
            status="pending"
        )
```

### 2. MCPToolExecutor

执行MCP工具调用。

```python
class MCPToolExecutor:
    """MCP工具执行器"""

    def __init__(self, mcp_clients: Dict[str, Any]):
        """
        初始化MCP工具执行器

        Args:
            mcp_clients: MCP客户端字典，key为工具名
        """
        self.mcp_clients = mcp_clients

    async def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ToolExecutionResult:
        """
        执行MCP工具

        Args:
            tool_name: 工具名称
            parameters: 参数
            context: 上下文

        Returns:
            ToolExecutionResult: 执行结果
        """
        if tool_name not in self.mcp_clients:
            raise ValueError(f"MCP工具不存在: {tool_name}")

        client = self.mcp_clients[tool_name]

        try:
            # 调用MCP工具
            result = await client.call(parameters)

            return ToolExecutionResult(
                success=True,
                output=result,
                tool_name=tool_name
            )

        except Exception as e:
            logger.error(f"MCP工具执行失败: {e}")
            return ToolExecutionResult(
                success=False,
                error=str(e),
                tool_name=tool_name
            )
```

### 3. NaturalLanguageWorkflowExecutor

核心执行器，负责解析和执行自然语言workflow。

```python
class NaturalLanguageWorkflowExecutor:
    """自然语言workflow执行器"""

    SYSTEM_PROMPT = """你是一个workflow执行管理器，负责动态解析和执行自然语言workflow。

你的职责：
1. 解析workflow步骤
2. 检测缺失信息
3. 决定是否需要询问用户
4. 协调工具和技能调用
5. 管理执行状态

返回格式必须是JSON。"""

    def __init__(
        self,
        llm_client: ZhipuAIClient,
        mcp_executor: MCPToolExecutor,
        skill_orchestrator: SkillOrchestrator,
        skill_registry: SkillRegistry
    ):
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

    async def _initialize_execution(
        self,
        skill_name: str,
        workflow_text: str,
        user_input: str,
        context: Dict[str, Any]
    ) -> ExecutionState:
        """初始化执行状态"""
        # 解析workflow
        plan = await self.parser.parse(workflow_text, user_input)

        return ExecutionState(
            skill_name=skill_name,
            workflow_text=workflow_text,
            user_input=user_input,
            plan=plan,
            current_step=0,
            collected_params=plan.extracted_params,
            missing_params=plan.missing_params,
            execution_results={}
        )

    async def _handle_missing_params(
        self,
        execution_state: ExecutionState,
        user_input: str
    ) -> ExecutionResult:
        """处理缺失参数"""
        # 使用LLM分析用户输入，提取参数
        result = await self._analyze_user_input_for_params(
            execution_state,
            user_input
        )

        if result.success:
            # 更新收集的参数
            execution_state.collected_params.update(result.extracted_params)
            execution_state.missing_params = result.remaining_missing

            # 如果还有缺失参数，继续询问
            if execution_state.missing_params:
                prompt = await self._generate_param_prompt(execution_state)
                return ExecutionResult(
                    status="waiting_input",
                    message=prompt,
                    execution_state=execution_state
                )

            # 参数收集完成，继续执行
            return await self._execute_workflow_steps(execution_state, {})
        else:
            # 分析失败，返回错误
            return ExecutionResult(
                status="failed",
                error=result.error
            )

    async def _execute_workflow_steps(
        self,
        execution_state: ExecutionState,
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """执行workflow步骤"""
        plan = execution_state.plan

        # 执行所有pending步骤
        for step_idx in range(execution_state.current_step, len(plan.steps)):
            step = plan.steps[step_idx]

            # 检查依赖是否满足
            if not self._check_dependencies(step, execution_state):
                continue

            # 执行步骤
            result = await self._execute_single_step(
                step,
                execution_state,
                context
            )

            if result.status == "waiting_input":
                # 需要用户输入
                execution_state.current_step = step_idx
                return ExecutionResult(
                    status="waiting_input",
                    message=result.message,
                    execution_state=execution_state
                )

            if result.status == "failed":
                # 步骤执行失败
                return ExecutionResult(
                    status="failed",
                    error=result.error
                )

            # 保存执行结果
            execution_state.execution_results[step.step_number] = result.output
            execution_state.current_step = step_idx + 1

        # 所有步骤完成
        return ExecutionResult(
            status="completed",
            output=self._generate_final_output(execution_state)
        )

    async def _execute_single_step(
        self,
        step: WorkflowStep,
        execution_state: ExecutionState,
        context: Dict[str, Any]
    ) -> StepExecutionResult:
        """执行单个步骤"""
        if step.requires_user_input and step.user_prompt:
            # 需要用户输入
            return StepExecutionResult(
                status="waiting_input",
                message=step.user_prompt
            )

        # 准备参数
        parameters = self._prepare_step_parameters(step, execution_state)

        if step.tool_type == "mcp_tool":
            # 执行MCP工具
            tool_result = await self.mcp_executor.execute(
                step.tool_name,
                parameters,
                context
            )

            return StepExecutionResult(
                status="completed" if tool_result.success else "failed",
                output=tool_result.output if tool_result.success else None,
                error=tool_result.error
            )

        elif step.tool_type == "skill":
            # 执行内部技能
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
- 已收集的参数: {json.dumps(execution_state.collected_params, ensure_ascii=False)}

请返回JSON格式:
{{
  "success": true/false,
  "extracted_params": {{"param_name": "value"}},
  "remaining_missing": ["param1", "param2"],
  "message": "分析消息"
}}"""

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
            }
        )

        return ParamAnalysisResult(
            success=result["success"],
            extracted_params=result.get("extracted_params", {}),
            remaining_missing=result.get("remaining_missing", []),
            message=result.get("message", "")
        )

    async def _generate_param_prompt(self, execution_state: ExecutionState) -> str:
        """生成参数收集提示词"""
        prompt = f"""请根据当前状态，生成友好的参数收集提示词。

缺失的参数: {', '.join(execution_state.missing_params)}
技能描述: {execution_state.skill_name}

请返回JSON格式:
{{
  "prompt": "友好的提示词"
}}"""

        result = await self.llm_client.structured_output(
            messages=[{"role": "user", "content": prompt}],
            output_schema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"}
                }
            }
        )

        return result.get("prompt", f"请提供以下参数: {', '.join(execution_state.missing_params)}")

    def _prepare_step_parameters(
        self,
        step: WorkflowStep,
        execution_state: ExecutionState
    ) -> Dict[str, Any]:
        """准备步骤参数"""
        parameters = step.parameters.copy()

        # 替换参数占位符
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                param_name = value[1:-1]
                if param_name in execution_state.collected_params:
                    parameters[key] = execution_state.collected_params[param_name]
                elif param_name in execution_state.execution_results:
                    parameters[key] = execution_state.execution_results[param_name]

        # 添加用户输入作为参数
        parameters["user_input"] = execution_state.user_input
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

    def _generate_final_output(self, execution_state: ExecutionState) -> Dict[str, Any]:
        """生成最终输出"""
        return {
            "skill_name": execution_state.skill_name,
            "steps_completed": len(execution_state.execution_results),
            "results": execution_state.execution_results,
            "collected_params": execution_state.collected_params
        }
```

## Skill定义示例

### 示例1: 研究和演示文稿生成

```markdown
---
name: research-and-presentation
description: 研究主题并生成演示文稿
version: 1.0.0
mcp_tools: [web_search, summarize]
---

# 研究并生成演示文稿

## 执行步骤
1. 使用web_search tool获取关于{topic}的最新进展，搜索关键词包括"{topic} 最新趋势"、"{topic} 技术突破"
2. 使用summarize skill对搜索结果进行总结，提取关键信息
3. 使用PPT skill根据总结内容生成演示文稿，每个关键信息点作为一页PPT
4. 将生成的演示文稿文件路径返回给用户

## 使用场景
- 快速研究一个新主题
- 准备演示材料
- 生成技术报告
```

### 示例2: 数据分析可视化

```markdown
---
name: data-visualization
description: 数据分析和可视化
version: 1.0.0
mcp_tools: []
---

# 数据分析和可视化

## 执行步骤
1. 读取用户提供的{data_file}数据文件
2. 检查数据质量，处理缺失值和异常值
3. 根据{analysis_type}执行相应的分析：
   - 描述性统计：计算均值、标准差等统计指标
   - 趋势分析：分析数据随时间的变化
   - 相关性分析：计算变量间相关系数
4. 使用visualization skill生成{chart_type}图表
5. 生成分析报告，包含统计结果和图表说明

## 注意事项
- 如果用户没有指定analysis_type，可以询问用户
- 支持的分析类型：描述性统计、趋势分析、相关性分析
- 支持的图表类型：折线图、柱状图、散点图、热力图
```

## 集成到Agent Runtime

```python
class AgentRuntime:
    def __init__(self):
        # ... 现有初始化 ...

        # MCP工具执行器
        self.mcp_executor = MCPToolExecutor(self.mcp_clients)

        # 自然语言workflow执行器
        self.workflow_executor = NaturalLanguageWorkflowExecutor(
            llm_client=self.llm_client,
            mcp_executor=self.mcp_executor,
            skill_orchestrator=self.skill_orchestrator,
            skill_registry=self.skill_registry
        )

    async def execute_skill_with_workflow(
        self,
        skill_name: str,
        user_input: str,
        context: Dict[str, Any],
        execution_state: Optional[ExecutionState] = None
    ) -> Dict[str, Any]:
        """执行带有workflow的技能"""
        # 获取skill定义
        skill_md_path = os.path.join(settings.SKILLS_DIR, skill_name, "SKILL.md")

        with open(skill_md_path, 'r', encoding='utf-8') as f:
            skill_content = f.read()

        # 提取workflow部分（## 执行步骤之后的内容）
        workflow_start = skill_content.find("## 执行步骤")
        if workflow_start == -1:
            # 没有workflow定义，直接执行
            return await self.skill_orchestrator.execute_single(skill_name, {}, context)

        workflow_text = skill_content[workflow_start:]

        # 执行workflow
        result = await self.workflow_executor.execute(
            skill_name=skill_name,
            workflow_text=workflow_text,
            user_input=user_input,
            context=context,
            execution_state=execution_state
        )

        return result
```

## 优势

1. **更灵活**: 自然语言描述比YAML更灵活，易于理解和修改
2. **智能解析**: LLM动态解析，自动识别工具和技能
3. **自适应**: 根据执行情况动态调整，不需要预先定义所有参数
4. **易于维护**: 不需要维护复杂的slot定义
5. **MCP集成**: 原生支持MCP工具调用
6. **跨技能调用**: 支持调用其他技能，形成技能链

## 注意事项

1. **prompt质量**: 需要精心设计prompt，确保LLM正确解析
2. **错误处理**: 需要完善的错误处理和降级机制
3. **性能考虑**: 每个步骤可能需要LLM调用，注意性能优化
4. **成本控制**: 注意token消耗
5. **测试覆盖**: 需要充分的测试确保各种场景
