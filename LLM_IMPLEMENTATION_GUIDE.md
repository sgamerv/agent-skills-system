# 基于LLM的Skill匹配机制实现指南

## 概述

本文档指导如何实现和使用基于智谱AI GLM-5-Turbo的智能Skill匹配系统。该系统参考了Claude和OpenAI的Tool Use/Function Calling机制，实现了更智能的意图分析和技能路由。

## 快速开始

### 1. 配置智谱AI API

在项目根目录创建或编辑 `.env` 文件：

```bash
# 智谱AI配置
ZHIPUAI_API_KEY=your_api_key_here
ZHIPUAI_MODEL=glm-5-turbo
ZHIPUAI_TEMPERATURE=0.7
ZHIPUAI_MAX_TOKENS=2000

# 启用LLM Skill Router
ENABLE_LLM_SKILL_ROUTER=true
LLM_ROUTER_FALLBACK_TO_RULES=true
```

### 2. 安装依赖

```bash
pip install openai>=1.0.0
```

### 3. 初始化LLM客户端

```python
from backend.llm.zhipuai_client import ZhipuAIClient
from backend.config.settings import settings

# 创建LLM客户端
llm_client = ZhipuAIClient(
    api_key=settings.ZHIPUAI_API_KEY,
    model=settings.ZHIPUAI_MODEL,
    temperature=settings.ZHIPUAI_TEMPERATURE,
    max_tokens=settings.ZHIPUAI_MAX_TOKENS
)
```

### 4. 使用LLM Skill Router

```python
from backend.core.llm_skill_router import LLMSkillRouter
from backend.core.skill_manager import SkillRegistry

# 初始化
skill_registry = SkillRegistry(settings.SKILLS_DIR)
router = LLMSkillRouter(llm_client, skill_registry)

# 路由用户请求
result = await router.route(
    user_input="帮我分析一下销售数据",
    context={
        "conversation_history": [],
        "session_state": {}
    }
)

# 处理结果
if result["action"] == "execute_skill":
    print(f"匹配到技能: {result['skill_name']}")
    print(f"相关度: {result['relevance']}")
    print(f"理由: {result['reasoning']}")
```

## 核心组件使用指南

### IntentAnalyzer - 意图分析器

分析用户的意图类型（执行技能、查看技能、修改参数等）。

```python
from backend.core.llm_skill_router import IntentAnalyzer

analyzer = IntentAnalyzer(llm_client)

intent = await analyzer.analyze(
    user_input="帮我分析数据",
    context={
        "conversation_history": [...],
        "session_state": {...},
        "available_skills": [...]
    }
)

print(f"意图类型: {intent.intent_type.value}")
print(f"目标技能: {intent.target_skill}")
print(f"参数: {intent.parameters}")
print(f"置信度: {intent.confidence}")
```

### SkillMatcher - 技能匹配器

根据用户意图匹配最合适的技能。

```python
from backend.core.llm_skill_router import SkillMatcher

matcher = SkillMatcher(llm_client)

matches = await matcher.match(
    intent=intent,
    available_skills=[
        {
            "name": "data-analysis",
            "description": "数据分析技能",
            "slots": [...]
        },
        ...
    ]
)

for match in matches:
    print(f"{match.skill_name}: {match.relevance} - {match.reasoning}")
```

### WorkflowManager - 工作流管理器

管理多轮对话流程，决定下一步动作。

```python
from backend.core.llm_skill_router import WorkflowManager

manager = WorkflowManager(llm_client)

action = await manager.decide_next_action(
    user_input="确认",
    current_state={
        "state": "collecting_parameters",
        "collected_parameters": {"data_file": "data.csv"}
    },
    context={"conversation_history": [...]}
)

print(f"动作类型: {action.action_type}")
print(f"消息: {action.message}")
```

### WorkflowEngine - 工作流执行引擎

执行Skill定义的workflow，管理参数收集和确认流程。

```python
from backend.core.workflow_engine import WorkflowEngine, WorkflowManager

# 初始化
workflow_engine = WorkflowEngine(orchestrator)
workflow_manager = WorkflowManager(workflow_engine)

# 获取workflow定义
skill_metadata = skill_registry.get_skill_metadata("data-analysis")
workflow_def = skill_metadata.get("workflow", {})

# 启动工作流
result = workflow_manager.start_workflow(
    session_id="session_123",
    skill_name="data-analysis",
    workflow_def=workflow_def,
    context={"current_skill": "data-analysis"},
    initial_params={}
)

if result.status == "waiting_input":
    print(f"需要用户输入: {result.message}")

# 用户输入后继续
result = workflow_manager.continue_workflow(
    session_id="session_123",
    user_input="data.csv"
)
```

