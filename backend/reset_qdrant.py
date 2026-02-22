"""Reset Qdrant collections with correct dimensions"""
from qdrant_client import QdrantClient
from backend.config import get_settings

settings = get_settings()

def reset_qdrant():
    client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    collections = ["car_brands", "car_models", "tyre_brands", "tyres"]
    
    print("Deleting old collections...")
    for collection_name in collections:
        try:
            if client.collection_exists(collection_name):
                client.delete_collection(collection_name)
                print(f"  Deleted: {collection_name}")
        except Exception as e:
            print(f"  Error deleting {collection_name}: {e}")
    
    print("\nCollections reset. Run seed.py to recreate with correct dimensions.")

if __name__ == "__main__":
    reset_qdrant()
