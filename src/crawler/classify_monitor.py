"""
分类接口监控
"""
import hashlib
from typing import Dict, Any, Optional

from config.settings import CLASSIFY_URL, CLASSIFY_FILE
from src.crawler.base_crawler import BaseCrawler
from src.utils.models import CrawlResult
from src.utils.logger import crawler_logger


class ClassifyMonitor(BaseCrawler):
    """分类接口监控器"""

    def __init__(self):
        super().__init__()
        self.classify_url = CLASSIFY_URL
        self.classify_file = CLASSIFY_FILE
        self.last_hash: Optional[str] = None

    async def crawl(self) -> CrawlResult:
        """监控分类接口是否有更新"""
        try:
            crawler_logger.info("开始监控分类接口")

            # 获取最新数据
            data = await self.http_client.get(self.classify_url)
            if not data:
                return self._create_result(False, error="获取分类数据失败")

            # 计算数据哈希
            current_hash = self._calculate_hash(data)

            # 检查是否有变化
            if await self._has_changed(current_hash):
                # 保存新数据
                success = await self._save_json(data, self.classify_file)
                if success:
                    self.last_hash = current_hash
                    crawler_logger.info("分类数据已更新并保存")
                    return self._create_result(True, data={"updated": True, "data": data})
                else:
                    return self._create_result(False, error="保存分类数据失败")
            else:
                crawler_logger.info("分类数据无变化")
                return self._create_result(True, data={"updated": False, "data": data})

        except Exception as e:
            crawler_logger.error(f"分类接口监控失败: {e}")
            return self._create_result(False, error=str(e))

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """计算数据的哈希值"""
        data_str = str(sorted(data.items()))
        return hashlib.md5(data_str.encode()).hexdigest()

    async def _has_changed(self, current_hash: str) -> bool:
        """检查数据是否发生变化"""
        if self.last_hash is None:
            # 首次运行，尝试加载历史哈希；若无历史记录则视为变化
            self.last_hash = await self._load_last_hash()
            if self.last_hash is None:
                return True
            return current_hash != self.last_hash

        return current_hash != self.last_hash

    async def _load_last_hash(self) -> Optional[str]:
        """从文件加载上次的哈希值"""
        try:
            if not self.classify_file.exists():
                return None

            # 读取现有数据计算哈希
            existing_data = await self._load_json(self.classify_file)
            if existing_data:
                return self._calculate_hash(existing_data)

        except Exception as e:
            crawler_logger.warning(f"加载历史哈希失败: {e}")

        return None

    async def get_classify_data(self) -> Optional[Dict[str, Any]]:
        """获取分类数据"""
        return await self._load_json(self.classify_file)

