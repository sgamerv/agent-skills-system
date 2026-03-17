# 基于LLM的Skill匹配机制设计文档

## 1. 背景与目标

### 1.1 现有问题
当前系统使用简单的关键词匹配进行技能选择，存在以下问题：
- 匹配精度低，容易误判用户意图
- 无法理解复杂的自然语言表达
- 多轮问答逻辑硬编码在代码中，缺乏灵活性
- 无法根据上下文动态调整交互策略

### 1.2 优化目标
- 引入智谱AI GLM-5-Turbo模型实现智能技能匹配
- 参考Claude和OpenAI的实现方式，将多轮问答逻辑交给LLM和Skill的workflow控制
- 提升系统理解用户意图的能力
- 实现更灵活、更智能的交互流程

## 2. 核心设计理念

### 2.1 LLM驱动的Skill匹配
```
用户输入 → LLM意图分析 → 匹配最适合的Skill → 返回推荐结果
```

### 2.2 Workflow控制的多轮对话
```
用户输入 → LLM分析当前状态 → 决定下一步动作
         → 执行Skill/收集参数/请求确认 → 循环直到完成
```

### 2.3 上下文感知的交互
- 维护对话历史和会话状态
- LLM根据上下文理解用户意图
- 动态调整交互策略

## 3. 系统架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户界面                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Agent Runtime                          │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Session Manager │  │  Memory Manager │                  │
│  └─────────────────┘  └─────────────────┘                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         LLM-based Skill Router (NEW)                 │   │
│  │  ┌──────────────┐  ┌──────────────┐                 │   │
│  │  │ Intent Analyzer│  │ Skill Matcher │                 │   │
│  │  └──────────────┘  └──────────────┘                 │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Skill Orchestrator                     │   │
│  │  ┌──────────────┐  ┌──────────────┐                 │   │
│  │  │ Skill Loader  │  │ Dependency   │                 │   │
│  │  │               │  │   Graph      │                 │   │
│  │  └──────────────┘  └──────────────┘                 │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
         ┌────────────────────┐
         │   智谱AI GLM-5-Turbo │
         └────────────────────┘
```

### 3.2 模块职责

#### 3.2.1 LLM Skill Router (新增)
- **Intent Analyzer**: 分析用户输入，提取意图和参数
- **Skill Matcher**: 基于意图匹配最合适的Skill
- **Workflow Manager**: 管理多轮对话流程

#### 3.2.2 Skill Orchestrator (优化)
- 保留现有依赖图管理功能
- 新增Workflow执行引擎
- 支持LLM驱动的动态决策

## 4. 核心实现方案

### 4.1 LLM Skill Router

#### 4.1.1 意图分析（Intent Analysis）
```python
class IntentAnalyzer:
    async def analyze(self, user_input: str, context: Dict) -> Intent:
        """
        分析用户意图

        Args:
            user_input: 用户输入
            context: 上下文（对话历史、会话状态等）

        Returns:
            Intent: 意图对象，包含：
                - intent_type: 意图类型（执行技能、查看技能、修改参数等）
                - parameters: 提取的参数
                - confidence: 置信度
        """
        prompt = self._build_intent_prompt(user_input, context)
        response = await self.llm_client.chat(prompt)
        return self._parse_intent(response)
```

**提示词设计**：
```
你是一个智能助手，负责分析用户意图。根据用户的输入和对话历史，判断用户想要做什么。

用户输入: {user_input}

对话历史:
{conversation_history}

当前会话状态:
{session_state}

可用技能:
{available_skills}

请分析用户意图并返回JSON格式:
{{
  "intent_type": "execute_skill|view_skills|modify_parameters|confirm|reject",
  "target_skill": "skill_name",
  "parameters": {{"param_name": "value"}},
  "confidence": 0.9,
  "reasoning": "分析理由"
}}
```

#### 4.1.2 技能匹配（Skill Matching）
```python
class SkillMatcher:
    async def match(
        self,
        intent: Intent,
        available_skills: List[SkillMetadata]
    ) -> List[SkillMatch]:
        """
        匹配最合适的技能

        Args:
            intent: 用户意图
            available_skills: 可用技能列表

        Returns:
            List[SkillMatch]: 匹配结果，按相关度排序
        """
        prompt = self._build_match_prompt(intent, available_skills)
        response = await self.llm_client.chat(prompt)
        return self._parse_matches(response)
```

**提示词设计**：
```
根据用户意图，从以下技能中选择最匹配的技能。

用户意图: {intent_type}
提取参数: {parameters}

可用技能列表:
{skills_list}

