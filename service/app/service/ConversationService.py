from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.ConversationCrud import ConversationCrud
from app.domain.conversation.schemas import ConversationCreate, ConversationResponse, ConversationDetailResponse


class ConversationService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = ConversationCrud(db)

    def list_by_user(self, user_id: int) -> List[ConversationResponse]:
        items = self.crud.get_by_user_id(user_id)
        return [ConversationResponse.model_validate(item) for item in items]

    def get_detail(self, conversation_id: str) -> ConversationDetailResponse:
        item = self.crud.get_detail(conversation_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return ConversationDetailResponse.model_validate(item)

    def create(self, payload: ConversationCreate) -> ConversationResponse:
        item = self.crud.create(payload)
        return ConversationResponse.model_validate(item)

    def delete(self, conversation_id: str) -> ConversationResponse:
        item = self.crud.remove(conversation_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return ConversationResponse.model_validate(item)
