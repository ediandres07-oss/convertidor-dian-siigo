from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from backend.db.database import Base


class MovementType(str, enum.Enum):
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"
    RETURN = "return"


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True, nullable=True)

    # Stock
    quantity = Column(Integer, default=0)
    minimum_quantity = Column(Integer, default=10)
    maximum_quantity = Column(Integer, default=1000)

    # Pricing
    cost_price = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")

    # Location
    warehouse = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    bin = Column(String(50), nullable=True)

    # Metadata
    image_url = Column(String(500), nullable=True)
    unit = Column(String(50), default="piece")
    barcode = Column(String(100), unique=True, index=True, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Dates
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_restock_date = Column(DateTime, nullable=True)

    # Relationships
    movements = relationship("InventoryMovement", back_populates="inventory", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Inventory {self.sku}>"

    def __str__(self):
        return f"{self.name} ({self.sku}) - Stock: {self.quantity}"

    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.minimum_quantity

    @property
    def stock_percentage(self) -> float:
        if self.maximum_quantity == 0:
            return 0
        return (self.quantity / self.maximum_quantity) * 100


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False, index=True)
    movement_type = Column(Enum(MovementType), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    reference = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    inventory = relationship("Inventory", back_populates="movements")

    def __repr__(self):
        return f"<InventoryMovement {self.id}>"

    def __str__(self):
        return f"{self.movement_type.value.upper()} {self.quantity} units"
