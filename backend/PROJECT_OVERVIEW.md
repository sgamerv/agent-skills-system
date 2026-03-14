# Agent Skills 知识问答+任务处理系统 - 项目概览

## 项目已完成

根据架构文档 `ARCHITECTURE.md`,已成功实现以下功能模块:

### 1. 核心框架层 ✓

#### 技能管理系统 (`core/skill_manager.py`)
- **SkillRegistry**: 扫描和加载技能元数据
- **SkillLoader**: 按需加载完整技能内容
- **ResourceManager**: 管理技能脚本和资源文件

#### 对话管理器 (`core/dialogue_manager.py`)
- **DialogueManager**: 管理多轮对话和 Slot Filling
- 支持 Slot 定义、验证和填充
- 对话状态管理(初始化/填充/执行/确认/完成/失败)
- Redis 持久化支持

#### 技能编排器 (`core/skill_orchestrator.py`)
- **SkillOrchestrator**: 管理 Skill 间调用
- **DependencyGraph**: 构建和解析技能依赖关系
- 支持技能链式调用
- 执行历史记录

#### 记忆系统 (`core/memory.py`)
- **MemoryExtractor**: 从对话中提取事实和偏好
- **MemoryManager**: 管理记忆的存储和检索
- **MemoryInjector**: 将相关记忆注入对话上下文
- **ProfileManager**: 管理用户画像和行为统计

#### 会话管理 (`core/session_manager.py`)
- **SessionManager**: 管理会话生命周期
- **MessageManager**: 管理对话消息
- **ArchiveManager**: 管理会话归档

#### Agent 运行时 (`core/agent_runtime.py`)
- **AgentRuntime**: 核心执行引擎
- 统一聊天接口
- 意图识别和参数检查
- 自动选择直接执行或多轮对话模式

### 2. 数据模型层 ✓

- **models/dialogue.py**: 对话相关模型(DialogueContext, SlotValue, SlotDefinition)
- **models/session.py**: 会话相关模型(Session, Message)
- **models/memory.py**: 记忆相关模型(Memory, UserProfile)

### 3. API 层 ✓

#### FastAPI 应用 (`api/main.py`)
- `/chat`: 聊天接口,支持多轮对话
- `/execute-skill`: 直接执行技能
- `/skills`: 获取技能列表
- `/skills/{skill_name}`: 获取技能详情
- `/sessions`: 会话管理接口
- `/users/{user_id}/profile`: 用户画像接口
- `/users/{user_id}/memories`: 用户记忆接口

### 4. 技能仓库 ✓

#### 已实现技能

1. **knowledge-qa-expert** (`skills/knowledge-qa/`)
   - 知识问答技能
   - 支持 RAG 文档检索
   - 包含执行脚本 `main.py`

2. **data-analysis** (`skills/data-analysis/`)
   - 数据分析技能
   - 支持 CSV/Excel 文件分析
   - 支持描述性统计、趋势分析、相关性分析
   - 包含完整的执行脚本 `main.py`

3. **visualization** (`skills/visualization/`)
   - 数据可视化技能
   - 支持折线图、柱状图、饼图、散点图、热力图
   - 包含执行脚本 `main.py`

### 5. 配置和工具 ✓

- **config/settings.py**: 应用配置管理
- **config/prompts.py**: 提示词模板
- **docker-compose.yml**: Redis 和 PostgreSQL 服务配置
- **scripts/init_db.py**: 系统初始化脚本
- **test_system.py**: 系统测试脚本

### 6. 依赖管理 ✓

- **requirements.txt**: 完整的 Python 依赖列表
- 支持 LangChain、LangGraph、FastAPI、Redis、PostgreSQL 等

## 项目结构

