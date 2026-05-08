from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.ChunkCrud import ChunkCrud
from app.domain.chunk.model import RagChunk
from app.domain.retrieval.pipeline import RetrievalPipeline


class FulltextPipeline(RetrievalPipeline):

    def __init__(
        self,
        db: Session,
        limit: int = settings.fulltext_search_top_k,
        knowledge_base_id: Optional[int] = None,
        standard_nos: Optional[List[str]] = None,
        part_types: Optional[List[str]] = None,
    ):
        self.db = db
        self.limit = limit
        self.knowledge_base_id = knowledge_base_id
        self.standard_nos = standard_nos
        self.part_types = part_types

    def search(self, query: str) -> List[RagChunk]:
        return ChunkCrud(self.db).fulltext_search(
            query_english=query,
            limit=self.limit,
            knowledge_base_id=self.knowledge_base_id,
            standard_nos=self.standard_nos,
            part_types=self.part_types,
        )