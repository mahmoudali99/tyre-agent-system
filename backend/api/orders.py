from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.database import get_db
from backend.models.order import Order, OrderItem
from backend.models.tyre import Tyre
from backend.models.tyre_brand import TyreBrand
from backend.models.schemas import OrderCreate, OrderResponse, OrderItemResponse, OrderStatusUpdate
from backend.agents.order_agent import OrderAgent

router = APIRouter(prefix="/orders", tags=["Orders"])
order_agent = OrderAgent()


@router.get("", response_model=list[OrderResponse])
async def get_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()

    response = []
    for order in orders:
        items_result = await db.execute(
            select(OrderItem, Tyre, TyreBrand.name.label("brand_name"))
            .join(Tyre, OrderItem.tyre_id == Tyre.id)
            .join(TyreBrand, Tyre.brand_id == TyreBrand.id)
            .where(OrderItem.order_id == order.id)
        )
        items = items_result.all()

        order_items = [
            OrderItemResponse(
                id=oi.id, tyre_id=oi.tyre_id,
                tyre_name=f"{brand_name} {tyre.model} {tyre.size}",
                quantity=oi.quantity, unit_price=oi.unit_price,
            )
            for oi, tyre, brand_name in items
        ]

        response.append(OrderResponse(
            id=order.id, customer_name=order.customer_name,
            status=order.status, total_amount=order.total_amount,
            shipping_address=order.shipping_address,
            payment_method=order.payment_method,
            items_count=len(order_items), items=order_items,
            created_at=order.created_at,
        ))

    return response


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items_result = await db.execute(
        select(OrderItem, Tyre, TyreBrand.name.label("brand_name"))
        .join(Tyre, OrderItem.tyre_id == Tyre.id)
        .join(TyreBrand, Tyre.brand_id == TyreBrand.id)
        .where(OrderItem.order_id == order.id)
    )
    items = items_result.all()

    order_items = [
        OrderItemResponse(
            id=oi.id, tyre_id=oi.tyre_id,
            tyre_name=f"{brand_name} {tyre.model} {tyre.size}",
            quantity=oi.quantity, unit_price=oi.unit_price,
        )
        for oi, tyre, brand_name in items
    ]

    return OrderResponse(
        id=order.id, customer_name=order.customer_name,
        status=order.status, total_amount=order.total_amount,
        shipping_address=order.shipping_address,
        payment_method=order.payment_method,
        items_count=len(order_items), items=order_items,
        created_at=order.created_at,
    )


@router.post("", response_model=OrderResponse)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    items_data = [{"tyre_id": item.tyre_id, "quantity": item.quantity} for item in data.items]
    result = await order_agent.create_order(
        db, data.customer_name, items_data,
        data.shipping_address, data.payment_method,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    order = await db.get(Order, result["order_id"])
    items_result = await db.execute(
        select(OrderItem, Tyre, TyreBrand.name.label("brand_name"))
        .join(Tyre, OrderItem.tyre_id == Tyre.id)
        .join(TyreBrand, Tyre.brand_id == TyreBrand.id)
        .where(OrderItem.order_id == order.id)
    )
    items = items_result.all()

    order_items = [
        OrderItemResponse(
            id=oi.id, tyre_id=oi.tyre_id,
            tyre_name=f"{brand_name} {tyre.model} {tyre.size}",
            quantity=oi.quantity, unit_price=oi.unit_price,
        )
        for oi, tyre, brand_name in items
    ]

    return OrderResponse(
        id=order.id, customer_name=order.customer_name,
        status=order.status, total_amount=order.total_amount,
        shipping_address=order.shipping_address,
        payment_method=order.payment_method,
        items_count=len(order_items), items=order_items,
        created_at=order.created_at,
    )


@router.put("/{order_id}/status")
async def update_order_status(order_id: int, data: OrderStatusUpdate, db: AsyncSession = Depends(get_db)):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = data.status
    await db.commit()
    return {"message": f"Order #{order_id} status updated to {data.status}"}


@router.delete("/{order_id}")
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    await db.delete(order)
    await db.commit()
    return {"message": "Order deleted"}
