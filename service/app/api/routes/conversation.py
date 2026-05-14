from typing import List

from fastapi import APIRouter, Depends

from app.api.dependencies import get_conversation_service
from app.domain.conversation.schemas import ConversationCreate, ConversationResponse, ConversationDetailResponse
from app.domain.http.schemas import HTTPResponse
from app.service.ConversationService import ConversationService

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.get("/list/{user_id}")
def list_conversation(
    user_id: int,
    service: ConversationService = Depends(get_conversation_service),
) -> HTTPResponse[List[ConversationResponse]]:
    result = service.list_by_user(user_id)
    return HTTPResponse.ok(data=result)


@router.get("/detail/{conversation_id}")
def get_conversation_detail(
    conversation_id: str,
    service: ConversationService = Depends(get_conversation_service),
) -> HTTPResponse[ConversationDetailResponse]:
    result = service.get_detail(conversation_id)
    return HTTPResponse.ok(data=result)


@router.post("/create")
def create_conversation(
    payload: ConversationCreate,
    service: ConversationService = Depends(get_conversation_service),
) -> HTTPResponse[ConversationResponse]:
    result = service.create(payload)
    return HTTPResponse.ok(data=result)


@router.delete("/delete/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    service: ConversationService = Depends(get_conversation_service),
) -> HTTPResponse[str]:
    result = service.delete(conversation_id)
    return HTTPResponse.ok(data=result.id)
