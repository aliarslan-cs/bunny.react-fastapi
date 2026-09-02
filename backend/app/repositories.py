from typing import Protocol
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Product, Sale, SupportRequest


class ProductRepository(Protocol):
    def list(self, search: str = "") -> list[Product]: ...


class SupportRepository(Protocol):
    def list(self) -> list[SupportRequest]: ...
    def add(self, title: str, product_id: int) -> SupportRequest: ...


class SalesRepository(Protocol):
    def list(self) -> list[Sale]: ...


class SqliteProductRepository:
    def __init__(self, db: Session): self.db = db
    def list(self, search: str = "") -> list[Product]:
        query = select(Product).order_by(Product.name)
        if search: query = query.where(Product.name.ilike(f"%{search}%"))
        return list(self.db.scalars(query))


class SqliteSupportRepository:
    def __init__(self, db: Session): self.db = db
    def list(self) -> list[SupportRequest]: return list(self.db.scalars(select(SupportRequest).order_by(SupportRequest.created_at.desc())))
    def add(self, title: str, product_id: int) -> SupportRequest:
        item = SupportRequest(title=title, product_id=product_id)
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item


class SqliteSalesRepository:
    def __init__(self, db: Session): self.db = db
    def list(self) -> list[Sale]: return list(self.db.scalars(select(Sale).order_by(Sale.sold_at)))