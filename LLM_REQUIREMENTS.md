# 新增依赖包

## LLM Skill Router 新增依赖

```txt
# 智谱AI SDK（使用OpenAI兼容接口）
openai>=1.0.0

# 现有依赖保持不变
...
```

## 安装命令

```bash
pip install openai>=1.0.0
```

或更新 requirements.txt 文件添加：
```
openai>=1.0.0
```

然后运行：
```bash
pip install -r requirements.txt
```

## 环境变量配置

在 `.env` 文件中添加：

```bash
# 智谱AI配置
ZHIPUAI_API_KEY=your_api_key_here
ZHIPUAI_MODEL=glm-5-turbo
ZHIPUAI_TEMPERATURE=0.7
ZHIPUAI_MAX_TOKENS=2000

# LLM Skill Router配置
ENABLE_LLM_SKILL_ROUTER=true
LLM_ROUTER_FALLBACK_TO_RULES=true
```

## 获取智谱AI API Key

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并登录
3. 进入控制台 -> API Keys
4. 创建新的API Key
5. 将API Key复制到 `.env` 文件中

## 支持的模型

- `glm-5-turbo` - 最新模型，推荐使用
- `glm-4-turbo` - 高性价比模型
- `glm-4` - 标准模型

根据需求选择合适的模型。对于生产环境，建议使用 `glm-5-turbo` 或 `glm-4-turbo`。
