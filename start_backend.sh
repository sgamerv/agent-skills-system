#!/bin/bash
cd /Users/mangguo/CodeBuddy/20260314024028

echo "🔄 启动后端API服务..."
echo "项目目录: $(pwd)"

# 检查Python环境
echo "📦 Python环境检查..."
python3 --version

# 启动后端服务
echo "🚀 启动FastAPI服务 (端口: 8000)..."
echo ""
echo "========================================"
echo "后端服务启动日志"
echo "========================================"

exec python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload