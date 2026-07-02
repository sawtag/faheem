from functools import lru_cache

from langchain_core.language_models import BaseChatModel

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    settings = get_settings()
    if settings.LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
        )
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )
