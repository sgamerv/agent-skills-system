# LLM 提供者配置指南

## 概述

系统支持两种 LLM 提供者：
- **ZhipuAI（智谱AI）**：默认提供者，使用智谱AI的 GLM 模型
- **Xinference**：本地部署的推理服务

## 配置方法

### 1. 切换到 ZhipuAI（推荐）

在 `backend/config/settings.py` 中设置：

```python
LLM_PROVIDER: str = "zhipuai"
```

同时确保智谱AI的 API 密钥已配置：

```python
ZHIPUAI_API_KEY: str = "your_api_key_here"
ZHIPUAI_MODEL: str = "glm-5-turbo"  # 或其他支持的模型
ZHIPUAI_TEMPERATURE: float = 0.7
ZHIPUAI_MAX_TOKENS: int = 8000
```

### 2. 切换到 Xinference

在 `backend/config/settings.py` 中设置：

```python
LLM_PROVIDER: str = "xinference"
```

同时确保 Xinference 服务正在运行：

```python
XINFERENCE_URL: str = "http://localhost:9997"
XINFERENCE_MODEL_UID: str = "qwen2.5-7b-instruct"  # 或其他模型
EMBEDDING_MODEL_UID: str = "bge-large-zh-v1.5"
```

## 启动 Xinference 服务

如果选择使用 Xinference，需要先启动 Xinference 服务：

```bash
# 安装 Xinference
pip install xinference

# 启动 Xinference
xinference-local --host 0.0.0.0 --port 9997

# 部署模型（可选）
xinference launch --model-name qwen2.5-7b-instruct --model-type llm
```

## 验证配置

### 1. 检查健康状态

```bash
curl http://localhost:8000/health
```

响应示例：

```json
{
  "status": "healthy",
  "llm_provider": "zhipuai",
  "llm_available": true,
  "zhipuai_available": true,
  "workflow_executor_available": true
}
```

### 2. 查看启动日志

```bash
tail -f /tmp/backend.log
```

关键日志信息：

```
测试LLM连接，提供者: zhipuai
成功创建智谱AI客户端，模型: glm-5-turbo
LLM连接测试成功
使用智谱AI作为LLM提供者
成功创建智谱AI客户端，模型: glm-5-turbo
LLM组件初始化完成
```

## 故障排除

### LLM 连接失败

**症状**：前端显示"无法连接到LLM服务"

**解决方法**：

1. 检查后端日志中的错误信息
2. 确认 API 密钥正确（对于 ZhipuAI）
3. 确认服务正在运行（对于 Xinference）
4. 检查网络连接

### ZhipuAI API 密钥无效

**症状**：日志显示"无法创建智谱AI客户端：未配置API密钥"或认证失败

**解决方法**：

1. 获取有效的 API 密钥：https://open.bigmodel.cn/
2. 在 `settings.py` 中更新 `ZHIPUAI_API_KEY`
3. 重启后端服务

### Xinference 连接失败

**症状**：日志显示"创建Xinference客户端失败"

**解决方法**：

1. 检查 Xinference 是否正在运行：`curl http://localhost:9997`
2. 检查模型是否已部署
3. 确认 `XINFERENCE_URL` 和 `XINFERENCE_MODEL_UID` 配置正确

## 环境变量配置

也可以通过环境变量配置（优先级高于 settings.py）：

```bash
# ZhipuAI
export LLM_PROVIDER="zhipuai"
export ZHIPUAI_API_KEY="your_api_key"
export ZHIPUAI_MODEL="glm-5-turbo"
export ZHIPUAI_TEMPERATURE=0.7
export ZHIPUAI_MAX_TOKENS=8000

# Xinference
export LLM_PROVIDER="xinference"
export XINFERENCE_URL="http://localhost:9997"
export XINFERENCE_MODEL_UID="qwen2.5-7b-instruct"
export EMBEDDING_MODEL_UID="bge-large-zh-v1.5"
```

## 性能对比

| 提供者 | 响应速度 | 成本 | 离线使用 | 推荐场景 |
|--------|---------|------|---------|---------|
| ZhipuAI | 快 | 按量计费 | 否 | 生产环境，快速部署 |
| Xinference | 慢（取决于硬件） | 免费 | 是 | 开发测试，数据隐私 |

## 最佳实践

1. **开发环境**：使用 Xinference，可以离线使用，节省成本
2. **生产环境**：使用 ZhipuAI，响应速度快，稳定性高
3. **混合使用**：可以在不同环境中切换不同的提供者
4. **监控日志**：定期检查后端日志，确保 LLM 服务正常运行

## 注意事项

1. 修改配置后需要重启后端服务
2. 确保 `ENABLE_LLM_SKILL_ROUTER` 设置为 `true` 以启用高级功能
3. 如果 LLM 连接失败，前端会显示友好的错误消息，但后端会记录详细的错误日志
4. 建议定期更新 API 密钥以确保安全性
