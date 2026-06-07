import logging
from typing import List

import dashscope

from app.core.config import settings
from app.domain.chunk.model import RagChunk

logger = logging.getLogger(__name__)


def rerank(query: str, chunks: List[RagChunk]) -> List[RagChunk]:
    if not chunks:
        return []

    top_n = min(settings.rerank_top_k, len(chunks))

    try:
        results = dashscope.TextReRank.call(
            model=settings.reranker_model,
            query=query,
            documents=[chunk.chunk_text for chunk in chunks],
            top_n=top_n,
            return_documents=False,
        )

        if results.output is None:
            logger.error(
                "reranker API error (status=%s): %s — falling back to RRF order",
                results.status_code,
                results.message,
            )
            return chunks[:top_n]

        return [chunks[res.index] for res in results.output.results]
    except Exception:
        logger.exception("reranker call failed, falling back to RRF order")
        return chunks[:top_n]
