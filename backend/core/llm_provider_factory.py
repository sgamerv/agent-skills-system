"""LLM客户端工厂模块"""
import logging
from typing import Optional, Union
from langchain_openai import ChatOpenAI

from backend.config.settings import settings
from backend.llm.zhipuai_client import ZhipuAIClient
from backend.llm.vllm_client import VLLMClient


logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """LLM客户端工厂，用于根据配置创建统一的LLM客户端"""

    @staticmethod
    def create_zhipuai_client() -> Optional[ZhipuAIClient]:
        """
        创建智谱AI客户端

        Returns:
            ZhipuAIClient: 智谱AI客户端，如果创建失败则返回None
        """
        if not settings.ZHIPUAI_API_KEY:
            logger.error("无法创建智谱AI客户端：未配置API密钥")
            return None

        try:
            client = ZhipuAIClient(
                api_key=settings.ZHIPUAI_API_KEY,
                model=settings.ZHIPUAI_MODEL,
                temperature=settings.ZHIPUAI_TEMPERATURE,
                max_tokens=settings.ZHIPUAI_MAX_TOKENS
            )
            logger.info(f"成功创建智谱AI客户端，模型: {settings.ZHIPUAI_MODEL}")
            return client
        except Exception as e:
            logger.error(f"创建智谱AI客户端失败: {e}", exc_info=True)
            return None

    @staticmethod
    def create_xinference_client() -> Optional[ChatOpenAI]:
        """
        创建Xinference客户端

        注意：Xinference不支持structured_output，建议使用vLLM或智谱AI。

        Returns:
            ChatOpenAI: Xinference客户端，如果创建失败则返回None
        """
        try:
            client = ChatOpenAI(
                base_url=settings.XINFERENCE_URL,
                api_key="empty",
                model=settings.XINFERENCE_MODEL_UID,
                temperature=0.7,
            )
            logger.info(f"成功创建Xinference客户端，URL: {settings.XINFERENCE_URL}，模型: {settings.XINFERENCE_MODEL_UID}")
            logger.warning("Xinference不支持structured_output，部分功能可能受限")
            return client
        except Exception as e:
            logger.error(f"创建Xinference客户端失败: {e}", exc_info=True)
            return None

    @staticmethod
    def create_vllm_client() -> Optional[VLLMClient]:
        """
        创建vLLM客户端

        vLLM支持OpenAI兼容API，并通过提示词引导实现structured_output。

        Returns:
            VLLMClient: vLLM客户端，如果创建失败则返回None
        """
        try:
            client = VLLMClient(
                base_url=settings.VLLM_BASE_URL,
                model=settings.VLLM_MODEL,
                api_key=settings.VLLM_API_KEY,
                temperature=settings.VLLM_TEMPERATURE,
                max_tokens=settings.VLLM_MAX_TOKENS
            )
            logger.info(f"成功创建vLLM客户端，URL: {settings.VLLM_BASE_URL}，模型: {settings.VLLM_MODEL}")
            return client
        except Exception as e:
            logger.error(f"创建vLLM客户端失败: {e}", exc_info=True)
            return None

    @staticmethod
    def create_llm() -> Optional[Union[ZhipuAIClient, VLLMClient, ChatOpenAI]]:
        return LLMProviderFactory._create_llm()

    @staticmethod
    def _create_llm() -> Optional[Union[ZhipuAIClient, VLLMClient, ChatOpenAI]]:
        """
        根据配置创建统一的LLM客户端

        所有组件（Router、Workflow、对话管理等）都使用同一个LLM客户端。

        推荐使用：
        - zhipuai: 云端API，稳定可靠
        - vllm: 本地部署，高性能推理，支持structured_output

        Returns:
            ZhipuAIClient 或 VLLMClient 或 ChatOpenAI: LLM客户端
        """
        provider = settings.LLM_PROVIDER.lower()

        if provider == "zhipuai":
            logger.info("使用智谱AI作为LLM提供者")
            client = LLMProviderFactory.create_zhipuai_client()
            if client is None:
                raise RuntimeError("智谱AI客户端创建失败，请检查API密钥配置")
            return client

        elif provider == "vllm":
            logger.info("使用vLLM作为LLM提供者")
            client = LLMProviderFactory.create_vllm_client()
            if client is None:
                raise RuntimeError("vLLM客户端创建失败，请检查服务配置")
            return client

        elif provider == "xinference":
            logger.info("使用Xinference作为LLM提供者")
            logger.warning("Xinference不支持structured_output，建议切换到vLLM")
            client = LLMProviderFactory.create_xinference_client()
            if client is None:
                raise RuntimeError("Xinference客户端创建失败，请检查服务配置")
            return client

        else:
            raise ValueError(f"未知的LLM提供者: {provider}，支持的提供者: 'xinference', 'zhipuai', 'vllm'")

    @staticmethod
    def test_connection() -> bool:
        """
        测试LLM连接

        Returns:
            bool: 连接是否成功
        """
        provider = settings.LLM_PROVIDER.lower()
        logger.info(f"测试LLM连接，提供者: {provider}")

        try:
            client = LLMProviderFactory.create_llm()
            return client is not None
        except Exception as e:
            logger.error(f"LLM连接测试失败: {e}")
            return False
