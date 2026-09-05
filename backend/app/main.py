from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from sqlalchemy import text
from sqlalchemy.orm import Session
from .config import settings
from .db import Base, engine, get_db
from .models import Product, Sale, SupportRequest, User
from .repositories import (
    MetricsRepository, ProductRepository, SalesRepository, SupportRepository,
    UserRepository, get_metrics_repository, get_product_repository,
    get_sales_repository, get_support_repository, get_user_repository,
)
from .schemas import (
    LoginRequest,
    ProductOut,
    SaleOut,
    SupportCreate,
    SupportOut,
    Token,
    UserOut,
)
from .logging_config import setup_logging
from .middleware import CorrelationMiddleware
from .security import create_token, current_user, manager_only, verify_password
from .telemetry import setup_telemetry

# Initialize structured logging subsystem
setup_logging()

app = FastAPI(title="Bunny Boilerplate API", version="0.1.0", redoc_url=None)

# Correlation and access logging middleware
app.add_middleware(CorrelationMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Trace-ID"],
)

# Setup OpenTelemetry distributed tracing and metrics
setup_telemetry(app, engine)


@app.get("/redoc", include_in_schema=False)
def redoc() -> str:
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title,
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.4.0/bundles/redoc.standalone.js",
    )


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(engine)
    if settings.cold_start:
        from scripts.seed import seed

        seed()


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception:
        raise HTTPException(503, "Database unavailable")


@app.post("/auth/login", response_model=Token)
def login(credentials: LoginRequest, repository: UserRepository = Depends(get_user_repository)) -> Token:
    user = repository.by_username(credentials.username)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(401, "Invalid username or password")
    return Token(access_token=create_token(user), user=UserOut.model_validate(user))


@app.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(current_user)) -> User:
    return user


@app.get("/products", response_model=list[ProductOut])
def products(
    search: str = Query(""),
    repository: ProductRepository = Depends(get_product_repository),
    _: User = Depends(current_user),
) -> list[Product]:
    return repository.list(search)


def to_support(item: SupportRequest) -> SupportOut:
    return SupportOut(
        id=item.id,
        title=item.title,
        status=item.status,
        product_id=item.product_id,
        product_name=item.product.name,
        created_at=item.created_at,
        resolved_at=item.resolved_at,
    )


@app.get("/support-requests", response_model=list[SupportOut])
def support_requests(
    repository: SupportRepository = Depends(get_support_repository), _: User = Depends(current_user)
) -> list[SupportOut]:
    return [to_support(item) for item in repository.list()]


@app.post("/support-requests", response_model=SupportOut)
def create_support(
    data: SupportCreate, repository: SupportRepository = Depends(get_support_repository), products: ProductRepository = Depends(get_product_repository), _: User = Depends(current_user)
) -> SupportOut:
    if not products.get(data.product_id):
        raise HTTPException(404, "Product not found")
    return to_support(repository.add(data.title, data.product_id))


@app.get("/sales", response_model=list[SaleOut])
def sales(
    repository: SalesRepository = Depends(get_sales_repository), _: User = Depends(manager_only)
) -> list[SaleOut]:
    return [
        SaleOut(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name,
            quantity=item.quantity,
            revenue=item.revenue,
            sold_at=item.sold_at,
        )
        for item in repository.list()
    ]


@app.get("/metrics/summary")
def metrics(
    repository: MetricsRepository = Depends(get_metrics_repository),
    _: User = Depends(manager_only),
) -> dict:
    return repository.summary()


@app.post("/dev/seed")
def reseed(_: User = Depends(manager_only)) -> dict[str, str]:
    from scripts.seed import seed

    seed()
    return {"status": "seeded"}
