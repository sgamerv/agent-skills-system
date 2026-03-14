#!/bin/bash

echo "=========================================="
echo "  Agent Skills 后端启动脚本"
echo "=========================================="
echo ""

# 切换到 backend 目录
cd "$(dirname "$0")"

# 检查 Python 版本
echo "1. 检查 Python 版本..."
python3 --version

# 检查虚拟环境
echo ""
echo "2. 检查虚拟环境..."
if [ -d "venv" ]; then
    echo "✓ 虚拟环境已存在"
    source venv/bin/activate
else
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 安装依赖
echo ""
echo "3. 安装依赖..."
pip install -q -r requirements.txt

# 检查 .env 文件
echo ""
echo "4. 检查配置文件..."
if [ ! -f ".env" ]; then
    echo "创建 .env 文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件并填入正确的配置"
fi

# 启动依赖服务
echo ""
echo "5. 启动 Redis 和 PostgreSQL..."
docker-compose up -d postgres

# 等待服务启动
echo "等待服务启动..."
sleep 5

echo ""
echo "=========================================="
echo "  启动完成!"
echo "=========================================="
echo ""
echo "启动 API 服务:"
echo "  python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "访问 API 文档: http://localhost:8000/docs"
echo ""
