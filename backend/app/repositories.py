from typing import Protocol
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import get_db
from .models import Product, Sale, SupportRequest, User


class UserRepository(Protocol):
    def by_id(self, user_id: int) -> User | None: ...
    def by_username(self, username: str) -> User | None: ...


class ProductRepository(Protocol):
    def get(self, product_id: int) -> Product | None: ...
    def list(self, search: str = "") -> list[Product]: ...


class SupportRepository(Protocol):
    def list(self) -> list[SupportRequest]: ...
    def add(self, title: str, product_id: int) -> SupportRequest: ...


class SalesRepository(Protocol):
    def list(self) -> list[Sale]: ...


class MetricsRepository(Protocol):
    def summary(self) -> dict: ...


class SqliteUserRepository:
    def __init__(self, db: Session): self.db = db
    def by_id(self, user_id: int) -> User | None: return self.db.get(User, user_id)
    def by_username(self, username: str) -> User | None: return self.db.scalar(select(User).where(User.username == username))


class SqliteProductRepository:
    def __init__(self, db: Session): self.db = db
    def get(self, product_id: int) -> Product | None: return self.db.get(Product, product_id)
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


class SqliteMetricsRepository:
    def __init__(self, db: Session): self.db = db
    def summary(self) -> dict:
        requests = list(self.db.scalars(select(SupportRequest)))
        sales = list(self.db.scalars(select(Sale)))
        revenue_by_product: dict[str, float] = {}
        for item in sales:
            revenue_by_product[item.product.name] = revenue_by_product.get(item.product.name, 0) + item.revenue
        resolved = sorted((item.resolved_at - item.created_at).total_seconds() / 86400 for item in requests if item.resolved_at)
        return {
            "revenue": round(sum(item.revenue for item in sales), 2),
            "sales_count": sum(item.quantity for item in sales),
            "open_requests": sum(item.status != "resolved" for item in requests),
            "average_resolution_days": round(sum(resolved) / len(resolved), 1) if resolved else 0,
            "p95_resolution_days": round(resolved[min(len(resolved) - 1, int(len(resolved) * 0.95))], 1) if resolved else 0,
            "revenue_by_product": revenue_by_product,
        }


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository: return SqliteUserRepository(db)
def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository: return SqliteProductRepository(db)
def get_support_repository(db: Session = Depends(get_db)) -> SupportRepository: return SqliteSupportRepository(db)
def get_sales_repository(db: Session = Depends(get_db)) -> SalesRepository: return SqliteSalesRepository(db)
def get_metrics_repository(db: Session = Depends(get_db)) -> MetricsRepository: return SqliteMetricsRepository(db)
