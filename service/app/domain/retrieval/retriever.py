from typing import List

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict

from app.domain.chunk.model import RagChunk
from app.domain.retrieval.pipeline import RetrievalPipeline


def _chunk_to_document(chunk: RagChunk) -> Document:
    return Document(
        page_content=chunk.chunk_text,
        metadata={
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "section_title": chunk.section_title,
            "page_no": chunk.page_no,
            **(chunk.metadata_json or {}),
        },
    )


class RAGRetriever(BaseRetriever):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    pipeline: RetrievalPipeline

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        chunks = self.pipeline.search(query)
        return [_chunk_to_document(chunk) for chunk in chunks]
