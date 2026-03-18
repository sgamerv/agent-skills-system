"""LLM客户端工厂模块"""
import logging
from typing import Optional
from langchain_openai import ChatOpenAI

from backend.config.settings import settings
from backend.llm.zhipuai_client import ZhipuAIClient


logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """LLM客户端工厂，用于根据配置创建不同的LLM客户端"""

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
            return client
        except Exception as e:
            logger.error(f"创建Xinference客户端失败: {e}", exc_info=True)
            return None

    @staticmethod
    def create_llm_client() -> tuple[Optional[ChatOpenAI], Optional[ZhipuAIClient]]:
        """
        根据配置创建LLM客户端

        Returns:
            tuple: (langchain_client, zhipuai_client)
                - langchain_client: LangChain兼容的客户端（用于Xinference）
                - zhipuai_client: 智谱AI客户端（用于ZhipuAI）
        """
        provider = settings.LLM_PROVIDER.lower()

        if provider == "zhipuai":
            logger.info("使用智谱AI作为LLM提供者")
            zhipuai_client = LLMProviderFactory.create_zhipuai_client()
            if zhipuai_client is None:
                logger.error("智谱AI客户端创建失败")
                return None, None
            return None, zhipuai_client

        elif provider == "xinference":
            logger.info("使用Xinference作为LLM提供者")
            xinference_client = LLMProviderFactory.create_xinference_client()
            if xinference_client is None:
                logger.error("Xinference客户端创建失败")
                return None, None
            return xinference_client, None

        else:
            logger.error(f"未知的LLM提供者: {provider}，支持的提供者: 'xinference', 'zhipuai'")
            return None, None

    @staticmethod
    def test_connection() -> bool:
        """
        测试LLM连接

        Returns:
            bool: 连接是否成功
        """
        provider = settings.LLM_PROVIDER.lower()
        logger.info(f"测试LLM连接，提供者: {provider}")

        if provider == "zhipuai":
            client = LLMProviderFactory.create_zhipuai_client()
            return client is not None

        elif provider == "xinference":
            client = LLMProviderFactory.create_xinference_client()
            return client is not None

        else:
            logger.error(f"未知的LLM提供者: {provider}")
            return False
