from fastapi import APIRouter, Depends

from src.api.dependencies import get_http_client
from src.crawler.classify_monitor import ClassifyMonitor
from src.utils.http_client import AbstractHTTPClient


router = APIRouter(prefix="/watch", tags=["watch"])


@router.get("", summary="检查分类接口是否更新")
async def watch_updates(
    client: AbstractHTTPClient = Depends(get_http_client),
):
    monitor = ClassifyMonitor()
    # 注入 DI 客户端
    monitor.http_client = client
    result = await monitor.crawl()
    # pydantic v2
    return result.model_dump()

