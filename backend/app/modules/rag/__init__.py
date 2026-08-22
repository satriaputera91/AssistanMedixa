"""
Dedicated RAG (Retrieval-Augmented Generation) & Knowledge Management Module.
Includes Qdrant vector database, Gemini embeddings, semantic section chunker, two-stage reranker, document file uploader, and form ingestion.
"""
from app.modules.rag.rag_service import qdrant_rag_service

__all__ = ["qdrant_rag_service"]
