"""
博客爬虫主应用
"""
import asyncio
import signal
import sys

from config.settings import MONITOR_INTERVAL
from src.crawler.classify_monitor import ClassifyMonitor
from src.crawler.month_data_fetcher import MonthDataFetcher
from src.crawler.content_fetcher import ContentFetcher
from src.utils.logger import crawler_logger


class BlogCrawlerApp:
    """博客爬虫主应用"""

    def __init__(self):
        self.running = False
        self.monitor_interval = MONITOR_INTERVAL

    async def run_once(self) -> bool:
        """执行一次完整的爬取流程"""
        try:
            crawler_logger.info("开始执行爬取任务")

            # 1. 监控分类接口
            crawler_logger.info("步骤1: 监控分类接口")
            async with ClassifyMonitor() as monitor:
                classify_result = await monitor.crawl()
                if not classify_result.success:
                    crawler_logger.error(f"分类接口监控失败: {classify_result.error}")
                    return False

                if classify_result.data and classify_result.data.get("updated", False):
                    crawler_logger.info("检测到分类数据更新，开始获取详细数据")
                else:
                    crawler_logger.info("分类数据无变化，跳过详细数据获取")

            # 2. 获取月份数据
            crawler_logger.info("步骤2: 获取月份数据")
            async with MonthDataFetcher() as fetcher:
                month_result = await fetcher.crawl()
                if not month_result.success:
                    crawler_logger.error(f"月份数据获取失败: {month_result.error}")
                    return False

                crawler_logger.info(f"月份数据获取完成: {month_result.data}")

            # 3. 获取内容详情
            crawler_logger.info("步骤3: 获取内容详情")
            async with ContentFetcher() as fetcher:
                content_result = await fetcher.crawl()
                if not content_result.success:
                    crawler_logger.error(f"内容详情获取失败: {content_result.error}")
                    return False

                crawler_logger.info(f"内容详情获取完成: {content_result.data}")

            crawler_logger.info("爬取任务执行完成")
            return True

        except Exception as e:
            crawler_logger.error(f"爬取任务执行失败: {e}")
            return False

    async def run_monitor(self):
        """运行监控模式"""
        crawler_logger.info(f"启动监控模式，间隔: {self.monitor_interval}秒")

        while self.running:
            try:
                success = await self.run_once()

                if success:
                    crawler_logger.info(f"等待 {self.monitor_interval} 秒后进行下次检查")
                else:
                    crawler_logger.warning("本次执行失败，将继续监控")

                await asyncio.sleep(self.monitor_interval)

            except asyncio.CancelledError:
                crawler_logger.info("监控任务被取消")
                break
            except Exception as e:
                crawler_logger.error(f"监控循环异常: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟再试

    async def start(self, monitor: bool = False):
        """启动应用"""
        self.running = True

        if monitor:
            # 监控模式
            crawler_logger.info("启动监控模式")

            def signal_handler(signum, frame):
                crawler_logger.info("收到停止信号，正在退出...")
                self.running = False

            # 注册信号处理器
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            try:
                await self.run_monitor()
            except KeyboardInterrupt:
                crawler_logger.info("收到键盘中断，正在退出...")
            finally:
                crawler_logger.info("监控模式已停止")

        else:
            # 单次执行模式
            crawler_logger.info("启动单次执行模式")
            success = await self.run_once()
            sys.exit(0 if success else 1)

    async def stop(self):
        """停止应用"""
        crawler_logger.info("正在停止应用...")
        self.running = False


async def main():
    """主入口函数"""
    import argparse

    parser = argparse.ArgumentParser(description="博客爬虫")
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="启用监控模式，定期检查更新"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=MONITOR_INTERVAL,
        help=f"监控间隔时间(秒)，默认: {MONITOR_INTERVAL}"
    )

    args = parser.parse_args()

    app = BlogCrawlerApp()
    app.monitor_interval = args.interval

    try:
        await app.start(monitor=args.monitor)
    except Exception as e:
        crawler_logger.error(f"应用启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
