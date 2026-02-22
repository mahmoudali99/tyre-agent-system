from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.database import get_db
from backend.models.order import Order
from backend.models.tyre import Tyre
from backend.models.car_model import CarModel
from backend.models.schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    orders_result = await db.execute(select(func.count(Order.id)))
    total_orders = orders_result.scalar() or 0

    revenue_result = await db.execute(select(func.sum(Order.total_amount)))
    total_revenue = revenue_result.scalar() or 0

    stock_result = await db.execute(select(func.sum(Tyre.stock)))
    tyres_in_stock = stock_result.scalar() or 0

    models_result = await db.execute(select(func.count(CarModel.id)))
    car_models = models_result.scalar() or 0

    return DashboardStats(
        total_orders=total_orders,
        total_revenue=total_revenue,
        tyres_in_stock=tyres_in_stock,
        car_models=car_models,
    )
