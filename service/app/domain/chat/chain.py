from operator import itemgetter
from typing import List

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable, RunnableLambda

from .llm import get_llm_model
from .prompt import prompt_rag, prompt_preprocess
from app.domain.chat.schemas import QueryProcessing

llm = get_llm_model()

def build_preprocessing_chain() -> Runnable[dict, QueryProcessing]:
    return prompt_preprocess | llm.with_structured_output(QueryProcessing)

def _format_docs(docs: List[Document]) -> str:
    if not docs: 
        return "No relevant documents found."
    parts = []
    for doc in docs:
        meta = doc.metadata
        page = meta.get("page_no") or "?"
        section_path: list = meta.get("section_path") or []
        section = " / ".join(section_path) if section_path else (meta.get("section_title") or "—")
        chunk_type = meta.get("chunk_type", "text")
        type_label = "Table" if chunk_type == "table" else "Text"
        refs_str: str =', '.join(meta.get("referenced_standards") or [])
        header = f"[§ {section}, p. {page} | {type_label} | refs: {refs_str}]"
        body = doc.page_content
        if meta.get("footnotes"):
            body += f"\nFootnotes: {meta.get('footnotes')}"
        parts.append(f"{header}\n{body}")
    return "\n\n---\n\n".join(parts)
    


def build_rag_chain(retriever: BaseRetriever) -> Runnable:
    
    #TODO: consider history management later
    return (
        {
            "context": itemgetter("english_query") | retriever | RunnableLambda(_format_docs),
            "query": itemgetter("original_query"),
        }
        | prompt_rag
        | llm
        | StrOutputParser()
    )
