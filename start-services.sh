#!/bin/bash

# 启动所有服务脚本

echo "==================================="
echo "启动 Agent Skills 系统服务"
echo "==================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 1. 检查并启动 Redis
echo "1. 检查 Redis 服务..."
if docker ps | grep -q agent-skills-redis; then
    echo "   ✓ Redis 已运行"
else
    echo "   → 启动 Redis..."
    cd backend && docker-compose up -d redis
    if [ $? -eq 0 ]; then
        echo "   ✓ Redis 启动成功"
    else
        echo "   ✗ Redis 启动失败"
        exit 1
    fi
    cd ..
fi
echo ""

# 2. 检查并启动后端
echo "2. 检查后端服务..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✓ 后端已在端口 8000 运行"
else
    echo "   → 启动后端服务..."
    PYTHONPATH="$SCRIPT_DIR" python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    sleep 2
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "   ✓ 后端启动成功 (PID: $BACKEND_PID)"
    else
        echo "   ✗ 后端启动失败，查看日志: tail -f /tmp/backend.log"
        exit 1
    fi
fi
echo ""

# 3. 检查并启动前端
echo "3. 检查前端服务..."
FRONTEND_PORT=3000
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✓ 前端已在端口 3000 运行"
elif lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✓ 前端已在端口 3001 运行"
    FRONTEND_PORT=3001
else
    echo "   → 启动前端服务..."
    cd frontend && npm run dev > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..

    # 等待前端启动
    sleep 5

    # 检查前端是否启动成功
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        FRONTEND_PORT=3000
        echo "   ✓ 前端启动成功 (PID: $FRONTEND_PID, 端口: $FRONTEND_PORT)"
    elif lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null 2>&1; then
        FRONTEND_PORT=3001
        echo "   ✓ 前端启动成功 (PID: $FRONTEND_PID, 端口: $FRONTEND_PORT)"
    else
        echo "   ✗ 前端启动失败，查看日志: tail -f /tmp/frontend.log"
        exit 1
    fi
fi
echo ""

# 4. 显示服务状态
echo "==================================="
echo "服务启动完成"
echo "==================================="
echo ""
echo "后端服务:   http://localhost:8000"
echo "前端服务:   http://localhost:$FRONTEND_PORT"
echo "Redis:       http://localhost:6379"
echo ""
echo "后端日志:   tail -f /tmp/backend.log"
echo "前端日志:   tail -f /tmp/frontend.log"
echo ""
echo "停止所有服务: ./stop-services.sh"
echo ""
echo "==================================="
echo "提示: Xinference (LLM 服务) 未启动"
echo "聊天功能将返回模拟响应"
echo "如需真实 AI 回复，请启动 Xinference"
echo "==================================="