```
/Users/mangguo/CodeBuddy/20260314024028/
├── api/                      # API 接口层
│   ├── __init__.py
│   └── main.py              # FastAPI 应用入口
├── core/                     # 核心业务逻辑
│   ├── __init__.py
│   ├── agent_runtime.py     # Agent 运行时
│   ├── dialogue_manager.py  # 对话管理器
│   ├── skill_manager.py     # 技能管理器
│   ├── skill_orchestrator.py # 技能编排器
│   ├── memory.py            # 记忆系统
│   └── session_manager.py   # 会话管理器
├── skills/                   # 技能仓库
│   ├── knowledge-qa/
│   │   ├── SKILL.md
│   │   └── scripts/main.py
│   ├── data-analysis/
│   │   ├── SKILL.md
│   │   └── scripts/main.py
│   └── visualization/
│       ├── SKILL.md
│       └── scripts/main.py
├── models/                   # 数据模型
│   ├── __init__.py
│   ├── dialogue.py
│   ├── session.py
│   └── memory.py
├── config/                   # 配置文件
│   ├── __init__.py
│   ├── settings.py
│   └── prompts.py
├── scripts/                  # 工具脚本
│   ├── __init__.py
│   └── init_db.py           # 初始化脚本
├── tests/                    # 测试文件
│   └── __init__.py
├── api/                      # API 接口层
│   ├── __init__.py
│   └── main.py
├── .env.example              # 环境变量示例
├── .gitignore
├── docker-compose.yml        # Docker Compose 配置
├── requirements.txt          # Python 依赖
├── README.md                 # 项目说明
└── test_system.py           # 系统测试脚本
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动依赖服务

```bash
docker-compose up -d
```

### 3. 初始化系统

```bash
python scripts/init_db.py
```

### 4. 启动 API 服务

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 运行测试

```bash
python test_system.py
```

### 6. 访问 API 文档

打开浏览器访问: http://localhost:8000/docs

## Chat 处理流程

系统提供完整的五步 Chat 处理流程，确保用户获得最佳体验：

### 第一步：技能匹配与推荐

**目标**: 通过用户输入，智能匹配可用的技能，并向用户说明匹配原因。

**处理流程**:
1. 分析用户输入的意图和关键词
2. 在技能注册表中搜索匹配的技能
3. 组织语言向用户说明：
   - 为什么推荐这些技能
   - 每个技能的功能描述
   - 可用技能列表（支持多个候选技能）
4. **兜底处理**：如果没有匹配到任何技能
   - 告知用户当前系统无法处理该请求
   - 建议联系人工客服或提供其他帮助方式

**示例响应**:
```json
{
  "response": "根据您的描述，我为您找到了以下技能：\n\n1. data-analysis - 数据分析功能，支持 CSV/Excel 数据处理和统计分析\n2. knowledge-qa - 专业知识问答功能，支持基于 RAG 的文档检索和智能回答\n\n请选择您想使用的技能，或输入"无匹配"转人工处理。",
  "available_skills": [
    {"name": "data-analysis", "description": "数据分析功能..."},
    {"name": "knowledge-qa", "description": "知识问答功能..."}
  ],
  "state": "skill_selection",
  "next_action": "user_select_skill"
}
```

### 第二步：参数收集与确认

**目标**: 当用户确认使用某个技能后，通过多轮对话收集执行所需的参数。

**处理流程**:
1. 用户确认选择某个技能
2. 系统检查该技能的 Slot 定义（必需参数和可选参数）
3. 按照优先级顺序逐个收集参数：
   - 根据描述和验证规则询问用户
   - 支持用户跳过可选参数
   - 提供默认值建议
4. 参数验证：
   - 类型验证（文件、字符串、枚举等）
   - 格式验证（文件扩展名、长度限制等）
   - 依赖验证（某些参数可能依赖其他参数）
5. **确认阶段**：所有必需参数收集完成后
   - 向用户展示所有参数的摘要
   - 询问用户是否确认执行
   - 支持用户修改参数

**示例响应**:
```json
{
  "response": "好的，我将使用 data-analysis 技能帮您分析数据。\n\n请提供需要分析的数据文件路径（支持 CSV/Excel 格式）：",
  "current_slot": {
    "name": "data_file",
    "type": "file",
    "required": true,
    "description": "需要分析的数据文件(CSV/Excel格式)",
    "prompt": "请提供需要分析的数据文件路径",
    "validation": {"file_extension": [".csv", ".xlsx", ".xls"], "max_size": "100MB"}
  },
  "state": "collecting_parameters",
  "next_action": "provide_parameter"
}
```

**确认阶段响应**:
```json
{
  "response": "参数已收集完成，请确认：\n\n- 数据文件: /path/to/data.csv\n- 分析类型: descriptive\n- 目标列: sales\n- 输出格式: json\n\n是否确认执行？（输入"确认"开始执行，或"修改"调整参数）",
  "collected_parameters": {
    "data_file": "/path/to/data.csv",
    "analysis_type": "descriptive",
    "target_column": "sales",
    "output_format": "json"
  },
  "state": "awaiting_confirmation",
  "next_action": "confirm_or_modify"
}
```

### 第三步：技能执行与结果返回

**目标**: 执行技能，并根据执行时间选择合适的返回方式。

**处理流程**:
1. 用户确认后，开始执行技能
2. **快速执行**（预期 < 5 秒）：
   - 等待执行完成
   - 直接返回完整结果给用户
   - 包含执行结果的详细信息
3. **长时间执行**（预期 > 5 秒）：
   - 立即返回执行开始的消息
   - 提供任务 ID 或进度查询方式
   - 告知用户如何获取执行结果：
     - 通过轮询接口查询状态
     - 通过 WebSocket 接收实时进度
     - 通过通知方式收到完成提醒

**快速执行响应**:
```json
{
  "response": "✅ 数据分析已完成！\n\n分析结果：\n- 数据行数: 1000\n- 列数: 5\n- 均值: 45.6\n- 标准差: 12.3\n- 中位数: 44.5\n\n请对结果进行评价，或继续使用其他功能。",
  "execution_result": {
    "success": true,
    "output": {"rows": 1000, "columns": 5, "mean": 45.6, "std": 12.3, "median": 44.5},
    "execution_time": "2.3s"
  },
  "state": "completed",
  "feedback_required": true,
  "next_action": "provide_feedback"
}
```

**长时间执行响应**:
```json
{
  "response": "📊 数据分析已开始执行，预计需要 30 秒左右。\n\n任务 ID: task_abc123\n\n您可以通过以下方式获取结果：\n1. 输入"查询状态 task_abc123"查看进度\n2. 等待完成后我会通知您\n\n分析完成后，您可以查看详细结果或继续使用其他功能。",
  "task_id": "task_abc123",
  "estimated_time": "30s",
  "state": "executing",
  "next_action": "wait_or_query_status",
  "query_methods": {
    "chat": "输入'查询状态 task_abc123'",
    "api": "GET /tasks/task_abc123",
    "websocket": "ws://localhost:8000/ws/tasks/task_abc123"
  }
}
```

### 第四步：用户反馈收集

**目标**: 收集用户对执行结果的满意度反馈。

**处理流程**:
1. **方式一：界面反馈**（推荐）
   - 在聊天结果项旁显示"👍 赞"和"👎 踩"按钮
   - 用户点击图标提交反馈
   - 记录反馈到系统

2. **方式二：文本反馈**
   - 用户通过 Chat 方式表达满意/不满意
   - 支持自然语言反馈（如"结果很好"、"不满意"等）
   - 解析用户的反馈情感和内容

3. **反馈内容**：
   - 满意度评分（满意/一般/不满意）
   - 反馈原因（可选）
   - 建议或意见（可选）

4. **反馈记录**：
   - 保存到 Redis（短期）
   - 同步到 PostgreSQL（长期）
   - 更新用户画像

**界面反馈响应**:
```json
{
  "response": "感谢您的反馈！",
  "feedback": {
    "rating": "positive",
    "timestamp": "2026-03-14T23:30:00Z",
    "user_id": "user123",
    "task_id": "task_abc123",
    "skill_name": "data-analysis"
  },
  "state": "feedback_received"
}
```

**文本反馈响应**:
```json
{
  "response": "收到您的反馈！\n\n反馈类型: 满意\n感谢您的支持，我们会继续优化服务质量。",
  "feedback": {
    "rating": "positive",
    "feedback_text": "结果很好，谢谢",
    "timestamp": "2026-03-14T23:30:00Z"
  },
  "state": "feedback_received"
}
```

### 第五步：反馈处理与响应

**目标**: 根据用户反馈提供适当的响应。

**处理流程**:
1. **用户表示不满**：
   - 真诚道歉
   - 表示会反馈给人工团队跟踪处理
   - 提供解决方案或替代方案
   - 记录问题用于后续改进
   - 询问用户是否需要转人工客服

2. **用户表示满意**：
   - 谦虚感谢用户的肯定
   - 表示会继续努力
   - 询问是否还需要其他帮助
   - 记录成功案例用于优化

3. **中立反馈**：
   - 感谢反馈
   - 询问可以改进的地方
   - 提供建议收集渠道

**不满意响应**:
```json
{
  "response": "非常抱歉给您带来了不好的体验！😔\n\n我已经将您的反馈记录下来，并会立即反馈给人工团队进行跟踪处理。我们的工作人员会在 24 小时内联系您。\n\n如果您希望立即转接人工客服，请输入"转人工"。",
  "feedback_handling": {
    "escalated": true,
    "assigned_to": "human_support",
    "expected_response_time": "24h",
    "follow_up": true
  },
  "state": "feedback_processed",
  "next_action": "wait_or_escalate"
}
```

**满意响应**:
```json
{
  "response": "太好了，谢谢您的支持和肯定！🎉\n\n能够帮到您是我们的荣幸。我们会继续努力，为您提供更好的服务。\n\n还有其他我可以帮助您的吗？",
  "feedback_handling": {
    "recorded": true,
    "sentiment": "positive",
    "thank_you": true
  },
  "state": "feedback_processed",
  "next_action": "continue_conversation"
}
```

## 流程状态机

```
┌─────────────────┐
│   初始状态      │
│ (用户输入)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  技能匹配       │
│  (分析意图)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌──────────┐
│ 找到   │  │ 未找到   │
│ 技能   │  │ 任何技能 │
└───┬────┘  └────┬─────┘
    │            │
    ▼            ▼
