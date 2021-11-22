from src.conf import logger
from fastapi import FastAPI, Request
from src.clients.milvus import MilvusHttpClient

__all__ = ("get_milvus",)


def get_milvus(request: Request):
    return request.app.state.milvus


async def on_startup(app: FastAPI) -> None:
    logger.info("Milvus dependency: start")
    app.state.milvus = MilvusHttpClient(
        base_url=app.state.settings.milvus.base_url
    )


async def on_shutdown(app: FastAPI) -> None:
    logger.info("Milvus dependency: shutdown")
    await app.state.milvus.close_session()
    app.state.milvus = None
