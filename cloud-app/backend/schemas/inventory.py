from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class MovementType(str, Enum):
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"
    RETURN = "return"


class InventoryBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    quantity: int = Field(default=0, ge=0)
    minimum_quantity: int = Field(default=10, ge=0)
    maximum_quantity: int = Field(default=1000, ge=0)
    cost_price: float = Field(default=0.0, ge=0)
    selling_price: float = Field(default=0.0, ge=0)
    currency: str = Field(default="USD", max_length=3)
    warehouse: Optional[str] = None
    location: Optional[str] = None
    unit: str = Field(default="piece")
    barcode: Optional[str] = None


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    minimum_quantity: Optional[int] = None
    maximum_quantity: Optional[int] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    warehouse: Optional[str] = None
    location: Optional[str] = None
    unit: Optional[str] = None


class InventoryMovementCreate(BaseModel):
    inventory_id: int
    movement_type: MovementType
    quantity: int = Field(..., gt=0)
    reference: Optional[str] = None
    notes: Optional[str] = None


class InventoryMovement(BaseModel):
    id: int
    inventory_id: int
    movement_type: MovementType
    quantity: int
    reference: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Inventory(InventoryBase):
    id: int
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_restock_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventoryResponse(Inventory):
    is_low_stock: bool
    stock_percentage: float
    movements: Optional[list[InventoryMovement]] = None

    class Config:
        from_attributes = True


class InventoryDetailResponse(InventoryResponse):
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class InventorySearchResult(BaseModel):
    id: int
    sku: str
    name: str
    quantity: int
    selling_price: float
    is_low_stock: bool
    warehouse: Optional[str] = None
    location: Optional[str] = None

    class Config:
        from_attributes = True
