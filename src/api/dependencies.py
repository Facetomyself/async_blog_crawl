from typing import AsyncGenerator

from fastapi import Depends, Query

from src.utils.http_client import AsyncHTTPClient, LocalHTTPClient, AbstractHTTPClient


async def get_http_client(
    offline: bool = Query(False, description="是否使用离线本地桩数据")
) -> AsyncGenerator[AbstractHTTPClient, None]:
    client: AbstractHTTPClient
    if offline:
        client = LocalHTTPClient()
    else:
        client = AsyncHTTPClient()

    await client.__aenter__()
    try:
        yield client
    finally:
        await client.__aexit__(None, None, None)

