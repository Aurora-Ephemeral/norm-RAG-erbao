import logging
from typing import List

from app.core.embedding import embed_batch
from app.domain.chunk.model import RagChunk

logger = logging.getLogger(__name__)

BATCH_SIZE = 10
MAX_WORKERS = 5


def embed_document(chunks: List[RagChunk]) -> List[dict]:
    texts = [c.chunk_text for c in chunks]
    embeddings = embed_batch(texts)
    return [{"id": chunk.id, "embedding": emb} for chunk, emb in zip(chunks, embeddings)]
