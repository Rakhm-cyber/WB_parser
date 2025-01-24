from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select

from models import Product
from database import factory


async def add_prod(articul: int, name: str, number: int, price: float, rate: float):
    async with factory() as db:
        stmt = insert(Product).values(
            articul=articul,
            name=name,
            number=number,
            price=price,
            rate=rate
        ).on_conflict_do_update(
            index_elements=["articul"],
            set_={
                "name": name,
                "number": number,
                "price": price,
                "rate": rate
            }
        )

        await db.execute(stmt)
        await db.commit()

        result = await db.execute(
            select(Product).where(Product.articul == articul)
        )
        updated_product = result.scalar_one_or_none()

        return updated_product
