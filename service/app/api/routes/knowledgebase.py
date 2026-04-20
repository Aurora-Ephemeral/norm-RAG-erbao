"""
four core conception in domain of knwoledage base function: 
    1. knowledge base: store and manage serveal documents
    2. document: an item in knowledge base, it has some attributes, such as title, content, author, create time, update time, etc.
    3. file: raw data of document, it can be uploaded and downloaded. one file can belong to multiple documents in different knowledge bases.
    4. chunk: a part of document, it has embedded value and can be used to search and preview.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.api.dependencies import get_knowledge_base_service
from app.service.KnowledgeBaseService import KnowledgeBaseService
from app.domain.http.schemas import HTTPResponse
from app.domain.knowledge_base.schemas import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBase
from typing import List

router = APIRouter(prefix="/knowledge_base", tags=["knowledge_base"])

# knowledge base related api
@router.get("/listAll")
def list_knowledge_bases(
    knowledge_base_service: KnowledgeBaseService = Depends(get_knowledge_base_service)
) -> HTTPResponse[List[KnowledgeBase]]:
    result:List[KnowledgeBase] = knowledge_base_service.get_knowledge_base_list();
    return HTTPResponse.ok(data=result)


@router.post("/create")
def create_knowledge_base(
    payload: KnowledgeBaseCreate,
    service: KnowledgeBaseService = Depends(get_knowledge_base_service)
    ) -> HTTPResponse[int]:
    result:KnowledgeBase = service.add_knowledge_base(payload)
    return HTTPResponse.ok(data=result.id)

@router.delete("/delete/{id}")
def delete_knowledge_base(id: int, service: KnowledgeBaseService = Depends(get_knowledge_base_service)):
    result:KnowledgeBase = service.delete_knowledge_base(id)
    return HTTPResponse.ok(data=result.id)

@router.patch("/update/{id}")
def update_knowledge_base(
    id: int,
    payload: KnowledgeBaseUpdate,
    service: KnowledgeBaseService = Depends(get_knowledge_base_service)
) -> HTTPResponse[int]:
    result:KnowledgeBase = service.update_knowledge_base(id, payload)
    return HTTPResponse.ok(data=result.id)


# file related api
@router.post("/file/upload")
def upload_file():
    # TODO: Implement file upload logic
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/file/preview")
def preview_file():
    # TODO: Implement file preview logic
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/file/listByPage")
def list_files():
    # TODO: Implement file list logic
    raise HTTPException(status_code=501, detail="Not implemented")


# chunk related api
# TODO:
