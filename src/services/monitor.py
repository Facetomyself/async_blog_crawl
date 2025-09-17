import asyncio
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Optional

from src.crawler.classify_monitor import ClassifyMonitor
from src.crawler.month_data_fetcher import MonthDataFetcher
from src.crawler.content_fetcher import ContentFetcher
from src.utils.http_client import AsyncHTTPClient, LocalHTTPClient, AbstractHTTPClient
from src.utils.logger import crawler_logger


@dataclass
class MonitorState:
    running: bool = False
    interval_seconds: int = 3600
    offline: bool = False
    crawl_on_update: bool = True
    cycles: int = 0
    last_run_started: Optional[str] = None
    last_run_finished: Optional[str] = None
    last_result: Optional[Dict[str, Any]] = None


class MonitorManager:
    def __init__(self) -> None:
        self._state = MonitorState()
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    def _make_client(self) -> AbstractHTTPClient:
        return LocalHTTPClient() if self._state.offline else AsyncHTTPClient()

    async def start(self, interval_seconds: int = 3600, offline: bool = False, crawl_on_update: bool = True) -> Dict[str, Any]:
        async with self._lock:
            self._state.interval_seconds = max(1, int(interval_seconds))
            self._state.offline = bool(offline)
            self._state.crawl_on_update = bool(crawl_on_update)

            if self._state.running and self._task and not self._task.done():
                return self.status()

            self._state.running = True
            self._task = asyncio.create_task(self._loop())
            crawler_logger.info(f"监控已启动，间隔 {self._state.interval_seconds}s，offline={self._state.offline}, crawl_on_update={self._state.crawl_on_update}")
            return self.status()

    async def stop(self) -> Dict[str, Any]:
        async with self._lock:
            self._state.running = False
            if self._task:
                self._task.cancel()
            crawler_logger.info("监控已停止")
            return self.status()

    async def set_interval(self, interval_seconds: int) -> Dict[str, Any]:
        async with self._lock:
            self._state.interval_seconds = max(1, int(interval_seconds))
            crawler_logger.info(f"监控间隔更新为 {self._state.interval_seconds}s")
            return self.status()

    def status(self) -> Dict[str, Any]:
        return asdict(self._state)

    async def _loop(self) -> None:
        try:
            while self._state.running:
                self._state.last_run_started = datetime.now().isoformat()
                try:
                    # 正确管理 HTTP 客户端生命周期
                    async with self._make_client() as client:
                        # 分类监控
                        monitor = ClassifyMonitor()
                        monitor.http_client = client
                        classify_result = await monitor.crawl()
                        updated = bool(classify_result.data and classify_result.data.get("updated"))

                        months_result = None
                        content_result = None
                        if updated and self._state.crawl_on_update:
                            # 月份数据
                            mf = MonthDataFetcher(); mf.http_client = client
                            months_result = await mf.crawl()
                            # 内容详情
                            cf = ContentFetcher(); cf.http_client = client
                            content_result = await cf.crawl()

                        self._state.last_result = {
                            "classify": classify_result.model_dump() if hasattr(classify_result, "model_dump") else classify_result,
                            "months": months_result.model_dump() if months_result and hasattr(months_result, "model_dump") else (months_result and months_result.__dict__),
                            "content": content_result.model_dump() if content_result and hasattr(content_result, "model_dump") else (content_result and content_result.__dict__),
                        }
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    crawler_logger.error(f"监控循环异常: {e}")
                    self._state.last_result = {"error": str(e)}
                finally:
                    self._state.last_run_finished = datetime.now().isoformat()
                    self._state.cycles += 1

                await asyncio.sleep(self._state.interval_seconds)
        finally:
            self._state.running = False


# module-level singleton
monitor_manager = MonitorManager()
