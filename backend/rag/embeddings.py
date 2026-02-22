import google.generativeai as genai
from backend.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)


def get_embedding(text: str) -> list[float]:
    result = genai.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_document",
    )
    return result["embedding"]


def get_query_embedding(text: str) -> list[float]:
    result = genai.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_query",
    )
    return result["embedding"]
