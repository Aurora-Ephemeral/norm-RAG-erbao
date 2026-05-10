import json
import logging
from typing import Generator

from sqlalchemy.orm import Session

from app.domain.chat.chain import build_preprocessing_chain, build_rag_chain
from app.domain.history.factory import create_history_provider
from app.domain.retrieval.hybrid import HybridPipeline
from app.domain.retrieval.retriever import RAGRetriever
from app.crud.MessageCrud import MessageCrud
from app.domain.message.schemas import MessageCreate
from app.domain.message.model import MessageRoleEnum
logger = logging.getLogger(__name__)


class ChatService:

    def __init__(self, db: Session):
        self.db = db
        self.preprocess_chain = build_preprocessing_chain()
        self.history_provider = create_history_provider(db)
        self.message_crud = MessageCrud(db)

    def ask_stream(self, query: str, conversation_id: int) -> Generator[str, None, None]:
        response_chunks = []
        try:
            chat_history = self.history_provider.get_messages(conversation_id)
            preprocess_result = self.preprocess_chain.invoke({"query": query, "chat_history": chat_history})
            logger.info(
                "ask_stream: original=%r  translated=%r  standard_nos=%r  part_types=%r",
                query,
                preprocess_result.english_query,
                preprocess_result.standard_nos,
                preprocess_result.part_types,
            )

            #TODO: get user accessible knowledge base later
            self.message_crud.create(
                MessageCreate(
                    conversation_id=conversation_id, 
                    content=query,
                    role=MessageRoleEnum.USER
                    )
                )
            retriever_pipeline = HybridPipeline(
                db=self.db,
                standard_nos=preprocess_result.standard_nos or None,
                part_types=preprocess_result.part_types or None,
            )
            retriever = RAGRetriever(pipeline=retriever_pipeline)
            rag_chain = build_rag_chain(retriever)
            for chunk in rag_chain.stream({"english_query": preprocess_result.english_query, "original_query": query, "chat_history": chat_history}):
                response_chunks.append(chunk)
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            self.message_crud.create(
                MessageCreate(
                    conversation_id=conversation_id,
                    content="".join(response_chunks),
                    role=MessageRoleEnum.ASSISTANT
                )
            )
        except Exception as e:
            logger.exception("ask_stream failed for query=%r", query)
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            yield "data: [DONE]\n\n"