## Skill Workflow定义

### 基本格式

在SKILL.md的YAML frontmatter中添加workflow定义：

```yaml
---
name: your-skill
description: 技能描述

# Workflow 定义
workflow:
  type: parameter_collection
  steps:
    - name: step_name
      type: user_input
      prompt: "提示消息"
      parameter: param_name
      options:
        - "选项1"
        - "选项2"

    - name: confirm_step
      type: confirmation
      prompt: "确认执行吗？参数：{param_name}"

    - name: execute_step
      type: execute
      prompt: "执行中..."
---
```

### 支持的步骤类型

#### 1. user_input - 用户输入

收集用户输入的参数。

```yaml
- name: collect_file_path
  type: user_input
  prompt: "请输入文件路径"
  parameter: file_path
  options:
    - "data.csv"
    - "results.xlsx"
```

#### 2. confirmation - 确认

请求用户确认操作。

```yaml
- name: confirm_execution
  type: confirmation
  prompt: "即将执行 {action} on {target}，确认吗？"
```

#### 3. execute - 执行

执行Skill。

```yaml
- name: execute_skill
  type: execute
  prompt: "正在执行..."
```

#### 4. conditional - 条件分支

根据条件决定是否继续。

```yaml
- name: check_permission
  type: conditional
  conditions:
    permission: "granted"
```

#### 5. loop - 循环

循环执行某个操作。

```yaml
- name: process_items
  type: loop
  prompt: "处理第 {item_index} 项"
```

### 提示词格式化

Workflow中的prompt可以使用 `{param_name}` 格式进行参数替换：

```yaml
- name: confirm_execution
  type: confirmation
  prompt: |
    即将执行以下操作：
    数据文件：{data_file}
    分析类型：{analysis_type}
    目标列：{target_column or '所有列'}

    确认吗？
```

## 集成到Agent Runtime

### 1. 初始化组件

```python
# 在 agent_runtime.py 的 __init__ 中添加
from backend.llm.zhipuai_client import ZhipuAIClient
from backend.core.llm_skill_router import LLMSkillRouter
from backend.core.workflow_engine import WorkflowEngine, WorkflowManager

class AgentRuntime:
    def __init__(self):
        # ... 现有初始化 ...

        # 初始化LLM组件
        if settings.ENABLE_LLM_SKILL_ROUTER and settings.ZHIPUAI_API_KEY:
            self.llm_client = ZhipuAIClient(
                api_key=settings.ZHIPUAI_API_KEY,
                model=settings.ZHIPUAI_MODEL
            )
            self.llm_router = LLMSkillRouter(self.llm_client, self.skill_registry)
            self.workflow_engine = WorkflowEngine(self.skill_orchestrator)
            self.workflow_manager = WorkflowManager(self.workflow_engine)
        else:
            self.llm_client = None
            self.llm_router = None
            self.workflow_engine = None
            self.workflow_manager = None
```

### 2. 使用LLM路由器

```python
async def _step1_skill_matching(
    self,
    user_input: str,
    user_id: str,
    conversation_id: str = None,
    session_id: str = None,
    memory_context: Dict = None
) -> Dict[str, Any]:
    """技能匹配与推荐"""

    # 检查是否启用LLM路由器
    if self.llm_router:
        # 使用LLM路由器
        context = {
            "conversation_history": await self._get_conversation_history(conversation_id),
            "session_state": await self._get_session_state(f"{user_id}:{session_id or 'default'}")
        }

        route_result = await self.llm_router.route(user_input, context)

        if route_result["action"] == "execute_skill":
            # 使用workflow引擎启动工作流
            skill_name = route_result["skill_name"]
            skill_metadata = self.skill_registry.get_skill_metadata(skill_name)

            if skill_metadata and skill_metadata.get("workflow"):
                workflow_def = skill_metadata["workflow"]
                workflow_result = self.workflow_manager.start_workflow(
                    session_id=session_id or "default",
                    skill_name=skill_name,
                    workflow_def=workflow_def,
                    context={"current_skill": skill_name},
                    initial_params=route_result.get("intent_parameters", {})
                )

                if workflow_result.status in ["waiting_input", "waiting_confirmation"]:
                    return {
                        "response": workflow_result.message,
                        "session_state": {
                            "state": "collecting_parameters",
                            "current_skill": skill_name,
                            "workflow_result": workflow_result
                        }
                    }
            else:
                # 没有workflow定义，使用旧逻辑
                return await self._step2_parameter_collection(...)
    else:
        # 使用旧的规则匹配逻辑
        matched_skills = self._match_skills(user_input)
        # ...
```