┌──────────┐  ┌──────────┐
│ 技能推荐  │  │ 人工处理 │
└────┬─────┘  └──────────┘
     │
     ▼
┌──────────┐
│ 用户确认  │
│ 技能选择  │
└────┬─────┘
     │
     ▼
┌──────────┐
│ 参数收集  │
│ (多轮对话)│
└────┬─────┘
     │
     ▼
┌──────────┐
│ 参数确认  │
└────┬─────┘
     │
     ▼
┌──────────┐
│ 技能执行  │
└────┬─────┘
     │
     ▼
┌──────────┐
│ 结果返回  │
└────┬─────┘
     │
     ▼
┌──────────┐
│ 用户反馈  │
└────┬─────┘
     │
  ┌──┴──┐
  │     │
  ▼     ▼
┌────┐ ┌────┐
│满意 │ │不满│
└────┘ └────┘
```

## API 状态码说明

### state 字段值

| 状态 | 说明 |
|------|------|
| `initial` | 初始状态，等待用户输入 |
| `skill_selection` | 技能选择阶段，用户需要从推荐列表中选择 |
| `collecting_parameters` | 参数收集阶段，逐个收集必需参数 |
| `awaiting_confirmation` | 等待确认阶段，用户确认参数和执行 |
| `executing` | 执行阶段，技能正在执行中 |
| `completed` | 执行完成，结果已返回 |
| `feedback_received` | 已收到用户反馈 |
| `feedback_processed` | 反馈已处理 |
| `escalated` | 已转人工处理 |

### next_action 字段值

| 状态 | 说明 |
|------|------|
| `user_select_skill` | 用户需要选择技能 |
| `provide_parameter` | 用户需要提供参数 |
| `confirm_or_modify` | 用户需要确认或修改参数 |
| `wait_or_query_status` | 用户可以等待或查询状态 |
| `provide_feedback` | 用户可以提供反馈 |
| `continue_conversation` | 用户可以继续对话 |
| `wait_or_escalate` | 用户可以等待或转人工 |

## 功能特性

### ✓ 已实现

1. **技能系统**
   - 技能发现和元数据管理
   - 渐进式技能加载
   - 技能依赖关系管理
   - 技能编排和链式调用

2. **多轮对话**
   - Slot Filling 机制
   - 智能参数收集
   - 对话状态跟踪
   - 确认和修改机制

3. **记忆系统**
   - 短期记忆提取
   - 记忆持久化存储
   - 记忆注入和检索
   - 用户画像管理

4. **会话管理**
   - 会话生命周期管理
   - 消息存储和检索
   - 会话归档
   - 上下文管理

5. **Agent 运行时**
   - 统一聊天接口
   - 意图识别
   - 自动模式选择(直接执行 vs 多轮对话)
   - 技能执行

6. **API 接口**
   - RESTful API 设计
   - Swagger 文档
   - 异步支持
   - 错误处理

7. **Chat 处理流程** ⭐
   - 技能匹配和推荐
   - 多轮对话参数收集
   - 技能执行和结果返回
   - 用户反馈机制
   - 满意度跟踪

## 技术栈

- **Python**: 3.12+
- **LangChain**: 0.3.x
- **LangGraph**: 0.2.x
- **FastAPI**: 0.109.0
- **Redis**: 7.x
- **PostgreSQL**: 15.x
- **Uvicorn**: 0.27.0
- **Pydantic**: 2.6.1
- **NetworkX**: 3.2.1

## 开发规范

本项目严格遵循 Python 3.12+ 开发规范,具体要求如下:

### 1. 代码风格规范 (PEP 8)

#### 1.1 基本规范
- **缩进**: 统一使用 4 个空格,不使用 Tab
- **行长限制**: 单行代码最大长度 99 字符(符合 Black 规范)
- **编码**: 所有文件使用 UTF-8 编码
- **导入顺序**: 标准库 → 第三方库 → 本地模块,用空行分隔

```python
# 正确的导入顺序
import os
import json
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from langchain_core.prompts import ChatPromptTemplate

