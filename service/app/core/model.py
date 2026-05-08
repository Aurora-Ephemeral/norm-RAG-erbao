from typing import List

from langchain_community.document_compressors.dashscope_rerank import DashScopeRerank

from app.core.config import settings


def return_rerank_model():
    return DashScopeRerank(
        model=settings.reranker_model,
        top_n=settings.rerank_top_k
    )