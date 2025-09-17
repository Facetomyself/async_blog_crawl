"""
基础爬虫抽象层
"""
import json
import aiofiles
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from config.settings import API_BASE_URL
from src.utils.http_client import AsyncHTTPClient, AbstractHTTPClient
from src.utils.models import CrawlResult
from src.utils.logger import crawler_logger


class BaseCrawler(ABC):
    """基础爬虫抽象类，支持注入 HTTP 客户端"""

    def __init__(self, base_url: str = API_BASE_URL, http_client: Optional[AbstractHTTPClient] = None):
        self.base_url = base_url
        self.http_client: Optional[AbstractHTTPClient] = http_client
        self._owns_client = False

    async def __aenter__(self):
        """异步上下文管理器入口"""
        if self.http_client is None:
            # 未注入客户端则自建并托管其生命周期
            self.http_client = AsyncHTTPClient()
            await self.http_client.__aenter__()
            self._owns_client = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.http_client and self._owns_client:
            await self.http_client.__aexit__(exc_type, exc_val, exc_tb)
            self._owns_client = False

    @abstractmethod
    async def crawl(self) -> CrawlResult:
        """执行爬取任务"""
        raise NotImplementedError

    async def _save_json(self, data: Dict[str, Any], file_path: Path) -> bool:
        """保存数据为JSON文件"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            crawler_logger.info(f"数据保存成功: {file_path}")
            return True
        except Exception as e:
            crawler_logger.error(f"数据保存失败: {file_path} - 错误: {e}")
            return False

    async def _save_markdown(self, content: str, file_path: Path) -> bool:
        """保存内容为Markdown文件"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            crawler_logger.info(f"Markdown保存成功: {file_path}")
            return True
        except Exception as e:
            crawler_logger.error(f"Markdown保存失败: {file_path} - 错误: {e}")
            return False

    async def _load_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """从JSON文件加载数据"""
        try:
            if not file_path.exists():
                return None
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            crawler_logger.error(f"数据加载失败: {file_path} - 错误: {e}")
            return None

    def _create_result(self, success: bool, data: Optional[Dict[str, Any]] = None,
                       error: Optional[str] = None) -> CrawlResult:
        """创建爬取结果"""
        return CrawlResult(
            success=success,
            data=data,
            error=error,
            timestamp=datetime.now()
        )

