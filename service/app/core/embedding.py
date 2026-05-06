from typing import List

from langchain_community.embeddings import DashScopeEmbeddings

from app.core.config import settings


def get_embedder() -> DashScopeEmbeddings:
    return DashScopeEmbeddings(model=settings.embedding_model)


def embed_query(text: str) -> List[float]:
    return get_embedder().embed_query(text)


def embed_batch(texts: List[str]) -> List[List[float]]:
    return get_embedder().embed_documents(texts)
