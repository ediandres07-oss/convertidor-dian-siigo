import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.user import User
from backend.models.order import Order, OrderStatus
from backend.models.inventory import Inventory
from backend.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get dashboard statistics."""
    try:
        # Orders statistics
        total_orders = db.query(Order).count()
        pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
        completed_orders = db.query(Order).filter(Order.status == OrderStatus.COMPLETED).count()

        # Calculate total revenue
        all_orders = db.query(Order).all()
        total_revenue = sum(order.final_amount for order in all_orders)

        # Inventory statistics
        inventory_items = db.query(Inventory).all()
        total_inventory = len(inventory_items)
        low_stock = sum(1 for item in inventory_items if item.is_low_stock)
        total_inventory_value = sum(item.quantity * item.cost_price for item in inventory_items)

        # Users (if admin)
        total_users = db.query(User).count() if current_user.is_admin else 1

        # Last 30 days orders
        last_30_days = datetime.utcnow() - timedelta(days=30)
        recent_orders = db.query(Order).filter(Order.created_at >= last_30_days).all()

        return {
            "orders": {
                "total": total_orders,
                "pending": pending_orders,
                "completed": completed_orders,
                "cancelled": db.query(Order).filter(Order.status == OrderStatus.CANCELLED).count(),
            },
            "revenue": {
                "total": total_revenue,
                "last_30_days": sum(o.final_amount for o in recent_orders),
                "average_order": total_revenue / total_orders if total_orders > 0 else 0,
            },
            "inventory": {
                "total_items": total_inventory,
                "low_stock_items": low_stock,
                "total_value": total_inventory_value,
            },
            "users": total_users if current_user.is_admin else None,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return {
            "error": "Error retrieving statistics",
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/recent-orders")
async def get_recent_orders(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recent orders."""
    try:
        from sqlalchemy import desc

        if current_user.is_admin:
            orders = db.query(Order).order_by(desc(Order.created_at)).limit(limit).all()
        else:
            orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(desc(Order.created_at)).limit(limit).all()

        return {
            "orders": [
                {
                    "id": order.id,
                    "order_number": order.order_number,
                    "status": order.status.value,
                    "amount": order.final_amount,
                    "date": order.created_at.isoformat(),
                }
                for order in orders
            ],
            "total": len(orders),
        }

    except Exception as e:
        logger.error(f"Error getting recent orders: {e}")
        return {"error": "Error retrieving orders", "total": 0, "orders": []}


@router.get("/inventory-status")
async def get_inventory_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get inventory status."""
    try:
        items = db.query(Inventory).all()

        categories = {}
        for item in items:
            if item.category not in categories:
                categories[item.category or "Uncategorized"] = {
                    "total": 0,
                    "value": 0,
                    "quantity": 0,
                }
            categories[item.category or "Uncategorized"]["total"] += 1
            categories[item.category or "Uncategorized"]["value"] += item.quantity * item.cost_price
            categories[item.category or "Uncategorized"]["quantity"] += item.quantity

        low_stock = [
            {
                "id": item.id,
                "sku": item.sku,
                "name": item.name,
                "quantity": item.quantity,
                "minimum": item.minimum_quantity,
            }
            for item in items if item.is_low_stock
        ]

        return {
            "total_items": len(items),
            "total_value": sum(item.quantity * item.cost_price for item in items),
            "low_stock_count": len(low_stock),
            "low_stock_items": low_stock[:5],  # Top 5
            "by_category": categories,
        }

    except Exception as e:
        logger.error(f"Error getting inventory status: {e}")
        return {"error": "Error retrieving inventory status"}


@router.get("/sales-chart")
async def get_sales_chart(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get sales data for chart."""
    try:
        from collections import defaultdict
        from sqlalchemy import func, Date

        start_date = datetime.utcnow() - timedelta(days=days)

        query = db.query(
            func.date(Order.created_at).label("date"),
            func.count(Order.id).label("count"),
            func.sum(Order.final_amount).label("amount"),
        ).filter(Order.created_at >= start_date).group_by(func.date(Order.created_at))

        if not current_user.is_admin:
            query = query.filter(Order.user_id == current_user.id)

        results = query.all()

        data = []
        for date, count, amount in results:
            data.append({
                "date": date.isoformat(),
                "orders": count,
                "revenue": float(amount or 0),
            })

        return {
            "period_days": days,
            "data": data,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting sales chart: {e}")
        return {"error": "Error retrieving sales data", "data": []}
