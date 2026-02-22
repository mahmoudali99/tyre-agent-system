from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.car_model import CarModel
from backend.models.car_brand import CarBrand
from backend.models.schemas import CarModelCreate, CarModelUpdate, CarModelResponse
from backend.rag.qdrant_client import upsert_record, delete_record

router = APIRouter(prefix="/car-models", tags=["Car Models"])


@router.get("", response_model=list[CarModelResponse])
async def get_car_models(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CarModel, CarBrand.name.label("brand_name"))
        .join(CarBrand, CarModel.brand_id == CarBrand.id)
        .order_by(CarBrand.name, CarModel.name)
    )
    rows = result.all()
    return [
        CarModelResponse(
            id=model.id, brand_id=model.brand_id, brand_name=brand_name,
            name=model.name, year=model.year, tyre_sizes=model.tyre_sizes or [],
        )
        for model, brand_name in rows
    ]


@router.get("/{model_id}", response_model=CarModelResponse)
async def get_car_model(model_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CarModel, CarBrand.name.label("brand_name"))
        .join(CarBrand, CarModel.brand_id == CarBrand.id)
        .where(CarModel.id == model_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Car model not found")
    model, brand_name = row
    return CarModelResponse(
        id=model.id, brand_id=model.brand_id, brand_name=brand_name,
        name=model.name, year=model.year, tyre_sizes=model.tyre_sizes or [],
    )


@router.post("", response_model=CarModelResponse)
async def create_car_model(data: CarModelCreate, db: AsyncSession = Depends(get_db)):
    brand = await db.get(CarBrand, data.brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Car brand not found")

    model = CarModel(
        brand_id=data.brand_id, name=data.name,
        year=data.year, tyre_sizes=data.tyre_sizes,
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)

    try:
        upsert_record(
            "car_models",
            model.id,
            f"{brand.name} {model.name} {model.year}",
            {
                "id": model.id, "brand_id": brand.id, "brand_name": brand.name,
                "name": model.name, "year": model.year,
                "tyre_sizes": model.tyre_sizes or [],
            },
        )
    except Exception as e:
        print(f"Qdrant upsert error: {e}")

    return CarModelResponse(
        id=model.id, brand_id=model.brand_id, brand_name=brand.name,
        name=model.name, year=model.year, tyre_sizes=model.tyre_sizes or [],
    )


@router.put("/{model_id}", response_model=CarModelResponse)
async def update_car_model(model_id: int, data: CarModelUpdate, db: AsyncSession = Depends(get_db)):
    model = await db.get(CarModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Car model not found")

    if data.brand_id is not None:
        brand = await db.get(CarBrand, data.brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Car brand not found")
        model.brand_id = data.brand_id
    if data.name is not None:
        model.name = data.name
    if data.year is not None:
        model.year = data.year
    if data.tyre_sizes is not None:
        model.tyre_sizes = data.tyre_sizes

    await db.commit()
    await db.refresh(model)

    brand = await db.get(CarBrand, model.brand_id)

    try:
        upsert_record(
            "car_models",
            model.id,
            f"{brand.name} {model.name} {model.year}",
            {
                "id": model.id, "brand_id": brand.id, "brand_name": brand.name,
                "name": model.name, "year": model.year,
                "tyre_sizes": model.tyre_sizes or [],
            },
        )
    except Exception as e:
        print(f"Qdrant upsert error: {e}")

    return CarModelResponse(
        id=model.id, brand_id=model.brand_id, brand_name=brand.name,
        name=model.name, year=model.year, tyre_sizes=model.tyre_sizes or [],
    )


@router.delete("/{model_id}")
async def delete_car_model(model_id: int, db: AsyncSession = Depends(get_db)):
    model = await db.get(CarModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Car model not found")

    await db.delete(model)
    await db.commit()

    try:
        delete_record("car_models", model_id)
    except Exception as e:
        print(f"Qdrant delete error: {e}")

    return {"message": "Car model deleted"}
