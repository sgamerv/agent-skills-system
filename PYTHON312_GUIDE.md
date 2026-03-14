# Python 3.12 特性使用指南

本项目基于 Python 3.12 开发,充分利用了 Python 3.12 的新特性和改进。

## Python 3.12 主要新特性

### 1. 更好的类型系统

#### 1.1 类型别名 (PEP 695)

```python
# 旧写法 (Python 3.11 及以下)
UserId = str
DialogueState = Literal["initializing", "filling", "completed"]

# 新写法 (Python 3.12+)
type UserId = str
type DialogueState = Literal["initializing", "filling", "completed"]
```

#### 1.2 类型参数 (PEP 695)

```python
from typing import Generic, TypeVar

# 旧写法
T = TypeVar('T')
class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

# 新写法 (Python 3.12+)
class Container[T]:
    def __init__(self, value: T) -> None:
        self.value = value
```

#### 1.3 类型守卫

```python
def is_valid_dialogue_id(value: Any) -> TypeGuard[str]:
    """类型守卫: 检查值是否为有效的对话 ID"""
    return isinstance(value, str) and len(value) == 36
```

### 2. 改进的 f-string (PEP 701)

```python
# 更清晰的 f-string 表达式
def format_response(user_id: str, message: str) -> str:
    """格式化响应消息"""
    return f"User {user_id}: {message}"  # 更好的语法高亮和错误提示

# 支持更复杂的表达式
value = 42
formatted = f"The value is {value:04d}"  # 总是 4 位数
```

### 3. 更好的错误提示

Python 3.12 提供了更清晰的错误消息:

```python
# 示例: 缺少括号的错误
# Python 3.11: SyntaxError: invalid syntax
# Python 3.12: SyntaxError: expected ')' after 'print' expression

print("Hello"  # Python 3.12 会提示缺少右括号
```

### 4. 性能改进

- 更快的启动时间
- 更好的内存使用
- 改进的垃圾回收

### 5. 其他改进

#### 5.1 路径协议支持

```python
from pathlib import Path

# 更好的路径操作
config_path = Path("./config/settings.py")
content = config_path.read_text(encoding="utf-8")
```

#### 5.2 更好的标准库

- `asyncio` 改进
- `math` 函数改进
- `typing` 模块增强

## 项目中使用的 Python 3.12 特性

### 1. 类型注解

```python
# 使用新的类型语法
from __future__ import annotations
from typing import Optional, Any

# 联合类型使用 | 语法
def get_dialogue_state(state: str | None) -> str:
    """获取对话状态"""
    return state or "unknown"

# 类型别名
type SlotValue = Any
type DialogueId = str
```

### 2. 结构模式匹配 (Python 3.10+, 3.12 增强)

```python
def handle_state(state: DialogueState) -> str:
    """处理对话状态 - 使用模式匹配"""
    match state:
        case DialogueState.INITIALIZING:
            return "正在初始化..."
        case DialogueState.SLOT_FILLING:
            return "正在收集信息..."
        case DialogueState.EXECUTING:
            return "正在执行..."
        case DialogueState.COMPLETED:
            return "已完成"
        case _:
            return "未知状态"
```

### 3. dataclass 改进

```python
from dataclasses import dataclass, field

@dataclass
class DialogueContext:
    """对话上下文 - 使用 dataclass"""
    conversation_id: str
    user_id: str
    skill_name: str
    state: DialogueState = DialogueState.INITIALIZING

    # 使用 field() 设置默认值
    messages: list[dict[str, Any]] = field(default_factory=list)
    context_data: dict[str, Any] = field(default_factory=dict)

    # 使用 slots 优化内存
    __slots__ = ['conversation_id', 'user_id', 'skill_name']
```

### 4. 异步编程

Python 3.12 对异步编程有更好的支持:

```python
import asyncio
import redis.asyncio as redis

async def save_dialogue(context: DialogueContext) -> None:
    """保存对话上下文 - 使用异步 Redis"""
    async with redis.from_url(settings.REDIS_URL) as client:
        key = f"dialogue:{context.conversation_id}"
        data = context.to_dict()
        await client.hset(key, mapping={
            "data": json.dumps(data, ensure_ascii=False),
            "updated_at": context.updated_at or datetime.now().isoformat()
        })
        await client.expire(key, 3600 * 24)
```

### 5. 改进的错误处理

```python
# 更精确的异常处理
try:
    result = await self.llm.ainvoke(prompt)
except json.JSONDecodeError as e:
    # Python 3.12 提供更详细的错误信息
    logger.error(
        "Failed to parse JSON response at position %d: %s",
        e.pos,
        e.msg,
        exc_info=e
    )
    raise ValueError(f"Invalid JSON format: {e.msg}") from e
except Exception as e:
    logger.error("Unexpected error: %s", e, exc_info=True)
    raise
```

## 迁移指南

### 从 Python 3.10/3.11 迁移到 3.12

1. **更新依赖版本**
   ```bash
   # 更新 requirements.txt
   pip install --upgrade pip
   pip install --upgrade -r requirements.txt
   ```

2. **检查类型注解**
   - 使用新的类型别名语法
   - 更新泛型类型定义

3. **更新配置文件**
   - `pyproject.toml`: 更新 `requires-python = ">=3.12"`
   - `tool.mypy.python_version = "3.12"`
   - `tool.ruff.target-version = "py312"`

4. **测试兼容性**
   ```bash
   # 运行所有测试
   python scripts/check_code_style.py
   ```

### 常见问题

#### Q: Python 3.12 兼容 Python 3.10/3.11 代码吗?
A: 是的,Python 3.12 完全向后兼容。现有代码可以直接运行。

#### Q: 需要立即使用新特性吗?
A: 不需要。新特性是可选的,可以逐步采用。

#### Q: 如何检查是否使用了 Python 3.12 特性?
A: 使用 `ruff check --select UP` 检查可以升级的代码。

## 性能优化建议

### 1. 使用类型注解
```python
# 类型注解有助于 MyPy 进行静态检查,提高代码质量
async def process_dialogue(
    dialogue_id: str,
    user_input: str
) -> dict[str, Any]:
    pass
```

### 2. 使用异步 I/O
```python
# Python 3.12 对异步支持更好
import asyncio

async def process_multiple_dialogues(dialogue_ids: list[str]) -> None:
    """并发处理多个对话"""
    tasks = [process_dialogue(did) for did in dialogue_ids]
    await asyncio.gather(*tasks)
```

### 3. 使用 dataclass slots
```python
@dataclass(slots=True)
class DialogueContext:
    """使用 slots 减少内存占用"""
    conversation_id: str
    user_id: str
```

## 参考资源

- [Python 3.12 Release Notes](https://docs.python.org/3.12/whatsnew/3.12.html)
- [PEP 695: Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [PEP 701: Syntactic formalization of f-strings](https://peps.python.org/pep-0701/)
- [What's New in Python 3.12](https://docs.python.org/3.12/whatsnew/3.12.html)

## 总结

Python 3.12 带来了许多改进和新特性,本项目充分利用了这些特性来提高代码质量、可维护性和性能。建议开发者逐步采用这些新特性,但不需要立即重写所有代码。
