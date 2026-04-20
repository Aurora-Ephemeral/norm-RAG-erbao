from app.service.KnowledgeBaseService import KnowledgeBaseService
from app.service.DocumentService import DocumentService
from app.db.Postgresql import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

def get_knowledge_base_service(db: Session = Depends(get_db)):
    return KnowledgeBaseService(db)

def get_document_service(db: Session = Depends(get_db)):
    return DocumentService(db)