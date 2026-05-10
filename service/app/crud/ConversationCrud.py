from typing import List, Optional

from sqlalchemy.orm import Session, selectinload

from app.crud.BaseCrud import BaseCrud
from app.domain.conversation.model import RagConversation
from app.domain.conversation.schemas import ConversationCreate, ConversationUpdate


class ConversationCrud(BaseCrud[RagConversation, ConversationCreate, ConversationUpdate]):
    def __init__(self, db: Session):
        super().__init__(RagConversation, db)

    def get_by_user_id(self, user_id: int) -> List[RagConversation]:
        return (
            self.db.query(RagConversation)
            .filter(RagConversation.user_id == user_id)
            .order_by(RagConversation.updated_time.desc())
            .all()
        )

    def get_detail(self, conversation_id: int) -> Optional[RagConversation]:
        return (
            self.db.query(RagConversation)
            .options(selectinload(RagConversation.messageList))
            .filter(RagConversation.id == conversation_id)
            .first()
        )

