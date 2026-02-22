from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.database import get_db
from backend.models.tyre_brand import TyreBrand
from backend.models.tyre import Tyre
from backend.models.schemas import TyreBrandCreate, TyreBrandUpdate, TyreBrandResponse
from backend.rag.qdrant_client import upsert_record, delete_record

router = APIRouter(prefix="/tyre-brands", tags=["Tyre Brands"])


@router.get("", response_model=list[TyreBrandResponse])
async def get_tyre_brands(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            TyreBrand,
            func.count(Tyre.id).label("tyres_count")
        )
        .outerjoin(Tyre, TyreBrand.id == Tyre.brand_id)
        .group_by(TyreBrand.id)
        .order_by(TyreBrand.name)
    )
    rows = result.all()
    return [
        TyreBrandResponse(id=brand.id, name=brand.name, country=brand.country, tyres_count=count)
        for brand, count in rows
    ]


@router.get("/{brand_id}", response_model=TyreBrandResponse)
async def get_tyre_brand(brand_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            TyreBrand,
            func.count(Tyre.id).label("tyres_count")
        )
        .outerjoin(Tyre, TyreBrand.id == Tyre.brand_id)
        .where(TyreBrand.id == brand_id)
        .group_by(TyreBrand.id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Tyre brand not found")
    brand, count = row
    return TyreBrandResponse(id=brand.id, name=brand.name, country=brand.country, tyres_count=count)


@router.post("", response_model=TyreBrandResponse)
async def create_tyre_brand(data: TyreBrandCreate, db: AsyncSession = Depends(get_db)):
    brand = TyreBrand(name=data.name, country=data.country)
    db.add(brand)
    await db.commit()
    await db.refresh(brand)

    try:
        upsert_record(
            "tyre_brands",
            brand.id,
            brand.name,
            {"id": brand.id, "name": brand.name, "country": brand.country},
        )
    except Exception as e:
        print(f"Qdrant upsert error: {e}")

    return TyreBrandResponse(id=brand.id, name=brand.name, country=brand.country, tyres_count=0)


@router.put("/{brand_id}", response_model=TyreBrandResponse)
async def update_tyre_brand(brand_id: int, data: TyreBrandUpdate, db: AsyncSession = Depends(get_db)):
    brand = await db.get(TyreBrand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Tyre brand not found")

    if data.name is not None:
        brand.name = data.name
    if data.country is not None:
        brand.country = data.country

    await db.commit()
    await db.refresh(brand)

    try:
        upsert_record(
            "tyre_brands",
            brand.id,
            brand.name,
            {"id": brand.id, "name": brand.name, "country": brand.country},
        )
    except Exception as e:
        print(f"Qdrant upsert error: {e}")

    tyres_count_result = await db.execute(
        select(func.count(Tyre.id)).where(Tyre.brand_id == brand.id)
    )
    tyres_count = tyres_count_result.scalar() or 0

    return TyreBrandResponse(id=brand.id, name=brand.name, country=brand.country, tyres_count=tyres_count)


@router.delete("/{brand_id}")
async def delete_tyre_brand(brand_id: int, db: AsyncSession = Depends(get_db)):
    brand = await db.get(TyreBrand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Tyre brand not found")

    await db.delete(brand)
    await db.commit()

    try:
        delete_record("tyre_brands", brand_id)
    except Exception as e:
        print(f"Qdrant delete error: {e}")

    return {"message": "Tyre brand deleted"}
