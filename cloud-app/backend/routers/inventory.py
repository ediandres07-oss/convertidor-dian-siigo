import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.db.session import get_db
from backend.schemas.inventory import (
    InventoryCreate, InventoryUpdate, InventoryResponse,
    InventoryMovementCreate, InventoryMovement, InventorySearchResult,
)
from backend.schemas.common import Message, PaginatedResponse
from backend.models.inventory import Inventory, InventoryMovement, MovementType
from backend.models.user import User
from backend.dependencies import get_current_user, get_current_admin_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(
    inventory_data: InventoryCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Create new inventory item (admin only)."""
    # Check if SKU already exists
    existing = db.query(Inventory).filter(Inventory.sku == inventory_data.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists",
        )

    inventory = Inventory(**inventory_data.dict())
    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    logger.info(f"Inventory item created: {inventory.sku}")
    return inventory


@router.get("/{inventory_id}", response_model=InventoryResponse)
async def get_inventory(
    inventory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get inventory item by ID."""
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    return inventory


@router.get("", response_model=PaginatedResponse[InventoryResponse])
async def list_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: str | None = None,
    warehouse: str | None = None,
    low_stock: bool | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List inventory items with filters."""
    query = db.query(Inventory)

    if category:
        query = query.filter(Inventory.category == category)

    if warehouse:
        query = query.filter(Inventory.warehouse == warehouse)

    total = query.count()
    items = query.order_by(desc(Inventory.updated_at)).offset(skip).limit(limit).all()

    # Filter low stock in memory
    if low_stock is True:
        items = [item for item in items if item.is_low_stock]
    elif low_stock is False:
        items = [item for item in items if not item.is_low_stock]

    return PaginatedResponse(
        items=items,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
    )


@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(
    inventory_id: int,
    inventory_data: InventoryUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Update inventory item (admin only)."""
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    update_data = inventory_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(inventory, field, value)

    db.commit()
    db.refresh(inventory)

    logger.info(f"Inventory item updated: {inventory.sku}")
    return inventory


@router.delete("/{inventory_id}", response_model=Message)
async def delete_inventory(
    inventory_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Delete inventory item (admin only)."""
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    db.delete(inventory)
    db.commit()

    logger.info(f"Inventory item deleted: {inventory.sku}")
    return Message(message=f"Inventory item {inventory.sku} deleted successfully")


@router.post("/{inventory_id}/movements", response_model=InventoryMovement, status_code=status.HTTP_201_CREATED)
async def record_movement(
    inventory_id: int,
    movement_data: InventoryMovementCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Record inventory movement (admin only)."""
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    # Update quantity
    if movement_data.movement_type == MovementType.IN:
        inventory.quantity += movement_data.quantity
    elif movement_data.movement_type == MovementType.OUT:
        if inventory.quantity < movement_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock",
            )
        inventory.quantity -= movement_data.quantity
    elif movement_data.movement_type == MovementType.ADJUSTMENT:
        inventory.quantity = movement_data.quantity
    elif movement_data.movement_type == MovementType.RETURN:
        inventory.quantity += movement_data.quantity

    # Record movement
    movement = InventoryMovement(
        inventory_id=inventory_id,
        movement_type=movement_data.movement_type,
        quantity=movement_data.quantity,
        reference=movement_data.reference,
        notes=movement_data.notes,
        created_by=current_user.username,
    )

    db.add(movement)
    db.commit()
    db.refresh(movement)

    logger.info(f"Inventory movement recorded: {inventory.sku} {movement_data.movement_type.value}")
    return movement


@router.get("/search", response_model=list[InventorySearchResult])
async def search_inventory(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search inventory by name, SKU, or barcode."""
    query = db.query(Inventory).filter(
        (Inventory.name.ilike(f"%{q}%")) |
        (Inventory.sku.ilike(f"%{q}%")) |
        (Inventory.barcode.ilike(f"%{q}%"))
    ).limit(20)

    return query.all()


@router.get("/low-stock", response_model=list[InventoryResponse])
async def get_low_stock(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all low stock items."""
    items = db.query(Inventory).all()
    low_stock_items = [item for item in items if item.is_low_stock]
    return low_stock_items
