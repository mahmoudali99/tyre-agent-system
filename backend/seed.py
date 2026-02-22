import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from backend.config import get_settings
from backend.database import Base
from backend.models.car_brand import CarBrand
from backend.models.car_model import CarModel
from backend.models.tyre_brand import TyreBrand
from backend.models.tyre import Tyre
from backend.models.order import Order, OrderItem
from backend.models.chat import ChatSession, ChatMessage
from backend.rag.qdrant_client import init_collections, upsert_record

settings = get_settings()

CAR_BRANDS = [
    {"name": "Toyota", "country": "Japan"},
    {"name": "Honda", "country": "Japan"},
    {"name": "BMW", "country": "Germany"},
    {"name": "Mercedes-Benz", "country": "Germany"},
    {"name": "Ford", "country": "USA"},
    {"name": "Chevrolet", "country": "USA"},
    {"name": "Volkswagen", "country": "Germany"},
    {"name": "Audi", "country": "Germany"},
    {"name": "Nissan", "country": "Japan"},
    {"name": "Hyundai", "country": "South Korea"},
]

CAR_MODELS = [
    {"brand": "Toyota", "name": "Camry", "year": 2024, "tyre_sizes": ["225/45R17", "225/55R17"]},
    {"brand": "Toyota", "name": "Corolla", "year": 2024, "tyre_sizes": ["205/55R16", "215/55R16"]},
    {"brand": "Toyota", "name": "RAV4", "year": 2024, "tyre_sizes": ["225/65R17", "225/60R18"]},
    {"brand": "Honda", "name": "Accord", "year": 2024, "tyre_sizes": ["225/45R17", "225/55R17"]},
    {"brand": "Honda", "name": "Civic", "year": 2024, "tyre_sizes": ["205/55R16", "215/50R17"]},
    {"brand": "Honda", "name": "CR-V", "year": 2024, "tyre_sizes": ["235/60R18", "235/65R17"]},
    {"brand": "BMW", "name": "320i", "year": 2024, "tyre_sizes": ["225/50R17", "225/45R18"]},
    {"brand": "BMW", "name": "530i", "year": 2024, "tyre_sizes": ["235/50R18", "245/45R19"]},
    {"brand": "BMW", "name": "X3", "year": 2024, "tyre_sizes": ["245/50R19", "245/45R20"]},
    {"brand": "Mercedes-Benz", "name": "C-Class", "year": 2024, "tyre_sizes": ["225/45R17", "225/40R18"]},
    {"brand": "Mercedes-Benz", "name": "E-Class", "year": 2024, "tyre_sizes": ["235/50R18", "245/45R19"]},
    {"brand": "Ford", "name": "F-150", "year": 2024, "tyre_sizes": ["265/70R17", "275/60R20"]},
    {"brand": "Ford", "name": "Mustang", "year": 2024, "tyre_sizes": ["235/50R18", "255/40R19"]},
    {"brand": "Chevrolet", "name": "Silverado", "year": 2024, "tyre_sizes": ["265/70R17", "275/65R18"]},
    {"brand": "Chevrolet", "name": "Camaro", "year": 2024, "tyre_sizes": ["245/40R20", "275/35R20"]},
    {"brand": "Volkswagen", "name": "Golf", "year": 2024, "tyre_sizes": ["205/55R16", "225/45R17"]},
    {"brand": "Volkswagen", "name": "Tiguan", "year": 2024, "tyre_sizes": ["215/65R17", "235/55R18"]},
    {"brand": "Audi", "name": "A4", "year": 2024, "tyre_sizes": ["225/50R17", "245/40R18"]},
    {"brand": "Audi", "name": "Q5", "year": 2024, "tyre_sizes": ["235/60R18", "255/45R20"]},
    {"brand": "Nissan", "name": "Altima", "year": 2024, "tyre_sizes": ["215/55R17", "235/40R19"]},
    {"brand": "Hyundai", "name": "Tucson", "year": 2024, "tyre_sizes": ["225/60R17", "235/55R18"]},
    {"brand": "Toyota", "name": "Corolla", "year": 2020, "tyre_sizes": ["205/55R16", "215/45R17"]},
    {"brand": "Toyota", "name": "Camry", "year": 2020, "tyre_sizes": ["215/55R17", "235/45R18"]},
]

