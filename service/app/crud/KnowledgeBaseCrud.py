from app.crud.BaseCrud import BaseCrud
from app.domain.knowledge_base.model import KnowledgeBase
from app.domain.knowledge_base.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
)
from sqlalchemy.orm import Session


class KnowledgeBaseCrud(BaseCrud[KnowledgeBase, KnowledgeBaseCreate, KnowledgeBaseUpdate]):
    def __init__(self, db: Session):
        super().__init__(KnowledgeBase, db)
