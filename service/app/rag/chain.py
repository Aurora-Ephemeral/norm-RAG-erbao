from langchain_community.chat_models import ChatTongyi
from app.core import settings
from .prompt import build_few_shot_prompt_template
from langchain_core.output_parsers import StrOutputParser
def build_rag_chain():
    #  TODO: implement retriever

    # select model
    try:
        llm = ChatTongyi(
            model=settings.llm_model,
            streaming=True,
            temperature=settings.temperature
        )
    except Exception as e:
        print(f"LLM Initialization failed: {e}")
        llm = None

    prompt = build_few_shot_prompt_template()

    chain = prompt | llm | StrOutputParser()

    return chain
