"""
Audit and privacy models.

Defines AuditLog and Consent models for compliance and privacy management.
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
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db import Base


class AuditAction(str, Enum):
    """Types of audit actions."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    EXPORT_DATA = "export_data"
    DELETE_DATA = "delete_data"
    CONSENT_GRANT = "consent_grant"
    CONSENT_REVOKE = "consent_revoke"
    PASSWORD_CHANGE = "password_change"
    PROFILE_UPDATE = "profile_update"
    API_ACCESS = "api_access"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    SYSTEM_ACTION = "system_action"


class ConsentKind(str, Enum):
    """Types of user consent."""

    DATA_PROCESSING = "data_processing"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    LOCATION = "location"
    NOTIFICATIONS = "notifications"
    VOICE_RECORDING = "voice_recording"
    DATA_SHARING = "data_sharing"
    THIRD_PARTY = "third_party"
    RESEARCH = "research"
    PROFILING = "profiling"


class AuditLog(Base):
    """
    Audit log model for tracking user actions and system events.
    
    Provides comprehensive audit trail for compliance and security.
    """

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    target_type = Column(String(100), nullable=True)  # Type of target (User, Farmer, etc.)
    target_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # ID of target object
    resource = Column(String(255), nullable=True)  # Resource being accessed
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6 address
    user_agent = Column(Text, nullable=True)  # User agent string
    session_id = Column(String(255), nullable=True)  # Session identifier
    request_id = Column(String(255), nullable=True)  # Request identifier
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    success = Column(Boolean, nullable=False, default=True)  # Action success status
    error_message = Column(Text, nullable=True)  # Error message if failed
    metadata = Column(JSONB, nullable=True)  # Additional audit metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action})>"

    @property
    def is_successful(self) -> bool:
        """Check if action was successful."""
        return self.success

    @property
    def is_failed(self) -> bool:
        """Check if action failed."""
        return not self.success

    @classmethod
    def create_log(
        cls,
        action: AuditAction,
        user_id: Optional[uuid.UUID] = None,
        target_type: Optional[str] = None,
        target_id: Optional[uuid.UUID] = None,
        resource: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> "AuditLog":
        """Create audit log entry."""
        return cls(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            request_id=request_id,
            success=success,
            error_message=error_message,
            metadata=metadata,
        )


class Consent(Base):
    """
    Consent model for managing user privacy preferences.
    
    Tracks user consent for various data processing activities.
    """

    __tablename__ = "consents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    kind = Column(SQLEnum(ConsentKind), nullable=False, index=True)
    granted = Column(Boolean, nullable=False, default=False)
    granted_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    purpose = Column(Text, nullable=True)  # Purpose of data processing
    purpose_ml = Column(Text, nullable=True)  # Malayalam purpose
    legal_basis = Column(String(255), nullable=True)  # Legal basis for processing
    retention_period = Column(String(100), nullable=True)  # Data retention period
    third_parties = Column(JSONB, nullable=True)  # Third parties with access
    conditions = Column(JSONB, nullable=True)  # Additional conditions
    version = Column(String(50), nullable=False, default="1.0")  # Consent version
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="consents")

    def __repr__(self) -> str:
        return f"<Consent(id={self.id}, user_id={self.user_id}, kind={self.kind}, granted={self.granted})>"

    @property
    def is_granted(self) -> bool:
        """Check if consent is currently granted."""
        return self.granted and not self.revoked_at

    @property
    def is_revoked(self) -> bool:
        """Check if consent has been revoked."""
        return self.revoked_at is not None

    @property
    def is_expired(self) -> bool:
        """Check if consent has expired."""
        # This would check against retention period
        # Implementation depends on retention period format
        return False

    def grant(self) -> None:
        """Grant consent."""
        self.granted = True
        self.granted_at = datetime.utcnow()
        self.revoked_at = None

    def revoke(self) -> None:
        """Revoke consent."""
        self.granted = False
        self.revoked_at = datetime.utcnow()

    @classmethod
    def get_user_consent(cls, user_id: uuid.UUID, kind: ConsentKind) -> Optional["Consent"]:
        """Get user's consent for a specific kind."""
        # This would be implemented as a query method
        return None

    @classmethod
    def has_consent(cls, user_id: uuid.UUID, kind: ConsentKind) -> bool:
        """Check if user has granted consent for a specific kind."""
        consent = cls.get_user_consent(user_id, kind)
        return consent is not None and consent.is_granted