TYRE_BRANDS = [
    {"name": "Michelin", "country": "France"},
    {"name": "Bridgestone", "country": "Japan"},
    {"name": "Continental", "country": "Germany"},
    {"name": "Goodyear", "country": "USA"},
    {"name": "Pirelli", "country": "Italy"},
    {"name": "Dunlop", "country": "UK"},
    {"name": "Hankook", "country": "South Korea"},
    {"name": "Kumho", "country": "South Korea"},
    {"name": "Yokohama", "country": "Japan"},
    {"name": "Toyo", "country": "Japan"},
]

TYRES = [
    {"brand": "Michelin", "model": "Pilot Sport 4", "size": "225/45R17", "type": "Performance", "price": 189.99, "cost": 95.50, "stock": 156, "min_stock_level": 100},
    {"brand": "Michelin", "model": "Primacy 4", "size": "205/55R16", "type": "Comfort", "price": 159.99, "cost": 80.00, "stock": 200, "min_stock_level": 100},
    {"brand": "Michelin", "model": "CrossClimate 2", "size": "225/65R17", "type": "All-Season", "price": 179.99, "cost": 90.00, "stock": 120, "min_stock_level": 80},
    {"brand": "Bridgestone", "model": "Turanza T005", "size": "225/45R17", "type": "Comfort", "price": 165.99, "cost": 82.75, "stock": 243, "min_stock_level": 150},
    {"brand": "Bridgestone", "model": "Potenza S001", "size": "235/40R19", "type": "Performance", "price": 229.99, "cost": 115.00, "stock": 75, "min_stock_level": 50},
    {"brand": "Bridgestone", "model": "Dueler H/P Sport", "size": "235/60R18", "type": "SUV", "price": 199.99, "cost": 100.00, "stock": 90, "min_stock_level": 60},
    {"brand": "Continental", "model": "EcoContact 6", "size": "205/55R16", "type": "Eco", "price": 129.99, "cost": 65.00, "stock": 318, "min_stock_level": 150},
    {"brand": "Continental", "model": "PremiumContact 6", "size": "225/45R18", "type": "Performance", "price": 199.99, "cost": 100.00, "stock": 85, "min_stock_level": 50},
    {"brand": "Continental", "model": "CrossContact LX", "size": "265/70R17", "type": "SUV", "price": 175.99, "cost": 88.00, "stock": 110, "min_stock_level": 70},
    {"brand": "Goodyear", "model": "Assurance MaxLife", "size": "225/60R17", "type": "All-Season", "price": 145.99, "cost": 73.00, "stock": 287, "min_stock_level": 150},
    {"brand": "Goodyear", "model": "Eagle F1 Asymmetric", "size": "245/45R19", "type": "Performance", "price": 239.99, "cost": 120.00, "stock": 60, "min_stock_level": 40},
    {"brand": "Pirelli", "model": "P Zero", "size": "235/40R19", "type": "Performance", "price": 249.99, "cost": 125.00, "stock": 89, "min_stock_level": 50},
    {"brand": "Pirelli", "model": "Cinturato P7", "size": "225/55R17", "type": "Comfort", "price": 175.99, "cost": 88.00, "stock": 140, "min_stock_level": 80},
    {"brand": "Dunlop", "model": "SP Sport Maxx", "size": "255/35R18", "type": "Performance", "price": 219.99, "cost": 110.00, "stock": 102, "min_stock_level": 60},
    {"brand": "Dunlop", "model": "Grandtrek PT3", "size": "225/65R17", "type": "SUV", "price": 155.99, "cost": 78.00, "stock": 130, "min_stock_level": 80},
    {"brand": "Hankook", "model": "Kinergy GT", "size": "215/60R16", "type": "All-Season", "price": 119.99, "cost": 60.00, "stock": 401, "min_stock_level": 200},
    {"brand": "Hankook", "model": "Ventus V12", "size": "225/50R17", "type": "Performance", "price": 149.99, "cost": 75.00, "stock": 170, "min_stock_level": 100},
    {"brand": "Kumho", "model": "Solus TA71", "size": "185/65R15", "type": "Comfort", "price": 109.99, "cost": 55.00, "stock": 523, "min_stock_level": 250},
    {"brand": "Kumho", "model": "Ecsta PS91", "size": "245/40R18", "type": "Performance", "price": 169.99, "cost": 85.00, "stock": 95, "min_stock_level": 50},
    {"brand": "Yokohama", "model": "Advan Sport V105", "size": "245/45R19", "type": "Performance", "price": 219.99, "cost": 110.00, "stock": 65, "min_stock_level": 40},
    {"brand": "Yokohama", "model": "BluEarth GT", "size": "215/55R17", "type": "Eco", "price": 139.99, "cost": 70.00, "stock": 180, "min_stock_level": 100},
    {"brand": "Toyo", "model": "Proxes Sport", "size": "235/50R18", "type": "Performance", "price": 179.99, "cost": 90.00, "stock": 115, "min_stock_level": 70},
    {"brand": "Toyo", "model": "Open Country A/T", "size": "275/60R20", "type": "All-Terrain", "price": 209.99, "cost": 105.00, "stock": 80, "min_stock_level": 50},
    {"brand": "Michelin", "model": "LTX M/S2", "size": "275/60R20", "type": "All-Season", "price": 219.99, "cost": 110.00, "stock": 70, "min_stock_level": 40},
    {"brand": "Continental", "model": "DWS 06 Plus", "size": "275/60R20", "type": "All-Season", "price": 199.99, "cost": 100.00, "stock": 55, "min_stock_level": 30},
    {"brand": "Goodyear", "model": "Wrangler AT/S", "size": "275/65R18", "type": "All-Terrain", "price": 189.99, "cost": 95.00, "stock": 100, "min_stock_level": 60},
    {"brand": "Pirelli", "model": "Scorpion Verde", "size": "235/55R19", "type": "SUV", "price": 209.99, "cost": 105.00, "stock": 72, "min_stock_level": 40},
    {"brand": "Hankook", "model": "Dynapro HP2", "size": "225/60R18", "type": "SUV", "price": 149.99, "cost": 75.00, "stock": 160, "min_stock_level": 90},
    {"brand": "Bridgestone", "model": "Ecopia EP422", "size": "215/55R16", "type": "Eco", "price": 119.99, "cost": 60.00, "stock": 210, "min_stock_level": 120},
    {"brand": "Continental", "model": "TrueContact Tour", "size": "215/50R17", "type": "All-Season", "price": 139.99, "cost": 70.00, "stock": 185, "min_stock_level": 100},
    {"brand": "Michelin", "model": "Defender LTX M/S", "size": "265/70R17", "type": "All-Season", "price": 195.99, "cost": 98.00, "stock": 130, "min_stock_level": 80},
    {"brand": "Goodyear", "model": "Assurance WeatherReady", "size": "215/55R17", "type": "All-Season", "price": 159.99, "cost": 80.00, "stock": 145, "min_stock_level": 80},
    {"brand": "Pirelli", "model": "P7 All Season Plus", "size": "205/55R16", "type": "All-Season", "price": 139.99, "cost": 70.00, "stock": 190, "min_stock_level": 100},
    {"brand": "Dunlop", "model": "Sport BluResponse", "size": "215/55R16", "type": "Comfort", "price": 129.99, "cost": 65.00, "stock": 175, "min_stock_level": 100},
    {"brand": "Yokohama", "model": "Geolandar CV G058", "size": "225/60R18", "type": "SUV", "price": 159.99, "cost": 80.00, "stock": 95, "min_stock_level": 50},
    {"brand": "Toyo", "model": "Celsius II", "size": "225/45R17", "type": "All-Season", "price": 149.99, "cost": 75.00, "stock": 200, "min_stock_level": 100},
    {"brand": "Kumho", "model": "Crugen HP71", "size": "235/65R17", "type": "SUV", "price": 139.99, "cost": 70.00, "stock": 150, "min_stock_level": 80},
]


