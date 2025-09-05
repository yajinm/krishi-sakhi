"""
User and authentication models.

Defines User and AuthProvider models for user management and authentication.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class UserRole(str, Enum):
    """User roles in the system."""

    FARMER = "farmer"
    STAFF = "staff"
    ADMIN = "admin"


class User(Base):
    """
    User model for authentication and basic user information.
    
    Stores user authentication data, preferences, and consent information.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.FARMER)
    locale = Column(String(10), nullable=False, default="ml-IN")  # Malayalam India
    consent_flags = Column(Text, nullable=True)  # JSON string of consent flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    auth_providers = relationship("AuthProvider", back_populates="user", cascade="all, delete-orphan")
    farmer = relationship("Farmer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, phone={self.phone}, role={self.role})>"

    @property
    def is_farmer(self) -> bool:
        """Check if user is a farmer."""
        return self.role == UserRole.FARMER

    @property
    def is_staff(self) -> bool:
        """Check if user is staff."""
        return self.role == UserRole.STAFF

    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN


class AuthProvider(Base):
    """
    Authentication provider model.
    
    Stores OAuth and other authentication provider information.
    """

    __tablename__ = "auth_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # phone, google, facebook, etc.
    provider_id = Column(String(255), nullable=False)  # phone number, email, etc.
    provider_data = Column(Text, nullable=True)  # JSON string of provider-specific data
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="auth_providers")

    def __repr__(self) -> str:
        return f"<AuthProvider(id={self.id}, provider={self.provider}, provider_id={self.provider_id})>"
