from app.service.KnowledgeBaseService import KnowledgeBaseService
from app.service.DocumentService import DocumentService
from app.service.FileService import FileService
from app.service.ChatService import ChatService
from app.db.Postgresql import get_db
from app.core.minIO import minio_client
from sqlalchemy.orm import Session
from fastapi import Depends

def get_knowledge_base_service(db: Session = Depends(get_db)):
    return KnowledgeBaseService(db)

def get_document_service(db: Session = Depends(get_db)):
    return DocumentService(db)

def get_file_service(db: Session = Depends(get_db)):
    return FileService(db, minio_client)

def get_chat_service(db: Session = Depends(get_db)):
    return ChatService(db)