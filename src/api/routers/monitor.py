from pydantic import BaseModel, Field
from fastapi import APIRouter

from config.settings import MONITOR_DEFAULT_INTERVAL
from src.services.monitor import monitor_manager


class StartRequest(BaseModel):
    interval_seconds: int = Field(MONITOR_DEFAULT_INTERVAL, ge=1, description="监控间隔秒数")
    offline: bool = Field(False, description="是否使用离线样例数据")
    crawl_on_update: bool = Field(True, description="检测到更新时是否执行完整抓取")


class IntervalRequest(BaseModel):
    interval_seconds: int = Field(MONITOR_DEFAULT_INTERVAL, ge=1)


router = APIRouter(prefix="/monitor", tags=["monitor"])


@router.get("/status", summary="获取监控状态")
async def status():
    return monitor_manager.status()


@router.post("/start", summary="启动监控循环")
async def start(req: StartRequest):
    return await monitor_manager.start(
        interval_seconds=req.interval_seconds,
        offline=req.offline,
        crawl_on_update=req.crawl_on_update,
    )


@router.post("/stop", summary="停止监控循环")
async def stop():
    return await monitor_manager.stop()


@router.post("/interval", summary="更新监控间隔")
async def set_interval(req: IntervalRequest):
    return await monitor_manager.set_interval(req.interval_seconds)

