import logging
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from APIrouters import router_api
from database import engine, Base
from scheduler import scheduler

app = FastAPI()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    scheduler.start()
    logger.info("Сервер запущен и планировщик задач активирован")


async def stop_app():
    scheduler.remove_all_jobs()
    logger.info("Сервер остановлен")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await stop_app()


app.include_router(router_api)

