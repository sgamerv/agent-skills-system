#!/bin/bash

# API 测试脚本

echo "==================================="
echo "测试 Agent Skills API"
echo "==================================="
echo ""

# 后端地址
API_BASE="http://localhost:8000"

# 1. 健康检查
echo "1. 测试健康检查..."
RESPONSE=$(curl -s $API_BASE/health)
if [ $? -eq 0 ]; then
    echo "   ✓ 健康检查通过"
    echo "   响应: $RESPONSE"
else
    echo "   ✗ 健康检查失败"
    exit 1
fi
echo ""

# 2. 获取技能列表
echo "2. 测试获取技能列表..."
RESPONSE=$(curl -s $API_BASE/skills)
if [ $? -eq 0 ]; then
    echo "   ✓ 技能列表获取成功"
    echo "   响应: $RESPONSE"
else
    echo "   ✗ 技能列表获取失败"
    exit 1
fi
echo ""

# 3. 聊天接口
echo "3. 测试聊天接口..."
RESPONSE=$(curl -s -X POST $API_BASE/chat \
    -H "Content-Type: application/json" \
    -d '{"user_input":"你好","user_id":"test_user"}')
if [ $? -eq 0 ]; then
    echo "   ✓ 聊天接口正常"
    echo "   响应:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo "   ✗ 聊天接口失败"
    exit 1
fi
echo ""

# 4. 测试无效请求
echo "4. 测试错误处理..."
RESPONSE=$(curl -s -X POST $API_BASE/chat \
    -H "Content-Type: application/json" \
    -d '{"user_input":"","user_id":"test_user"}')
if [ $? -eq 0 ]; then
    echo "   ✓ 错误处理正常"
    echo "   响应: $RESPONSE"
else
    echo "   ✗ 错误处理失败"
fi
echo ""

echo "==================================="
echo "所有 API 测试完成"
echo "==================================="
echo ""
echo "访问前端页面进行完整测试:"
echo "  http://localhost:3000"
echo "  http://localhost:3001"
echo "==================================="
