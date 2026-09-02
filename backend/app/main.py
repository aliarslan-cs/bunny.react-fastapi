from collections import defaultdict
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import settings
from .db import Base, engine, get_db
from .models import Product, Sale, SupportRequest, User
from .repositories import SqliteProductRepository, SqliteSalesRepository, SqliteSupportRepository
from .schemas import LoginRequest, ProductOut, SaleOut, SupportCreate, SupportOut, Token, UserOut
from .security import create_token, current_user, manager_only, verify_password

app = FastAPI(title="Bunny Boilerplate API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(engine)
    if settings.cold_start:
        from scripts.seed import seed
        seed()


@app.get("/health")
def health() -> dict[str, str]: return {"status": "ok"}


@app.post("/auth/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = db.scalar(select(User).where(User.username == credentials.username))
    if not user or not verify_password(credentials.password, user.password_hash): raise HTTPException(401, "Invalid username or password")
    return Token(access_token=create_token(user), user=UserOut.model_validate(user))


@app.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(current_user)) -> User: return user


@app.get("/products", response_model=list[ProductOut])
def products(search: str = Query(""), db: Session = Depends(get_db), _: User = Depends(current_user)) -> list[Product]: return SqliteProductRepository(db).list(search)


def to_support(item: SupportRequest) -> SupportOut:
    return SupportOut(id=item.id, title=item.title, status=item.status, product_id=item.product_id, product_name=item.product.name, created_at=item.created_at, resolved_at=item.resolved_at)


@app.get("/support-requests", response_model=list[SupportOut])
def support_requests(db: Session = Depends(get_db), _: User = Depends(current_user)) -> list[SupportOut]: return [to_support(item) for item in SqliteSupportRepository(db).list()]


@app.post("/support-requests", response_model=SupportOut)
def create_support(data: SupportCreate, db: Session = Depends(get_db), _: User = Depends(current_user)) -> SupportOut:
    if not db.get(Product, data.product_id): raise HTTPException(404, "Product not found")
    return to_support(SqliteSupportRepository(db).add(data.title, data.product_id))


@app.get("/sales", response_model=list[SaleOut])
def sales(db: Session = Depends(get_db), _: User = Depends(manager_only)) -> list[SaleOut]:
    return [SaleOut(id=item.id, product_id=item.product_id, product_name=item.product.name, quantity=item.quantity, revenue=item.revenue, sold_at=item.sold_at) for item in SqliteSalesRepository(db).list()]


@app.get("/metrics/summary")
def metrics(db: Session = Depends(get_db), _: User = Depends(manager_only)) -> dict:
    requests = list(db.scalars(select(SupportRequest)))
    sales_items = list(db.scalars(select(Sale)))
    by_product = defaultdict(float)
    for item in sales_items: by_product[item.product.name] += item.revenue
    resolved = sorted((item.resolved_at - item.created_at).total_seconds() / 86400 for item in requests if item.resolved_at)
    return {"revenue": round(sum(item.revenue for item in sales_items), 2), "sales_count": sum(item.quantity for item in sales_items), "open_requests": sum(item.status != "resolved" for item in requests), "average_resolution_days": round(sum(resolved) / len(resolved), 1) if resolved else 0, "p95_resolution_days": round(resolved[min(len(resolved) - 1, int(len(resolved) * .95))], 1) if resolved else 0, "revenue_by_product": dict(by_product)}


@app.post("/dev/seed")
def reseed(_: User = Depends(manager_only)) -> dict[str, str]:
    from scripts.seed import seed
    seed(); return {"status": "seeded"}