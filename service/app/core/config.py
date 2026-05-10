import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('APP_ENV', 'development')}",
    )

    temperature: float = 0.0
    llm_model: str = "qwen3-max"
    llm_max_tokens: int = 2048
    llm_enable_thinking: bool = False
    embedding_model: str = "text-embedding-v3"
    reranker_model: str = "gte-rerank"
    vector_search_top_k: int = 10
    fulltext_search_top_k: int = 10
    hybrid_candidate_k: int = 30
    rerank_top_k: int = 8
    last_n_messages: int = 10
    history_strategy: str = "sliding_window"
    database_url: str

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    minio_secure: bool = False

    redis_url: str

settings = Settings()
