from fastapi import FastAPI, Request, status, Depends, Cookie
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.exception_handlers import (
    http_exception_handler as fastapi_http_exception_handler,
    request_validation_exception_handler as fastapi_request_validation_exception_handler,
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from pprint import pprint
import json
from typing import Annotated
import uvicorn
from contextlib import asynccontextmanager
from pydantic import BaseModel
from inspect import cleandoc
from core.exception_handlers import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
import apps.users.routers
import time as time_module
import threading
from core.settings import settings
from core.database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(
    debug=False,
    exception_handlers={
        Exception: general_exception_handler,
        StarletteHTTPException: http_exception_handler,
        RequestValidationError: validation_exception_handler,
    },
    lifespan=lifespan
)

templates = settings.templates

app.include_router(apps.blog.routers.views_router)
app.include_router(apps.blog.routers.api_router, tags=["posts"], prefix="/api")
app.include_router(apps.users.routers.views_router)
app.include_router(apps.users.routers.api_router, tags=["users"], prefix="/api")

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app)
