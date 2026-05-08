from typing import List

from app.domain.chunk.model import RagChunk


def reciprocal_rank_fusion(
    results: List[List[RagChunk]],
    k: int = 60,
) -> List[RagChunk]:
    scores: dict[int, float] = {}
    chunks: dict[int, RagChunk] = {}
    # each result 
    for result_list in results:
        for rank, chunk in enumerate(result_list, start=1):
            scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (k + rank)
            chunks[chunk.id] = chunk

    sorted_ids = sorted(scores, key=lambda i: scores[i], reverse=True)
    return [chunks[i] for i in sorted_ids]
