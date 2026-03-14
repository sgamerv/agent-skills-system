# Agent Skills System - 快速开始

## 快速启动

### 启动所有服务
```bash
./start-services.sh
```

### 停止所有服务
```bash
./stop-services.sh
```

### 测试 API
```bash
./test-api.sh
```

## 访问地址

- **前端**: http://localhost:3000 或 http://localhost:3001
- **后端**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **Redis**: localhost:6379

## 服务状态

### 当前状态
- ✅ 后端服务 - 运行正常
- ✅ 前端服务 - 运行正常
- ✅ Redis - 运行正常
- ⚠️  Xinference (LLM) - 未启动

### 注意事项
- Xinference 未启动时，聊天功能返回模拟响应
- 要获得真实 AI 回复，需要启动 Xinference

## 功能

### 首页 (/)
- 系统介绍
- 功能展示
- 快速导航

### 聊天页面 (/chat)
- 发送消息
- 查看 AI 回复
- 实时交互

### 技能列表 (/skills)
- 查看所有技能
- 技能状态管理
- 技能详情展示

## API 端点

### 健康检查
```
GET /health
```

### 技能管理
```
GET /skills
GET /skills/{skill_name}
```

### 聊天
```
POST /chat
```

### 会话管理
```
POST /sessions
GET /sessions/{session_id}
GET /users/{user_id}/sessions
GET /sessions/{session_id}/messages
```

### 用户数据
```
GET /users/{user_id}/profile
GET /users/{user_id}/memories
```

## 文档

- **API 使用指南**: `frontend/API_GUIDE.md`
- **修复总结**: `FIXES_SUMMARY.md`
- **前端 README**: `frontend/README.md`
- **后端 README**: `backend/README.md`

## 配置

### 后端配置
- 配置文件: `backend/config/settings.py`
- 环境变量: `.env`

### 前端配置
- 配置文件: `frontend/nuxt.config.ts`
- 环境变量: `frontend/.env`

## 故障排除

### 后端无法启动
```bash
# 检查端口占用
lsof -i:8000

# 检查 Redis
docker ps | grep redis

# 查看日志
tail -f /tmp/backend.log
```

### 前端无法启动
```bash
# 检查端口占用
lsof -i:3000
lsof -i:3001

# 查看日志
tail -f /tmp/frontend.log
```

### Redis 无法连接
```bash
# 重启 Redis 容器
docker restart agent-skills-redis

# 重新创建 Redis 容器
cd backend && docker-compose up -d redis
```

### API 调用失败
```bash
# 测试后端健康
curl http://localhost:8000/health

# 测试技能列表
curl http://localhost:8000/skills

# 测试聊天
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input":"测试","user_id":"test"}'
```

## 开发

### 启动 Xinference (可选)
```bash
# 安装 Xinference
pip install "xinference[all]"

# 启动 Xinference
xinference-local --host 0.0.0.0 --port 9997

# 启动模型
xinference launch --model-name qwen2.5-7b-instruct --model-type LLM
```

### 添加新技能
```bash
cd backend/skills
mkdir my_skill
cat > my_skill/SKILL.md << 'EOF'
---
name: my_skill
description: 我的技能
category: test
tags: [demo]
---

这是我的技能描述。
EOF
```

### 修改配置
```bash
# 后端配置
vim backend/config/settings.py

# 前端配置
vim frontend/nuxt.config.ts
vim frontend/.env
```

## 贡献

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 开启 Pull Request

## 许可证

MIT License
