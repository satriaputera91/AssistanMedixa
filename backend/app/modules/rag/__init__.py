"""
Dedicated RAG (Retrieval-Augmented Generation) & Knowledge Management Module.
Includes Qdrant vector database, Generative AI embeddings, semantic section chunker, two-stage reranker, document file uploader, and form ingestion.
"""
from app.modules.rag.rag_service import qdrant_rag_service, DedicatedQdrantRAGService
from app.modules.rag.initial_knowledge import INITIAL_KNOWLEDGE_BASE

__all__ = ["qdrant_rag_service", "DedicatedQdrantRAGService", "INITIAL_KNOWLEDGE_BASE"]
