import re
from fastapi import FastAPI, Request
from src.conf import logger


__all__ = (
    "get_slug",
    "get_version",
)

SLUG_RE = re.compile(r"\W")


def get_version(request: Request):
    return request.app.version


def get_slug(request: Request):
    return SLUG_RE.sub("-", request.app.title.lower())


def on_startup(app: FastAPI) -> None:
    logger.info("App instance: start")
    pass


def on_shutdown(app: FastAPI):
    logger.info("App instance: shutdown")
    pass
