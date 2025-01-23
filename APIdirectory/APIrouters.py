from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.triggers.interval import IntervalTrigger
from pytz import utc
import httpx
from ORM import add_prod
from database import engine, Base
import asyncio

app = FastAPI()

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

class ProdReq(BaseModel):
    articul: int


router_api = APIRouter()

scheduler = AsyncIOScheduler(jobstores = jobstores)

async def product_search(artikul: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={artikul}")
            response.raise_for_status()
            data = response.json()
            print(f"обновляю данные о продукте({artikul})...")
            if "data" not in data or "products" not in data["data"] or not data["data"]["products"]:
                raise HTTPException(status_code=404, detail="Product not found")

            product_data = data["data"]["products"][0]
            articul = product_data["id"]
            name = product_data["name"]
            price = product_data.get("salePriceU", 0) / 100
            number = product_data.get("totalQuantity", 0)
            rate = product_data.get("reviewRating", 0)
            return await add_prod(articul, name, number, price, rate)
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=404, detail="Product not found")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    scheduler.start()

@router_api.get("/")
async def firstendpoint():
    return {"answer": "Hello, user"}

@router_api.post("/api/v1/products")
async def create_product(product: ProdReq):
    return await product_search(product.articul)

@router_api.get("/api/v1/subscribe/{artikul}")
async def product_subscribe(artikul: int):
    job_id = f'job_{artikul}'
    if scheduler.get_job(job_id):
        return {"message": f"Подписка на товар с артикулом {artikul} уже запущена"}
    scheduler.add_job(
        product_search,
        trigger=IntervalTrigger(seconds=5),
        args=[artikul],
        jobstore='default'
    )
    return {"message": f"Подписка на товар с артикулом {artikul} запущена"}

@router_api.get("/api/v1/remove_all_jobs")
async def remove_all_jobs_endpoint():
    scheduler.remove_all_jobs()
    return {"message": "Все задачи удалены"}

app.include_router(router_api)
