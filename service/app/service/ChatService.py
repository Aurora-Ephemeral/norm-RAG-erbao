import json
import logging
from typing import Generator

from sqlalchemy.orm import Session

from app.domain.chat.chain import build_preprocessing_chain

logger = logging.getLogger(__name__)


class ChatService:

    def __init__(self, db: Session):
        self.db = db
        self.preprocess_chain = build_preprocessing_chain()

    def ask_stream(self, query: str, session_id: str) -> Generator[str, None, None]:
        preprocess_result = self.preprocess_chain.invoke({"query": query})
        logger.info("ask_stream: original=%r  translated=%r", query, preprocess_result.english_query)
        yield f"data: {json.dumps({'content': preprocess_result.english_query}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
