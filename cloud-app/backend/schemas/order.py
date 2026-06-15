from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class OrderItem(BaseModel):
    product_name: str
    sku: Optional[str] = None
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    discount: Optional[float] = 0.0
    total: Optional[float] = None

    def calculate_total(self):
        self.total = (self.quantity * self.price) - (self.discount or 0)
        return self.total


class OrderBase(BaseModel):
    description: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItem] = []


class OrderCreate(OrderBase):
    user_id: int
    due_date: Optional[datetime] = None
    discount: Optional[float] = 0.0
    tax: Optional[float] = 0.0


class OrderUpdate(BaseModel):
    description: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[OrderStatus] = None
    discount: Optional[float] = None
    tax: Optional[float] = None
    items: Optional[List[OrderItem]] = None
    due_date: Optional[datetime] = None


class Order(OrderBase):
    id: int
    order_number: str
    user_id: int
    status: OrderStatus
    total_amount: float
    discount: float
    tax: float
    final_amount: float
    order_date: datetime
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    is_archived: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderResponse(Order):
    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    user: Optional[dict] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
