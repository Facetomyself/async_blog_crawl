"""
HTTP 客户端抽象与实现
"""
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional, Protocol, runtime_checkable

import aiohttp

from config.settings import (
    HEADERS,
    IMAGE_HEADERS,
    REQUEST_TIMEOUT,
    MAX_CONCURRENT_REQUESTS,
    BASE_DIR,
)
from src.utils.logger import crawler_logger


@runtime_checkable
class AbstractHTTPClient(Protocol):
    async def __aenter__(self) -> "AbstractHTTPClient":
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        ...

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        ...

    async def download_file(self, url: str, save_path: str) -> bool:
        ...


class AsyncHTTPClient:
    """基于 aiohttp 的异步 HTTP 客户端"""

    def __init__(self):
        self.headers = HEADERS
        self.image_headers = IMAGE_HEADERS
        self.timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout,
            connector=connector
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        async with self.semaphore:
            try:
                crawler_logger.debug(f"发起请求: {method} {url}")
                assert self.session is not None, "HTTP session not initialized"
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
        return await self._make_request("GET", url, **kwargs)

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        if data:
            kwargs["json"] = data
        return await self._make_request("POST", url, **kwargs)

    async def download_file(self, url: str, save_path: str) -> bool:
        async with self.semaphore:
            try:
                crawler_logger.debug(f"开始下载文件 {url}")

                # 根据URL类型选择不同的headers
                headers = self._get_headers_for_url(url)
                assert self.session is not None, "HTTP session not initialized"
                async with self.session.get(url, headers=headers) as response:
                    crawler_logger.debug(f"响应状态 {response.status}, 响应头 {dict(response.headers)}")
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
        if 'cdn.nlark.com' in url or 'yuque.com' in url:
            # 图片等静态资源使用图片专用headers
            return self.image_headers
        else:
            # 其他请求使用默认headers
            return self.headers


class LocalHTTPClient:
    """本地桩实现：用于无网络的离线调试"""

    def __init__(self):
        self.response_dir = BASE_DIR / 'design' / 'response'

    async def __aenter__(self) -> 'LocalHTTPClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        return None

    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        try:
            if url.endswith('/classify'):
                return self._load_json('classify.json')

            if '/classify/' in url and 'month=' in url:
                return self._load_json('classify_month.json')

            if '/article/' in url:
                return self._load_json('article.json')

            if '/section/' in url:
                return self._load_json('section.json')

            crawler_logger.warning(f'本地桩未匹配 URL: {url}')
            return {}
        except Exception as e:
            crawler_logger.error(f'本地桩读取失败: {url} - 错误: {e}')
            return {}

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        return {"ok": True}

    async def download_file(self, url: str, save_path: str) -> bool:
        try:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            Path(save_path).write_bytes(b"")
            return True
        except Exception as e:
            crawler_logger.error(f'本地桩下载失败: {url} - 错误: {e}')
            return False

    def _load_json(self, name: str) -> Dict[str, Any]:
        file_path = self.response_dir / name
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

