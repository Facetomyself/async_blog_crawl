"""
月份数据获取器
"""
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

from config.settings import API_BASE_URL, MONTH_DATA_DIR
from src.crawler.base_crawler import BaseCrawler
from src.utils.models import CrawlResult, ContentItem
from src.utils.logger import crawler_logger


class MonthDataFetcher(BaseCrawler):
    """月份数据获取器"""

    def __init__(self):
        super().__init__()
        self.month_data_dir = MONTH_DATA_DIR

    async def crawl(self) -> CrawlResult:
        """获取所有月份的数据"""
        try:
            crawler_logger.info("开始获取月份数据")

            # 获取分类数据来确定有哪些月份
            classify_data = await self._get_classify_data()
            if not classify_data:
                return self._create_result(False, error="无法获取分类数据")

            months = list(classify_data.keys())
            crawler_logger.info(f"发现 {len(months)} 个月份需要处理")

            results = {}
            success_count = 0
            skipped_count = 0

            # 并发获取所有月份的数据
            tasks = []
            for month in months:
                task = self._fetch_month_data(month)
                tasks.append(task)

            # 等待所有任务完成
            month_results = await asyncio.gather(*tasks, return_exceptions=True)

            for month, result in zip(months, month_results):
                if isinstance(result, Exception):
                    crawler_logger.error(f"月份 {month} 获取失败: {result}")
                    results[month] = {"success": False, "error": str(result)}
                else:
                    results[month] = result
                    if result["success"]:
                        success_count += 1
                        if result.get("skipped", False):
                            skipped_count += 1

            crawler_logger.info(f"月份数据获取完成: {success_count}/{len(months)} 成功，其中 {skipped_count} 个跳过下载")

            return self._create_result(
                True,
                data={
                    "total_months": len(months),
                    "success_count": success_count,
                    "results": results
                }
            )

        except Exception as e:
            crawler_logger.error(f"月份数据获取失败: {e}")
            return self._create_result(False, error=str(e))

    async def _get_classify_data(self) -> Optional[Dict[str, Any]]:
        """获取分类数据"""
        from src.crawler.classify_monitor import ClassifyMonitor

        async with ClassifyMonitor() as monitor:
            return await monitor.get_classify_data()

    async def _fetch_month_data(self, month: str) -> Dict[str, Any]:
        """获取指定月份的数据"""
        try:
            file_path = self.month_data_dir / f"{month}.json"

            # 检查本地文件是否已存在且有效
            if file_path.exists():
                # 尝试读取现有数据
                existing_data = await self._load_json(file_path)
                if existing_data and len(existing_data) > 0:
                    crawler_logger.debug(f"月份 {month} 数据已存在，跳过下载")
                    # 解析内容项
                    content_items = self._parse_content_items(existing_data)
                    return {
                        "success": True,
                        "month": month,
                        "item_count": len(content_items),
                        "items": content_items,
                        "skipped": True
                    }

            # 文件不存在或无效，重新下载
            crawler_logger.debug(f"下载月份数据: {month}")
            url = f"{self.base_url}/classify/?month={month}"
            data = await self.http_client.get(url)

            if not data:
                return {"success": False, "error": "获取数据为空"}

            # 保存月份数据
            success = await self._save_json(data, file_path)

            if success:
                # 解析内容项
                content_items = self._parse_content_items(data)
                return {
                    "success": True,
                    "month": month,
                    "item_count": len(content_items),
                    "items": content_items,
                    "skipped": False
                }
            else:
                return {"success": False, "error": "保存数据失败"}

        except Exception as e:
            crawler_logger.error(f"获取月份 {month} 数据失败: {e}")
            return {"success": False, "error": str(e)}

    def _parse_content_items(self, data: List[Dict[str, Any]]) -> List[ContentItem]:
        """解析内容项"""
        items = []
        for item_data in data:
            try:
                item = ContentItem(**item_data)
                items.append(item)
            except Exception as e:
                crawler_logger.warning(f"解析内容项失败: {item_data} - 错误: {e}")
                continue

        return items

    async def get_month_data(self, month: str) -> Optional[List[Dict[str, Any]]]:
        """获取指定月份的数据"""
        file_path = self.month_data_dir / f"{month}.json"
        return await self._load_json(file_path)
