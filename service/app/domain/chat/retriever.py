from typing import List, Optional

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict
from sqlalchemy.orm import Session
from app.core.embedding import embed_query
from app.crud.ChunkCrud import ChunkCrud


class VectorRetriever(BaseRetriever):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    db: Session
    knowledge_base_id: Optional[List[str]] = None
    standard_nos: Optional[List[str]] = None
    part_types: Optional[List[str]] = None

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        query_vector = embed_query(query)
        chunks = ChunkCrud(self.db).vector_search(
            query_vector=query_vector,
            knowledge_base_id=self.knowledge_base_id,
            standard_nos=self.standard_nos,
            part_types=self.part_types,
        )
        return [
            Document(
                page_content=chunk.chunk_text,
                metadata={
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "section_title": chunk.section_title,
                    "page_no": chunk.page_no,
                    **(chunk.metadata_json or {}),
                },
            )
            for chunk in chunks
        ]
