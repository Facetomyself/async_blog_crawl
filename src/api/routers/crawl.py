from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_http_client
from src.crawler.classify_monitor import ClassifyMonitor
from src.crawler.month_data_fetcher import MonthDataFetcher
from src.crawler.content_fetcher import ContentFetcher
from src.utils.http_client import AbstractHTTPClient
from src.utils.models import ContentItem


router = APIRouter(prefix="/crawl", tags=["crawl"])


@router.post("/run", summary="执行一次完整的爬取流程")
async def crawl_once(
    client: AbstractHTTPClient = Depends(get_http_client),
):
    # 1. 分类监控
    monitor = ClassifyMonitor()
    monitor.http_client = client
    classify_result = await monitor.crawl()
    if not classify_result.success:
        return {"success": False, "stage": "classify", "error": classify_result.error}

    # 2. 月份列表 & 数据
    month_fetcher = MonthDataFetcher()
    month_fetcher.http_client = client
    month_result = await month_fetcher.crawl()
    if not month_result.success:
        return {"success": False, "stage": "months", "error": month_result.error}

    # 3. 内容详情
    content_fetcher = ContentFetcher()
    content_fetcher.http_client = client
    content_result = await content_fetcher.crawl()
    if not content_result.success:
        return {"success": False, "stage": "content", "error": content_result.error}

    return {
        "success": True,
        "classify": classify_result.model_dump(),
        "months": month_result.model_dump(),
        "content": content_result.model_dump(),
    }


@router.post("/item/{type}/{item_id}", summary="爬取单个内容详情（支持跳过已存在）")
async def crawl_single_item(
    type: str,
    item_id: int,
    force: bool = False,
    client: AbstractHTTPClient = Depends(get_http_client),
):
    if type not in {"article", "section"}:
        raise HTTPException(status_code=400, detail="type must be 'article' or 'section'")

    fetcher = ContentFetcher()
    fetcher.http_client = client

    # 构造最小可用的内容项（标题仅用于返回展示）
    item = ContentItem(type=type, id=item_id, title=f"{type}-{item_id}", created_time="1970-01-01T00:00:00Z")

    # 如强制，先删除本地已存在文件再拉取
    if force:
        md = Path(fetcher.content_data_dir / f"{type}_{item_id}.md")
        meta = Path(fetcher.content_data_dir / f"{type}_{item_id}_meta.json")
        for fp in (md, meta):
            if fp.exists():
                fp.unlink()

    result = await fetcher._fetch_content_detail(item)
    return result

