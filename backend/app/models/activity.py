"""
Activity tracking models.

Defines Activity and Media models for logging farming activities.
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
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db import Base


class ActivityKind(str, Enum):
    """Types of farming activities."""

    SOWING = "sowing"
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    PESTICIDE = "pesticide"
    HARVEST = "harvest"
    PLOWING = "plowing"
    WEEDING = "weeding"
    PRUNING = "pruning"
    TRANSPLANTING = "transplanting"
    THINNING = "thinning"
    MULCHING = "mulching"
    TRELLISING = "trellising"
    POLLINATION = "pollination"
    PEST_CONTROL = "pest_control"
    DISEASE_CONTROL = "disease_control"
    SOIL_TESTING = "soil_testing"
    WEATHER_OBSERVATION = "weather_observation"
    MARKET_VISIT = "market_visit"
    OTHER = "other"


class MediaType(str, Enum):
    """Types of media attachments."""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


class Activity(Base):
    """
    Activity model for logging farming activities.
    
    Stores activity details including text, parsed data, and metadata.
    """

    __tablename__ = "activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    kind = Column(SQLEnum(ActivityKind), nullable=True)  # Parsed activity type
    text_raw = Column(Text, nullable=True)  # Original text input
    text_processed = Column(Text, nullable=True)  # Processed/cleaned text
    data_json = Column(JSONB, nullable=True)  # Parsed structured data
    language = Column(String(10), nullable=True)  # Detected language (ml-IN, en)
    confidence_score = Column(Integer, nullable=True)  # NLU confidence (0-100)
    is_verified = Column(Boolean, default=False, nullable=False)  # Farmer verified
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farmer = relationship("Farmer", back_populates="activities")
    field = relationship("Field", back_populates="activities")
    media = relationship("Media", back_populates="activity", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, farmer_id={self.farmer_id}, kind={self.kind})>"

    @property
    def parsed_data(self) -> Optional[dict]:
        """Get parsed activity data as dictionary."""
        return self.data_json if self.data_json else None

    @property
    def has_media(self) -> bool:
        """Check if activity has media attachments."""
        return len(self.media) > 0


class Media(Base):
    """
    Media model for storing file attachments.
    
    Handles images, audio, video, and document attachments for activities.
    """

    __tablename__ = "media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_id = Column(UUID(as_uuid=True), ForeignKey("activities.id"), nullable=False, index=True)
    media_type = Column(SQLEnum(MediaType), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    mime_type = Column(String(100), nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # For audio/video
    width = Column(Integer, nullable=True)  # For images/video
    height = Column(Integer, nullable=True)  # For images/video
    metadata = Column(JSONB, nullable=True)  # Additional file metadata
    is_processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    activity = relationship("Activity", back_populates="media")

    def __repr__(self) -> str:
        return f"<Media(id={self.id}, type={self.media_type}, filename={self.filename})>"

    @property
    def file_extension(self) -> str:
        """Get file extension from filename."""
        return self.filename.split(".")[-1].lower() if "." in self.filename else ""

    @property
    def is_image(self) -> bool:
        """Check if media is an image."""
        return self.media_type == MediaType.IMAGE

    @property
    def is_audio(self) -> bool:
        """Check if media is audio."""
        return self.media_type == MediaType.AUDIO

    @property
    def is_video(self) -> bool:
        """Check if media is video."""
        return self.media_type == MediaType.VIDEO

    @property
    def is_document(self) -> bool:
        """Check if media is a document."""
        return self.media_type == MediaType.DOCUMENT
