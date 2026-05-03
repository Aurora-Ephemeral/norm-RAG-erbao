from .llm import get_llm_model
from .prompt import _PREPROCESS_SYSTEM
from langchain_core.prompts import ChatPromptTemplate
from app.domain.chat.schemas import QueryProcessing
from langchain_core.runnables import Runnable

def build_preprocessing_chain() -> Runnable[dict, QueryProcessing]:
    llm = get_llm_model()
    return ChatPromptTemplate.from_messages([
        ("system", _PREPROCESS_SYSTEM),
        ("human", "{query}") 
    ]) | llm.with_structured_output(QueryProcessing)

def build_rag_chain():
    pass