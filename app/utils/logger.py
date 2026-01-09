"""
日志配置模块
使用 loguru 实现结构化日志，支持控制台和文件输出
"""
import sys
from pathlib import Path

from loguru import logger

from app.core.config import get_settings


def setup_logging() -> "logger":
    """
    配置应用日志系统

    - 控制台彩色输出
    - 文件日志轮转
    - 结构化日志格式
    """
    settings = get_settings()

    # 移除默认处理器
    logger.remove()

    # 控制台输出格式（彩色）
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # 添加文件处理器
    if settings.LOG_FILE:
        # 确保日志目录存在
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )

        logger.add(
            settings.LOG_FILE,
            format=file_format,
            level=settings.LOG_LEVEL,
            rotation="10 MB",      # 文件达到 10MB 时轮转
            retention="30 days",   # 保留 30 天
            compression="gz",      # 压缩旧日志
            enqueue=True,          # 异步写入，避免阻塞
        )

    return logger
