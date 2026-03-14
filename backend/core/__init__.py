"""核心模块包初始化文件"""
from backend.config.logging_config import get_logger

logger = get_logger(__name__)

__all__ = ["logger"]
