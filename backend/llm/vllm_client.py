"""vLLM客户端 - 支持OpenAI兼容API和structured output"""
from typing import Dict, List, Optional, Any
import logging
import json
import asyncio
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class VLLMClient:
    """vLLM客户端，支持OpenAI兼容API"""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "EMPTY",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """
        初始化vLLM客户端

        Args:
            base_url: vLLM服务地址（如 http://localhost:8000/v1）
            model: 模型名称
            api_key: API密钥（vLLM通常不需要，默认EMPTY）
            temperature: 温度参数
            max_tokens: 最大token数
        """
        self.base_url = base_url
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens

        # 使用OpenAI兼容的API
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )

    async def chat(
        self,
        messages: List[Dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        聊天接口

        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            temperature: 温度参数（可选，使用实例值）
            max_tokens: 最大token数（可选，使用实例值）
            **kwargs: 其他参数

        Returns:
            str: 模型回复

        Raises:
            Exception: API调用失败
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"vLLM API调用失败: {e}")
            raise

    async def chat_with_system(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        **kwargs
    ) -> str:
        """
        带系统提示词的聊天

        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            conversation_history: 对话历史（可选）
            **kwargs: 其他参数

        Returns:
            str: 模型回复
        """
        messages = [{"role": "system", "content": system_prompt}]

        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)

        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})

        return await self.chat(messages, **kwargs)

    async def structured_output(
        self,
        messages: List[Dict],
        output_schema: Dict,
        output_example: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        获取结构化输出

        vLLM本身不支持structured output，通过提示词引导模型返回JSON格式。

        Args:
            messages: 消息列表
            output_schema: 输出结构的JSON Schema
            output_example: 输出示例（推荐使用，效果更好）
            **kwargs: 其他参数

        Returns:
            Dict: 解析后的结构化数据
        """
        # 构建系统提示词
        if output_example:
            # 如果提供了示例，使用示例而不是schema
            system_message = {
                "role": "system",
                "content": f"""请严格按照以下JSON格式返回答案，不要返回JSON Schema：

```json
{json.dumps(output_example, ensure_ascii=False, indent=2)}
```

重要：
1. 直接返回JSON数据，不要包含字段类型定义
2. 不要返回 type、properties 等 schema 字段
3. values 应该是实际的数据值，不是数据类型描述
4. 只返回JSON，不要包含其他文字说明"""
            }
        else:
            system_message = {
                "role": "system",
                "content": f"请严格按照以下JSON格式返回答案，只返回JSON，不要包含其他内容：\n{json.dumps(output_schema, ensure_ascii=False, indent=2)}"
            }

        enhanced_messages = [system_message] + messages

        response = await self.chat(enhanced_messages, **kwargs)

        # 打印原始响应以便调试
        logger.debug(f"[structured_output] 原始响应: {response}")

        # 解析JSON响应
        try:
            # 尝试提取JSON部分
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                logger.debug(f"[structured_output] 解析结果: {json.dumps(result, ensure_ascii=False)}")
                return result
            else:
                # 如果没有找到JSON，尝试整个响应
                result = json.loads(response)
                logger.debug(f"[structured_output] 解析结果: {json.dumps(result, ensure_ascii=False)}")
                return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 原始响应: {response}")
            raise ValueError(f"无法解析LLM的JSON响应: {e}")

    async def stream_chat(
        self,
        messages: List[Dict],
        **kwargs
    ):
        """
        流式聊天

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Yields:
            str: 流式输出的内容片段
        """
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"流式聊天失败: {e}")
            raise

    def close(self):
        """关闭客户端"""
        asyncio.create_task(self.client.close())
