from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.chunk.model import RagChunk
from app.domain.retrieval.rerank import rerank
from app.domain.retrieval.pipeline import RetrievalPipeline
from app.domain.retrieval.vector import VectorPipeline
from app.domain.retrieval.fulltext import FulltextPipeline
from app.domain.retrieval.fusion import reciprocal_rank_fusion


class HybridPipeline(RetrievalPipeline):

    def __init__(
        self,
        db: Session,
        limit: int = settings.hybrid_candidate_k,
        knowledge_base_id: Optional[int] = None,
        standard_nos: Optional[List[str]] = None,
        part_types: Optional[List[str]] = None,
    ):
        self.vector = VectorPipeline(
            db=db,
            limit=limit,
            knowledge_base_id=knowledge_base_id,
            standard_nos=standard_nos,
            part_types=part_types,
        )
        self.fulltext = FulltextPipeline(
            db=db,
            limit=limit,
            knowledge_base_id=knowledge_base_id,
            standard_nos=standard_nos,
            part_types=part_types,
        )

    def search(self, query: str) -> List[RagChunk]:
        vector_result = self.vector.search(query)
        fulltext_result = self.fulltext.search(query)
        fused = reciprocal_rank_fusion(results=[vector_result, fulltext_result])
        return rerank(query=query, chunks=fused)
