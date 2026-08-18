import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.router import api_router
from app.core.db import mongodb
from app.core.exception import register_exception_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb.connect()
    yield
    await mongodb.close()


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Hello World"}
