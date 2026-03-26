"""应用配置模块"""
from __future__ import annotations

import logging
import os
from pydantic_settings import BaseSettings


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "Agent Skills System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

    @property
    def LOG_LEVEL_INT(self) -> int:
        """获取日志级别的整数值"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map.get(self.LOG_LEVEL.upper(), logging.INFO)

    # Xinference 配置
    XINFERENCE_URL: str = "http://localhost:9997"
    XINFERENCE_MODEL_UID: str = "qwen2.5-7b-instruct"
    EMBEDDING_MODEL_UID: str = "bge-large-zh-v1.5"

    # 智谱AI配置
    ZHIPUAI_API_KEY: str = "f71a7b9f11b74a5d981e0ce613e9890d.sscNNfODNvcf6XcY"
    ZHIPUAI_MODEL: str = "glm-5-turbo"
    ZHIPUAI_TEMPERATURE: float = 0.7
    ZHIPUAI_MAX_TOKENS: int = 8000  # 增加到8000以支持更长的JSON响应

    # vLLM配置
    VLLM_BASE_URL: str = "http://localhost:8000/v1"
    VLLM_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
    VLLM_API_KEY: str = "EMPTY"
    VLLM_TEMPERATURE: float = 0.7
    VLLM_MAX_TOKENS: int = 4000

    # LLM 提供者配置
    LLM_PROVIDER: str = "zhipuai"  # 可选: "xinference", "zhipuai", "vllm"

    # 数据库配置
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/agent_skills"

    # 向量数据库
    VECTOR_DB_PATH: str = "./data/chroma_db"

    # 会话配置
    SESSION_TIMEOUT: int = 3600  # 秒
    MAX_DIALOGUE_TURNS: int = 10

    # 记忆配置
    MEMORY_TTL: int = 7200  # 秒
    SHORT_TERM_MEMORY_LIMIT: int = 100

    # 文件存储
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB

    # Skills 目录
    SKILLS_DIR: str = "./backend/skills"

    # Agent架构选择
    AGENT_ARCHITECTURE: str = "agent_loop"  # 可选: "legacy", "agent_loop"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }

    def ensure_dirs(self) -> None:
        """确保必要的目录存在"""
        dirs = [self.UPLOAD_DIR, self.VECTOR_DB_PATH, self.SKILLS_DIR]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
