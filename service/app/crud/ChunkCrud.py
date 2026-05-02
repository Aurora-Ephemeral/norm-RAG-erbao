from typing import List

from sqlalchemy.orm import Session

from app.crud.BaseCrud import BaseCrud
from app.domain.chunk.model import RagChunk
from app.domain.chunk.schemas import ChunkCreate


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

    def bulk_update_embeddings(self, updates: List[dict]) -> None:
        try:
            self.db.bulk_update_mappings(RagChunk, updates)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
