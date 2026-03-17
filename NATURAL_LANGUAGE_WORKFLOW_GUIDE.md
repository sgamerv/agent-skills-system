# 自然语言Workflow集成指南

## 概述

本文档说明如何使用基于自然语言的Workflow执行系统，替代之前的YAML workflow和slot定义。

## 主要变化

### 之前的方式（已废弃）
- 使用YAML定义workflow步骤
- 使用slot定义参数
- 硬编码的多轮对话逻辑
- 缺乏灵活性

### 新的方式（当前）
- 使用自然语言描述执行步骤
- LLM动态解析workflow
- 智能参数收集
- 支持MCP工具调用

## Skill定义格式

### 基本模板

```markdown
---
name: skill-name
description: 技能描述
version: 1.0.0
author: Your Name
category: category
tags: [tag1, tag2]
mcp_tools: [tool1, tool2]
---

# 技能名称

## 执行步骤
1. 步骤描述，使用{parameter}标记参数
2. 调用tool_name tool执行某操作
3. 调用skill_name skill处理结果
4. 返回结果给用户

## 使用场景
- 场景1
- 场景2

## 参数说明
- param1: 参数1说明（必填）
- param2: 参数2说明（可选，默认值）

## 注意事项
- 注意事项1
- 注意事项2
```

### 示例：数据分析技能

```markdown
---
name: data-analysis
description: 数据分析技能
version: 2.0.0
mcp_tools: []
---

# 数据分析技能

## 执行步骤
1. 读取用户提供的{data_file}数据文件
2. 根据{analysis_type}执行分析
3. 生成{output_format}格式的结果
4. 返回分析结果

## 参数说明
- data_file: 数据文件路径（必填）
- analysis_type: 分析类型（必填）
- output_format: 输出格式（可选，默认JSON）
```

### 示例：研究演示文稿（包含MCP工具）

```markdown
---
name: research-presentation
description: 研究主题并生成演示文稿
version: 1.0.0
mcp_tools: [web_search, summarize]
---

# 研究并生成演示文稿

## 执行步骤
1. 使用web_search tool获取关于{topic}的最新进展
2. 使用summarize skill对搜索结果进行总结
3. 使用PPT skill生成演示文稿
4. 返回演示文稿文件路径

## 参数说明
- topic: 研究主题（必填）
```

## 集成到Agent Runtime

### 1. 初始化组件

```python
from backend.core.natural_language_workflow import (
    NaturalLanguageWorkflowExecutor,
    MCPToolExecutor
)
from backend.llm.zhipuai_client import ZhipuAIClient

class AgentRuntime:
    def __init__(self):
        # ... 现有初始化 ...

        # MCP工具执行器
        self.mcp_executor = MCPToolExecutor()

        # 注册MCP工具（示例）
        # self.mcp_executor.register_tool("web_search", web_search_client)
        # self.mcp_executor.register_tool("summarize", summarize_client)

        # 自然语言workflow执行器
        self.workflow_executor = NaturalLanguageWorkflowExecutor(
            llm_client=self.llm_client,
            mcp_executor=self.mcp_executor,
            skill_orchestrator=self.skill_orchestrator,
            skill_registry=self.skill_registry
        )
```

### 2. 执行带有workflow的技能

```python
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
        # 没有workflow定义，直接执行技能
        return await self.skill_orchestrator.execute_single(
            skill_name,
            {},
            context
        )

    workflow_text = skill_content[workflow_start:]

    # 执行workflow
    result = await self.workflow_executor.execute(
        skill_name=skill_name,
        workflow_text=workflow_text,
        user_input=user_input,
        context=context,
        execution_state=execution_state
    )

    return result.to_dict()
```

### 3. 处理多轮对话

```python
async def process_chat(
    self,
    user_input: str,
    user_id: str,
    conversation_id: str,
    session_id: str
) -> Dict[str, Any]:
    """处理聊天消息"""

    # 检查是否有活动的workflow执行
    state_key = f"{user_id}:{session_id}"
    execution_state = await self._get_execution_state(state_key)

    if execution_state:
        # 继续执行workflow
        result = await self.workflow_executor.execute(
            skill_name=execution_state.skill_name,
            workflow_text=execution_state.workflow_text,
            user_input=user_input,
            context={},
            execution_state=execution_state
        )

        # 保存执行状态
        if result.status == "waiting_input":
            await self._save_execution_state(state_key, result.execution_state)

        return result.to_dict()

    else:
        # 新的请求，使用LLM路由器匹配技能
        route_result = await self.llm_router.route(
            user_input=user_input,
            context={}
        )

        if route_result["action"] == "execute_skill":
            # 执行技能
            result = await self.execute_skill_with_workflow(
                skill_name=route_result["skill_name"],
                user_input=user_input,
                context={}
            )

            # 如果需要用户输入，保存状态
            if result.get("status") == "waiting_input":
                await self._save_execution_state(
                    state_key,
                    result["execution_state"]
                )

            return result
```

## MCP工具集成

### 1. 创建MCP工具客户端

