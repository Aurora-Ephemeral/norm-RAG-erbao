from app.service.KnowledgeBaseService import KnowledgeBaseService
from app.db.Postgresql import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

def get_knowledge_base_service(db: Session = Depends(get_db)):
    return KnowledgeBaseService(db)