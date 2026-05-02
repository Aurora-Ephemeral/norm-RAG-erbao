import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from http import HTTPStatus
from typing import List

from dashscope import TextEmbedding

from app.core.config import settings
from app.domain.chunk.model import RagChunk

logger = logging.getLogger(__name__)

BATCH_SIZE = 10
MAX_WORKERS = 5


def _embed_batch(texts: List[str]) -> List[List[float]]:
    """Call DashScope embedding API for one batch. Raises on failure."""
    resp = TextEmbedding.call(
        model=settings.embedding_model,
        input=texts,
    )
    if resp.status_code != HTTPStatus.OK:
        raise RuntimeError(f"DashScope embedding error: {resp.message}")
    sorted_embs = sorted(resp.output["embeddings"], key=lambda e: e["text_index"])
    return [e["embedding"] for e in sorted_embs]


def embed_document(chunks:List[RagChunk] = []) -> List[dict]:
    """
    Embed all unembedded chunks for a document and persist the vectors.
    Idempotent: only processes chunks where embedding IS NULL.
    Returns the number of chunks embedded this run.
    """
    batches = [chunks[i: i + BATCH_SIZE] for i in range(0, len(chunks), BATCH_SIZE)]
    updates: List[dict] = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_batch = {
            executor.submit(_embed_batch, [c.chunk_text for c in batch]): batch
            for batch in batches
        }
        for future in as_completed(future_to_batch):
            batch = future_to_batch[future]
            embeddings = future.result()
            for chunk, embedding in zip(batch, embeddings):
                updates.append({"id": chunk.id, "embedding": embedding})

    return updates
