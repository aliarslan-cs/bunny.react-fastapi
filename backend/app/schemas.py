from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProductOut(BaseModel):
    id: int
    name: str
    category: str
    price: float
    model_config = ConfigDict(from_attributes=True)


class SupportCreate(BaseModel):
    title: str
    product_id: int


class SupportOut(BaseModel):
    id: int
    title: str
    status: str
    product_id: int
    product_name: str
    created_at: datetime
    resolved_at: datetime | None


class SaleOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    revenue: float
    sold_at: datetime