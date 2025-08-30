"""
日志管理器
"""
import sys
from pathlib import Path
from loguru import logger
from config.settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT, LOG_MAX_SIZE, LOG_BACKUP_COUNT


def setup_logger():
    """设置日志配置"""
    # 移除默认的handler
    logger.remove()

    # 使用 loguru 格式语法
    loguru_format = "{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}"

    # 控制台日志
    logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        format=loguru_format,
        colorize=True
    )

    # 文件日志
    log_file = LOGS_DIR / "blog_crawler.log"
    logger.add(
        log_file,
        level=LOG_LEVEL,
        format=loguru_format,
        rotation=LOG_MAX_SIZE,
        retention=LOG_BACKUP_COUNT,
        encoding="utf-8"
    )

    return logger


# 创建全局logger实例
crawler_logger = setup_logger()
