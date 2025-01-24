import os

import httpx
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

from ORM import add_prod
from scheduler import scheduler

load_dotenv()

router_api = APIRouter()

SECRET_TOKEN = os.getenv("SECRET_TOKEN")
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return credentials.credentials


class ProdReq(BaseModel):
    articul: int


async def product_search(artikul: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={artikul}")
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



@router_api.get("/")
async def firstendpoint(token: str = Depends(verify_token)):
    return {"answer": "Hello, user"}


@router_api.post("/api/v1/products")
async def create_product(product: ProdReq, token: str = Depends(verify_token)):
    return await product_search(product.articul)


@router_api.get("/api/v1/subscribe/{artikul}")
async def product_subscribe(artikul: int, token: str = Depends(verify_token)):
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
async def remove_all_jobs_endpoint(token: str = Depends(verify_token)):
    scheduler.remove_all_jobs()
    return {"message": "Все задачи удалены"}
