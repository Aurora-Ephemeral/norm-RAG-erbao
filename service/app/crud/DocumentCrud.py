from sqlalchemy.orm import Session
from typing import Optional
from app.crud.BaseCrud import BaseCrud
from app.domain.document.model import Document
from app.domain.document.schemas import DocumentCreate, DocumentUpdate


class DocumentCrud(BaseCrud[Document, DocumentCreate, DocumentUpdate]):
    def __init__(self, db: Session):
        super().__init__(Document, db)
    
    def get_by_kb_id_and_file_id(self, knowledge_base_id: int, file_id: int) -> Optional[Document]:
        return self.db.query(self.model).filter(
            self.model.knowledge_base_id == knowledge_base_id,
            self.model.file_id == file_id
        ).first()
