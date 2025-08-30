"""
异步HTTP客户端
"""
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from config.settings import HEADERS, IMAGE_HEADERS, REQUEST_TIMEOUT, MAX_CONCURRENT_REQUESTS
from src.utils.logger import crawler_logger


class AsyncHTTPClient:
    """异步HTTP客户端"""

    def __init__(self):
        self.headers = HEADERS
        self.image_headers = IMAGE_HEADERS
        self.timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout,
            connector=connector
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """执行HTTP请求"""
        async with self.semaphore:
            try:
                crawler_logger.debug(f"发起请求: {method} {url}")

                async with self.session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    data = await response.json()
                    crawler_logger.debug(f"请求成功: {method} {url} - 状态码: {response.status}")
                    return data

            except aiohttp.ClientError as e:
                crawler_logger.error(f"请求失败: {method} {url} - 错误: {e}")
                raise
            except Exception as e:
                crawler_logger.error(f"未知错误: {method} {url} - 错误: {e}")
                raise

    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """GET请求"""
        return await self._make_request("GET", url, **kwargs)

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """POST请求"""
        if data:
            kwargs["json"] = data
        return await self._make_request("POST", url, **kwargs)

    async def download_file(self, url: str, save_path: str) -> bool:
        """下载文件"""
        async with self.semaphore:
            try:
                crawler_logger.debug(f"开始下载文件: {url}")

                # 根据URL类型选择不同的headers
                headers = self._get_headers_for_url(url)

                async with self.session.get(url, headers=headers) as response:
                    crawler_logger.debug(f"响应状态: {response.status}, 响应头: {dict(response.headers)}")
                    response.raise_for_status()

                    with open(save_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)

                    crawler_logger.debug(f"文件下载成功: {url} -> {save_path}")
                    return True

            except aiohttp.ClientError as e:
                crawler_logger.error(f"文件下载失败: {url} - 错误: {e}")
                return False
            except Exception as e:
                crawler_logger.error(f"文件下载异常: {url} - 错误: {e}")
                return False

    def _get_headers_for_url(self, url: str) -> Dict[str, str]:
        """根据URL类型返回相应的headers"""
        if 'cdn.nlark.com' in url or 'yuque.com' in url:
            # 图片等静态资源使用图片专用headers
            return self.image_headers
        else:
            # 其他请求使用默认headers
            return self.headers
