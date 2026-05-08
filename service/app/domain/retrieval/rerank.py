import logging
from typing import List

from langchain_core.documents import Document

from app.core.config import settings
from app.core.model import return_rerank_model
from app.domain.chunk.model import RagChunk

logger = logging.getLogger(__name__)


def rerank(query: str, chunks: List[RagChunk]) -> List[RagChunk]:
    if not chunks:
        return []

    documents = [
        Document(
            page_content=chunk.chunk_text,
            metadata={"chunk_id": chunk.id},
        )
        for chunk in chunks
    ]
    chunk_map = {chunk.id: chunk for chunk in chunks}

    try:
        rerank_model = return_rerank_model()
        reranked_docs = rerank_model.compress_documents(documents=documents, query=query)
        return [chunk_map[doc.metadata["chunk_id"]] for doc in reranked_docs]
    except Exception:
        logger.exception("reranker call failed, falling back to RRF order")
        top_n = min(settings.rerank_top_k, len(chunks))
        return chunks[:top_n]