from core.agent_runtime import AgentRuntime
from config import settings
```

#### 1.2 命名规范
- **类名**: 大驼峰命名法 (PascalCase)
  ```python
  class DialogueManager:
      pass
  ```

- **函数和变量**: 小写加下划线 (snake_case)
  ```python
  def extract_facts(conversation_history: List[Dict]) -> List[Memory]:
      pass

  user_id = "12345"
  ```

- **常量**: 全大写加下划线 (UPPER_SNAKE_CASE)
  ```python
  MAX_DIALOGUE_TURNS = 10
  MEMORY_TTL = 7200
  ```

- **私有成员**: 单下划线前缀 (_protected)
- **内部成员**: 双下划线前缀 (__private)

#### 1.3 类型注解 (Python 3.12+)

所有函数必须使用类型注解:

```python
# 使用 from __future__ import annotations 启用延迟求值
from __future__ import annotations
from typing import Dict, List, Optional, Any

# 函数签名
async def chat(
    user_input: str,
    user_id: str,
    conversation_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    pass

# 类方法
def get_next_slot_to_fill(self) -> Optional[SlotDefinition]:
    pass
```

#### 1.4 文档字符串规范 (PEP 257)

使用 Google 风格的文档字符串:

```python
def extract_facts(
    self,
    conversation_history: List[Dict[str, Any]],
    user_id: str
) -> List[Memory]:
    """
    从对话历史中提取事实信息。

    Args:
        conversation_history: 对话历史记录列表
        user_id: 用户唯一标识符

    Returns:
        提取的记忆列表

    Raises:
        ValueError: 当对话历史为空时

    Example:
        >>> facts = await extractor.extract_facts(history, "user123")
    """
    pass
```

#### 1.5 异常处理

- 使用具体异常类型,不使用裸 except
- 异常消息应包含足够的上下文信息

```python
# 正确
try:
    result = await self.llm.ainvoke(prompt)
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse JSON response: {e}")
    raise ValueError("Invalid JSON format in LLM response") from e
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise

# 错误
try:
    result = await self.llm.ainvoke(prompt)
except:
    pass  # 永远不要这样做
```

#### 1.6 异步编程规范

- 异步函数使用 `async def` 定义
- 异步操作使用 `await` 调用
- 避免阻塞操作,使用异步库

```python
import redis.asyncio as redis

async def save_memory(self, memory: Memory) -> None:
    """保存记忆到 Redis"""
    key = f"memory:{memory.user_id}:{memory.memory_id}"
    data = memory.to_dict()
    await self.redis_client.hset(key, mapping={
        "data": json.dumps(data, ensure_ascii=False),
        "updated_at": memory.updated_at or datetime.now().isoformat()
    })
    await self.redis_client.expire(key, ttl)
```

#### 1.7 日志规范

使用 Python 标准库 logging 模块:

```python
import logging

logger = logging.getLogger(__name__)

# 在代码中使用
logger.info("Starting dialogue for skill: %s", skill_name)
logger.warning("Failed to connect to Redis: %s", str(e))
logger.error("Critical error occurred", exc_info=True)
```

### 2. Python 3.12+ 特性使用

#### 2.1 类型注解新特性

```python
# 使用 | 语法代替 Optional (Python 3.12+ 推荐)
from __future__ import annotations

# 旧写法 (兼容)
def get_user(user_id: Optional[str] = None) -> Optional[User]:
    pass

# 新写法 (Python 3.12+)
def get_user(user_id: str | None = None) -> User | None:
    pass
```

#### 2.2 结构模式匹配 (match-case)

```python
def handle_state(state: DialogueState) -> str:
    """处理对话状态"""
    match state:
        case DialogueState.INITIALIZING:
            return "正在初始化..."
        case DialogueState.SLOT_FILLING:
            return "正在收集信息..."
        case DialogueState.COMPLETED:
            return "已完成"
        case _:
            return "未知状态"
```

#### 2.3 dataclass 增强功能

```python
from dataclasses import dataclass, field

@dataclass
class DialogueContext:
    """对话上下文"""
    conversation_id: str
    user_id: str
    skill_name: str

    # 使用 field() 设置默认值
    messages: List[Dict[str, Any]] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)

    # 使用 slots 优化内存 (Python 3.10+)
    __slots__ = ['conversation_id', 'user_id', 'skill_name']
