from app.crud.KnowledgeBaseCrud import KnowledgeBaseCrud
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.knowledge_base.schemas import KnowledgeBase, KnowledgeBaseCreate
from typing import List

class KnowledgeBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = KnowledgeBaseCrud(db)

    def get_knowledge_base_list(self) -> List[KnowledgeBase]:
        fetch_result = self.crud.get_all()

        return [KnowledgeBase.model_validate(item) for item in fetch_result]
    
    def add_knowledge_base(self, knowledge_base: KnowledgeBaseCreate) -> KnowledgeBase:
        try:
            db_knowledge_base = self.crud.create(knowledge_base)
            return KnowledgeBase.model_validate(db_knowledge_base)
        except IntegrityError as exc:
            error_message = str(exc.orig).lower() if exc.orig else str(exc).lower()
            if "duplicate key" in error_message or "unique constraint" in error_message:
                raise HTTPException(status_code=409, detail="Knowledge Base already exists")
            raise
    
    def update_knowledge_base(self, id:int, knowledge_base: KnowledgeBaseCreate) -> KnowledgeBase:
        db_knowledge_base = self.crud.update(id, knowledge_base)
        return KnowledgeBase.model_validate(db_knowledge_base)
    
    def delete_knowledge_base(self, id:int) -> KnowledgeBase:
        db_knowledge_base = self.crud.remove(id)
        return KnowledgeBase.model_validate(db_knowledge_base)
