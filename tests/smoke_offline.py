import asyncio
from typing import Tuple

from src.crawler.classify_monitor import ClassifyMonitor
from src.crawler.month_data_fetcher import MonthDataFetcher
from src.crawler.content_fetcher import ContentFetcher
from src.utils.http_client import LocalHTTPClient


async def run_once() -> Tuple[int, int]:
    client = LocalHTTPClient()

    # 1) Classify
    m = ClassifyMonitor()
    m.http_client = client
    classify = await m.crawl()
    assert classify.success, f"classify failed: {classify.error}"

    # 2) Months
    mf = MonthDataFetcher()
    mf.http_client = client
    months = await mf.crawl()
    assert months.success, f"months failed: {months.error}"
    total_months = months.data.get("total_months", 0)  # pyright: ignore[reportOptionalMemberAccess]
    print(f"months total: {total_months}")

    # 3) Content
    cf = ContentFetcher()
    cf.http_client = client
    content = await cf.crawl()
    assert content.success, f"content failed: {content.error}"
    total_items = content.data.get("total_items", 0) # pyright: ignore[reportOptionalMemberAccess]
    skipped = sum(1 for v in content.data.get("results", {}).values() if v.get("skipped")) # pyright: ignore[reportOptionalMemberAccess]
    print(f"content total: {total_items}, skipped: {skipped}")
    return total_items, skipped


async def main():
    total1, skipped1 = await run_once()
    # Run again to validate skip logic
    total2, skipped2 = await run_once()
    assert total2 == total1, "total items changed between runs"
    assert skipped2 >= skipped1, "second run should skip more or equal"
    print("OK: skip logic verified")


if __name__ == "__main__":
    asyncio.run(main())