def seed_database():
    print("Starting database seed...")
    engine = create_engine(settings.DATABASE_URL_SYNC)

    Base.metadata.create_all(engine)
    print("Tables created.")

    with Session(engine) as db:
        existing = db.execute(text("SELECT COUNT(*) FROM car_brands")).scalar()
        if existing > 0:
            print("Database already seeded. Skipping...")
            db.close()
            engine.dispose()
            seed_qdrant(engine)
            return

        brand_map = {}
        for data in CAR_BRANDS:
            brand = CarBrand(name=data["name"], country=data["country"])
            db.add(brand)
            db.flush()
            brand_map[data["name"]] = brand.id
        print(f"Inserted {len(CAR_BRANDS)} car brands.")

        for data in CAR_MODELS:
            brand_id = brand_map.get(data["brand"])
            if brand_id:
                model = CarModel(
                    brand_id=brand_id, name=data["name"],
                    year=data["year"], tyre_sizes=data["tyre_sizes"],
                )
                db.add(model)
        db.flush()
        print(f"Inserted {len(CAR_MODELS)} car models.")

        tyre_brand_map = {}
        for data in TYRE_BRANDS:
            brand = TyreBrand(name=data["name"], country=data["country"])
            db.add(brand)
            db.flush()
            tyre_brand_map[data["name"]] = brand.id
        print(f"Inserted {len(TYRE_BRANDS)} tyre brands.")

        for data in TYRES:
            brand_id = tyre_brand_map.get(data["brand"])
            if brand_id:
                tyre = Tyre(
                    brand_id=brand_id, model=data["model"], size=data["size"],
                    type=data["type"], price=data["price"], cost=data["cost"],
                    stock=data["stock"], min_stock_level=data["min_stock_level"],
                )
                db.add(tyre)
        db.flush()
        print(f"Inserted {len(TYRES)} tyres.")

        db.commit()
        print("Database seed complete!")

    seed_qdrant(engine)
    engine.dispose()


