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

## 总结

本项目已完整实现了架构文档中定义的核心功能,包括:

✓ 技能管理系统
✓ 多轮对话和 Slot Filling
✓ 技能编排和依赖管理
✓ 记忆系统(短期记忆、用户画像)
✓ 会话管理系统
✓ Agent 运行时
✓ RESTful API 接口
✓ 3个示例技能(知识问答、数据分析、可视化)
✓ 完整的测试脚本

系统已具备基本运行能力,可以支持知识问答、任务处理、多轮对话等核心功能。
