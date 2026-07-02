"""
Qdrant vector store — in-memory mode for demo, swap location for production.

Usage:
    from app.core.vectorstore import get_vectorstore

    vs = get_vectorstore()
    vs.add_documents(docs)
    results = vs.similarity_search("revenue growth", k=5)
"""
from __future__ import annotations

from functools import lru_cache

from langchain_core.vectorstores import VectorStore
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.core.config import get_settings

COLLECTION_NAME = "faheem_documents"


def _get_embeddings():
    settings = get_settings()
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=settings.OPENAI_API_KEY,
    )


@lru_cache(maxsize=1)
def get_vectorstore() -> VectorStore:
    settings = get_settings()
    client = QdrantClient(location=settings.QDRANT_URL)

    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=_get_embeddings(),
    )