def seed_qdrant(engine):
    print("\nStarting Qdrant seed...")
    try:
        init_collections()
        print("Qdrant collections initialized.")
    except Exception as e:
        print(f"Error initializing Qdrant collections: {e}")
        return

    with Session(engine) as db:
        car_brands = db.execute(text("SELECT id, name, country FROM car_brands")).fetchall()
        for row in car_brands:
            try:
                upsert_record("car_brands", row[0], row[1], {
                    "id": row[0], "name": row[1], "country": row[2],
                })
            except Exception as e:
                print(f"Error embedding car brand {row[1]}: {e}")
        print(f"Embedded {len(car_brands)} car brands.")

        car_models = db.execute(text(
            "SELECT cm.id, cb.name as brand_name, cm.name, cm.year, cm.tyre_sizes, cm.brand_id "
            "FROM car_models cm JOIN car_brands cb ON cm.brand_id = cb.id"
        )).fetchall()
        for row in car_models:
            try:
                upsert_record("car_models", row[0], f"{row[1]} {row[2]} {row[3]}", {
                    "id": row[0], "brand_id": row[5], "brand_name": row[1],
                    "name": row[2], "year": row[3],
                    "tyre_sizes": list(row[4]) if row[4] else [],
                })
            except Exception as e:
                print(f"Error embedding car model {row[1]} {row[2]}: {e}")
        print(f"Embedded {len(car_models)} car models.")

        tyre_brands = db.execute(text("SELECT id, name, country FROM tyre_brands")).fetchall()
        for row in tyre_brands:
            try:
                upsert_record("tyre_brands", row[0], row[1], {
                    "id": row[0], "name": row[1], "country": row[2],
                })
            except Exception as e:
                print(f"Error embedding tyre brand {row[1]}: {e}")
        print(f"Embedded {len(tyre_brands)} tyre brands.")

        tyres = db.execute(text(
            "SELECT t.id, tb.name as brand_name, t.model, t.size, t.type, t.price, t.stock, t.brand_id "
            "FROM tyres t JOIN tyre_brands tb ON t.brand_id = tb.id"
        )).fetchall()
        for row in tyres:
            try:
                upsert_record("tyres", row[0], f"{row[1]} {row[2]} {row[3]}", {
                    "id": row[0], "brand_id": row[7], "brand_name": row[1],
                    "model": row[2], "size": row[3], "type": row[4],
                    "price": float(row[5]), "stock": row[6],
                })
            except Exception as e:
                print(f"Error embedding tyre {row[1]} {row[2]}: {e}")
        print(f"Embedded {len(tyres)} tyres.")

    print("Qdrant seed complete!")


if __name__ == "__main__":
    seed_database()