### 3. 处理多轮对话

```python
async def _continue_flow(
    self,
    user_input: str,
    user_id: str,
    conversation_id: str = None,
    session_id: str = None,
    session_state: Dict = None
) -> Dict[str, Any]:
    """根据会话状态继续流程"""

    state_key = f"{user_id}:{session_id or 'default'}"
    current_state = session_state.get("state")

    if current_state == "collecting_parameters" and self.workflow_manager:
        # 继续workflow
        workflow_result = self.workflow_manager.continue_workflow(
            session_id=session_id or "default",
            user_input=user_input
        )

        if workflow_result.status in ["waiting_input", "waiting_confirmation"]:
            return {
                "response": workflow_result.message,
                "session_state": session_state
            }
        elif workflow_result.status == "completed":
            # 工作流完成
            return {
                "response": f"执行成功！\n{json.dumps(workflow_result.result, ensure_ascii=False, indent=2)}",
                "session_state": None
            }
        elif workflow_result.status == "failed":
            return {
                "response": f"执行失败：{workflow_result.error}",
                "session_state": None
            }

    # ... 其他状态处理 ...
```

## 测试

### 单元测试

```python
import pytest
from backend.llm.zhipuai_client import ZhipuAIClient

@pytest.mark.asyncio
async def test_llm_client():
    client = ZhipuAIClient(api_key="test_key")

    response = await client.chat_with_system(
        system_prompt="你是一个助手",
        user_message="你好"
    )

    assert response is not None
```

### 集成测试

```python
async def test_skill_routing():
    # 初始化
    llm_client = ZhipuAIClient(api_key=settings.ZHIPUAI_API_KEY)
    skill_registry = SkillRegistry(settings.SKILLS_DIR)
    router = LLMSkillRouter(llm_client, skill_registry)

    # 测试路由
    result = await router.route(
        user_input="分析数据",
        context={}
    )

    assert result["action"] == "execute_skill"
    assert "skill_name" in result
```

## 监控和日志

### 启用日志

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"意图分析结果: {intent.intent_type.value}")
logger.info(f"技能匹配: {matches[0].skill_name}")
```

### 性能监控

```python
import time

start_time = time.time()
result = await router.route(user_input, context)
end_time = time.time()

logger.info(f"路由耗时: {end_time - start_time:.2f}秒")
```

## 错误处理

### LLM API失败

```python
try:
    intent = await analyzer.analyze(user_input, context)
except Exception as e:
    logger.error(f"LLM调用失败: {e}")
    # 降级到规则匹配
    intent = analyzer._fallback_analyze(user_input, context)
```

### 配置降级

```python
if settings.ENABLE_LLM_SKILL_ROUTER and settings.ZHIPUAI_API_KEY:
    # 使用LLM路由器
    pass
elif settings.LLM_ROUTER_FALLBACK_TO_RULES:
    # 使用旧的规则匹配
    pass
else:
    # 直接返回错误
    return {"response": "系统配置错误，请联系管理员"}
```

## 性能优化建议

### 1. 缓存常用意图

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cache_intent_key(user_input: str, context_hash: str) -> str:
    return f"{user_input}:{context_hash}"
```

### 2. 并行请求

```python
import asyncio

# 并行执行多个LLM请求
intent, matches = await asyncio.gather(
    analyzer.analyze(user_input, context),
    matcher.match(intent, skills)
)
```

### 3. 流式响应

```python
async for chunk in llm_client.stream_chat(messages):
    print(chunk, end="", flush=True)
```

## 常见问题

### Q: LLM响应时间过长怎么办？

A: 可以：
1. 降低 `max_tokens` 参数
2. 使用更简单的模型（如 `glm-4-turbo`）
3. 启用降级到规则匹配

### Q: 如何提高匹配准确率？

A: 可以：
1. 改进Skill的描述信息
2. 在SKILL.md中提供更详细的example
3. 调整 `temperature` 参数（越低越确定）

### Q: 如何调试意图分析？

A: 查看日志中的 `reasoning` 字段：

```python
logger.info(f"意图分析理由: {intent.reasoning}")
```

## 参考资源

- [智谱AI API文档](https://open.bigmodel.cn/dev/api)
- [Claude Tool Use文档](https://docs.anthropic.com/claude/docs/tool-use)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [设计文档](./LLM_SKILL_MATCHING_DESIGN.md)
