import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import uuid

from backend.db.session import get_db
from backend.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderDetailResponse
from backend.schemas.common import Message, PaginatedResponse
from backend.models.order import Order, OrderStatus
from backend.models.user import User
from backend.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


def generate_order_number():
    """Generate unique order number."""
    return f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


@router.post("", response_model=OrderDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new order."""
    user = db.query(User).filter(User.id == order_data.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Calculate totals
    total_amount = sum(item.quantity * item.price for item in order_data.items)
    final_amount = (total_amount - (order_data.discount or 0)) + (order_data.tax or 0)

    order = Order(
        order_number=generate_order_number(),
        user_id=order_data.user_id,
        description=order_data.description,
        notes=order_data.notes,
        items=[item.dict() for item in order_data.items],
        total_amount=total_amount,
        discount=order_data.discount or 0.0,
        tax=order_data.tax or 0.0,
        final_amount=final_amount,
        due_date=order_data.due_date,
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    logger.info(f"Order created: {order.order_number}")
    return order


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get order by ID."""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order",
        )

    return order


@router.get("", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: OrderStatus | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List orders."""
    query = db.query(Order)

    # Filter by user if not admin
    if not current_user.is_admin:
        query = query.filter(Order.user_id == current_user.id)

    if status_filter:
        query = query.filter(Order.status == status_filter)

    query = query.filter(Order.is_deleted == False)

    total = query.count()
    orders = query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()

    return PaginatedResponse(
        items=orders,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
    )


@router.put("/{order_id}", response_model=OrderDetailResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update order."""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this order",
        )

    update_data = order_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        if field == "items" and value:
            setattr(order, field, [item.dict() for item in value])
        else:
            setattr(order, field, value)

    # Recalculate totals if items or discount/tax changed
    if "items" in update_data or "discount" in update_data or "tax" in update_data:
        if order.items:
            order.total_amount = sum(item.get("quantity", 0) * item.get("price", 0) for item in order.items)
        order.final_amount = (order.total_amount - order.discount) + order.tax

    # Set completed date if status is completed
    if order_data.status == OrderStatus.COMPLETED:
        order.completed_date = datetime.utcnow()

    db.commit()
    db.refresh(order)

    logger.info(f"Order updated: {order.order_number}")
    return order


@router.delete("/{order_id}", response_model=Message)
async def delete_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete order (soft delete)."""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this order",
        )

    order.is_deleted = True
    db.commit()

    logger.info(f"Order deleted: {order.order_number}")
    return Message(message=f"Order {order.order_number} deleted successfully")


@router.post("/{order_id}/archive", response_model=Message)
async def archive_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Archive order."""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive this order",
        )

    order.is_archived = True
    db.commit()

    logger.info(f"Order archived: {order.order_number}")
    return Message(message=f"Order {order.order_number} archived")