```python
class WebSearchClient:
    """Web搜索MCP客户端"""

    async def call(self, parameters: Dict) -> str:
        """执行搜索"""
        query = parameters.get("query", "")

        # 实际的搜索逻辑
        # 这里可以使用搜索API，如Google Search API
        results = await self._search(query)

        # 返回搜索结果
        return self._format_results(results)

    async def _search(self, query: str) -> List[Dict]:
        """执行搜索"""
        # 实现搜索逻辑
        pass

    def _format_results(self, results: List[Dict]) -> str:
        """格式化结果"""
        # 实现格式化逻辑
        pass
```

### 2. 注册MCP工具

```python
# 在AgentRuntime初始化时
web_search_client = WebSearchClient()
self.mcp_executor.register_tool("web_search", web_search_client)
```

### 3. 在Skill中使用MCP工具

```markdown
## 执行步骤
1. 使用web_search tool搜索{query}
2. 处理搜索结果
```

## 参数标记语法

### 基本语法

使用 `{parameter_name}` 格式标记参数：

```markdown
## 执行步骤
1. 读取{data_file}文件
2. 使用{analysis_type}方法分析
3. 生成{output_format}格式结果
```

### 参数传递

参数来源：
1. 用户输入中提取
2. 上一步执行结果
3. 已收集的参数

示例：
```markdown
## 执行步骤
1. 使用web_search tool搜索{topic}
2. 使用summarize skill处理上一步的{search_results}
3. 生成关于{topic}的{report_type}报告
```

## 跨Skill调用

### 调用其他Skill

在workflow中可以调用其他skill：

```markdown
## 执行步骤
1. 读取数据文件
2. 调用visualization skill生成图表
3. 调用PPT skill生成演示文稿
4. 返回最终结果
```

### 参数传递

```markdown
## 执行步骤
1. 使用web_search tool搜索{topic}，保存为{search_results}
2. 使用summarize skill处理{search_results}，生成{summary}
3. 使用PPT skill根据{summary}生成演示文稿
```

## 错误处理

### Workflow解析失败

系统会自动降级到规则匹配：

```python
try:
    plan = await self.parser.parse(workflow_text, user_input)
except Exception as e:
    logger.error(f"解析失败: {e}")
    plan = self.parser._fallback_parse(workflow_text, user_input)
```

### 参数提取失败

LLM会多次尝试提取参数：

```python
result = await self._analyze_user_input_for_params(
    execution_state,
    user_input
)

if not result.success:
    # 询问用户重新输入
    prompt = await self._generate_param_prompt(execution_state)
    return ExecutionResult(
        status="waiting_input",
        message=prompt
    )
```

## 性能优化

### 1. 缓存解析结果

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def parse_workflow_cached(workflow_text: str) -> WorkflowPlan:
    return self.parser.parse(workflow_text)
```

### 2. 并行执行独立步骤

```python
import asyncio

# 识别独立步骤并并行执行
independent_steps = self._find_independent_steps(plan)
results = await asyncio.gather(*[
    self._execute_single_step(step, execution_state, context)
    for step in independent_steps
])
```

### 3. 减少LLM调用

- 使用缓存
- 批量参数收集
- 流式输出

## 迁移指南

### 从YAML workflow迁移

#### 旧的格式
```yaml
workflow:
  type: parameter_collection
  steps:
    - name: collect_file
      type: user_input
      prompt: "请提供文件路径"
      parameter: data_file
```

#### 新的格式
```markdown
## 执行步骤
1. 读取用户提供的{data_file}数据文件
```

### 从slot定义迁移

#### 旧的格式
```yaml
slots:
  - name: data_file
    type: file
    required: true
    description: "数据文件"
```

#### 新的格式
```markdown
## 参数说明
- data_file: 数据文件路径（必填）
```

## 测试

### 单元测试

```python
async def test_workflow_parsing():
    parser = NaturalLanguageWorkflowParser(llm_client)

    workflow_text = """
    ## 执行步骤
    1. 读取{data_file}
    2. 分析{analysis_type}
    """

    plan = await parser.parse(workflow_text, "分析销售数据.csv")

    assert len(plan.steps) == 2
    assert "data_file" in plan.required_params
```

### 集成测试

```python
async def test_full_workflow():
    executor = NaturalLanguageWorkflowExecutor(...)

    result = await executor.execute(
        skill_name="data-analysis",
        workflow_text="## 执行步骤\n1. 读取{data_file}",
        user_input="分析data.csv",
        context={}
    )

    assert result.status in ["waiting_input", "completed"]
```

## 常见问题

### Q: 如何添加新的MCP工具？

A: 创建工具客户端类，然后注册：

```python
class MyToolClient:
    async def call(self, parameters: Dict) -> Any:
        # 实现工具逻辑
        pass

# 注册
self.mcp_executor.register_tool("my_tool", MyToolClient())
```

### Q: 如何调试workflow执行？

A: 启用DEBUG日志：

```python
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info(f"执行步骤: {step.description}")
logger.info(f"收集的参数: {execution_state.collected_params}")
```

### Q: 如何处理复杂的条件逻辑？

A: 在workflow描述中明确说明条件：

```markdown
## 执行步骤
1. 如果用户指定了{target_column}，则分析该列
2. 如果未指定，则分析所有列
3. 根据分析结果决定是否调用visualization skill
```

## 参考资料

- [设计文档](./LLM_WORKFLOW_NATURAL_LANGUAGE_DESIGN.md)
- [LLM实现指南](./LLM_IMPLEMENTATION_GUIDE.md)
