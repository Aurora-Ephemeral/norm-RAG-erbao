import json
import logging
from typing import Generator

from sqlalchemy.orm import Session

from app.domain.chat.chain import build_preprocessing_chain, build_rag_chain
from app.domain.chat.retriever import VectorRetriever


logger = logging.getLogger(__name__)


class ChatService:

    def __init__(self, db: Session):
        self.db = db
        self.preprocess_chain = build_preprocessing_chain()

    def ask_stream(self, query: str, session_id: str) -> Generator[str, None, None]:
        try:
            preprocess_result = self.preprocess_chain.invoke({"query": query})
            logger.info(
                "ask_stream: original=%r  translated=%r  standard_nos=%r  part_types=%r",
                query,
                preprocess_result.english_query,
                preprocess_result.standard_nos,
                preprocess_result.part_types,
            )

            #TODO: get user accessible knowledge base later

            #TODO: get user history later

            retriever = VectorRetriever(
                db=self.db,
                standard_nos=preprocess_result.standard_nos or None,
                part_types=preprocess_result.part_types or None,
            )
            rag_chain = build_rag_chain(retriever)

            for chunk in rag_chain.stream({"english_query": preprocess_result.english_query, "original_query": query}):
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.exception("ask_stream failed for query=%r", query)
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            yield "data: [DONE]\n\n"
