from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ---- Car Brand ----
class CarBrandCreate(BaseModel):
    name: str
    country: str

class CarBrandUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None

class CarBrandResponse(BaseModel):
    id: int
    name: str
    country: str
    models_count: int = 0

    class Config:
        from_attributes = True


# ---- Car Model ----
class CarModelCreate(BaseModel):
    brand_id: int
    name: str
    year: int
    tyre_sizes: list[str] = []

class CarModelUpdate(BaseModel):
    brand_id: Optional[int] = None
    name: Optional[str] = None
    year: Optional[int] = None
    tyre_sizes: Optional[list[str]] = None

class CarModelResponse(BaseModel):
    id: int
    brand_id: int
    brand_name: str = ""
    name: str
    year: int
    tyre_sizes: list[str] = []

    class Config:
        from_attributes = True


# ---- Tyre Brand ----
class TyreBrandCreate(BaseModel):
    name: str
    country: str

class TyreBrandUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None

class TyreBrandResponse(BaseModel):
    id: int
    name: str
    country: str
    tyres_count: int = 0

    class Config:
        from_attributes = True


# ---- Tyre ----
class TyreCreate(BaseModel):
    brand_id: int
    model: str
    size: str
    type: str
    price: float
    cost: float = 0
    stock: int = 0
    min_stock_level: int = 50

class TyreUpdate(BaseModel):
    brand_id: Optional[int] = None
    model: Optional[str] = None
    size: Optional[str] = None
    type: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    stock: Optional[int] = None
    min_stock_level: Optional[int] = None

class TyreResponse(BaseModel):
    id: int
    brand_id: int
    brand_name: str = ""
    model: str
    size: str
    type: str
    price: float
    cost: float
    stock: int
    min_stock_level: int = 50

    class Config:
        from_attributes = True


# ---- Order ----
class OrderItemCreate(BaseModel):
    tyre_id: int
    quantity: int = 1

class OrderCreate(BaseModel):
    customer_name: str
    shipping_address: Optional[str] = None
    payment_method: Optional[str] = None
    items: list[OrderItemCreate] = []

class OrderItemResponse(BaseModel):
    id: int
    tyre_id: int
    tyre_name: str = ""
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    status: str
    total_amount: float
    shipping_address: Optional[str] = None
    payment_method: Optional[str] = None
    items_count: int = 0
    items: list[OrderItemResponse] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str


# ---- Chat ----
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None

class ChatMessageResponse(BaseModel):
    id: int
    sender: str
    text: str
    timestamp: str = ""

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    session_id: int
    message: ChatMessageResponse
    agent_response: ChatMessageResponse


# ---- Dashboard ----
class DashboardStats(BaseModel):
    total_orders: int
    total_revenue: float
    tyres_in_stock: int
    car_models: int


# ---- Stock ----
class StockItemResponse(BaseModel):
    id: int
    brand_name: str
    model: str
    size: str
    current_stock: int
    min_level: int
    status: str
    last_update: str

    class Config:
        from_attributes = True

class StockUpdate(BaseModel):
    stock: int