请选择最匹配的技能并返回JSON格式:
{{
  "matches": [
    {{
      "skill_name": "skill_name",
      "relevance": 0.95,
      "reasoning": "匹配理由"
    }}
  ],
  "need_more_info": false,
  "missing_parameters": []
}}
```

#### 4.1.3 Workflow Manager（多轮对话管理）
```python
class WorkflowManager:
    async def decide_next_action(
        self,
        user_input: str,
        current_state: WorkflowState,
        context: Dict
    ) -> NextAction:
        """
        决定下一步动作

        Args:
            user_input: 用户输入
            current_state: 当前工作流状态
            context: 上下文

        Returns:
            NextAction: 下一步动作
                - action_type: 动作类型
                - target: 目标（技能名称、参数名等）
                - message: 要发送给用户的消息
        """
        prompt = self._build_decision_prompt(user_input, current_state, context)
        response = await self.llm_client.chat(prompt)
        return self._parse_action(response)
```

**提示词设计**：
```
你是一个智能助手，负责管理多轮对话流程。

当前状态: {current_state}
历史交互: {history}
用户最新输入: {user_input}

可用动作:
- execute_skill: 执行技能
- collect_parameter: 收集参数
- confirm: 请求确认
- modify: 修改参数
- complete: 完成任务

请决定下一步动作并返回JSON格式:
{{
  "action_type": "execute_skill|collect_parameter|confirm|modify|complete",
  "target": "skill_name or parameter_name",
  "message": "要发送给用户的消息",
  "parameters": {{"key": "value"}}
}}
```

### 4.2 智谱AI集成

#### 4.2.1 LLM客户端封装
```python
class ZhipuAIClient:
    """智谱AI客户端"""

    def __init__(self, api_key: str, model: str = "glm-5-turbo"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4"
        )

    async def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        聊天接口

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            str: 模型回复
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
```

#### 4.2.2 配置管理
```python
# config/settings.py
class Settings(BaseSettings):
    # 智谱AI配置
    ZHIPUAI_API_KEY: str = ""
    ZHIPUAI_MODEL: str = "glm-5-turbo"
    ZHIPUAI_TEMPERATURE: float = 0.7
    ZHIPUAI_MAX_TOKENS: int = 2000
```

### 4.3 Workflow定义

#### 4.3.1 Skill元数据扩展
```yaml
# skills/xxx/SKILL.md
---
name: data-analysis
description: 数据分析技能
version: "1.0.0"

# 新增：工作流定义
workflow:
  type: parameter_collection
  steps:
    - name: collect_data_source
      type: user_input
      prompt: "请提供数据源路径或上传数据文件"
      parameter: data_source

    - name: collect_analysis_type
      type: user_input
      prompt: "请选择分析类型：描述性统计、趋势分析、相关性分析"
      parameter: analysis_type
      options:
        - 描述性统计
        - 趋势分析
        - 相关性分析

    - name: confirm
      type: confirmation
      prompt: "即将执行以下分析：{analysis_type} on {data_source}，确认吗？"

slots:
  - name: data_source
    type: string
    required: true

  - name: analysis_type
    type: enum
    required: true
    values:
      - 描述性统计
      - 趋势分析
      - 相关性分析
---
# Skill指令内容...
```

#### 4.3.2 Workflow执行引擎
```python
class WorkflowEngine:
    """工作流执行引擎"""

    async def execute_workflow(
        self,
        skill_name: str,
        workflow_def: Dict,
        context: Dict
    ) -> WorkflowResult:
        """
        执行工作流

        Args:
            skill_name: 技能名称
            workflow_def: 工作流定义
            context: 上下文

        Returns:
            WorkflowResult: 执行结果
        """
        current_step = 0
        collected_params = {}

        while current_step < len(workflow_def['steps']):
            step = workflow_def['steps'][current_step]

            if step['type'] == 'user_input':
                # 请求用户输入
                return WorkflowResult(
                    status='waiting_input',
                    message=step['prompt'],
                    next_step=current_step,
                    collected_params=collected_params
                )

            elif step['type'] == 'confirmation':
                # 请求确认
                return WorkflowResult(
                    status='waiting_confirmation',
                    message=step['prompt'].format(**collected_params),
                    next_step=current_step,
                    collected_params=collected_params
                )

            elif step['type'] == 'execute':
                # 执行技能
                result = await self.orchestrator.execute_single(
                    skill_name,
                    collected_params,
                    context
                )
                return WorkflowResult(
                    status='completed',
                    result=result,
                    collected_params=collected_params
                )

            current_step += 1
```

### 4.4 多轮对话优化

#### 4.4.1 状态机优化
```python
class ConversationState(Enum):
    """对话状态枚举"""
    IDLE = "idle"                          # 空闲
    SKILL_MATCHING = "skill_matching"      # 技能匹配中
    PARAMETER_COLLECTING = "collecting"    # 参数收集中
    AWAITING_CONFIRMATION = "confirming"   # 等待确认
    EXECUTING = "executing"                # 执行中
    COMPLETED = "completed"                # 已完成
