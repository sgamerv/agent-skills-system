"""全局日志配置模块"""
from __future__ import annotations

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
) -> None:
    """配置全局日志

    Args:
        level: 日志级别，默认为 INFO
        log_format: 日志格式，默认为标准化格式
        date_format: 日期格式，默认为 ISO 8601
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"

    # 清除现有的处理器
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # 配置日志
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,  # 强制覆盖现有配置
    )

    # 设置第三方库的日志级别，避免过于冗余
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """获取命名日志记录器

    Args:
        name: 日志记录器名称，通常使用 __name__

    Returns:
        配置好的日志记录器实例
    """
    return logging.getLogger(name)
