"""
Advisory system models.

Defines Advisory, AdvisoryRule, and Trigger models for personalized farming advice.
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


class AdvisorySeverity(str, Enum):
    """Advisory severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AdvisorySource(str, Enum):
    """Sources of advisories."""

    RULE_ENGINE = "rule_engine"
    WEATHER = "weather"
    PEST_ALERT = "pest_alert"
    PRICE_ALERT = "price_alert"
    CROP_CALENDAR = "crop_calendar"
    EXPERT = "expert"
    AI_MODEL = "ai_model"
    MANUAL = "manual"


class TriggerType(str, Enum):
    """Types of advisory triggers."""

    WEATHER = "weather"
    PEST = "pest"
    PRICE = "price"
    CROP_STAGE = "crop_stage"
    TIME_BASED = "time_based"
    MANUAL = "manual"
    EXTERNAL_API = "external_api"


class Advisory(Base):
    """
    Advisory model for storing personalized farming advice.
    
    Contains advice text, severity, source, and acknowledgment status.
    """

    __tablename__ = "advisories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    text_ml = Column(Text, nullable=True)  # Malayalam translation
    severity = Column(SQLEnum(AdvisorySeverity), nullable=False, default=AdvisorySeverity.MEDIUM)
    tags = Column(JSONB, nullable=True)  # Array of tags for categorization
    source = Column(SQLEnum(AdvisorySource), nullable=False)
    source_data = Column(JSONB, nullable=True)  # Source-specific data
    rule_id = Column(UUID(as_uuid=True), ForeignKey("advisory_rules.id"), nullable=True)
    is_acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Advisory expiration
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farmer = relationship("Farmer", back_populates="advisories")
    field = relationship("Field", back_populates="advisories")
    rule = relationship("AdvisoryRule", back_populates="advisories")

    def __repr__(self) -> str:
        return f"<Advisory(id={self.id}, farmer_id={self.farmer_id}, severity={self.severity})>"

    @property
    def is_expired(self) -> bool:
        """Check if advisory has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_urgent(self) -> bool:
        """Check if advisory is urgent (high or critical severity)."""
        return self.severity in [AdvisorySeverity.HIGH, AdvisorySeverity.CRITICAL]

    def acknowledge(self) -> None:
        """Mark advisory as acknowledged."""
        self.is_acknowledged = True
        self.acknowledged_at = datetime.utcnow()

    def mark_read(self) -> None:
        """Mark advisory as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()


class AdvisoryRule(Base):
    """
    Advisory rule model for defining advisory generation rules.
    
    Contains rule conditions, actions, and metadata.
    """

    __tablename__ = "advisory_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    conditions = Column(JSONB, nullable=False)  # Rule conditions in JSON format
    actions = Column(JSONB, nullable=False)  # Rule actions in JSON format
    priority = Column(Integer, default=100, nullable=False)  # Lower number = higher priority
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System vs user-defined rules
    created_by = Column(UUID(as_uuid=True), nullable=True)  # User who created the rule
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    advisories = relationship("Advisory", back_populates="rule")
    triggers = relationship("Trigger", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AdvisoryRule(id={self.id}, name={self.name}, priority={self.priority})>"

    @property
    def is_builtin(self) -> bool:
        """Check if this is a built-in system rule."""
        return self.is_system


class Trigger(Base):
    """
    Trigger model for scheduling advisory rule evaluations.
    
    Defines when and how often rules should be evaluated.
    """

    __tablename__ = "triggers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("advisory_rules.id"), nullable=False, index=True)
    trigger_type = Column(SQLEnum(TriggerType), nullable=False)
    schedule = Column(String(100), nullable=True)  # Cron expression for time-based triggers
    conditions = Column(JSONB, nullable=True)  # Additional trigger conditions
    is_active = Column(Boolean, default=True, nullable=False)
    last_triggered = Column(DateTime(timezone=True), nullable=True)
    next_trigger = Column(DateTime(timezone=True), nullable=True)
    trigger_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    rule = relationship("AdvisoryRule", back_populates="triggers")

    def __repr__(self) -> str:
        return f"<Trigger(id={self.id}, rule_id={self.rule_id}, type={self.trigger_type})>"

    @property
    def is_due(self) -> bool:
        """Check if trigger is due for execution."""
        if not self.next_trigger:
            return False
        return datetime.utcnow() >= self.next_trigger

    def mark_triggered(self) -> None:
        """Mark trigger as executed."""
        self.last_triggered = datetime.utcnow()
        self.trigger_count += 1