```

#### 4.4.2 LLM驱动的状态转换
```python
class StateTransitionManager:
    """状态转换管理器"""

    async def transition(
        self,
        current_state: ConversationState,
        user_input: str,
        context: Dict
    ) -> StateTransition:
        """
        状态转换决策

        Args:
            current_state: 当前状态
            user_input: 用户输入
            context: 上下文

        Returns:
            StateTransition: 状态转换结果
        """
        prompt = self._build_transition_prompt(
            current_state,
            user_input,
            context
        )
        response = await self.llm_client.chat(prompt)
        return self._parse_transition(response)
```

**提示词设计**：
```
你是一个对话状态管理器，负责决定状态转换。

当前状态: {current_state}
用户输入: {user_input}
对话历史: {history}

可能的转换:
- {current_state} -> IDLE: 用户取消或完成
- {current_state} -> SKILL_MATCHING: 用户想执行新任务
- {current_state} -> PARAMETER_COLLECTING: 提供了参数
- {current_state} -> AWAITING_CONFIRMATION: 参数收集完成
- {current_state} -> EXECUTING: 确认执行

请决定状态转换并返回JSON格式:
{{
  "next_state": "next_state_name",
  "action": "action_to_take",
  "message": "message_to_user",
  "confidence": 0.9
}}
```

## 5. 实现计划

### 5.1 Phase 1: LLM集成（Week 1-2）
- [ ] 集成智谱AI API
- [ ] 实现LLM客户端封装
- [ ] 添加配置管理
- [ ] 单元测试

### 5.2 Phase 2: LLM Skill Router（Week 2-3）
- [ ] 实现Intent Analyzer
- [ ] 实现Skill Matcher
- [ ] 实现Workflow Manager
- [ ] 集成到Agent Runtime
- [ ] 测试与优化

### 5.3 Phase 3: Workflow引擎（Week 3-4）
- [ ] 设计Workflow定义格式
- [ ] 实现Workflow Engine
- [ ] 扩展Skill元数据
- [ ] 迁移现有Skills
- [ ] 测试

### 5.4 Phase 4: 多轮对话优化（Week 4-5）
- [ ] 优化状态机
- [ ] 实现状态转换管理器
- [ ] 集成LLM驱动的决策
- [ ] 测试与优化

### 5.5 Phase 5: 部署与监控（Week 5-6）
- [ ] 性能优化
- [ ] 日志与监控
- [ ] 错误处理
- [ ] 文档完善
- [ ] 生产部署

## 6. 参考实现

### 6.1 Claude的Tool Use机制
Claude通过以下方式实现工具调用：
1. LLM分析用户意图
2. 返回工具调用请求（格式化JSON）
3. 系统执行工具
4. 将结果返回给LLM
5. LLM根据结果决定下一步动作
6. 循环直到任务完成

**关键点**：
- 系统提示词（System Prompt）定义工具列表
- LLM输出结构化的工具调用
- 明确的反馈循环

### 6.2 OpenAI的Function Calling
OpenAI的实现方式：
1. 在API调用中定义functions
2. LLM返回函数调用请求
3. 执行函数
4. 将结果返回给LLM
5. 继续对话

**关键点**：
- JSON Schema定义函数参数
- 清晰的函数描述
- 支持多个函数调用

## 7. 技术细节

### 7.1 提示词工程
- **Few-shot Learning**: 提供示例
- **Chain of Thought**: 让LLM解释推理过程
- **Self-Consistency**: 多次采样取一致性最高的结果

### 7.2 错误处理
- LLM输出解析失败时的降级策略
- 重试机制（最多3次）
- 人为干预机制（转人工）

### 7.3 性能优化
- 并行调用多个LLM请求
- 缓存常见意图的解析结果
- 使用流式响应提升体验

### 7.4 安全考虑
- 验证LLM输出的JSON格式
- 限制技能执行权限
- 审计日志记录

## 8. 测试策略

### 8.1 单元测试
- LLM Client测试
- Intent Analyzer测试
- Skill Matcher测试
- Workflow Engine测试

### 8.2 集成测试
- 端到端对话流程测试
- 多轮对话场景测试
- 错误恢复测试

### 8.3 评估指标
- 意图识别准确率
- 技能匹配准确率
- 平均对话轮次
- 用户满意度

## 9. 风险与挑战

### 9.1 技术风险
- LLM API稳定性
- 响应延迟
- 成本控制

### 9.2 缓解措施
- 多模型备份
- 请求限流
- 缓存策略
- 降级方案

## 10. 附录

### 10.1 术语表
- **Intent**: 用户意图
- **Skill**: 技能/工具
- **Workflow**: 工作流
- **State**: 对话状态
- **Context**: 上下文

### 10.2 参考资料
- [智谱AI文档](https://open.bigmodel.cn/dev/api)
- [Claude Tool Use文档](https://docs.anthropic.com/claude/docs/tool-use)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
