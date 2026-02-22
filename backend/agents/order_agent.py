from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.order import Order, OrderItem
from backend.models.tyre import Tyre
from backend.models.tyre_brand import TyreBrand


class OrderAgent:
    async def create_order(
        self,
        db: AsyncSession,
        customer_name: str,
        items: list[dict],
        shipping_address: str = None,
        payment_method: str = None,
    ) -> dict:
        total = 0.0
        order_items = []

        for item in items:
            tyre = await db.get(Tyre, item["tyre_id"])
            if not tyre:
                return {"success": False, "message": f"Tyre ID {item['tyre_id']} not found"}
            if tyre.stock < item.get("quantity", 1):
                return {
                    "success": False,
                    "message": f"Insufficient stock for tyre ID {tyre.id}. Available: {tyre.stock}",
                }

            qty = item.get("quantity", 1)
            order_items.append(
                OrderItem(tyre_id=tyre.id, quantity=qty, unit_price=tyre.price)
            )
            total += tyre.price * qty
            tyre.stock -= qty

        order = Order(
            customer_name=customer_name,
            status="Pending",
            total_amount=total,
            shipping_address=shipping_address,
            payment_method=payment_method,
        )
        db.add(order)
        await db.flush()

        for oi in order_items:
            oi.order_id = order.id
            db.add(oi)

        await db.commit()
        await db.refresh(order)

        return {
            "success": True,
            "order_id": order.id,
            "total_amount": total,
            "items_count": len(order_items),
            "message": f"Order #{order.id} created successfully. Total: ${total:.2f}",
        }

    async def get_order(self, db: AsyncSession, order_id: int) -> dict | None:
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            return None

        items_result = await db.execute(
            select(OrderItem, Tyre, TyreBrand.name.label("brand_name"))
            .join(Tyre, OrderItem.tyre_id == Tyre.id)
            .join(TyreBrand, Tyre.brand_id == TyreBrand.id)
            .where(OrderItem.order_id == order.id)
        )
        items = [
            {
                "tyre": f"{brand_name} {tyre.model} {tyre.size}",
                "quantity": oi.quantity,
                "unit_price": oi.unit_price,
            }
            for oi, tyre, brand_name in items_result.all()
        ]

        return {
            "id": order.id,
            "order_code": f"MTX-{order.id:05d}",
            "customer_name": order.customer_name,
            "status": order.status,
            "total_amount": order.total_amount,
            "items": items,
            "created_at": str(order.created_at) if order.created_at else None,
        }

    async def get_order_by_code(self, db: AsyncSession, order_code: str) -> dict | None:
        """Look up an order by its MTX-XXXXX code."""
        try:
            order_id = int(order_code.replace("MTX-", "").replace("mts-", "").replace("MTS-", "").replace("mtx-", "").lstrip("0") or "0")
        except ValueError:
            return None
        return await self.get_order(db, order_id)
