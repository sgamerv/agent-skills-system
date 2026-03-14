"""配置包初始化文件"""
from backend.config.logging_config import get_logger, setup_logging
from backend.config.settings import settings

# 自动配置日志（仅当尚未配置时）
setup_logging()

__all__ = ["settings", "get_logger", "setup_logging"]
