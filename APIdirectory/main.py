import logging
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from APIrouters import router_api
from database import engine, Base
from scheduler import scheduler

app = FastAPI()


@app.on_event("startup")
async def startup():
    print("Сервер запущен, создается база данных...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    scheduler.start()


app.include_router(router_api)