```

#### 2.4 类型别名和类型守卫 (Python 3.12+)

```python
# 类型别名
type UserId = str
type DialogueState = Literal["initializing", "filling", "completed"]

# 类型守卫
def is_user_id(value: Any) -> TypeGuard[UserId]:
    """检查值是否为有效的用户 ID"""
    return isinstance(value, str) and len(value) == 36
```

#### 2.5 类型参数 (Python 3.12+)

```python
from typing import TypeVar

# 使用类型参数定义泛型类型
T = TypeVar('T')

async def process_items(items: list[T]) -> list[T]:
    """处理同类型的项目列表"""
    return [await process_item(item) for item in items]
```

### 3. 项目结构规范

```
project/
├── api/                 # API 层
│   ├── __init__.py
│   └── main.py         # FastAPI 入口
├── core/                # 核心业务逻辑
│   ├── __init__.py
│   ├── agent_runtime.py
│   └── ...
├── models/              # 数据模型
│   ├── __init__.py
│   └── dialogue.py
├── config/              # 配置文件
│   ├── __init__.py
│   ├── settings.py
│   └── prompts.py
├── scripts/             # 工具脚本
├── tests/               # 测试文件
├── skills/              # 技能仓库
├── .gitignore
├── requirements.txt
├── pyproject.toml      # 项目配置
└── README.md
```

### 4. 依赖管理

使用 pyproject.toml 管理项目配置和依赖:

```toml
[project]
name = "agent-skills-system"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.109.0",
    "langchain>=0.3.0",
    "pydantic>=2.6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=24.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[tool.black]
