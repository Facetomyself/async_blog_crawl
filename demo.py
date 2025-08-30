#!/usr/bin/env python3
"""
博客爬虫演示脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.crawler.classify_monitor import ClassifyMonitor
from src.crawler.month_data_fetcher import MonthDataFetcher
from src.crawler.content_fetcher import ContentFetcher
from src.utils.logger import crawler_logger


async def demo():
    """演示爬虫功能"""
    print("博客爬虫演示开始...")

    try:
        # 1. 演示分类接口监控
        print("\n1. 监控分类接口...")
        async with ClassifyMonitor() as monitor:
            result = await monitor.crawl()
            print(f"分类接口监控结果: {'成功' if result.success else '失败'}")
            if result.success and result.data:
                updated = result.data.get("updated", False)
                print(f"数据是否更新: {'是' if updated else '否'}")

        # 2. 演示月份数据获取
        print("\n2. 获取月份数据...")
        async with MonthDataFetcher() as fetcher:
            result = await fetcher.crawl()
            print(f"月份数据获取结果: {'成功' if result.success else '失败'}")
            if result.success and result.data:
                total = result.data.get("total_months", 0)
                success = result.data.get("success_count", 0)
                print(f"月份总数: {total}, 成功获取: {success}")

        # 3. 演示内容详情获取
        print("\n3. 获取内容详情...")
        async with ContentFetcher() as fetcher:
            try:
                result = await fetcher.crawl()
                print(f"内容详情获取结果: {'成功' if result.success else '失败'}")
                if result.success and result.data:
                    total = result.data.get("total_items", 0)
                    success = result.data.get("success_count", 0)
                    print(f"内容项总数: {total}, 成功获取: {success}")
                elif not result.success:
                    print(f"失败原因: {result.error}")
            except Exception as e:
                print(f"内容详情获取异常: {e}")
                import traceback
                traceback.print_exc()

        print("\n演示完成！")

    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(demo())
    sys.exit(0 if success else 1)
