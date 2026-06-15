from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import enum

from backend.db.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Financial
    total_amount = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    final_amount = Column(Float, default=0.0)

    # Items
    items = Column(JSON, nullable=True)

    # Dates
    order_date = Column(DateTime, default=datetime.utcnow, index=True)
    due_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Metadata
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    metadata = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders")

    def __repr__(self):
        return f"<Order {self.order_number}>"

    def __str__(self):
        return f"Order {self.order_number} - {self.status.value}"

    def calculate_total(self):
        if self.items:
            self.total_amount = sum(item.get("quantity", 0) * item.get("price", 0) for item in self.items)
            self.final_amount = (self.total_amount - self.discount) + self.tax
