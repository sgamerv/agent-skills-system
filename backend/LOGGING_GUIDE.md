# 日志配置使用指南

## 概述

本项目使用统一的日志配置系统，确保所有模块的日志输出格式一致、级别可控。

## 配置模块

### config/logging_config.py

提供全局日志配置功能：

```python
def setup_logging(
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
) -> None:
    """配置全局日志"""

def get_logger(name: str) -> logging.Logger:
    """获取命名日志记录器"""
```

## 使用方法

### 1. 应用启动时配置（main.py）

```python
from backend.config import settings
from backend.config.logging_config import setup_logging, get_logger

# 配置全局日志
setup_logging(level=settings.LOG_LEVEL_INT)

# 获取应用日志记录器
logger = get_logger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting...")
```

### 2. 模块中使用

```python
from backend.config.logging_config import get_logger

logger = get_logger(__name__)

def some_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message: %s", str(error))
    logger.critical("Critical message")
```

### 3. 自动配置（推荐）

导入 `backend.config` 包时，日志会自动配置：

```python
import backend.config  # 自动执行 setup_logging()

# 然后直接使用
logger = get_logger(__name__)
```

## 日志格式

统一格式为：
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

示例输出：
```
2026-03-14 23:19:31 - backend.api.main - INFO - Successfully connected to Redis
2026-03-14 23:19:31 - backend.api.main - INFO - Agent Skills System started successfully!
2026-03-14 23:20:15 - backend.core.agent_runtime - WARNING - LLM service unavailable
2026-03-14 23:20:20 - backend.core.skill_manager - ERROR - Failed to load skill: data-analysis
```

## 日志级别配置

通过环境变量或 `.env` 文件配置：

```bash
# .env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

或在 `settings.py` 中配置：

```python
LOG_LEVEL: str = "INFO"
```

支持的级别：
- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息（默认）
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

## 第三方库日志级别

全局日志配置会自动调整第三方库的日志级别，避免过于冗余：

```python
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
```

## 最佳实践

### 1. 使用正确的日志级别

```python
logger.debug("详细调试信息，仅用于开发")  # 生产环境不显示
logger.info("重要信息，记录关键操作")      # 生产环境显示
logger.warning("警告信息，不影响运行")    # 生产环境显示
logger.error("错误信息，需要关注")        # 生产环境显示
logger.critical("严重错误，需要立即处理") # 生产环境显示
```

### 2. 使用参数化日志

```python
# ✅ 推荐
logger.error("Failed to connect to %s: %s", host, error)

# ❌ 不推荐（字符串拼接）
logger.error(f"Failed to connect to {host}: {error}")
```

### 3. 记录异常信息

```python
try:
    some_operation()
except Exception as e:
    logger.error("Operation failed: %s", str(e))
    logger.exception("Full traceback:")  # 包含堆栈跟踪
```

### 4. 结构化日志

```python
logger.info("User login", extra={
    "user_id": user.id,
    "username": user.username,
    "ip_address": request.client.host
})
```

## 日志输出位置

默认输出到 `stdout`，可以通过以下方式重定向：

```bash
# 输出到文件
python -m uvicorn backend.api.main:app > app.log 2>&1

# 同时输出到控制台和文件
python -m uvicorn backend.api.main:app 2>&1 | tee app.log
```

## 调试日志

如果需要查看更详细的日志，设置 `LOG_LEVEL=DEBUG`：

```bash
LOG_LEVEL=DEBUG python -m uvicorn backend.api.main:app
```

## 日志文件轮转（生产环境推荐）

生产环境建议使用日志轮转：

```python
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    "app.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)
```

## 监控日志

实时查看日志：

```bash
# 查看后端日志
tail -f /tmp/backend.log

# 过滤特定级别的日志
tail -f /tmp/backend.log | grep ERROR

# 过滤特定模块的日志
tail -f /tmp/backend.log | grep "backend.api.main"
```

## 常见问题

### Q: 为什么日志没有输出？

A: 确保导入 `backend.config` 或调用 `setup_logging()`。

### Q: 如何更改日志格式？

A: 调用 `setup_logging()` 时传入自定义格式：

```python
setup_logging(
    log_format="%(levelname)s - %(message)s"
)
```

### Q: 如何禁用某些模块的日志？

A: 设置特定模块的日志级别：

```python
logging.getLogger("some.module").setLevel(logging.CRITICAL)
```

## 参考资料

- [Python logging 模块文档](https://docs.python.org/3/library/logging.html)
- [PEP 282 - Logging System](https://www.python.org/dev/peps/pep-0282/)
- [FastAPI 日志配置](https://fastapi.tiangolo.com/tutorial/logging/)
