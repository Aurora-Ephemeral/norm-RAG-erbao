from sqlalchemy.orm import Session

from app.crud.BaseCrud import BaseCrud
from app.domain.document.model import Document
from app.domain.document.schemas import DocumentCreate, DocumentUpdate


class DocumentCrud(BaseCrud[Document, DocumentCreate, DocumentUpdate]):
    def __init__(self, db: Session):
        super().__init__(Document, db)
