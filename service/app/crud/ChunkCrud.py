from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.crud.BaseCrud import BaseCrud
from app.domain.chunk.model import RagChunk
from app.domain.chunk.schemas import ChunkCreate
from app.domain.document.model import Document, DocStatusEnum


class ChunkCrud(BaseCrud[RagChunk, ChunkCreate, ChunkCreate]):
    def __init__(self, db: Session):
        super().__init__(RagChunk, db)


    def get_unembedded(self, document_id: int) -> List[RagChunk]:
        return (
            self.db.query(RagChunk)
            .filter(RagChunk.document_id == document_id, RagChunk.embedding == None)
            .order_by(RagChunk.chunk_index)
            .all()
        )
    # vector similarity search
    def vector_search(
            self,
            query_vector: List[float],
            limit: int = settings.vector_search_top_k,
            knowledge_base_id: Optional[int] = None,
            standard_nos: Optional[List[str]] = None,
            part_types: Optional[List[str]] = None,
        ) -> List[RagChunk]:
        query = (
            self.db.query(RagChunk)
            .join(Document, Document.id == RagChunk.document_id)
            .filter(
                Document.doc_status == DocStatusEnum.ACTIVE,
                RagChunk.embedding.isnot(None)
            )
        )
        if knowledge_base_id:
            query = query.filter(Document.knowledge_base_id == knowledge_base_id)
        if standard_nos:
            query = query.filter(Document.standard_no.in_(standard_nos))
        if part_types:
            query = query.filter(Document.part_type.in_(part_types))

        return (
            query.order_by(RagChunk.embedding.cosine_distance(query_vector))
            .limit(limit)
            .all()
        )
    # bm25 search
    def fulltext_search(
            self,
            query_english: str,
            limit: int = settings.fulltext_search_top_k,
            knowledge_base_id: Optional[int] = None,
            standard_nos: Optional[List[str]] = None,
            part_types: Optional[List[str]] = None,
        ) -> List[RagChunk]:
        ts_query = func.plainto_tsquery('english', query_english)
        query = (
            self.db.query(RagChunk)
            .join(Document, Document.id == RagChunk.document_id)
            .filter(
                Document.doc_status == DocStatusEnum.ACTIVE,
                RagChunk.fts_vector.isnot(None),
                RagChunk.fts_vector.op("@@")(ts_query)
            )
        )
        if knowledge_base_id:
            query = query.filter(Document.knowledge_base_id == knowledge_base_id)
        if standard_nos:
            query = query.filter(Document.standard_no.in_(standard_nos))
        if part_types:
            query = query.filter(Document.part_type.in_(part_types))
        return (
            query.order_by(func.ts_rank(RagChunk.fts_vector, ts_query).desc())
            .limit(limit)
            .all()
        )

    def bulk_update_embeddings(self, updates: List[dict]) -> None:
        try:
            self.db.bulk_update_mappings(RagChunk, updates)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
