from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class Product(Base):
    __tablename__ = "product"
    articul: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    number: Mapped[int]
    price: Mapped[float]
    rate: Mapped[float]