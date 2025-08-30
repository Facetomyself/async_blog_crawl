"""
文章/笔记详情获取器
"""
import asyncio
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse

from config.settings import API_BASE_URL, CONTENT_DATA_DIR, IMAGES_DIR
from src.crawler.base_crawler import BaseCrawler
from src.utils.models import CrawlResult, ContentItem, ArticleDetail, SectionDetail
from src.utils.logger import crawler_logger


class ContentFetcher(BaseCrawler):
    """文章/笔记详情获取器"""

    def __init__(self):
        super().__init__()
        self.content_data_dir = CONTENT_DATA_DIR
        self.images_dir = IMAGES_DIR

    async def crawl(self) -> CrawlResult:
        """获取所有内容的详情"""
        try:
            crawler_logger.info("开始获取内容详情")

            # 获取所有内容项
            content_items = await self._get_all_content_items()
            if not content_items:
                return self._create_result(False, error="无法获取内容项列表")

            crawler_logger.info(f"发现 {len(content_items)} 个内容项需要处理")

            results = {}
            success_count = 0
            skipped_count = 0

            # 并发获取所有内容的详情
            tasks = []
            for item in content_items:
                task = self._fetch_content_detail(item)
                tasks.append(task)

            # 分批处理，避免并发过多
            batch_size = 10
            for i in range(0, len(tasks), batch_size):
                batch_tasks = tasks[i:i + batch_size]
                batch_items = content_items[i:i + batch_size]

                crawler_logger.debug(f"处理批次 {i//batch_size + 1}: {len(batch_tasks)} 个任务")

                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                for item, result in zip(batch_items, batch_results):
                    item_key = f"{item.type}_{item.id}"
                    if isinstance(result, Exception):
                        crawler_logger.error(f"内容 {item_key} 获取失败: {result}")
                        results[item_key] = {"success": False, "error": str(result)}
                    else:
                        results[item_key] = result
                        if result["success"]:
                            success_count += 1
                            if result.get("skipped", False):
                                skipped_count += 1

            crawler_logger.info(f"内容详情获取完成: {success_count}/{len(content_items)} 成功，其中 {skipped_count} 个跳过下载")

            return self._create_result(
                True,
                data={
                    "total_items": len(content_items),
                    "success_count": success_count,
                    "results": results
                }
            )

        except Exception as e:
            crawler_logger.error(f"内容详情获取失败: {e}")
            return self._create_result(False, error=str(e))

    async def _get_all_content_items(self) -> List[ContentItem]:
        """获取所有内容项"""
        from src.crawler.classify_monitor import ClassifyMonitor
        from src.crawler.month_data_fetcher import MonthDataFetcher

        items = []
        classify_data = None

        # 获取分类数据来确定月份
        async with ClassifyMonitor() as monitor:
            classify_data = await monitor.get_classify_data()
            if not classify_data:
                crawler_logger.warning("未找到分类数据")
                return items

        crawler_logger.info(f"找到 {len(classify_data)} 个月份")

        # 获取所有月份的数据
        async with MonthDataFetcher() as fetcher:
            for month in classify_data.keys():
                month_data = await fetcher.get_month_data(month)
                if month_data:
                    for item_data in month_data:
                        try:
                            item = ContentItem(**item_data)
                            items.append(item)
                        except Exception as e:
                            crawler_logger.warning(f"解析内容项失败: {item_data} - 错误: {e}")
                else:
                    crawler_logger.warning(f"月份 {month} 没有数据")

        crawler_logger.info(f"总共找到 {len(items)} 个内容项")
        return items

    async def _fetch_content_detail(self, item: ContentItem) -> Dict[str, Any]:
        """获取单个内容的详情"""
        try:
            markdown_file = self.content_data_dir / f"{item.type}_{item.id}.md"
            json_file = self.content_data_dir / f"{item.type}_{item.id}_meta.json"

            # 检查本地文件是否已存在且有效
            if markdown_file.exists() and json_file.exists():
                # 检查文件大小是否合理
                markdown_size = markdown_file.stat().st_size
                json_size = json_file.stat().st_size

                if markdown_size > 100 and json_size > 10:  # 合理的文件大小阈值
                    crawler_logger.debug(f"内容 {item.type}/{item.id} 已存在，跳过下载")
                    return {
                        "success": True,
                        "type": item.type,
                        "id": item.id,
                        "title": item.title,
                        "markdown_file": str(markdown_file),
                        "meta_file": str(json_file),
                        "skipped": True,
                        "image_download_results": []
                    }

            # 文件不存在或无效，重新下载
            crawler_logger.debug(f"下载内容详情: {item.type}/{item.id}")
            url = f"{self.base_url}/{item.type}/{item.id}"
            data = await self.http_client.get(url)

            if not data:
                return {"success": False, "error": "获取数据为空"}

            # 分离正文和其他数据
            body_content = data.get("body", "")
            meta_data = {k: v for k, v in data.items() if k != "body"}

            # 处理图片下载
            processed_body, image_results = await self._process_images(body_content)

            # 保存正文为markdown文件
            success_md = await self._save_markdown(processed_body, markdown_file)

            # 保存元数据为json文件
            success_json = await self._save_json(meta_data, json_file)

            if success_md and success_json:
                return {
                    "success": True,
                    "type": item.type,
                    "id": item.id,
                    "title": item.title,
                    "markdown_file": str(markdown_file),
                    "meta_file": str(json_file),
                    "image_download_results": image_results,
                    "skipped": False
                }
            else:
                return {"success": False, "error": "保存文件失败"}

        except Exception as e:
            crawler_logger.error(f"获取内容 {item.type}/{item.id} 详情失败: {e}")
            return {"success": False, "error": str(e)}

    async def _process_images(self, body: str) -> Tuple[str, List[Dict[str, Any]]]:
        """处理正文中的图片"""
        if not body:
            return body, []

        # 匹配markdown中的图片链接
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(image_pattern, body)

        if not matches:
            return body, []

        results = []
        processed_body = body

        for alt_text, image_url in matches:
            if image_url.startswith('http'):
                # 下载图片
                local_path, success = await self._download_image(image_url)

                if success and local_path:
                    # 替换为本地路径
                    relative_path = f"./images/{Path(local_path).name}"
                    old_pattern = f'![{alt_text}]({image_url})'
                    new_pattern = f'![{alt_text}]({relative_path})'
                    processed_body = processed_body.replace(old_pattern, new_pattern)

                results.append({
                    "url": image_url,
                    "local_path": local_path,
                    "success": success
                })

        return processed_body, results

    async def _download_image(self, url: str) -> Tuple[Optional[str], bool]:
        """下载图片"""
        try:
            # 清理URL，去掉查询参数
            parsed_url = urlparse(url)
            clean_url = parsed_url._replace(query='').geturl()

            # 生成文件名
            import hashlib
            url_hash = hashlib.md5(clean_url.encode()).hexdigest()

            # 更好地处理扩展名
            ext = self._get_image_extension(clean_url)
            filename = f"{url_hash}{ext}"
            save_path = self.images_dir / filename

            # 检查是否已存在
            if save_path.exists():
                crawler_logger.debug(f"图片已存在: {save_path}")
                return str(save_path), True

            # 下载图片
            success = await self.http_client.download_file(url, str(save_path))

            if success:
                return str(save_path), True
            else:
                return None, False

        except Exception as e:
            crawler_logger.error(f"下载图片失败: {url} - 错误: {e}")
            return None, False

    def _get_image_extension(self, url: str) -> str:
        """获取图片扩展名"""
        # 从URL路径中提取扩展名
        path = Path(urlparse(url).path)
        ext = path.suffix.lower()

        # 如果没有扩展名或扩展名不完整，尝试从Content-Type推断
        if not ext or len(ext) < 3:
            # 常见的图片扩展名
            return '.png'

        # 确保是有效的图片扩展名
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
        if ext in valid_extensions:
            return ext

        # 如果不是标准扩展名，返回png
        return '.png'
