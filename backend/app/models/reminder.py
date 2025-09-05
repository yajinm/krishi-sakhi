"""
Reminder and notification models.

Defines Reminder and Notification models for scheduling and delivering alerts.
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


class ReminderKind(str, Enum):
    """Types of reminders."""

    FARMING_ACTIVITY = "farming_activity"
    WEATHER_ALERT = "weather_alert"
    PEST_ALERT = "pest_alert"
    PRICE_ALERT = "price_alert"
    HARVEST_TIME = "harvest_time"
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    PESTICIDE = "pesticide"
    MARKET_VISIT = "market_visit"
    MEETING = "meeting"
    PAYMENT = "payment"
    CUSTOM = "custom"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""

    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    EMAIL = "email"
    IN_APP = "in_app"
    VOICE_CALL = "voice_call"


class NotificationStatus(str, Enum):
    """Notification delivery status."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Reminder(Base):
    """
    Reminder model for scheduling farming activities and alerts.
    
    Contains reminder details, scheduling, and recurrence information.
    """

    __tablename__ = "reminders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=True, index=True)
    kind = Column(SQLEnum(ReminderKind), nullable=False)
    title = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    text_ml = Column(Text, nullable=True)  # Malayalam translation
    due_ts = Column(DateTime(timezone=True), nullable=False, index=True)  # Due timestamp
    recur_cron = Column(String(100), nullable=True)  # Cron expression for recurrence
    is_recurring = Column(Boolean, default=False, nullable=False)
    is_paused = Column(Boolean, default=False, nullable=False)
    priority = Column(Integer, default=100, nullable=False)  # Lower number = higher priority
    metadata = Column(JSONB, nullable=True)  # Additional reminder metadata
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farmer = relationship("Farmer", back_populates="reminders")
    field = relationship("Field", back_populates="reminders")
    notifications = relationship("Notification", back_populates="reminder", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Reminder(id={self.id}, farmer_id={self.farmer_id}, kind={self.kind})>"

    @property
    def is_due(self) -> bool:
        """Check if reminder is due."""
        return datetime.utcnow() >= self.due_ts

    @property
    def is_overdue(self) -> bool:
        """Check if reminder is overdue."""
        return datetime.utcnow() > self.due_ts

    def pause(self) -> None:
        """Pause the reminder."""
        self.is_paused = True

    def resume(self) -> None:
        """Resume the reminder."""
        self.is_paused = False

    def calculate_next_due(self) -> Optional[datetime]:
        """Calculate next due date for recurring reminders."""
        if not self.is_recurring or not self.recur_cron:
            return None
        
        # This would typically use a cron parser library
        # For now, return None as placeholder
        return None


class Notification(Base):
    """
    Notification model for tracking message delivery.
    
    Stores notification details, delivery status, and channel information.
    """

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)
    reminder_id = Column(UUID(as_uuid=True), ForeignKey("reminders.id"), nullable=True, index=True)
    channel = Column(SQLEnum(NotificationChannel), nullable=False)
    recipient = Column(String(255), nullable=False)  # Phone, email, device ID, etc.
    title = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    message_ml = Column(Text, nullable=True)  # Malayalam translation
    payload_json = Column(JSONB, nullable=True)  # Channel-specific payload
    status = Column(SQLEnum(NotificationStatus), nullable=False, default=NotificationStatus.PENDING)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)  # When to send
    sent_at = Column(DateTime(timezone=True), nullable=True)  # When sent
    delivered_at = Column(DateTime(timezone=True), nullable=True)  # When delivered
    error_message = Column(Text, nullable=True)  # Error details if failed
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    provider_response = Column(JSONB, nullable=True)  # Provider response data
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farmer = relationship("Farmer", back_populates="notifications")
    reminder = relationship("Reminder", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, farmer_id={self.farmer_id}, channel={self.channel})>"

    @property
    def is_sent(self) -> bool:
        """Check if notification has been sent."""
        return self.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]

    @property
    def is_failed(self) -> bool:
        """Check if notification failed."""
        return self.status == NotificationStatus.FAILED

    @property
    def can_retry(self) -> bool:
        """Check if notification can be retried."""
        return (
            self.status == NotificationStatus.FAILED
            and self.retry_count < self.max_retries
        )

    def mark_sent(self) -> None:
        """Mark notification as sent."""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.utcnow()

    def mark_delivered(self) -> None:
        """Mark notification as delivered."""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = datetime.utcnow()

    def mark_failed(self, error_message: str) -> None:
        """Mark notification as failed."""
        self.status = NotificationStatus.FAILED
        self.error_message = error_message
        self.retry_count += 1

    def cancel(self) -> None:
        """Cancel the notification."""
        self.status = NotificationStatus.CANCELLED
