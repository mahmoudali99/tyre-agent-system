from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.database import get_db
from backend.models.car_brand import CarBrand
from backend.models.car_model import CarModel
from backend.models.schemas import CarBrandCreate, CarBrandUpdate, CarBrandResponse
from backend.rag.qdrant_client import upsert_record, delete_record

router = APIRouter(prefix="/car-brands", tags=["Car Brands"])


@router.get("", response_model=list[CarBrandResponse])
async def get_car_brands(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            CarBrand,
            func.count(CarModel.id).label("models_count")
        )
        .outerjoin(CarModel, CarBrand.id == CarModel.brand_id)
        .group_by(CarBrand.id)
        .order_by(CarBrand.name)
    )
    rows = result.all()
    return [
        CarBrandResponse(id=brand.id, name=brand.name, country=brand.country, models_count=count)
        for brand, count in rows
    ]


@router.get("/{brand_id}", response_model=CarBrandResponse)
async def get_car_brand(brand_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            CarBrand,
            func.count(CarModel.id).label("models_count")
        )
        .outerjoin(CarModel, CarBrand.id == CarModel.brand_id)
        .where(CarBrand.id == brand_id)
        .group_by(CarBrand.id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Car brand not found")
    brand, count = row
    return CarBrandResponse(id=brand.id, name=brand.name, country=brand.country, models_count=count)


@router.post("", response_model=CarBrandResponse)
async def create_car_brand(data: CarBrandCreate, db: AsyncSession = Depends(get_db)):
    brand = CarBrand(name=data.name, country=data.country)
    db.add(brand)
    await db.commit()
    await db.refresh(brand)

    try:
        upsert_record(
            "car_brands",
            brand.id,
            brand.name,
            {"id": brand.id, "name": brand.name, "country": brand.country},
        )
    except Exception as e:
        print(f"Qdrant upsert error: {e}")

    return CarBrandResponse(id=brand.id, name=brand.name, country=brand.country, models_count=0)


@router.put("/{brand_id}", response_model=CarBrandResponse)
async def update_car_brand(brand_id: int, data: CarBrandUpdate, db: AsyncSession = Depends(get_db)):
    brand = await db.get(CarBrand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Car brand not found")

    if data.name is not None:
        brand.name = data.name
    if data.country is not None:
        brand.country = data.country

    await db.commit()
    await db.refresh(brand)

    try:
        upsert_record(
            "car_brands",
            brand.id,
            brand.name,
            {"id": brand.id, "name": brand.name, "country": brand.country},
        )
    except Exception as e:
        print(f"Qdrant upsert error: {e}")

    models_count_result = await db.execute(
        select(func.count(CarModel.id)).where(CarModel.brand_id == brand.id)
    )
    models_count = models_count_result.scalar() or 0

    return CarBrandResponse(id=brand.id, name=brand.name, country=brand.country, models_count=models_count)


@router.delete("/{brand_id}")
async def delete_car_brand(brand_id: int, db: AsyncSession = Depends(get_db)):
    brand = await db.get(CarBrand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Car brand not found")

    await db.delete(brand)
    await db.commit()

    try:
        delete_record("car_brands", brand_id)
    except Exception as e:
        print(f"Qdrant delete error: {e}")

    return {"message": "Car brand deleted"}
