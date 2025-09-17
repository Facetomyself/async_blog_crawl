from fastapi import FastAPI

from src.api.routers.watch import router as watch_router
from src.api.routers.crawl import router as crawl_router
from src.api.routers.verify import router as verify_router


def create_app() -> FastAPI:
    app = FastAPI(title="Blog Crawler API", version="1.0.0")

    @app.get("/health", tags=["system"], summary="健康检查")
    async def health():
        return {"status": "ok"}

    app.include_router(watch_router)
    app.include_router(crawl_router)
    app.include_router(verify_router)
    return app


app = create_app()

