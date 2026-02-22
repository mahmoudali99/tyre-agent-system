from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.tyre import Tyre
from backend.models.tyre_brand import TyreBrand
from backend.models.schemas import TyreCreate, TyreUpdate, TyreResponse, StockItemResponse, StockUpdate
from backend.rag.qdrant_client import upsert_record, delete_record

router = APIRouter(prefix="/tyres", tags=["Tyres"])


@router.get("", response_model=list[TyreResponse])
async def get_tyres(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Tyre, TyreBrand.name.label("brand_name"))
        .join(TyreBrand, Tyre.brand_id == TyreBrand.id)
        .order_by(TyreBrand.name, Tyre.model)
    )
    rows = result.all()
    return [
        TyreResponse(
            id=tyre.id, brand_id=tyre.brand_id, brand_name=brand_name,
            model=tyre.model, size=tyre.size, type=tyre.type,
            price=tyre.price, cost=tyre.cost, stock=tyre.stock,
            min_stock_level=tyre.min_stock_level,
        )
        for tyre, brand_name in rows
    ]


@router.get("/stock", response_model=list[StockItemResponse])
async def get_stock(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Tyre, TyreBrand.name.label("brand_name"))
        .join(TyreBrand, Tyre.brand_id == TyreBrand.id)
        .order_by(TyreBrand.name, Tyre.model)
    )
    rows = result.all()
    items = []
    for tyre, brand_name in rows:
        if tyre.stock < tyre.min_stock_level // 2:
            status = "Critical"
        elif tyre.stock <= tyre.min_stock_level:
            status = "Low"
        else:
            status = "OK"
        items.append(StockItemResponse(
            id=tyre.id, brand_name=brand_name, model=tyre.model,
            size=tyre.size, current_stock=tyre.stock, min_level=tyre.min_stock_level,
            status=status,
            last_update=str(tyre.updated_at.date()) if tyre.updated_at else "",
        ))
    return items


@router.get("/{tyre_id}", response_model=TyreResponse)
async def get_tyre(tyre_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Tyre, TyreBrand.name.label("brand_name"))
        .join(TyreBrand, Tyre.brand_id == TyreBrand.id)
        .where(Tyre.id == tyre_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Tyre not found")
    tyre, brand_name = row
    return TyreResponse(
        id=tyre.id, brand_id=tyre.brand_id, brand_name=brand_name,
        model=tyre.model, size=tyre.size, type=tyre.type,
        price=tyre.price, cost=tyre.cost, stock=tyre.stock,
        min_stock_level=tyre.min_stock_level,
    )


@router.post("", response_model=TyreResponse)
async def create_tyre(data: TyreCreate, db: AsyncSession = Depends(get_db)):
    brand = await db.get(TyreBrand, data.brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Tyre brand not found")

    tyre = Tyre(
        brand_id=data.brand_id, model=data.model, size=data.size,
        type=data.type, price=data.price, cost=data.cost,
        stock=data.stock, min_stock_level=data.min_stock_level,
    )
    db.add(tyre)
    await db.commit()
    await db.refresh(tyre)

    try:
        upsert_record(
            "tyres",
            tyre.id,
            f"{brand.name} {tyre.model} {tyre.size}",
            {
                "id": tyre.id, "brand_id": brand.id, "brand_name": brand.name,
                "model": tyre.model, "size": tyre.size, "type": tyre.type,
                "price": tyre.price, "stock": tyre.stock,
            },
        )
    except Exception as e:
        print(f"Qdrant upsert error: {e}")

    return TyreResponse(
        id=tyre.id, brand_id=tyre.brand_id, brand_name=brand.name,
        model=tyre.model, size=tyre.size, type=tyre.type,
        price=tyre.price, cost=tyre.cost, stock=tyre.stock,
        min_stock_level=tyre.min_stock_level,
    )


@router.put("/{tyre_id}", response_model=TyreResponse)
async def update_tyre(tyre_id: int, data: TyreUpdate, db: AsyncSession = Depends(get_db)):
    tyre = await db.get(Tyre, tyre_id)
    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")

    if data.brand_id is not None:
        brand = await db.get(TyreBrand, data.brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Tyre brand not found")
        tyre.brand_id = data.brand_id
    if data.model is not None:
        tyre.model = data.model
    if data.size is not None:
        tyre.size = data.size
    if data.type is not None:
        tyre.type = data.type
    if data.price is not None:
        tyre.price = data.price
    if data.cost is not None:
        tyre.cost = data.cost
    if data.stock is not None:
        tyre.stock = data.stock
    if data.min_stock_level is not None:
        tyre.min_stock_level = data.min_stock_level

    await db.commit()
    await db.refresh(tyre)

    brand = await db.get(TyreBrand, tyre.brand_id)

    try:
        upsert_record(
            "tyres",
            tyre.id,
            f"{brand.name} {tyre.model} {tyre.size}",
            {
                "id": tyre.id, "brand_id": brand.id, "brand_name": brand.name,
                "model": tyre.model, "size": tyre.size, "type": tyre.type,
                "price": tyre.price, "stock": tyre.stock,
            },
        )
    except Exception as e:
        print(f"Qdrant upsert error: {e}")

    return TyreResponse(
        id=tyre.id, brand_id=tyre.brand_id, brand_name=brand.name,
        model=tyre.model, size=tyre.size, type=tyre.type,
        price=tyre.price, cost=tyre.cost, stock=tyre.stock,
        min_stock_level=tyre.min_stock_level,
    )


@router.put("/{tyre_id}/stock", response_model=TyreResponse)
async def update_stock(tyre_id: int, data: StockUpdate, db: AsyncSession = Depends(get_db)):
    tyre = await db.get(Tyre, tyre_id)
    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")

    tyre.stock = data.stock
    await db.commit()
    await db.refresh(tyre)

    brand = await db.get(TyreBrand, tyre.brand_id)

    try:
        upsert_record(
            "tyres",
            tyre.id,
            f"{brand.name} {tyre.model} {tyre.size}",
            {
                "id": tyre.id, "brand_id": brand.id, "brand_name": brand.name,
                "model": tyre.model, "size": tyre.size, "type": tyre.type,
                "price": tyre.price, "stock": tyre.stock,
            },
        )
    except Exception as e:
        print(f"Qdrant upsert error: {e}")

    return TyreResponse(
        id=tyre.id, brand_id=tyre.brand_id, brand_name=brand.name,
        model=tyre.model, size=tyre.size, type=tyre.type,
        price=tyre.price, cost=tyre.cost, stock=tyre.stock,
        min_stock_level=tyre.min_stock_level,
    )


@router.delete("/{tyre_id}")
async def delete_tyre(tyre_id: int, db: AsyncSession = Depends(get_db)):
    tyre = await db.get(Tyre, tyre_id)
    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")

    await db.delete(tyre)
    await db.commit()

    try:
        delete_record("tyres", tyre_id)
    except Exception as e:
        print(f"Qdrant delete error: {e}")

    return {"message": "Tyre deleted"}
