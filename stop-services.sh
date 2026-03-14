#!/bin/bash

# 停止所有服务脚本

echo "==================================="
echo "停止 Agent Skills 系统服务"
echo "==================================="
echo ""

# 1. 停止后端
echo "1. 停止后端服务..."
BACKEND_PID=$(lsof -ti:8000 2>/dev/null)
if [ -n "$BACKEND_PID" ]; then
    kill -9 $BACKEND_PID
    echo "   ✓ 后端服务已停止 (PID: $BACKEND_PID)"
else
    echo "   → 后端服务未运行"
fi
echo ""

# 2. 停止前端
echo "2. 停止前端服务..."
FRONTEND_PID=$(lsof -ti:3000 2>/dev/null)
if [ -n "$FRONTEND_PID" ]; then
    kill -9 $FRONTEND_PID
    echo "   ✓ 前端服务已停止 (PID: $FRONTEND_PID, 端口: 3000)"
else
    FRONTEND_PID=$(lsof -ti:3001 2>/dev/null)
    if [ -n "$FRONTEND_PID" ]; then
        kill -9 $FRONTEND_PID
        echo "   ✓ 前端服务已停止 (PID: $FRONTEND_PID, 端口: 3001)"
    else
        echo "   → 前端服务未运行"
    fi
fi
echo ""

# 3. 停止 Nuxt dev 进程
echo "3. 停止 Nuxt 开发服务器..."
NXT_PID=$(pgrep -f "nuxt dev" | head -1)
if [ -n "$NXT_PID" ]; then
    kill -9 $NXT_PID
    echo "   ✓ Nuxt dev 进程已停止 (PID: $NXT_PID)"
else
    echo "   → Nuxt dev 进程未运行"
fi
echo ""

# 4. 停止 Redis（可选，询问用户）
echo "4. Redis 容器状态"
if docker ps | grep -q agent-skills-redis; then
    echo "   Redis 容器正在运行"
    read -p "   是否要停止 Redis 容器? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker stop agent-skills-redis
        echo "   ✓ Redis 容器已停止"
    else
        echo "   → Redis 容器保持运行"
    fi
else
    echo "   → Redis 容器未运行"
fi
echo ""

echo "==================================="
echo "所有服务已停止"
echo "==================================="
echo ""
echo "清理日志:"
echo "  rm /tmp/backend.log"
echo "  rm /tmp/frontend.log"
echo ""
echo "重新启动服务:"
echo "  ./start-services.sh"
echo "==================================="