line-length = 99
target-version = ['py312']

[tool.ruff]
line-length = 99
select = ["E", "F", "I", "N", "W"]
```

### 5. 代码检查和格式化

#### 5.1 Black (代码格式化)

```bash
# 安装
pip install black

# 格式化代码
black .

# 检查格式
black --check .
```

#### 5.2 Ruff (代码检查)

```bash
# 安装
pip install ruff

# 检查代码
ruff check .

# 自动修复
ruff check --fix .
```

#### 5.3 MyPy (类型检查)

```bash
# 安装
pip install mypy

# 类型检查
mypy .
```

### 6. 测试规范

使用 pytest 编写测试:

```python
import pytest
from core.dialogue_manager import DialogueManager

@pytest.mark.asyncio
async def test_start_dialogue():
    """测试开始对话"""
    manager = DialogueManager(skill_registry, skill_loader, llm)
    context = await manager.start_dialogue(
        skill_name="data-analysis",
        user_id="test_user"
    )
    assert context.user_id == "test_user"
    assert context.state == DialogueState.INITIALIZING
```

### 7. Git 提交规范

使用约定式提交 (Conventional Commits):

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型 (type):
- feat: 新功能
- fix: 修复
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建/工具相关

示例:
```
feat(dialogue): add slot filling confirmation step

- Add confirmation message before executing skill
- Allow users to modify slots before execution

Closes #123
```

### 8. 文件编码和行尾

- 所有文件使用 UTF-8 编码
- 行尾使用 LF (Unix 风格)
- 在 Git 中配置 `.gitattributes`:

```
* text=auto eol=lf
*.py text eol=lf
```

## 开发工具

### 代码检查脚本

项目提供了自动化的代码检查脚本:

```bash
# 运行所有检查
python scripts/check_code_style.py

# 或使用 Makefile
make check
```

检查脚本会自动执行:
- Python 版本检查
- 导入顺序检查
- 代码格式检查
- 代码质量检查
- 类型注解检查
- 安全问题检查
- 单元测试运行

### Makefile 快捷命令

```bash
# 安装依赖
make install-dev

# 格式化代码
make format

# 检查代码
make lint

# 运行测试
make test

# 启动服务
make serve

# 查看所有命令
make help
```

### Pre-commit Hooks

安装 pre-commit hooks 后,每次提交代码前会自动运行检查:

```bash
# 安装 hooks
pre-commit install

# 手动运行所有 hooks
pre-commit run --all-files
```

### 代码编辑器配置

#### VS Code

创建 `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.ruff": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm

1. 安装 Black 和 Ruff 插件
2. 配置代码风格为 Black
3. 启用 Ruff 作为代码检查工具
4. 配置 MyPy 作为类型检查工具

## 规范符合性检查

项目已按照 PEP 8 和 Python 3.10+ 规范进行优化:

### ✅ 已完成的优化

1. **导入顺序**
   - 标准库 → 第三方库 → 本地模块
   - 使用 `from __future__ import annotations`
   - 添加 logging 模块替代 print

2. **类型注解**
   - 所有函数添加类型注解
   - 使用 `Optional` 处理可空类型
   - 返回值类型明确

3. **异常处理**
   - 使用具体异常类型
   - 捕获异常后记录日志
   - 使用 `from e` 保留异常链

4. **文档字符串**
   - 使用 Google 风格
   - 包含 Args、Returns、Raises

5. **代码格式**
   - 4 空格缩进
   - 99 字符行长限制
   - 一致的空格使用

6. **配置管理**
   - 使用 pydantic-settings
   - Pydantic v2 语法 (`model_config`)

