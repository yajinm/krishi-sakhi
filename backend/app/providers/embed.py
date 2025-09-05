"""
Embedding provider for vector search.

Provides text embedding functionality using sentence-transformers.
"""

from abc import ABC, abstractmethod
from typing import List

from app.config import settings


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed text into vector."""
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts into vectors."""
        pass


class SentenceTransformerProvider(EmbeddingProvider):
    """Sentence transformer embedding provider."""
    
    def __init__(self):
        self.model_name = settings.embed_model_name
        self.model = None
    
    def _load_model(self):
        """Load the embedding model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"Failed to load embedding model: {e}")
                self.model = None
    
    def embed_text(self, text: str) -> List[float]:
        """Embed single text."""
        self._load_model()
        if self.model is None:
            return [0.0] * 384  # Default dimension
        
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception:
            return [0.0] * 384
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        self._load_model()
        if self.model is None:
            return [[0.0] * 384] * len(texts)
        
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception:
            return [[0.0] * 384] * len(texts)


def get_embedding_provider() -> EmbeddingProvider:
    """Get embedding provider."""
    return SentenceTransformerProvider()
