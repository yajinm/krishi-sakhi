"""
Knowledge base models.

Defines Doc, Chunk, and Embedding models for document storage and vector search.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db import Base


class DocSource(str, Enum):
    """Sources of knowledge base documents."""

    UPLOAD = "upload"
    URL = "url"
    API = "api"
    MANUAL = "manual"
    SYSTEM = "system"


class DocType(str, Enum):
    """Types of documents."""

    PDF = "pdf"
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    WORD = "word"
    EXCEL = "excel"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class Doc(Base):
    """
    Document model for storing knowledge base documents.
    
    Contains document metadata, content, and processing status.
    """

    __tablename__ = "docs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    title_ml = Column(String(500), nullable=True)  # Malayalam title
    source = Column(SQLEnum(DocSource), nullable=False)
    doc_type = Column(SQLEnum(DocType), nullable=False)
    url = Column(String(1000), nullable=True)  # Source URL if applicable
    file_path = Column(String(1000), nullable=True)  # Local file path
    content = Column(Text, nullable=True)  # Full document content
    summary = Column(Text, nullable=True)  # Document summary
    summary_ml = Column(Text, nullable=True)  # Malayalam summary
    language = Column(String(10), nullable=False, default="en")  # Document language
    meta_json = Column(JSONB, nullable=True)  # Additional metadata
    file_size = Column(Integer, nullable=True)  # File size in bytes
    page_count = Column(Integer, nullable=True)  # Number of pages
    word_count = Column(Integer, nullable=True)  # Word count
    is_processed = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    chunks = relationship("Chunk", back_populates="doc", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Doc(id={self.id}, title={self.title}, type={self.doc_type})>"

    @property
    def chunk_count(self) -> int:
        """Get number of chunks in this document."""
        return len(self.chunks)

    @property
    def is_malayalam(self) -> bool:
        """Check if document is in Malayalam."""
        return self.language.startswith("ml")


class Chunk(Base):
    """
    Chunk model for storing document segments.
    
    Represents a segment of a document for vector search and retrieval.
    """

    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(UUID(as_uuid=True), ForeignKey("docs.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    text_ml = Column(Text, nullable=True)  # Malayalam translation
    order = Column(Integer, nullable=False)  # Order within document
    start_char = Column(Integer, nullable=True)  # Start character position
    end_char = Column(Integer, nullable=True)  # End character position
    page_number = Column(Integer, nullable=True)  # Page number if applicable
    section = Column(String(255), nullable=True)  # Section or heading
    metadata = Column(JSONB, nullable=True)  # Chunk-specific metadata
    word_count = Column(Integer, nullable=True)  # Word count in chunk
    is_processed = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    doc = relationship("Doc", back_populates="chunks")
    embeddings = relationship("Embedding", back_populates="chunk", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Chunk(id={self.id}, doc_id={self.doc_id}, order={self.order})>"

    @property
    def has_embedding(self) -> bool:
        """Check if chunk has vector embedding."""
        return len(self.embeddings) > 0

    @property
    def preview(self) -> str:
        """Get text preview (first 100 characters)."""
        return self.text[:100] + "..." if len(self.text) > 100 else self.text


class Embedding(Base):
    """
    Embedding model for storing vector embeddings.
    
    Contains vector representations of chunks for semantic search.
    """

    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("chunks.id"), nullable=False, index=True)
    model_name = Column(String(255), nullable=False)  # Embedding model used
    model_version = Column(String(50), nullable=True)  # Model version
    vector = Column(String, nullable=False)  # Vector as string (will be converted to pgvector)
    dimension = Column(Integer, nullable=False)  # Vector dimension
    metadata = Column(JSONB, nullable=True)  # Embedding metadata
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    chunk = relationship("Chunk", back_populates="embeddings")

    def __repr__(self) -> str:
        return f"<Embedding(id={self.id}, chunk_id={self.chunk_id}, model={self.model_name})>"

    @property
    def vector_array(self) -> list[float]:
        """Get vector as Python list."""
        # This would parse the vector string into a list
        # Implementation depends on how vectors are stored
        return []

    @classmethod
    def from_vector(cls, vector: list[float], **kwargs) -> "Embedding":
        """Create embedding from vector list."""
        # This would convert vector list to string format
        vector_str = ",".join(map(str, vector))
        return cls(vector=vector_str, dimension=len(vector), **kwargs)
