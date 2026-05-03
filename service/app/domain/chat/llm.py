from langchain_community.chat_models import ChatTongyi

from app.core.config import settings


def get_llm_model() -> ChatTongyi:
    return ChatTongyi(
        model=settings.llm_model,
        model_kwargs={
            "temperature": settings.temperature,
            "max_tokens": settings.llm_max_tokens,
            "enable_thinking": settings.llm_enable_thinking,
            "enable_search": False,
        },
    )