7. **异步编程**
   - 正确使用 async/await
   - 使用 redis.asyncio

### 📋 待完成优化

以下区域可以进一步优化(不影响核心功能):

1. 添加更多单元测试覆盖
2. 完善类型注解,消除 MyPy 警告
3. 添加性能基准测试
4. 集成 CI/CD 自动化检查
5. 添加 API 文档生成

## 待扩展功能

根据架构文档,以下功能可以进一步扩展:

1. **向量数据库集成**
   - ChromaDB 集成用于 RAG
   - 文档向量化
   - 语义检索

2. **Xinference 深度集成**
   - LLM 模型调用优化
   - Embedding 模型集成
   - 流式响应支持

3. **数据库持久化**
   - PostgreSQL 表结构设计
   - SQLAlchemy ORM 集成
   - Alembic 数据库迁移

4. **Web UI**
   - React/Vue 前端
   - 对话界面
   - 技能管理界面
   - 用户画像展示

5. **WebSocket 支持**
   - 实时对话
   - 流式输出
   - 进度更新

6. **更多技能**
   - 文档处理技能
   - Web 抓取技能
   - 邮件发送技能
   - 通知技能

## 注意事项

1. **Xinference 配置**
   - 确保 Xinference 服务已启动
   - 模型已加载(推荐: qwen2.5-7b-instruct)
   - 确认服务 URL 和模型 UID 正确

2. **Redis 连接**
   - 确保 Redis 服务已启动
   - 检查连接配置

3. **文件权限**
   - 确保 `./uploads`, `./output`, `./data` 目录有写入权限

4. **Python 版本**
   - 需要 Python 3.12 或更高版本

## API 接口说明

### 根路径

#### GET /
系统基本信息

**响应示例**:
```json
{
  "app": "Agent Skills System",
  "version": "1.0.0",
  "status": "running"
}
```

### 健康检查

#### GET /health
健康检查接口

**响应示例**:
```json
{
  "status": "healthy"
}
```

### 聊天接口

#### POST /chat
发送聊天消息，支持多轮对话和 5 步处理流程

**请求参数**:
```json
{
  "user_input": "我想分析一个数据文件",
  "user_id": "user123",
  "conversation_id": "conv_abc123",  // 可选
  "session_id": "session_xyz789"    // 可选
}
```

**响应字段**:
- `response`: AI 回复内容
- `conversation_id`: 对话 ID
- `session_id`: 会话 ID
- `mode`: 模式（direct/dialogue）
- `state`: 状态（initial/skill_selection/collecting_parameters/awaiting_confirmation/executing/completed/feedback_received/feedback_processed/escalated）
- `available_skills`: 可用技能列表
- `current_slot`: 当前收集的槽位信息
- `collected_parameters`: 已收集参数
- `execution_result`: 执行结果
- `task_id`: 任务 ID
- `feedback_required`: 是否需要反馈
- `feedback`: 反馈信息
- `next_action`: 下一步操作

**响应示例**:
```json
{
  "response": "根据您的需求，我推荐以下技能：",
  "session_id": "session_xyz789",
  "conversation_id": "conv_abc123",
  "mode": "dialogue",
  "state": "skill_selection",
  "available_skills": [
    {
      "name": "data-analysis",
      "description": "数据分析技能",
      "reason": "匹配到关键词：分析"
    }
  ],
  "next_action": "user_select_skill"
}
```

### 技能接口

#### GET /skills
获取所有可用技能列表

**响应示例**:
```json
{
  "skills": [
    {
      "name": "data-analysis",
      "description": "数据分析技能,支持 CSV/Excel 数据处理和统计分析",
      "category": "analysis",
      "tags": ["data", "analysis", "statistics"],
      "version": "1.0.0"
    }
  ],
  "total": 3
}
```

#### GET /skills/{skill_name}
获取指定技能的详细信息

**路径参数**:
- `skill_name`: 技能名称

**响应示例**:
```json
{
  "name": "data-analysis",
  "description": "数据分析技能",
  "category": "analysis",
  "tags": ["data", "analysis"],
  "version": "1.0.0",
  "slots": {
    "file_path": {
      "type": "string",
      "description": "数据文件路径",
      "required": true
    }
  },
  "can_call": true
}
```

#### POST /execute-skill
直接执行指定技能（不经过对话流程）

**请求参数**:
```json
{
  "skill_name": "data-analysis",
  "parameters": {
    "file_path": "/data/sales.csv"
  },
  "context": {
    "user_id": "user123"
  }
}
```

**响应示例**:
```json
{
  "skill": "data-analysis",
  "success": true,
  "output": "分析完成",
  "error": null
}
```

