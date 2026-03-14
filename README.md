# Agent Skills System

智能多技能编排系统 - 基于 AI 的知识问答、数据分析和可视化平台

## 项目结构

```
agent-skills-system/
├── backend/                # 后端服务 (FastAPI)
│   ├── api/               # API 接口
│   ├── core/              # 核心业务逻辑
│   ├── models/            # 数据模型
│   ├── config/            # 配置文件
│   ├── skills/            # 技能定义
│   ├── scripts/           # 脚本工具
│   ├── tests/             # 测试代码
│   ├── docker-compose.yml # Docker 配置
│   ├── requirements.txt   # Python 依赖
│   └── pyproject.toml    # 项目配置
├── frontend/              # 前端应用 (Vue 3)
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 公共组件
│   │   ├── stores/       # 状态管理
│   │   ├── router/       # 路由配置
│   │   └── assets/       # 静态资源
│   ├── package.json      # 前端依赖
│   └── vite.config.js    # Vite 配置
└── README.md             # 项目说明
```

## 技术栈

### 后端
- **框架**: FastAPI + Uvicorn
- **AI 框架**: LangChain + LangGraph
- **数据库**: PostgreSQL + Redis
- **语言**: Python 3.12+
- **容器**: Docker & Docker Compose

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **路由**: Vue Router
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **工具库**: @vueuse/core

## 快速开始

### 后端启动

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动 Docker 服务
docker-compose up -d

# 启动 API 服务
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档: http://localhost:8000/docs

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端访问: http://localhost:3000

## 功能特性

### 后端功能
- ✅ 多技能编排系统
- ✅ 智能对话管理
- ✅ 记忆系统与用户画像
- ✅ RAG 知识问答
- ✅ 异步任务处理
- ✅ RESTful API 接口

### 前端功能
- ✅ 响应式设计
- ✅ 实时对话界面
- ✅ 技能列表展示
- ✅ 路由管理
- ✅ API 代理配置

## 可用技能

1. **knowledge-qa** - 知识问答
   - 基于 RAG 的文档检索
   - 智能问答系统

2. **data-analysis** - 数据分析
   - CSV/Excel 数据处理
   - 统计分析

3. **visualization** - 数据可视化
   - 图表生成
   - 数据展示

## API 端点

### 公共端点
- `GET /` - 应用信息
- `GET /health` - 健康检查

### 对话端点
- `POST /chat` - 聊天接口
- `GET /skills` - 技能列表
- `GET /skills/{name}` - 技能详情

### 会话端点
- `POST /sessions` - 创建会话
- `GET /sessions/{id}` - 获取会话
- `GET /sessions/{id}/messages` - 获取消息

## 开发指南

### 文档
- [项目概览](backend/PROJECT_OVERVIEW.md) - 完整的项目架构和功能说明
- [开发指南](backend/DEVELOPMENT.md) - 环境设置、工作流和调试
- [Python 3.12 指南](backend/PYTHON312_GUIDE.md) - Python 3.12 特性使用
- [代码规范](backend/CODE_STANDARDS_SUMMARY.md) - 代码标准和最佳实践

### 代码规范
- Python: 遵循 PEP 8 规范
- 前端: 遵循 Vue 3 风格指南
- 使用 Black 格式化 Python 代码
- 使用 ESLint + Prettier 格式化前端代码

### 提交规范
```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

## 许可证

MIT License
