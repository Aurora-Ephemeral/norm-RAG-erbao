from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.DocumentCrud import DocumentCrud
from app.domain.common.schemas import PageResult
from app.domain.document.schemas import Document, DocumentCreate, DocumentUpdate, DocumentFilter


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = DocumentCrud(db)

    def get_document_list_by_page(self, current: int, size: int, filter_obj:DocumentFilter) -> PageResult[Document]:
        filter_dict = filter_obj.model_dump(exclude_none=True)
        result = self.crud.get_by_page(current, size, filter_dict)
        convert_rows = [Document.model_validate(row) for row in result.rows]
        return PageResult[Document](rows=convert_rows, current=current, size=size, total=result.total)

    def add_document(self, payload: DocumentCreate) -> Document:
        try:
            db_document = self.crud.create(payload)
            return Document.model_validate(db_document)
        except IntegrityError as exc:
            error_message = str(exc.orig).lower() if exc.orig else str(exc).lower()
            if "duplicate key" in error_message or "unique constraint" in error_message:
                raise HTTPException(status_code=409, detail="Document already exists in this knowledge base")
            raise

    def update_document(self, id: int, payload: DocumentUpdate) -> Document:
        db_document = self.crud.update(id, payload)
        return Document.model_validate(db_document)

    def delete_document(self, id: int) -> Document:
        db_document = self.crud.remove(id)
        if db_document is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return Document.model_validate(db_document)
