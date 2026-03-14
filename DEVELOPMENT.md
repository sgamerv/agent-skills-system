# Agent Skills System - 开发指南

## 环境设置

### 1. 前置要求

- Python 3.12 或更高版本
- Redis 7.x
- PostgreSQL 15.x (可选)
- Docker 和 Docker Compose (用于快速启动依赖服务)

### 2. 克隆项目

```bash
git clone <repository-url>
cd agent-skills-system
```

### 3. 创建虚拟环境

```bash
# 使用 venv
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 使用 conda
conda create -n agent-skills python=3.12
conda activate agent-skills
```

### 4. 安装依赖

```bash
# 安装基础依赖
pip install -e .

# 安装开发依赖
pip install -e .[dev]

# 或使用 pip-tools
pip install pip-tools
pip-compile requirements.in --output-file requirements.txt
pip install -r requirements.txt
```

### 5. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件,填入实际的配置值
```

### 6. 启动依赖服务

```bash
# 使用 Docker Compose
docker-compose up -d

# 检查服务状态
docker-compose ps
```

### 7. 安装 pre-commit hooks

```bash
pre-commit install
```

### 8. 初始化数据库

```bash
python scripts/init_db.py
```

## 开发工作流

### 代码检查和格式化

在提交代码之前,请运行以下命令:

```bash
# 1. 运行所有检查
python scripts/check_code_style.py

# 2. 或者单独运行各项检查
# 格式化代码
black .

# 检查并修复代码风格问题
ruff check --fix .

# 类型检查
mypy .

# 运行测试
pytest tests/ -v

# 安全检查
bandit -r .
```

### Pre-commit 自动检查

安装 pre-commit hooks 后,每次提交都会自动运行检查:

```bash
git add .
git commit  # 自动运行 pre-commit 检查
```

如果检查失败,可以手动修复或使用 `--no-verify` 跳过(不推荐):

```bash
git commit --no-verify
```

### 分支策略

- `main`: 主分支,保持稳定
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 修复分支
- `hotfix/*`: 紧急修复分支

### 提交规范

使用约定式提交 (Conventional Commits):

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型 (type):
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

示例:

```bash
git commit -m "feat(dialogue): add slot filling confirmation step

- Add confirmation message before executing skill
- Allow users to modify slots before execution

Closes #123"
```

## 代码风格指南

### 基本规范

1. **缩进**: 使用 4 个空格,不使用 Tab
2. **行长**: 最大 99 字符
3. **编码**: UTF-8
4. **行尾**: LF (Unix 风格)

### 命名规范

```python
# 类名: PascalCase
class DialogueManager:
    pass

# 函数和变量: snake_case
def extract_facts():
    pass

user_id = "12345"

# 常量: UPPER_SNAKE_CASE
MAX_DIALOGUE_TURNS = 10
```

### 类型注解

```python
from __future__ import annotations
from typing import Optional

async def chat(
    user_input: str,
    user_id: str,
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    pass
```

### 文档字符串

使用 Google 风格:

```python
def extract_facts(
    conversation_history: List[Dict[str, Any]],
    user_id: str,
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
    """
    pass
```

### 异常处理

```python
try:
    result = await self.llm.ainvoke(prompt)
except json.JSONDecodeError as e:
    logger.error("Failed to parse JSON: %s", e)
    raise ValueError("Invalid JSON format") from e
except Exception as e:
    logger.error("Unexpected error: %s", e)
    raise
```

## 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_dialogue_manager.py

# 运行特定测试函数
pytest tests/test_dialogue_manager.py::test_start_dialogue

# 查看覆盖率
pytest --cov=api --cov=core --cov=models --cov-report=html

# 只运行标记为 unit 的测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"
```

### 编写测试

```python
import pytest
from core.dialogue_manager import DialogueManager


@pytest.mark.asyncio
async def test_start_dialogue():
    """测试开始对话"""
    manager = DialogueManager(skill_registry, skill_loader, llm)
    context = await manager.start_dialogue(
        skill_name="data-analysis",
        user_id="test_user",
    )
    assert context.user_id == "test_user"
    assert context.state == DialogueState.INITIALIZING


@pytest.mark.unit
async def test_slot_filling():
    """测试槽位填充"""
    pass


@pytest.mark.integration
async def test_redis_integration():
    """测试 Redis 集成"""
    pass
```

## 调试

### 启用调试模式

在 `.env` 中设置:

```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### 使用 VS Code 调试

创建 `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": ["api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            "jinja": true,
            "justMyCode": false
        }
    ]
}
```

### 日志查看

```bash
# 查看实时日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 使用 journalctl (如果使用 systemd)
journalctl -u agent-skills -f
```

## 常见问题

### 1. 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. Redis 连接失败

```bash
# 检查 Redis 是否运行
redis-cli ping

# 启动 Redis
redis-server

# 或使用 Docker
docker-compose up -d redis
```

### 3. 类型检查错误

```bash
# 安装类型注解库
pip install types-PyYAML types-redis

# 忽略特定错误
# 在代码中添加: # type: ignore
result = complex_function()  # type: ignore
```

### 4. 测试失败

```bash
# 清理测试缓存
pytest --cache-clear

# 只运行失败的测试
pytest --lf

# 进入 pdb 调试
pytest --pdb
```

## 性能优化

### 1. 使用异步 I/O

```python
import redis.asyncio as redis

async def get_data(key: str) -> Optional[str]:
    """异步获取数据"""
    async with redis.from_url(settings.REDIS_URL) as client:
        return await client.get(key)
```

### 2. 连接池

```python
# Redis 连接池
redis_pool = redis.ConnectionPool.from_url(settings.REDIS_URL)

# 数据库连接池
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
)
```

### 3. 缓存

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_skill_metadata(skill_name: str) -> Optional[Dict]:
    """缓存技能元数据"""
    return skill_registry.get(skill_name)
```

## 部署

### 使用 Docker

```bash
# 构建镜像
docker build -t agent-skills:latest .

# 运行容器
docker run -p 8000:8000 agent-skills:latest
```

### 使用 Kubernetes

参考 `k8s/` 目录中的部署配置。

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

MIT License
