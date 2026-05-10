from typing import List

from sqlalchemy.orm import Session

from app.crud.BaseCrud import BaseCrud
from app.domain.message.model import RagMessage
from app.domain.message.schemas import MessageCreate, MessageInDBBase


class MessageCrud(BaseCrud[RagMessage, MessageCreate, MessageInDBBase]):
    def __init__(self, db: Session):
        super().__init__(RagMessage, db)

    def get_by_conversation_id(self, conversation_id: int) -> List[RagMessage]:
        return (
            self.db.query(RagMessage)
            .filter(RagMessage.conversation_id == conversation_id)
            .order_by(RagMessage.created_time)
            .all()
        )