### 会话管理接口

#### POST /sessions
创建新会话

**请求参数**:
```json
{
  "user_id": "user123",
  "title": "当前会话"  // 可选
}
```

**响应示例**:
```json
{
  "session_id": "session_abc123",
  "user_id": "user123",
  "status": "active",
  "title": "当前会话",
  "created_at": "2026-03-15T01:00:00",
  "updated_at": "2026-03-15T01:00:00"
}
```

#### GET /sessions/{session_id}
获取会话详情

**路径参数**:
- `session_id`: 会话 ID

**响应示例**:
```json
{
  "session_id": "session_abc123",
  "user_id": "user123",
  "status": "active",
  "title": "数据分析会话",
  "created_at": "2026-03-15T01:00:00",
  "updated_at": "2026-03-15T02:00:00"
}
```

#### PUT /sessions/{session_id}
更新会话信息（目前支持更新标题）

**路径参数**:
- `session_id`: 会话 ID

**请求参数**:
```json
{
  "title": "新标题"
}
```

**响应示例**:
```json
{
  "session_id": "session_abc123",
  "user_id": "user123",
  "status": "active",
  "title": "新标题",
  "created_at": "2026-03-15T01:00:00",
  "updated_at": "2026-03-15T03:00:00"
}
```

#### GET /users/{user_id}/sessions
获取用户的所有会话列表

**路径参数**:
- `user_id`: 用户 ID

**响应示例**:
```json
{
  "sessions": [
    {
      "session_id": "session_abc123",
      "user_id": "user123",
      "status": "active",
      "title": "数据分析会话",
      "created_at": "2026-03-15T01:00:00",
      "updated_at": "2026-03-15T02:00:00"
    },
    {
      "session_id": "session_def456",
      "user_id": "user123",
      "status": "active",
      "title": "知识问答",
      "created_at": "2026-03-14T10:00:00",
      "updated_at": "2026-03-14T11:00:00"
    }
  ],
  "total": 2
}
```

#### GET /sessions/{session_id}/messages
获取会话的所有消息

**路径参数**:
- `session_id`: 会话 ID

**查询参数**:
- `limit`: 返回消息数量限制，默认 50

**响应示例**:
```json
{
  "messages": [
    {
      "message_id": "msg_001",
      "session_id": "session_abc123",
      "conversation_id": "conv_123",
      "role": "user",
      "content": "我想分析一个数据文件",
      "created_at": "2026-03-15T01:00:00",
      "skill_name": null,
      "skill_result": null
    },
    {
      "message_id": "msg_002",
      "session_id": "session_abc123",
      "conversation_id": "conv_123",
      "role": "assistant",
      "content": "好的，请提供数据文件的路径。",
      "created_at": "2026-03-15T01:00:01",
      "skill_name": null,
      "skill_result": null
    }
  ],
  "total": 2
}
```

### 用户接口

#### GET /users/{user_id}/profile
获取用户画像

**路径参数**:
- `user_id`: 用户 ID

**响应示例**:
```json
{
  "user_id": "user123",
  "preferences": {
    "preferred_skills": ["data-analysis"],
    "language": "zh-CN"
  },
  "behavior_stats": {
    "total_sessions": 10,
    "total_messages": 100,
    "skill_usage": {
      "data-analysis": 5,
      "knowledge-qa": 3
    }
  }
}
```

#### GET /users/{user_id}/memories
获取用户的记忆

**路径参数**:
- `user_id`: 用户 ID

**查询参数**:
- `memory_type`: 记忆类型（可选）
- `limit`: 返回记忆数量限制，默认 10

**响应示例**:
```json
{
  "memories": [
    {
      "memory_id": "mem_001",
      "user_id": "user123",
      "type": "fact",
      "content": "用户喜欢使用数据分析功能",
      "created_at": "2026-03-15T01:00:00"
    }
  ],
  "total": 1
}
```

### 错误响应格式

所有接口在出错时都会返回以下格式：

```json
{
  "detail": "错误描述信息"
}
```

常见 HTTP 状态码：
- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

## 总结

本项目已完整实现了架构文档中定义的核心功能,包括:

✓ 技能管理系统
✓ 多轮对话和 Slot Filling
✓ 技能编排和依赖管理
✓ 记忆系统(短期记忆、用户画像)
✓ 会话管理系统
✓ Agent 运行时
✓ RESTful API 接口
✓ 会话管理接口（创建、查询、更新、消息获取）
✓ 3个示例技能(知识问答、数据分析、可视化)
✓ 完整的测试脚本

系统已具备基本运行能力,可以支持知识问答、任务处理、多轮对话等核心功能。
