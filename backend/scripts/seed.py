from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.db import Base, SessionLocal, engine
from app.models import Product, Sale, SupportRequest, User
from app.security import hash_password


def seed() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.username == "manager")): return
        db.add_all([User(username="manager", password_hash=hash_password("reganam"), role="manager"), User(username="worker", password_hash=hash_password("rekrow"), role="worker")])
        products = [Product(name="Field Kit", category="Hardware", price=149), Product(name="Cloud Sync", category="Software", price=39), Product(name="Care Plan", category="Service", price=79)]
        db.add_all(products); db.flush()
        now = datetime.now(timezone.utc)
        db.add_all([SupportRequest(title="Sync is delayed", product_id=products[1].id), SupportRequest(title="Replace damaged kit", product_id=products[0].id, status="resolved", created_at=now - timedelta(days=12), resolved_at=now - timedelta(days=8))])
        db.add_all([Sale(product_id=products[0].id, quantity=8, revenue=1192, sold_at=now - timedelta(days=4)), Sale(product_id=products[1].id, quantity=22, revenue=858, sold_at=now - timedelta(days=18)), Sale(product_id=products[2].id, quantity=14, revenue=1106, sold_at=now - timedelta(days=35))])
        db.commit()


if __name__ == "__main__": seed()