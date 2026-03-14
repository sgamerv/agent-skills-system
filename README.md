# Agent Skills 知识问答+任务处理系统

基于 Agent Skills 开放标准的智能问答与任务处理系统,使用 Python/LangChain/Xinference 技术栈。

## 功能特性

- 知识问答 (基于 RAG 的文档检索)
- 任务处理 (通过 Skills 封装的自动化流程)
- 多轮对话和 Slot Filling 机制
- 技能编排和依赖管理
- 短期记忆系统
- 用户画像系统
- 会话管理系统

## 技术栈

- Python 3.12+
- LangChain 0.3.x
- LangGraph 0.2.x
- FastAPI
- Redis
- PostgreSQL
- ChromaDB

## 代码规范

本项目严格遵循 Python 3.10+ 开发规范:

- **代码风格**: PEP 8,使用 Black 自动格式化
- **代码检查**: Ruff (Flake8 + isopt + pyupgrade)
- **类型注解**: MyPy 静态类型检查
- **文档字符串**: Google 风格文档字符串
- **提交规范**: 约定式提交 (Conventional Commits)

详细的开发规范请查看 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) 中的"开发规范"部分。

### 代码检查

```bash
# 运行所有检查
python scripts/check_code_style.py

# 格式化代码
black .

# 检查代码风格
ruff check --fix .

# 类型检查
mypy .
```

### 安装开发工具

```bash
pip install -e .[dev]
pre-commit install
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件,填入必要的配置
```

### 3. 启动服务

```bash
# 启动 Redis 和 PostgreSQL
docker-compose up -d

# 初始化数据库
python scripts/init_db.py

# 启动 API 服务
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问文档

启动后访问 http://localhost:8000/docs 查看 API 文档。

## 项目结构

```
.
├── api/                    # API 接口层
│   ├── main.py            # FastAPI 应用入口
│   └── routes/            # 路由定义
├── core/                   # 核心业务逻辑
│   ├── agent_runtime.py   # Agent 运行时
│   ├── dialogue_manager.py # 对话管理器
│   ├── skill_manager.py   # 技能管理器
│   ├── skill_orchestrator.py # 技能编排器
│   ├── memory.py          # 记忆系统
│   ├── profile_manager.py # 用户画像管理
│   └── session_manager.py # 会话管理器
├── skills/                 # 技能仓库
│   ├── knowledge-qa/      # 知识问答技能
│   ├── data-analysis/     # 数据分析技能
│   └── visualization/     # 可视化技能
├── models/                 # 数据模型
│   ├── dialogue.py        # 对话模型
│   ├── session.py         # 会话模型
│   └── memory.py          # 记忆模型
├── database/              # 数据库相关
│   ├── connection.py      # 数据库连接
│   └── migrations/        # 数据库迁移
├── config/                 # 配置文件
│   ├── settings.py        # 应用配置
│   └── prompts.py         # 提示词模板
├── scripts/               # 工具脚本
│   └── init_db.py        # 初始化脚本
├── tests/                 # 测试文件
└── requirements.txt       # 依赖列表
```

## 文档

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - 项目概览和开发规范
- [DEVELOPMENT.md](DEVELOPMENT.md) - 详细开发指南
- [PYTHON312_GUIDE.md](PYTHON312_GUIDE.md) - Python 3.12 特性使用指南
- [PYTHON312_COMPATIBILITY_REPORT.md](PYTHON312_COMPATIBILITY_REPORT.md) - Python 3.12 兼容性报告
- [pyproject.toml](pyproject.toml) - 项目配置和依赖

## 使用示例

### 知识问答

```python
from core.agent_runtime import AgentRuntime
from core.skill_manager import SkillRegistry

agent = AgentRuntime(...)
result = await agent.chat("什么是 RAG 技术?")
```

### 任务处理

```python
result = await agent.chat("分析 sales.csv 文件,生成趋势图表")
# 系统会自动进行 Slot Filling,收集必要参数
```

## 开发指南

### 添加新技能

1. 在 `skills/` 目录下创建新技能文件夹
2. 创建 `SKILL.md` 文件,定义技能元数据和执行步骤
3. 在 `scripts/` 目录下添加执行脚本(可选)
4. 技能自动被发现和加载

### 扩展记忆系统

编辑 `core/memory.py`,添加新的记忆提取器和注入器。

## License

MIT
