from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.models import Order, OrderStatus, Rider, RiderStatus
from app.schemas.schemas import OrderCreate, OrderOut, OrderStatusUpdate, AssignmentResult
from app.services.assignment_engine import assign_single_order
from app.db.redis_client import decrement_rider_orders, publish_event

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(
    data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    order = Order(
        customer_id=data.customer_id,
        supermarket_id=data.supermarket_id,
        delivery_lat=data.delivery_lat,
        delivery_lon=data.delivery_lon,
        delivery_address=data.delivery_address,
        items_json=data.items_json,
        status=OrderStatus.pending,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    # Trigger immediate assignment attempt in background
    background_tasks.add_task(_try_assign, order.id)
    return order


async def _try_assign(order_id: int):
    """Background task: attempt to assign the order immediately."""
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await assign_single_order(order_id, db)


@router.get("/", response_model=List[OrderOut])
async def list_orders(
    status: OrderStatus = None,
    rider_id: int = None,
    supermarket_id: int = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(Order)
    if status:
        query = query.where(Order.status == status)
    if rider_id:
        query = query.where(Order.rider_id == rider_id)
    if supermarket_id:
        query = query.where(Order.supermarket_id == supermarket_id)
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status
    order.status = data.status
    now = datetime.now(timezone.utc)

    # Set timestamps based on transition
    if data.status == OrderStatus.picked_up:
        order.picked_up_at = now
    elif data.status == OrderStatus.delivered:
        order.delivered_at = now
        # Decrement rider's active order count in Redis
        if order.rider_id:
            await decrement_rider_orders(order.rider_id)
            # Increment total deliveries on rider
            rider = await db.get(Rider, order.rider_id)
            if rider:
                rider.total_deliveries += 1

    await db.commit()
    await db.refresh(order)

    # Publish status change event
    await publish_event("status_updates", {
        "event": "order_status_changed",
        "order_id": order_id,
        "old_status": old_status,
        "new_status": data.status,
        "rider_id": order.rider_id,
    })

    return order


@router.post("/trigger-assignment", response_model=dict)
async def trigger_manual_assignment(db: AsyncSession = Depends(get_db)):
    """
    Manually trigger an assignment cycle (useful for testing or ops override).
    """
    from app.services.assignment_engine import run_assignment_cycle
    result = await run_assignment_cycle(db)
    return {
        "assigned": len(result.assignments),
        "unassigned": len(result.unassigned_order_ids),
        "total_processed": result.total_orders_processed,
        "details": [a.model_dump() for a in result.assignments],
    }
