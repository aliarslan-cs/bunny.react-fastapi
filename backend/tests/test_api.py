import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["COLD_START"] = "false"
from fastapi.testclient import TestClient
from app.db import Base, engine
from app.main import app
from scripts.seed import seed

Base.metadata.drop_all(engine); Base.metadata.create_all(engine); seed()
client = TestClient(app)


def token(username: str, password: str) -> str:
    return client.post("/auth/login", json={"username": username, "password": password}).json()["access_token"]


def test_login_and_product_access():
    response = client.get("/products", headers={"Authorization": f"Bearer {token('worker', 'rekrow')}"})
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_worker_cannot_see_sales():
    response = client.get("/sales", headers={"Authorization": f"Bearer {token('worker', 'rekrow')}"})
    assert response.status_code == 403


def test_correlation_headers():
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert response.headers["x-request-id"].startswith("req-")


def test_custom_request_id_propagated():
    custom_id = "test-custom-request-id-12345"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == custom_id