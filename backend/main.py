from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.database import init_db
from backend.config import get_settings
from backend.api import car_brands, car_models, tyre_brands, tyres, orders, chat, dashboard

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Matrax Tyres Multi-Agent System API",
    description="Backend API for Matrax Tyres - A Tyre Company Multi-Agent System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3007",
        "http://127.0.0.1:3007",
        "http://185.137.122.199:3007",
        "http://localhost:3000",  # Legacy port support
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api")
app.include_router(car_brands.router, prefix="/api")
app.include_router(car_models.router, prefix="/api")
app.include_router(tyre_brands.router, prefix="/api")
app.include_router(tyres.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "TyreHub API"}


@app.post("/api/seed")
async def seed_data():
    import subprocess
    try:
        result = subprocess.run(
            ["python", "-m", "backend.seed"],
            capture_output=True, text=True, timeout=300,
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout,
            "errors": result.stderr,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
