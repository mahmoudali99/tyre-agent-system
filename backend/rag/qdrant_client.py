from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from backend.config import get_settings
from backend.rag.embeddings import get_embedding, get_query_embedding
import uuid

settings = get_settings()

EMBEDDING_DIM = settings.EMBEDDING_DIMENSION  # gemini-embedding-001 dimension (3072)

COLLECTIONS = ["car_brands", "car_models", "tyre_brands", "tyres"]


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)


def init_collections():
    client = get_qdrant_client()
    for collection_name in COLLECTIONS:
        if not client.collection_exists(collection_name):
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )


def upsert_record(collection_name: str, record_id: int, text_to_embed: str, payload: dict):
    client = get_qdrant_client()
    embedding = get_embedding(text_to_embed)
    point = PointStruct(
        id=record_id,
        vector=embedding,
        payload=payload,
    )
    client.upsert(collection_name=collection_name, points=[point])


def delete_record(collection_name: str, record_id: int):
    client = get_qdrant_client()
    client.delete(collection_name=collection_name, points_selector=[record_id])


def search_collection(collection_name: str, query: str, limit: int = 5) -> list[dict]:
    client = get_qdrant_client()
    query_vector = get_query_embedding(query)
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit,
    )
    return [
        {
            "id": hit.id,
            "score": hit.score,
            "payload": hit.payload,
        }
        for hit in results
    ]


def search_all_collections(query: str, limit: int = 5) -> dict[str, list[dict]]:
    results = {}
    for collection_name in COLLECTIONS:
        try:
            results[collection_name] = search_collection(collection_name, query, limit)
        except Exception:
            results[collection_name] = []
    return results
