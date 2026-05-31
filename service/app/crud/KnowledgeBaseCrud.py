from app.crud.BaseCrud import BaseCrud
from app.domain.knowledge_base.model import KnowledgeBase
from app.domain.knowledge_base.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
)
from sqlalchemy import update
from sqlalchemy.orm import Session


class KnowledgeBaseCrud(BaseCrud[KnowledgeBase, KnowledgeBaseCreate, KnowledgeBaseUpdate]):
    def __init__(self, db: Session):
        super().__init__(KnowledgeBase, db)
    def increment_document_count(self, kb_id: int, delta: int = 1) -> None:
        self.db.execute(
            update(KnowledgeBase)
            .where(KnowledgeBase.id == kb_id)
            .values(document_count=KnowledgeBase.document_count + delta)
        )
        self.db.commit()

    def decrement_document_count(self, kb_id: int, delta: int = 1) -> None:
        self.db.execute(
            update(KnowledgeBase)
            .where(KnowledgeBase.id == kb_id)
            .values(document_count=KnowledgeBase.document_count - delta)
        )
        self.db.commit()
