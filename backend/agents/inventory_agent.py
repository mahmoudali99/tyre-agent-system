from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.tyre import Tyre
from backend.models.tyre_brand import TyreBrand


class InventoryAgent:
    async def check_stock(self, db: AsyncSession, tyre_id: int) -> dict:
        result = await db.execute(
            select(Tyre, TyreBrand.name.label("brand_name"))
            .join(TyreBrand, Tyre.brand_id == TyreBrand.id)
            .where(Tyre.id == tyre_id)
        )
        row = result.first()
        if not row:
            return {"available": False, "message": "Tyre not found"}

        tyre, brand_name = row
        return {
            "available": tyre.stock > 0,
            "tyre_id": tyre.id,
            "brand": brand_name,
            "model": tyre.model,
            "size": tyre.size,
            "stock": tyre.stock,
            "price": tyre.price,
            "message": f"{brand_name} {tyre.model} ({tyre.size}): {tyre.stock} in stock at ${tyre.price:.2f}",
        }

    async def check_stock_by_size(self, db: AsyncSession, size: str) -> list[dict]:
        result = await db.execute(
            select(Tyre, TyreBrand.name.label("brand_name"))
            .join(TyreBrand, Tyre.brand_id == TyreBrand.id)
            .where(Tyre.size == size)
            .where(Tyre.stock > 0)
        )
        rows = result.all()
        return [
            {
                "tyre_id": tyre.id,
                "brand": brand_name,
                "model": tyre.model,
                "size": tyre.size,
                "type": tyre.type,
                "stock": tyre.stock,
                "price": tyre.price,
            }
            for tyre, brand_name in rows
        ]

    async def get_low_stock(self, db: AsyncSession) -> list[dict]:
        result = await db.execute(
            select(Tyre, TyreBrand.name.label("brand_name"))
            .join(TyreBrand, Tyre.brand_id == TyreBrand.id)
            .where(Tyre.stock <= Tyre.min_stock_level)
        )
        rows = result.all()
        return [
            {
                "tyre_id": tyre.id,
                "brand": brand_name,
                "model": tyre.model,
                "size": tyre.size,
                "stock": tyre.stock,
                "min_level": tyre.min_stock_level,
                "status": "Critical" if tyre.stock < tyre.min_stock_level // 2 else "Low",
            }
            for tyre, brand_name in rows
        ]
