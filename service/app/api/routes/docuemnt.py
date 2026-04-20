from fastapi import APIRouter, Depends
from app.api.dependencies import get_document_service
from app.service.DocumentService import DocumentService
from app.domain.http.schemas import HTTPResponse, HTTPResponsePage
from app.domain.document.schemas import Document, DocumentCreate, DocumentUpdate, DocumentFilter
from typing import List

router = APIRouter(prefix="/document", tags=["document"])


@router.get("/listByPage/{current}/{size}")
def list_documents(
    current: int,
    size: int,
    filter_obj: DocumentFilter = Depends(),
    service: DocumentService = Depends(get_document_service),
) -> HTTPResponsePage[List[Document]]:
    result = service.get_document_list_by_page(current, size, filter_obj)
    return HTTPResponsePage.ok(data=result.rows, total=result.total, current=result.current, size=result.size)


@router.post("/create")
def create_document(
    payload: DocumentCreate,
    service: DocumentService = Depends(get_document_service),
) -> HTTPResponse[int]:
    result: Document = service.add_document(payload)
    return HTTPResponse.ok(data=result.id)


@router.patch("/update/{id}")
def update_document(
    id: int,
    payload: DocumentUpdate,
    service: DocumentService = Depends(get_document_service),
) -> HTTPResponse[int]:
    result: Document = service.update_document(id, payload)
    return HTTPResponse.ok(data=result.id)


@router.delete("/delete/{id}")
def delete_document(
    id: int,
    service: DocumentService = Depends(get_document_service),
) -> HTTPResponse[int]:
    result: Document = service.delete_document(id)
    return HTTPResponse.ok(data=result.id)
