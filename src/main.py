import asyncio
from fastapi import FastAPI

from src.conf import settings
from src.dependencies import base, milvus
from src.routers import monitor

__version__ = "0.1.0"


def setup_app(application: FastAPI) -> None:
    dependencies = [base, milvus]

    @application.on_event("startup")
    async def startup():
        application.state.settings = settings

        try:
            for dependency in dependencies:
                coroutine = dependency.on_startup(application)
                if asyncio.iscoroutine(coroutine):
                    await coroutine
        except Exception as e:
            try:
                await shutdown()
            finally:
                raise e

    @application.on_event("shutdown")
    async def shutdown():
        for dependency in reversed(dependencies):
            try:
                coroutine = dependency.on_shutdown(application)
                if asyncio.iscoroutine(coroutine):
                    await coroutine
            except Exception as e:
                raise e


app = FastAPI(
    title="magic-matcher-svc",
    openapi_prefix=settings.api_prefix,
    version=__version__,
)

setup_app(app)

# Setup monitor routers
app.include_router(
    monitor.router, responses={404: {"description": "Not found"}}
)
